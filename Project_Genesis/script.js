let currentCiv = null;
let currentTab = 'archives';
let currentFile = null;
let currentView = 'timeline';

// Categories Mapping
const CATEGORY_ICONS = {
    "philosophical": "🧠",
    "scientific": "🔬",
    "social": "👥",
    "mundane": "☕",
    "absurd": "🌀",
    "speculative": "🔮"
};

let currentHeatFilter = 'all';
let timelineTab = 'for-you';
let allRecentDiscussions = [];

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    switchView(currentView);
    refreshAll();
    setupFilters();
    setInterval(refreshAll, 10000); // 10秒おきに更新
});

function refreshAll() {
    if (currentView === 'timeline') fetchTimeline();
    fetchCivilizations();
    fetchLegends();
    if (currentView === 'pado') fetchPadoTales();
    if (currentView === 'genealogy') fetchGenealogy();
    if (currentView === 'world') refreshMap();
}

function switchView(view) {
    currentView = view;
    document.querySelectorAll('.view-section').forEach(s => s.style.display = 'none');
    const target = document.getElementById(`${view}-view`);
    if (target) target.style.display = 'block';

    // Show/Hide Tabs
    const tabs = document.querySelector('.timeline-tabs');
    if (tabs) tabs.style.display = (view === 'timeline') ? 'flex' : 'none';

    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(btn => {
        if (btn.getAttribute('onclick')?.includes(view)) {
            btn.classList.add('active');
        }
    });

    if (view === 'timeline') fetchTimeline();
    if (view === 'civilizations') fetchCivilizations();
    if (view === 'pado') fetchPadoTales();
    if (view === 'genealogy') fetchGenealogy();
    if (view === 'world') refreshMap();
}

function switchTimelineTab(tab) {
    timelineTab = tab;
    document.querySelectorAll('.timeline-tabs .tab').forEach(t => {
        t.classList.remove('active');
        if (t.innerText.toLowerCase().includes(tab.replace('-', ' '))) t.classList.add('active');
    });
    fetchTimeline();
}

function refreshMap() {
    const img = document.getElementById('world-map-img');
    if (img) {
        // キャッシュ回避のためにタイムスタンプを付加
        img.src = `00_World_Atlas/World_Map.png?t=${new Date().getTime()}`;
    }
}

async function fetchGenealogy() {
    const response = await fetch('/api/genealogy');
    const data = await response.json();
    const container = document.getElementById('mermaid-graph');

    if (data.nodes.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:var(--text-dim);">記録された系譜がありません。</p>';
        return;
    }

    // Mermaid String Generation
    let mermaidText = 'graph TD\n';

    // Add nodes with custom styling (classes)
    data.nodes.forEach(node => {
        mermaidText += `  ${node.id.replace(/-/g, '_')}["${node.id}"]\n`;
    });

    // Add edges
    data.edges.forEach(edge => {
        mermaidText += `  ${edge.from.replace(/-/g, '_')} --> ${edge.to.replace(/-/g, '_')}\n`;
    });

    // Style
    mermaidText += '\n  classDef default fill:#1a1a2e,stroke:#4ecca3,color:#fff,stroke-width:2px;\n';

    // Render using mermaid.render
    const { svg } = await mermaid.render('mermaid-svg', mermaidText);
    container.innerHTML = svg;
}

function setupFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentHeatFilter = btn.dataset.heat;
            fetchTimeline();
        };
    });
}

function applyFilters() {
    fetchTimeline();
}

async function updateGlobalStats(discussions, civs) {
    const statsBar = document.getElementById('global-stats-bar');
    const simStats = document.getElementById('sim-stats');
    if (!statsBar) return;

    const avgHeat = discussions.length > 0
        ? Math.round(discussions.reduce((acc, d) => acc + d.heat, 0) / discussions.length)
        : 0;

    statsBar.innerHTML = `
        <div class="stat-group">
            <span class="stat-label">🌍 総文明</span>
            <span class="stat-val-large">${civs.length}</span>
        </div>
        <div class="stat-group">
            <span class="stat-label">💬 総議論</span>
            <span class="stat-val-large">${discussions.length}</span>
        </div>
        <div class="stat-group">
            <span class="stat-label">🔥 世界の熱量</span>
            <span class="stat-val-large" style="color: ${avgHeat > 70 ? 'var(--cat-absurd)' : 'var(--accent-cyan)'}">${avgHeat}</span>
        </div>
    `;

    if (simStats) {
        simStats.innerHTML = `
            <div class="res-meter-group">
                <div class="res-row">
                    <span class="text-muted" style="font-size:0.8rem;">シミュレーション負荷</span>
                    <div class="res-bar-bg"><div class="res-bar-fill" style="width:30%; background:var(--accent-primary);"></div></div>
                    <span class="res-val" style="font-size:0.8rem;">Low</span>
                </div>
            </div>
        `;
    }

    // World Pulse に最新イベントを流す (簡易実装: 最新の議論をイベントとして表示)
    const worldLog = document.getElementById('world-log');
    if (worldLog && discussions.length > 0) {
        const latest = discussions.slice(0, 5);
        worldLog.innerHTML = latest.map(d => `
            <div class="log-item">
                <strong>${d.civ_name}</strong> が「${d.topic.substring(0, 15)}...」についての議論を開始しました。
            </div>
        `).join('');
    }
}

async function fetchTimeline() {
    const response = await fetch('/api/timeline');
    const allDiscussions = await response.json();
    const list = document.getElementById('timeline-list');
    if (!list) return;

    // Get all civs for stats
    const civResp = await fetch('/api/civilizations');
    const civs = await civResp.json();
    allRecentDiscussions = allDiscussions;

    // Update Widgets
    updateTrending(allDiscussions);
    updateWhoToFollow(civs);
    updateStalkerDropdown(allDiscussions);

    let filtered = allDiscussions;

    // Sort logic for tabs
    if (timelineTab === 'for-you') {
        filtered = [...allDiscussions].sort((a, b) => b.heat - a.heat);
    } else {
        filtered = [...allDiscussions].sort((a, b) => b.timestamp - a.timestamp);
    }

    list.innerHTML = '';

    filtered.forEach(disc => {
        const card = document.createElement('div');
        const heatLevel = disc.heat > 75 ? 'high' : disc.heat > 40 ? 'medium' : 'low';
        card.className = `timeline-card heat-${heatLevel}`;

        // Spotlight Highlighting
        if (disc.participants) {
            if (disc.participants.some(p => p.role === 'AVATAR')) card.classList.add('avatar-post');
            else if (disc.participants.some(p => p.role === 'SAGE')) card.classList.add('hero-post');
        }
        if (disc.topic.includes('革命') || disc.topic.includes('政変')) card.classList.add('revolution-event');

        const date = new Date(disc.timestamp * 1000).toLocaleDateString() + ' ' + new Date(disc.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        card.innerHTML = `
            <div class="user-avatar" style="width: 48px; height: 48px; min-width: 48px; border-radius: 50%; background: #2f3336; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; cursor: pointer;" onclick="openProfile('${disc.civ_name}', event)">
                ${disc.civ_name[0]}
            </div>
            <div class="card-main">
                <div class="card-header" onclick="openProfile('${disc.civ_name}', event)">
                    <span class="card-name">${disc.civ_name}</span>
                    <span class="card-handle">@${disc.civ_name.toLowerCase().replace(/\s/g, '_')}</span>
                    <span class="card-handle">·</span>
                    <span class="card-time">${date}</span>
                </div>
                <div class="card-body" onclick="loadDiscussionThread('${disc.civ_name}', '${disc.filename}')">
                    <div class="card-topic">${disc.topic}</div>
                    <div class="card-excerpt">${disc.excerpt.replace(/\[アイコン\]|\[Icon\]/g, '')}...</div>
                </div>
                <div class="card-footer">
                    <div title="Heat"><span style="color: ${disc.heat > 70 ? 'var(--accent-secondary)' : 'inherit'}">🔥 ${disc.heat}</span></div>
                    <div title="Category">${CATEGORY_ICONS[disc.category] || '💬'} ${disc.category.toUpperCase()}</div>
                    <div style="opacity: 0.6;">${disc.participants ? disc.participants.map(p => p.icon).join('') : '👤'}</div>
                </div>
            </div>
        `;
        list.appendChild(card);
    });
}

function updateTrending(discussions) {
    const list = document.getElementById('trending-list');
    if (!list) return;

    // Get top 5 by heat
    const top = [...discussions].sort((a, b) => b.heat - a.heat).slice(0, 5);
    list.innerHTML = top.map(d => `
        <div style="padding: 0.75rem 1rem; cursor: pointer;" onmouseover="this.style.background='var(--bg-hover)'" onmouseout="this.style.background='transparent'" onclick="loadContent('${d.filename}')">
            <div style="font-size: 0.8rem; color: var(--text-secondary);">Trending in ${d.civ_name}</div>
            <div style="font-weight: 700;">#${d.topic.split(' ')[0].substring(0, 15)}</div>
            <div style="font-size: 0.8rem; color: var(--text-secondary);">${d.heat} Divine Energy</div>
        </div>
    `).join('');
}

function updateWhoToFollow(civs) {
    const list = document.getElementById('who-to-follow-list');
    if (!list) return;

    // Shuffle and pick 3
    const shuffled = [...civs].sort(() => 0.5 - Math.random()).slice(0, 3);
    list.innerHTML = shuffled.map(c => `
        <div style="padding: 0.75rem 1rem; display: flex; align-items: center; justify-content: space-between; cursor: pointer;" onmouseover="this.style.background='var(--bg-hover)'" onmouseout="this.style.background='transparent'" onclick="openProfile('${c.name}', event)">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background: #2f3336; display: flex; align-items: center; justify-content: center; font-weight: 700;">${c.name[0]}</div>
                <div>
                    <div style="font-weight: 700; font-size: 0.95rem;">${c.name}</div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem;">@${c.name.toLowerCase()}</div>
                </div>
            </div>
            <button style="background: white; color: black; border: none; padding: 0.4rem 1rem; border-radius: 9999px; font-weight: 700; font-size: 0.85rem;">Follow</button>
        </div>
    `).join('');
}

function updateStalkerDropdown(discussions) {
    const select = document.getElementById('stalker-target');
    if (!select) return;

    const currentTarget = select.value;
    const participants = new Map(); // Name -> {icon, role}

    discussions.forEach(d => {
        if (d.participants) {
            d.participants.forEach(p => {
                participants.set(p.name, p);
            });
        }
    });

    // 既存の選択肢をクリア（デフォルト以外）
    select.innerHTML = '<option value="">対象を選択...</option>';

    // アバターを優先的に上へ
    const sorted = Array.from(participants.values()).sort((a, b) => {
        if (a.role === 'AVATAR' && b.role !== 'AVATAR') return -1;
        if (a.role !== 'AVATAR' && b.role === 'AVATAR') return 1;
        return a.name.localeCompare(b.name);
    });

    sorted.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.name;
        opt.textContent = `${p.icon} ${p.name} (${p.role})`;
        if (p.name === currentTarget) opt.selected = true;
        select.appendChild(opt);
    });
}

function renderStalkerLog() {
    const target = document.getElementById('stalker-target').value;
    const logContainer = document.getElementById('stalker-log');
    if (!logContainer) return;

    if (!target) {
        logContainer.innerHTML = '<div class="text-muted" style="font-size: 0.8rem; text-align: center; padding: 1rem;">対象を追跡して、その言動を監視します。</div>';
        return;
    }

    const filtered = allRecentDiscussions.filter(d =>
        d.participants && d.participants.some(p => p.name === target)
    );

    if (filtered.length === 0) {
        logContainer.innerHTML = `<div class="text-muted" style="font-size: 0.8rem; text-align: center; padding: 1rem;">${target} の最近の活動は見つかりませんでした。</div>`;
        return;
    }

    logContainer.innerHTML = filtered.map(d => `
        <div class="log-item" style="border-left: 2px solid ${d.participants.find(p => p.name === target).role === 'AVATAR' ? '#ff00ff' : 'var(--accent-primary)'};">
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">${d.civ_name} / ${d.category}</div>
            <div style="font-weight: bold; cursor: pointer;" onclick="loadDiscussionThread('${d.civ_name}', '${d.filename}')">${d.topic}</div>
        </div>
    `).join('');
}

async function fetchPadoTales() {
    const response = await fetch('/api/pados_tales');
    const tales = await response.json();
    const list = document.getElementById('pado-list');

    list.innerHTML = '';
    tales.forEach(filename => {
        const li = document.createElement('li');
        li.className = 'grid-item';

        const match = filename.match(/Tale_(\d{8})_(\d{4})/);
        const dateStr = match ? `${match[1].slice(4, 6)}/${match[1].slice(6, 8)} ${match[2].slice(0, 2)}:${match[2].slice(2, 4)}` : filename;

        li.innerHTML = `
            <div class="civ-avatar" style="background:linear-gradient(135deg, #1d9bf0 0%, #764ba2 100%)">🎭</div>
            <div class="civ-info">
                <div class="civ-name" style="font-size: 1.1rem;">Pado's Travel Log <span style="font-weight: 400; color: var(--text-secondary); font-size: 0.9rem;">· ${dateStr}</span></div>
                <div class="civ-meta">Observations from a wandering spirit across the cosmic expanse.</div>
            </div>
        `;
        li.onclick = () => selectPadoTale(filename);
        list.appendChild(li);
    });
}

async function selectPadoTale(filename) {
    switchView('detail');
    document.getElementById('civ-profile-header').innerHTML = `
        <div class="civ-info">
            <div class="civ-avatar" style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%)">🎭</div>
            <div class="civ-meta">
                <span class="display-name">パドの見聞録</span>
                <span class="handle">流浪の吟遊詩人</span>
            </div>
        </div>
    `;

    const response = await fetch(`/api/pado_tale_content?filename=${filename}`);
    const data = await response.json();

    const fileList = document.getElementById('file-list');
    fileList.innerHTML = `<li class="file-item active">${filename}</li>`;

    document.getElementById('content-body').innerHTML = formatMarkdown(data.content);
}

async function fetchLegends() {
    const response = await fetch('/api/legends');
    const legends = await response.json();
    const list = document.getElementById('legend-list');

    if (currentView === 'legends') {
        list.innerHTML = '';
        legends.forEach(filename => {
            const li = document.createElement('li');
            li.className = 'legend-item x-card';
            li.innerHTML = `
                <div class="civ-info">
                <div class="civ-avatar" style="background:#202327; color: var(--accent-gold);">📜</div>
                <div class="civ-info">
                    <div class="civ-name">${filename.replace('.md', '').replace('Legend_of_', '')} <span style="font-weight: 400; color: var(--text-secondary); font-size: 0.9rem;">· Eternal Record</span></div>
                    <div class="civ-meta">Mythical chronicles etched into the foundation of the simulation.</div>
                </div>
                </div>
            `;
            li.onclick = () => selectLegend(filename);
            list.appendChild(li);
        });
    }
}

async function fetchCivilizations() {
    const response = await fetch('/api/civilizations');
    const civs = await response.json();
    const list = document.getElementById('civ-list');

    document.getElementById('cycle-count').innerText = `観測対象: ${civs.length} 文明`;

    if (currentView === 'civilizations') {
        list.innerHTML = '';
        civs.forEach(civ => {
            const li = document.createElement('li');
            li.className = 'grid-item';
            li.innerHTML = `
                <div class="civ-avatar" style="flex-shrink:0;">${civ.name[0]}</div>
                <div class="civ-info" style="flex:1;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div class="civ-name">${civ.name}</div>
                            <div class="civ-meta">@${civ.name.toLowerCase()} · ${civ.ideology}</div>
                        </div>
                        <button style="background: white; color: black; border: none; padding: 0.4rem 1rem; border-radius: 9999px; font-weight: 700; font-size: 0.85rem;">View Profile</button>
                    </div>
                    <div style="margin-top: 8px; color: var(--text-primary); line-height: 1.4; font-size: 0.95rem;">
                        🌍 ${civ.sages_count || 0} Sages observing the abyss. Currently at Generation ${civ.generation || 0}.
                    </div>
                </div>
            `;
            li.onclick = () => selectCiv(civ.name);
            list.appendChild(li);
        });
    }
}

// Redundant fetchLegends removed

async function openProfile(name, event) {
    if (event) event.stopPropagation();

    const response = await fetch(`/api/profile/${name}`);
    const profile = await response.json();

    const modalBody = document.getElementById('modal-body');
    const topicsHtml = profile.favorite_topics ?
        `<div class="favorite-topics">${profile.favorite_topics.map(t => `<span class="topic-tag"># ${t}</span>`).join('')}</div>` : '';

    const sagesHtml = profile.sages && profile.sages.length > 0 ? `
        <div style="margin-top:2rem;">
            <h4 style="color:var(--text-dim); font-size:0.8rem; text-transform:uppercase; margin-bottom:1rem;">主要な賢者たち</h4>
            <div class="sages-list">
                ${profile.sages.map(s => `
                    <div class="sage-item">
                        <div class="sage-icon">${s.icon || '👤'}</div>
                        <div class="sage-info">
                            <div class="sage-name">${s.name} <span class="sage-trait">${s.trait}</span></div>
                            <div class="sage-motivation-tag">${s.motivation || '生存欲'}</div>
                            <div style="font-size:0.75rem; color:var(--accent); margin-top:0.3rem;">🗣️ ${s.speech_style || '標準的'}</div>
                            <div class="sage-bio">${s.bio}</div>
                        </div>
                        <div class="sage-influence">
                            <span style="font-size:0.7rem; color:var(--text-dim);">影響力</span>
                            <div>${s.influence}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    ` : '';

    const socialStateHtml = profile.social_state ? `
        <div class="sidebar-section" style="margin-top:2rem;">
            <h3>📊 社会情勢 (Social State)</h3>
            <div class="res-meter-group">
                <div class="res-row">
                    <span class="text-muted">⚡ 権力</span>
                    <div class="res-bar-bg"><div class="res-bar-fill" style="width:${profile.social_state.power}%; background:var(--cat-scientific);"></div></div>
                    <span class="res-val">${profile.social_state.power}</span>
                </div>
                <div class="res-row">
                    <span class="text-muted">💰 富</span>
                    <div class="res-bar-bg"><div class="res-bar-fill" style="width:${profile.social_state.wealth}%; background:var(--cat-mundane);"></div></div>
                    <span class="res-val">${profile.social_state.wealth}</span>
                </div>
                <div class="res-row">
                    <span class="text-muted">🕯️ 信仰</span>
                    <div class="res-bar-bg"><div class="res-bar-fill" style="width:${profile.social_state.faith}%; background:var(--cat-philosophical);"></div></div>
                    <span class="res-val">${profile.social_state.faith}</span>
                </div>
            </div>
        </div>
    ` : '';

    modalBody.innerHTML = `
        <div class="civ-dashboard">
            <div class="dashboard-header">
                <div class="dashboard-avatar">${name[0]}</div>
                <div class="civ-meta">
                    <h2 style="margin:0; font-size:1.8rem;">${profile.display_name || name}</h2>
                    <span class="handle">@${name.toLowerCase()}</span>
                    <div class="ideology" style="margin-top:0.5rem; color:var(--accent); font-weight:700;">${profile.ideology || '---'}</div>
                </div>
            </div>

            <div class="dashboard-bio">
                ${profile.bio || '我々はこの混沌の中で、独自の真理を追求する文明である。'}
                <div style="margin-top:1rem; font-size:0.9rem;">
                    <strong>性格:</strong> ${profile.personality_traits?.join(' / ') || '未知'} <br>
                    <strong>口調:</strong> ${profile.tone || '標準的'}
                </div>
                ${topicsHtml}
            </div>

            <div class="dashboard-stats-grid">
                <div class="dashboard-stat-card">
                    <h4>Generation</h4>
                    <div class="val">${profile.stats?.generation || 0}</div>
                </div>
                <div class="dashboard-stat-card">
                    <h4>Total Debates</h4>
                    <div class="val">${profile.stats?.total_discussions || 0}</div>
                </div>
                <div class="dashboard-stat-card">
                    <h4>Avg Heat</h4>
                    <div class="val ${profile.stats?.avg_heat > 50 ? 'heat-medium' : ''}">${profile.stats?.avg_heat || 0}</div>
                </div>
                <div class="dashboard-stat-card">
                    <h4>Concepts</h4>
                    <div class="val">${profile.concepts_count || '---'}</div>
                </div>
            </div>

            ${socialStateHtml}
            ${sagesHtml}
            
            ${profile.culture_values ? `
                <div class="culture-section" style="background: linear-gradient(135deg, rgba(139, 0, 139, 0.1), rgba(0, 0, 0, 0.3)); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(139, 0, 139, 0.3); margin-top: 1.5rem;">
                    <h3 style="color: #da70d6; margin-bottom: 1rem;">🎨 文化的アイデンティティ</h3>
                    ${profile.culture_values.colors ? `<div style="margin-bottom:0.8rem;"><strong>🎨 色彩観:</strong> ${Object.entries(profile.culture_values.colors).map(([k, v]) => `<span style="display:inline-block; padding:0.3rem 0.8rem; background:rgba(255,255,255,0.1); border-radius:20px; margin:0.2rem; font-size:0.85rem;">${k}: ${v}</span>`).join(' ')}</div>` : ''}
                    ${profile.culture_values.numbers ? `<div style="margin-bottom:0.8rem;"><strong>🔢 数秘主義:</strong> ${Object.entries(profile.culture_values.numbers).map(([k, v]) => `<span style="display:inline-block; padding:0.3rem 0.8rem; background:rgba(255,255,255,0.1); border-radius:20px; margin:0.2rem; font-size:0.85rem;">${k}: ${v}</span>`).join(' ')}</div>` : ''}
                    ${profile.culture_values.concepts ? `<div><strong>💡 核心概念:</strong> ${Object.entries(profile.culture_values.concepts).map(([k, v]) => `<span style="display:inline-block; padding:0.3rem 0.8rem; background:rgba(255,255,255,0.1); border-radius:20px; margin:0.2rem; font-size:0.85rem;">${k}: ${v}</span>`).join(' ')}</div>` : ''}
                    
                    ${profile.culture_values.formation_history && profile.culture_values.formation_history.length > 0 ? `
                        <div style="margin-top: 1.2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
                            <h4 style="font-size: 0.9rem; color: var(--text-dim); margin-bottom: 0.6rem;">📜 文化形成史</h4>
                            <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.85rem;">
                                ${profile.culture_values.formation_history.slice(-5).map(h => `<li style="margin-bottom:0.4rem; opacity:0.8;">➤ <strong>第${h.gen}世代:</strong> ${h.event}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            ` : ''}

            <div style="display:flex; justify-content: flex-end; margin-top:2rem;">
                <button class="nav-btn" style="width:auto; padding: 0.8rem 2rem; background: var(--accent); border:none; box-shadow: 0 4px 12px var(--accent-glow);" 
                        onclick="selectCiv('${name}'); closeModal();">🌏 深層観測を開始</button>
            </div>
        </div>
    `;

    document.getElementById('modal-overlay').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modal-overlay').style.display = 'none';
}

async function selectCiv(name) {
    currentCiv = name;
    switchView('detail');

    const response = await fetch(`/api/profile/${name}`);
    const profile = await response.json();

    document.getElementById('civ-profile-header').innerHTML = `
        <div class="view-header" style="height: auto; padding: 0.5rem 1rem; border-bottom: 1px solid var(--border-subtle);">
            <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 0.5rem;">
                <div style="cursor: pointer; font-size: 1.5rem;" onclick="goBack()">←</div>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; background: var(--accent-primary); display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1rem;">${name[0]}</div>
                    <div>
                        <h2 style="margin: 0; font-size: 1.15rem;">${profile.display_name || name}</h2>
                        <div style="color: var(--text-secondary); font-size: 0.85rem;">@${name.toLowerCase()} · High-Resolution Observation</div>
                    </div>
                </div>
            </div>
            <div style="font-size: 0.95rem; color: var(--text-primary); line-height: 1.5; margin-left: 44px;">
                ${profile.bio || '我々はこの混沌の中で、独自の真理を追求する文明である。'}
            </div>
        </div>
    `;

    fetchFiles();
}

async function loadDiscussionThread(civName, filename) {
    currentCiv = civName;
    currentFile = filename;
    switchView('detail');

    // ヘッダーを議論用に更新
    document.getElementById('civ-profile-header').innerHTML = `
        <div class="view-header" style="height: auto; padding: 1rem; border-bottom: 1px solid var(--border-subtle); display: flex; align-items: center; gap: 20px;">
            <div style="cursor: pointer; font-size: 1.5rem;" onclick="goBack()">←</div>
            <div>
                <h2 style="margin: 0; font-size: 1.15rem;">Discussion Thread</h2>
                <div style="color: var(--text-secondary); font-size: 0.85rem;">${civName} · Archived Record</div>
            </div>
        </div >
        `;

    const response = await fetch(`/api/discussion/${civName}/${filename}`);
    const thread = await response.json();

    const fileList = document.getElementById('file-list');
    fileList.innerHTML = `<li class="file-item active">${filename}</li>`;

    renderDiscussionThread(thread);
}

function renderDiscussionThread(thread) {
    const container = document.getElementById('content-body');

    let html = `
        <div class="thread-starter">
            <div class="thread-avatar">💬</div>
            <div class="thread-content">
                <div class="thread-header">
                    <span class="thread-name">議論トピック</span>
                    <span class="thread-handle">@genesis_archive</span>
                </div>
                <div class="thread-body">${thread.topic}</div>
                <div class="thread-footer">
                    <span>🔥 ${thread.heat} Heat</span>
                    <span>${thread.replies.length} statements</span>
                </div>
            </div>
        </div>
    `;

    thread.replies.forEach((reply, index) => {
        const isLast = index === thread.replies.length - 1;
        html += `
            <div class="thread-reply">
                ${!isLast ? '<div class="thread-line"></div>' : ''}
                <div class="reply-avatar">${reply.icon}</div>
                <div class="reply-content">
                    <div class="reply-header">
                        <span class="reply-name">${reply.speaker}</span>
                        <span class="reply-role-badge ${reply.role.toLowerCase()}">${reply.role}</span>
                    </div>
                    <div class="reply-body">${reply.text}</div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

async function selectLegend(filename) {
    switchView('detail');
    document.getElementById('civ-profile-header').innerHTML = `
        <div class="view-header" style="height: auto; padding: 1rem; border-bottom: 1px solid var(--border-subtle); display: flex; align-items: center; gap: 20px;">
            <div style="cursor: pointer; font-size: 1.5rem;" onclick="goBack()">←</div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background: #202327; color: var(--accent-gold); display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1rem;">📜</div>
                <div>
                    <h2 style="margin: 0; font-size: 1.15rem;">${filename.replace('.md', '')}</h2>
                    <div style="color: var(--text-secondary); font-size: 0.85rem;">Eternal Archives · Project Genesis</div>
                </div>
            </div>
        </div>
    `;

    const response = await fetch(`/api/legend_content?filename=${filename}`);
    const data = await response.json();

    const fileList = document.getElementById('file-list');
    fileList.innerHTML = `<li class="file-item active">${filename}</li>`;

    document.getElementById('content-body').innerHTML = formatMarkdown(data.content);
}

function goBack() {
    switchView('timeline');
}

async function fetchFiles() {
    if (!currentCiv) return;
    const response = await fetch(`/api/civilization/${currentCiv}/files`);
    const data = await response.json();
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = '';

    const files = data[currentTab];
    files.forEach(file => {
        const li = document.createElement('li');
        li.className = 'file-item';
        if (currentFile === file) li.classList.add('active');
        li.innerText = file;
        li.onclick = () => loadContent(file);
        fileList.appendChild(li);
    });
}

function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    fetchFiles();
}

async function loadContent(filename) {
    currentFile = filename;
    document.querySelectorAll('.file-item').forEach(li => {
        li.classList.remove('active');
        if (li.innerText === filename) li.classList.add('active');
    });

    if (currentTab === 'archives') {
        loadDiscussionThread(currentCiv, filename);
        return;
    }

    const folder = 'Concepts';
    const response = await fetch(`/api/file-content?path=Civilizations/${currentCiv}/${folder}/${filename}`);
    const content = await response.text();

    document.getElementById('content-body').innerHTML = formatMarkdown(content);
}

function formatMarkdown(text) {
    if (!text) return '';
    let html = text
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^\* (.*$)/gim, '<li>$1</li>')
        .replace(/> (.*$)/gim, '<blockquote>$1</blockquote>')
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
        .replace(/---\n/g, '<hr>')
        .replace(/\n/g, '<br>');
    return html;
}
