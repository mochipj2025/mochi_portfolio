const works = [
  {
    title: "salon-prompt-maker",
    short: "Salon Prompt",
    type: "Practical prompt tool",
    category: "featured prompt",
    url: "https://mochipj2025.github.io/salon-prompt-maker/",
    tone: "mint",
    description:
      "サロンや店舗の画像生成プロンプトを、選択式で安全に組み立てる実用ツール。すぐ使える価値が伝わる作品。",
    tags: ["Prompt", "Safety", "Utility"]
  },
  {
    title: "Codequarium",
    short: "Codequarium",
    type: "Interactive experiment",
    category: "featured experience world",
    url: "https://mochipj2025.github.io/Codequarium/",
    tone: "aqua",
    description:
      "音、流体、センサーを組み合わせたアルゴリズム水槽。AIが観測する環境の原型として見せられる体験作品。",
    tags: ["Canvas", "Audio", "Environment"]
  },
  {
    title: "キコロット・タロット",
    short: "Kiko Tarot",
    type: "Character reading UI",
    category: "identity experience",
    url: "https://mochipj2025.github.io/test_kiko/",
    tone: "violet",
    description:
      "キャラクターとカード図鑑を使ったリーディング体験。診断、物語、人格設計を一つにした作品。",
    tags: ["Tarot", "Character", "Reading"]
  },
  {
    title: "Kettu Prompt Maker",
    short: "Kettu",
    type: "Identity prompt system",
    category: "identity prompt",
    url: "https://mochipj2025.github.io/Kettu/",
    tone: "rose",
    description:
      "キャラクター設定、名札、ランダム要素を組み合わせるGPTプロンプトメーカー。人格設計の部品として強い。",
    tags: ["Identity", "Prompt", "Character"]
  },
  {
    title: "おぱんちゅラボ",
    short: "Opanchu Lab",
    type: "Portal experience",
    category: "experience identity",
    url: "https://mochipj2025.github.io/Substack_2026_opanchu/",
    tone: "peach",
    description:
      "画像主体の入口からポータルへ入る体験型ページ。コミュニティやキャラクター世界への導入として使える。",
    tags: ["Portal", "Community", "Character"]
  },
  {
    title: "ケツ印どうぶつ診断",
    short: "Animal Reading",
    type: "Diagnosis app",
    category: "identity experience",
    url: "https://mochipj2025.github.io/Substack-/",
    tone: "lemon",
    description:
      "生年月日、血液型、五行質問から分類する診断UI。ユーザーの状態を読むAgent前段の入力層。",
    tags: ["Diagnosis", "Input", "Classification"]
  },
  {
    title: "noteジャック大作戦",
    short: "Note Jack",
    type: "Community campaign LP",
    category: "experience",
    url: "https://mochipj2025.github.io/Substack-2026/",
    tone: "orange",
    description:
      "音源、参加導線、FAQを持つコミュニティ企画LP。人を巻き込む設計の実験として見せられる。",
    tags: ["Community", "Campaign", "Audio"]
  },
  {
    title: "不条理の庭",
    short: "Absurd Garden",
    type: "Digital art gallery LP",
    category: "experience lp",
    url: "https://mochipj2025.github.io/LP0003/",
    tone: "crimson",
    description:
      "耽美な和モダンのデジタルアートLP。ギャラリー、シミュレーター、販売導線を含む展示型作品。",
    tags: ["LP", "Gallery", "Commerce"]
  },
  {
    title: "かずみんママ社長 LP",
    short: "Kazumin LP",
    type: "Branding landing page",
    category: "lp",
    url: "https://mochipj2025.github.io/kazumin_LP/",
    tone: "wine",
    description:
      "高級感のあるブランディングLP。世界観、プロフィール、CTAモーダルまで整った見せるためのページ。",
    tags: ["Branding", "LP", "Motion"]
  },
  {
    title: "Hex-Circuit",
    short: "Hex Circuit",
    type: "Mini game",
    category: "experience world",
    url: "https://mochipj2025.github.io/puzzle/",
    tone: "lime",
    description:
      "音つきのCanvasパズルゲーム。ルール、反応、スコアを持つ小さな環境としてポートフォリオに置ける。",
    tags: ["Game", "Canvas", "Interaction"]
  }
];

const grid = document.querySelector("#works-grid");
const buttons = document.querySelectorAll(".filter-button");

function renderWorks(filter = "all") {
  const visibleWorks = works.filter((work) => {
    if (filter === "all") return true;
    return work.category.split(" ").includes(filter);
  });

  grid.innerHTML = visibleWorks
    .map(
      (work) => `
      <article class="work-card compact-card" data-category="${work.category}">
        <div class="preview-shell ${work.tone}" aria-hidden="true">
          <div class="preview-label">
            <span>${work.type}</span>
            <strong>${work.short}</strong>
          </div>
          <div class="preview-lines">
            <i></i><i></i><i></i>
          </div>
        </div>
        <div class="work-body">
          <p class="work-type">${work.type}</p>
          <h3>${work.title}</h3>
          <p>${work.description}</p>
          <div class="tag-row">
            ${work.tags.map((tag) => `<span>${tag}</span>`).join("")}
          </div>
          <div class="card-actions">
            <a href="${work.url}" target="_blank" rel="noreferrer">View Site</a>
          </div>
        </div>
      </article>
    `
    )
    .join("");
}

buttons.forEach((button) => {
  button.addEventListener("click", () => {
    buttons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    renderWorks(button.dataset.filter);
  });
});

renderWorks();
