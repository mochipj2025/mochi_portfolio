async function fetchPadoTales() {
    const response = await fetch('/api/pados_tales');
    const tales = await response.json();
    const list = document.getElementById('pado-list');

    list.innerHTML = '';
    tales.forEach(filename => {
        const li = document.createElement('li');
        li.className = 'legend-item x-card';

        // タイムスタンプを抽出してフレンドリーに表示
        const match = filename.match(/Tale_(\d{8})_(\d{4})/);
        const dateStr = match ? `${match[1].slice(0, 4)}/${match[1].slice(4, 6)}/${match[1].slice(6, 8)} ${match[2].slice(0, 2)}:${match[2].slice(2, 4)}` : filename;

        li.innerHTML = `
            <div class="civ-info">
                <div class="civ-avatar" style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%)">🎭</div>
                <div class="civ-meta">
                    <span class="display-name">パドの見聞録</span>
                    <span class="handle">${dateStr}</span>
                </div>
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
