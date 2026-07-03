import os
import json
import time
import random
import datetime
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests  # ローカルLLM API呼び出し用
from world_map import WorldMap
from novel_compiler import ChronicleCompiler

# ==========================================
# ⚙️ CONFIGURATION (神の設定項目)
# ==========================================
# ObsidianのVaultパス (現在のプロジェクトディレクトリを使用)
OBSIDIAN_VAULT_PATH = r"d:\00000\mochisura-lab\Project_Genesis"

# ローカルLLMのエンドポイント (例: Ollama, LM Studio)
# OpenAI互換のローカルサーバーを想定
LLM_API_URL = "http://localhost:11434/v1/chat/completions"
LLM_MODEL = "llama3" # または "mistral", "gemma" など

# 時間設定 (デバッグ用に1サイクルを短くしています)
CYCLE_DURATION_SEC = 30  # 1世代の長さ (ユーザー提示の60秒よりさらに短縮して動作確認)
MAX_GENERATIONS = 1000   # 安全装置: 最大世代数
MAX_DEPTH = 4            # 階層深度リミット

# ==========================================
# 🧠 AI ENGINE (ローカル脳)
# ==========================================
def chat_with_gods(messages, temperature=0.7):
    """ローカルLLMに思考をリクエストする"""
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1000
    }
    try:
        response = requests.post(LLM_API_URL, json=payload).json()
        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content']
        else:
            print(f"⚠️ Unexpected response structure: {response}")
            return "思考停止（応答形式エラー）"
    except Exception as e:
        print(f"⚡ ERROR: 神託の受信に失敗 ({e})")
        return "思考停止（エラー発生）"

# ==========================================
# 🎨 TOPIC GENERATOR (話題生成)
# ==========================================
class TopicGenerator:
    """話題生成エンジン - 多様な議論テーマを提供"""
    
    TOPIC_POOL = {
        "philosophical": [
            "意識とは単なる情報処理の副産物なのか",
            "美は観測者に依存するのか、それとも普遍的に存在するのか",
            "無限とは何か、そして我々は無限を理解できるのか",
            "自由意志は実在するか、それとも電気信号の錯覚か",
            "魂の重さを定義することは可能か",
            "死後の世界という概念が社会に与える影響"
        ],
        "scientific": [
            "重力は物質の性質なのか、それとも空間の歪みなのか",
            "生命とは自己複製する化学反応の連鎖に過ぎないのか",
            "この宇宙はシミュレーションである可能性はあるか",
            "時間の不可逆性は物理的な制約か、それとも観測の限界か",
            "エントロピーの増大を食い止める文明は存在し得るか"
        ],
        "social": [
            "完璧な公平性は社会の成長を阻害するか",
            "通貨という概念を排除した文明における価値の定義",
            "リーダーシップは天性か、それとも絶望が生む必要悪か",
            "私有財産の禁止がもたらす幸福の形",
            "デジタル人格に市民権を与えるべきか"
        ],
        "mundane": [
            "朝食は本当に一日で最も重要な食事なのか",
            "なぜ人は同じ靴下を揃えることにこだわるのか",
            "雨の日の匂いに名前をつけるべきか",
            "行列に並ぶという行為の中に潜む原始的な安心感",
            "理想的な睡眠時間の定義は誰が決めるべきか"
        ],
        "absurd": [
            "もし重力が週に一度だけ反転したら社会はどう適応するか",
            "影には意思があるのか、それとも我々が投影しているだけか",
            "なぜ円は角がないのに完璧とされるのか",
            "言葉が物理的な重さを持っていたら、沈黙は豊かさの証になるか",
            "鏡の中の世界とこちらの世界が入れ替わる瞬間を見分ける方法"
        ],
        "speculative": [
            "もしAIが神を自称し始めたら、人間は何を拠り所にするか",
            "感情を外部メモリに保存できるようになった後の愛の定義",
            "太陽が二つある世界の色彩感覚と芸術",
            "夢の内容を共有できるSNSがもたらすプライバシーの終焉"
        ]
    }
    
    DISCUSSION_MODES = ["SERIOUS", "CASUAL", "OBSERVATIONAL", "SPECULATIVE"]
    
    @staticmethod
    def generate_topic(ideology=None, previous_topics=None):
        """話題とモードを生成し、白熱度の基礎データを返す"""
        category = random.choices(
            list(TopicGenerator.TOPIC_POOL.keys()),
            weights=[20, 15, 20, 25, 15, 5],  # 哲学, 科学, 社会, 日常, 奇妙, 妄想
            k=1
        )[0]
        
        topic = random.choice(TopicGenerator.TOPIC_POOL[category])
        mode = random.choice(TopicGenerator.DISCUSSION_MODES)
        
        # 将来的にはイデオロギーに基づいた調整や前回との関連性もここに
        return topic, mode, category

def calculate_heat(discussion_log, category, mode):
    """議論の白熱度を計算（0-100）"""
    heat = 0.0
    
    # カテゴリによる基礎熱量
    category_weight = {
        "philosophical": 0.7,
        "social": 0.8,
        "scientific": 0.6,
        "mundane": 0.3,
        "absurd": 0.5,
        "speculative": 0.6
    }
    heat += category_weight.get(category, 0.5)
    
    # モードによる加点
    if mode == "SERIOUS":
        heat += 0.3
    
    # テキスト解析による動的計算（日本語に対応）
    heat += discussion_log.count("！") * 0.02
    heat += discussion_log.count("!") * 0.02
    heat += discussion_log.count("？") * 0.01
    heat += discussion_log.count("?") * 0.01
    heat += discussion_log.count("しかし") * 0.03
    heat += discussion_log.count("反対") * 0.04
    heat += discussion_log.count("異議") * 0.05
    heat += discussion_log.count("同感") * 0.02
    
    # 0-100のスケールに調整
    final_heat = min(100, int(heat * 45 + random.randint(0, 10)))
    return final_heat

# ==========================================
# 🧠 KNOWLEDGE BASE (集合知管理)
# ==========================================
class KnowledgeBase:
    """文明全体の集合知を管理し、LLMに教える"""
    
    def __init__(self, root_path):
        self.kb_path = Path(root_path) / "00_Knowledge_Base"
        self.kb_path.mkdir(exist_ok=True)
        self.concepts = {}
        self._wisdom_cache = {}  # カテゴリごとのキャッシュ
        self._load_knowledge()

    def _load_knowledge(self):
        """蓄積された知識をロード"""
        for file in self.kb_path.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.concepts[file.stem] = data
            except:
                pass

    def get_related_wisdom(self, category, limit=3):
        """カテゴリに関連する知恵を取得（キャッシュ付き）"""
        cache_key = f"{category}_{limit}"
        if cache_key in self._wisdom_cache:
            return self._wisdom_cache[cache_key]
        
        if category in self.concepts:
            wisdom_list = self.concepts[category].copy()
            random.shuffle(wisdom_list)
            result = wisdom_list[:limit]
            self._wisdom_cache[cache_key] = result
            return result
        return []

    def add_wisdom(self, category, concept_name, definition, heat):
        """新しい知恵を蓄積（白熱したもののみ）"""
        if heat < 65: return
        
        if category not in self.concepts:
            self.concepts[category] = []
        
        # 重複チェック
        if any(c["name"] == concept_name for c in self.concepts[category]):
            return
            
        self.concepts[category].append({
            "name": concept_name,
            "definition": definition,
            "born_at": datetime.datetime.now().isoformat()
        })
        
        # 保存
        with open(self.kb_path / f"{category}.json", "w", encoding="utf-8") as f:
            json.dump(self.concepts[category], f, ensure_ascii=False, indent=2)

# ==========================================
# 💀 ENTROPY MANAGER (掃除屋)
# ==========================================
class EntropyManager:
    def __init__(self, root_path, max_depth=5):
        self.root_path = Path(root_path)
        self.max_depth = max_depth
        self.graveyard = self.root_path / "00_Legends" # 墓場
        self.graveyard.mkdir(exist_ok=True)

    def perform_metabolism(self, civ_list):
        """新陳代謝の実行：生存リストを返す"""
        surviving_civs = []
        
        for civ in civ_list:
            genealogy_depth = civ.name.count("Orthodox") + civ.name.count("Reformed")
            
            if genealogy_depth > 5:
                print(f"💀 REAPER: {civ.name} は血統が複雑になりすぎました（深度{genealogy_depth}）。化石化します。")
                self._fossilize(civ)
                continue 

            if random.random() < 0.05:
                print(f"☄️ CATASTROPHE: {civ.name} に予期せぬ災害が発生！")
                self._fossilize(civ)
                continue

            surviving_civs.append(civ)
            
        return surviving_civs

    def _fossilize(self, civ):
        """文明を圧縮してアーカイブし、物理削除する"""
        try:
            print(f"🕯️ {civ.name} の終焉を記録中...")
            
            history_summary = f"# 滅亡した文明: {civ.name}\n"
            history_summary += f"## 最後のイデオロギー\n{civ.ideology}\n\n"
            
            const_path = civ.path / "Constitution.md"
            if const_path.exists():
                with open(const_path, "r", encoding="utf-8") as f:
                    history_summary += f"## 遺された憲法\n{f.read()}\n"

            legend_prompt = [
                {"role": "system", "content": "あなたは滅びた文明の歴史を神話として語り継ぐ吟遊詩人です。"},
                {"role": "user", "content": f"以下の文明情報を基に、かつて存在した『{civ.name}』の物語を日本語で美しく、少し悲傷を込めて書き記してください。\n\n{history_summary}"}
            ]
            legend_text = chat_with_gods(legend_prompt, temperature=0.8)
            
            tombstone = self.graveyard / f"Legend_of_{civ.name}.md"
            with open(tombstone, "w", encoding="utf-8") as f:
                f.write(f"# 伝説: {civ.name}\n\n{legend_text}\n\n---\n*この文明は第{datetime.datetime.now().year}年に幕を閉じた*")
            
            if civ.path.exists():
                shutil.rmtree(civ.path)
            print(f"⚰️ {civ.name} は伝説となり、星屑に還りました。")
            
        except Exception as e:
            print(f"⚡ Error during fossilization of {civ.name}: {e}")

# ==========================================
# 📚 ARCHIVE MANAGER (記録の新陳代謝)
# ==========================================
class ArchiveManager:
    """議論記録の新陳代謝を管理"""
    
    MAX_ARCHIVES_PER_CIV = 15  # 保持する最大議論数（UIのために少し少なめに設定）
    
    def metabolize_archives(self, civ):
        """古い議論を整理・圧縮"""
        archive_dir = civ.path / "Archives"
        if not archive_dir.exists():
            return
        
        archives = sorted(
            archive_dir.glob("*.md"),
            key=lambda f: f.stat().st_mtime
        )
        
        if len(archives) > self.MAX_ARCHIVES_PER_CIV:
            old_archives = archives[:-self.MAX_ARCHIVES_PER_CIV]
            
            to_compress = []
            for archive in old_archives:
                # _digestファイルは除外
                if archive.name.startswith("_"): continue
                
                heat = self._extract_heat(archive)
                if heat < 75:  # 白熱度75未満は圧縮対象（殿堂入りは残す）
                    to_compress.append(archive)
            
            if to_compress:
                print(f"♻️ METABOLISM: {civ.name} の古い議論をダイジェスト化します...")
                self._create_digest(civ, to_compress)
                for file in to_compress:
                    file.unlink()
    
    def _extract_heat(self, archive_file):
        """Archiveファイルからheat値を抽出"""
        try:
            with open(archive_file, "r", encoding="utf-8") as f:
                for line in f:
                    if "**白熱度**:" in line:
                        # 絵文字等を除外して数値だけ取り出す
                        parts = line.split("(")
                        if len(parts) > 1:
                            return int(parts[1].split(")")[0])
        except:
            pass
        return 0
    
    def _create_digest(self, civ, archive_files):
        """古い議論をダイジェスト版として統合"""
        digest_path = civ.path / "Archives" / "_digest_old_discussions.md"
        
        with open(digest_path, "a", encoding="utf-8") as digest:
            if digest.tell() == 0:
                digest.write(f"# {civ.name} 歴史の断片（ダイジェスト）\n\n")
            
            digest.write(f"\n---\n## 観測記録: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n")
            
            for archive in archive_files:
                with open(archive, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 最初の方だけ要約のヒントとして抽出
                summary_prompt = [
                    {"role": "system", "content": "あなたは文明の歴史要約者です。"},
                    {"role": "user", "content": f"以下の議論内容を3行程度の日本語で要約してください。\n\n{content[:800]}..."}
                ]
                summary = chat_with_gods(summary_prompt, temperature=0.3)
                digest.write(f"### {archive.stem}\n{summary}\n\n")

# ==========================================
# 👤 PROFILE GENERATOR (SNSプロフィール生成)
# ==========================================
class CivilizationProfileGenerator:
    """文明のSNS風プロフィールを生成"""
    
    def generate_profile(self, civ_name, ideology, parent_name=None):
        """文明のキャラクター設定を生成"""
        print(f"👤 Creating identity for {civ_name}...")
        
        prompt = [
            {"role": "system", "content": "あなたはキャラクター設定の専門家です。文明を魅力的なキャラクターとして日本語で表現してください。"},
            {"role": "user", "content": f"以下の文明のSNSプロフィールをJSON形式で作成せよ：\n- 名前: {civ_name}\n- イデオロギー: {ideology}\n- 親文明: {parent_name if parent_name else 'なし'}\n\n形式:\n{{\"display_name\": \"愛称\", \"personality_traits\": [\"特性1\", \"特性2\"], \"tone\": \"話し方の特徴\", \"bio\": \"自己紹介文(2-3文)\", \"favorite_topics\": [\"話題1\", \"話題2\"]}}"}
        ]
        
        try:
            result = chat_with_gods(prompt, temperature=0.7)
            # JSON部分を力ずくで抽出
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                profile_data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found")
        except Exception as e:
            print(f"⚠️ Profile Gen Error: {e}")
            profile_data = {
                "display_name": civ_name,
                "personality_traits": ["不明"],
                "tone": "標準的",
                "bio": f"{ideology}を信奉する文明。",
                "favorite_topics": ["全般"]
            }
        
        # 共通データを追加
        profile_data.update({
            "name": civ_name,
            "ideology": ideology,
            "stats": {
                "generation": 0,
                "total_discussions": 0,
                "avg_heat": 0
            },
            "created_at": datetime.datetime.now().isoformat()
        })
        
        return profile_data

# ==========================================
# 🧘 SAGE SYSTEM (賢者システム)
# ==========================================
class Sage:
    def __init__(self, name, trait, bio, icon="👤", speech_style="標準的", motivation="安定", influence=10, relationships=None):
        self.name = name
        self.trait = trait
        self.bio = bio
        self.icon = icon            # 個別アイコン (絵文字)
        self.speech_style = speech_style # 話し方の特徴
        self.motivation = motivation
        self.influence = influence
        self.relationships = relationships or {}

    def to_dict(self):
        return {
            "name": self.name,
            "trait": self.trait,
            "bio": self.bio,
            "icon": self.icon,
            "speech_style": self.speech_style,
            "motivation": self.motivation,
            "influence": self.influence,
            "relationships": self.relationships
        }

class SageGenerator:
    """文明の『魂』となる賢者たちを生成"""
    def generate_sages(self, civ_name, ideology, count=3):
        print(f"🕯️ Awakening Sages for {civ_name}...")
        
        prompt = [
            {"role": "system", "content": "あなたは文明の歴史家です。文明の精神を体現する、個性的で魅力的な名前を持つ3人の『賢者』を日本語で作成してください。"},
            {"role": "user", "content": (
                f"文明名: {civ_name}\n"
                f"イデオロギー: {ideology}\n\n"
                f"以下のJSON形式で3人のキャラクターを作成せよ。彼らは互いに異なる気質、アイコン、特徴的な【話し方】、そして『動機』を持つこと。\n"
                f"形式:\n"
                f"[{{\"name\": \"名前\", \"icon\": \"絵文字\", \"trait\": \"一言の気質\", \"speech_style\": \"話し方の特徴(例: 語尾が〜である、荒々しい、等)\", \"bio\": \"信念の要約\", \"motivation\": \"拡張欲/生存欲/探求欲\"}}]"
            )}
        ]
        
        try:
            result = chat_with_gods(prompt, temperature=0.8)
            import re
            json_match = re.search(r'\[.*\s*\]', result, re.DOTALL)
            if json_match:
                sages_data = json.loads(json_match.group())
                sages = [Sage(
                    name=s["name"], 
                    trait=s["trait"], 
                    bio=s["bio"], 
                    icon=s.get("icon", "👤"), 
                    speech_style=s.get("speech_style", "標準的"),
                    motivation=s.get("motivation", "生存欲")
                ) for s in sages_data[:count]]
                
                # 初期人間関係（お互いに中立 0）
                for s in sages:
                    for other in sages:
                        if s.name != other.name:
                            s.relationships[other.name] = 0
                return sages
            else:
                raise ValueError("No JSON found")
        except Exception as e:
            print(f"⚠️ Sage Gen Error: {e}")
            return [
                Sage(f"賢者{i}", "中庸", "安定を望む名もなき悟りびと。") for i in range(1, count+1)
            ]

# ==========================================
# 🎭 WANDERING BARD (流浪の詩人パド)
# ==========================================
class WanderingBard:
    """文明を渡り歩き、断片的な記録を物語として紡ぐ語り部"""
    
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.tales_dir = self.root_path / "00_The_Origin" / "Pados_Tales"
        self.tales_dir.mkdir(parents=True, exist_ok=True)
        self.last_journey = 0
        self.journey_interval = 3600  # 1時間 (秒)
    
    def should_journey(self):
        """旅の時間かどうかを判定"""
        import time
        current_time = time.time()
        if current_time - self.last_journey >= self.journey_interval:
            self.last_journey = current_time
            return True
        return False
    
    def embark_on_journey(self, civilizations):
        """旅に出て、物語を紡ぐ"""
        if not civilizations:
            print("🎭 PADO: まだ訪れるべき文明が存在しません...")
            return
        
        # ランダムに3〜5文明を選択
        num_to_visit = min(random.randint(3, 5), len(civilizations))
        visited_civs = random.sample(civilizations, num_to_visit)
        
        print(f"\n🎭 PADO: 旅に出ます... 今回は{num_to_visit}つの文明を訪問します。")
        
        # 各文明から情報を収集
        fragments = []
        for civ in visited_civs:
            fragment = self._gather_fragment(civ)
            if fragment:
                fragments.append(fragment)
        
        if not fragments:
            print("🎭 PADO: 今回は何も見つかりませんでした...")
            return
        
        # LLMで物語を生成
        tale = self._weave_tale(fragments)
        
        # 保存
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        tale_file = self.tales_dir / f"Tale_{timestamp}.md"
        with open(tale_file, "w", encoding="utf-8") as f:
            f.write(tale)
        
        print(f"📖 PADO: 新しい物語を紡ぎました → {tale_file.name}")
    
    def _gather_fragment(self, civ):
        """文明から断片を収集"""
        fragment = {
            "name": civ.name,
            "ideology": civ.ideology,
            "constitution": None,
            "latest_discussion": None,
            "latest_concept": None
        }
        
        # 憲法を取得
        const_path = civ.path / "Constitution.md"
        if const_path.exists():
            with open(const_path, "r", encoding="utf-8") as f:
                fragment["constitution"] = f.read()[:300]  # 冒頭のみ
        
        # 最新の議論を取得
        archive_dir = civ.path / "Archives"
        if archive_dir.exists():
            archives = sorted(archive_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
            if archives and not archives[0].name.startswith("_"):
                with open(archives[0], "r", encoding="utf-8") as f:
                    fragment["latest_discussion"] = f.read()[:500]
        
        # 最新の概念を取得
        concept_dir = civ.path / "Concepts"
        if concept_dir.exists():
            concepts = sorted(concept_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
            if concepts:
                with open(concepts[0], "r", encoding="utf-8") as f:
                    fragment["latest_concept"] = f.read()[:300]
        
        return fragment
    
    def _weave_tale(self, fragments):
        """断片を物語として紡ぐ"""
        # プロンプト構築
        context = "\n\n".join([
            f"【文明: {frag['name']}】\n"
            f"イデオロギー: {frag['ideology']}\n"
            f"憲法: {frag['constitution'] or '不明'}\n"
            f"最新の議論: {frag['latest_discussion'] or 'なし'}\n"
            f"最新の概念: {frag['latest_concept'] or 'なし'}"
            for frag in fragments
        ])
        
        prompt = [
            {"role": "system", "content": "あなたは流浪の吟遊詩人『パド』です。世界を旅し、様々な文明の断片的な記録を詩的に繋ぎ合わせて、一つの寓話や見聞録として語り継ぎます。日本語で、美しく、情緒的に。"},
            {"role": "user", "content": f"以下は私が訪れた文明の記録です。これらを一つの物語として紡いでください。\n\n{context}\n\n※ Markdown形式で、タイトル（# パドの見聞録: 〇〇）から始めてください。"}
        ]
        
        tale = chat_with_gods(prompt, temperature=0.9)
        
        # メタデータを追記
        journey_date = datetime.datetime.now().strftime("%Y年%m月%d日 %H時%M分")
        visited_names = "、".join([f['name'] for f in fragments])
        
        tale_with_meta = f"{tale}\n\n---\n*{journey_date} の旅 | 訪問: {visited_names}*"
        return tale_with_meta

# ==========================================
# 🏛️ CIVILIZATION MANAGER (文明管理)
# ==========================================
class Civilization:
    def __init__(self, name, parent_path, ideology, parent_name=None):
        self.name = name
        self.path = Path(parent_path) / "Civilizations" / name
        self.ideology = ideology
        self.parent_name = parent_name
        self.dogma_level = 0.1
        self._setup_structure()

    def _setup_structure(self):
        """フォルダ構造と憲法を生成"""
        (self.path / "Archives").mkdir(parents=True, exist_ok=True)
        (self.path / "Concepts").mkdir(parents=True, exist_ok=True)
        
        # 憲法 (Constitution) の制定
        const_path = self.path / "Constitution.md"
        if not const_path.exists():
            with open(const_path, "w", encoding="utf-8") as f:
                f.write(f"# {self.name} 憲法\n\n**絶対的イデオロギー:** {self.ideology}\n\n我々はこの真理を探求するために存在する。")

        # プロフィールの初期生成（存在しない場合）
        profile_path = self.path / "Profile.json"
        if not profile_path.exists():
            gen = CivilizationProfileGenerator()
            profile = gen.generate_profile(self.name, self.ideology, self.parent_name)
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)

        # 文化的価値観の初期生成（存在しない場合）
        culture_path = self.path / "Culture_Values.json"
        if not culture_path.exists():
            self._initialize_culture()

        # 賢者たちの初期生成（存在しない場合）
        sages_path = self.path / "Sages.json"
        if not sages_path.exists():
            gen = SageGenerator()
            sages = gen.generate_sages(self.name, self.ideology)
            with open(sages_path, "w", encoding="utf-8") as f:
                json.dump([s.to_dict() for s in sages], f, ensure_ascii=False, indent=2)

        # 社会資源 (Social State) の初期化
        state_path = self.path / "Social_State.json"
        if not state_path.exists():
            initial_state = {
                "power": 50,  # 統制力
                "wealth": 50, # 富
                "faith": 50   # 信仰
            }
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(initial_state, f, ensure_ascii=False, indent=2)

    def _update_stats(self, heat):
        """プロフィールの統計を更新"""
        profile_path = self.path / "Profile.json"
        if profile_path.exists():
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                
                stats = profile["stats"]
                old_total = stats["total_discussions"]
                old_avg = stats["avg_heat"]
                
                stats["generation"] += 1
                stats["total_discussions"] += 1
                stats["avg_heat"] = int((old_avg * old_total + heat) / stats["total_discussions"])
                
                with open(profile_path, "w", encoding="utf-8") as f:
                    json.dump(profile, f, ensure_ascii=False, indent=2)
            except:
                pass

    def _update_sage_influence(self, winner_name):
        """特定の賢者の影響力をアップさせる"""
        sages = self._get_sages()
        for s in sages:
            if s["name"] == winner_name:
                s["influence"] += 5
                print(f"🌟 {winner_name} の影響力が上昇した (+5)")
                break
        self._save_sages(sages)

    def _get_sages(self):
        sages_path = self.path / "Sages.json"
        if sages_path.exists():
            with open(sages_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_sages(self, sages):
        sages_path = self.path / "Sages.json"
        with open(sages_path, "w", encoding="utf-8") as f:
            json.dump(sages, f, ensure_ascii=False, indent=2)

    def _add_sage(self, sage_dict):
        sages = self._get_sages()
        sages.append(sage_dict)
        self._save_sages(sages)

    def _initialize_culture(self):
        """文化的価値観の初期生成"""
        print(f"🎨 Generating cultural identity for {self.name}...")
        
        prompt = [
            {"role": "system", "content": "あなたは文化人類学者です。文明の独自性を定義してください。"},
            {"role": "user", "content": (
                f"文明名: {self.name}\n"
                f"イデオロギー: {self.ideology}\n\n"
                f"この文明が大切にする3つの『文化的価値観』をJSON形式で作成してください。\n"
                f"形式:\n"
                f"{{\n"
                f"  \"colors\": {{\"red\": \"divine\"}},\n"
                f"  \"numbers\": {{\"3\": \"lucky\"}},\n"
                f"  \"concepts\": {{\"fire\": \"symbol_of_rebirth\"}}\n"
                f"}}"
            )}
        ]
        
        try:
            result = chat_with_gods(prompt, temperature=0.7)
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                culture_data = json.loads(json_match.group())
            else:
                culture_data = {}
        except:
            culture_data = {}  # フォールバック
        
        # 履歴の追加
        culture_data["formation_history"] = [
            {"gen": 0, "event": f"Founded with ideology: {self.ideology}"}
        ]
        
        culture_path = self.path / "Culture_Values.json"
        with open(culture_path, "w", encoding="utf-8") as f:
            json.dump(culture_data, f, ensure_ascii=False, indent=2)
    
    def _get_culture_values(self):
        """文化的価値観を取得"""
        culture_path = self.path / "Culture_Values.json"
        if culture_path.exists():
            with open(culture_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _add_cultural_event(self, generation, event_description):
        """文化履歴にイベントを追加"""
        culture = self._get_culture_values()
        if "formation_history" not in culture:
            culture["formation_history"] = []
        culture["formation_history"].append({"gen": generation, "event": event_description})
        
        culture_path = self.path / "Culture_Values.json"
        with open(culture_path, "w", encoding="utf-8") as f:
            json.dump(culture, f, ensure_ascii=False, indent=2)

    def _check_revolution(self, log, generation):
        """革命（Revolution）の判定：不満が溜まると憲法を書き換える"""
        state = self._get_social_state()
        # 権力が低すぎる、または富が極端に偏っている場合に発生
        if (state["power"] < 20 or state["wealth"] < 15 or state["wealth"] > 85):
            if random.random() < 0.3:
                print(f"🔥 REVOLUTION: {self.name} で民衆が蜂起！体制が崩壊します。")
                
                rev_prompt = [
                    {"role": "system", "content": "あなたは革命の目撃者です。"},
                    {"role": "user", "content": f"議論の文脈({log})と現在の不満に基づき、新たな【革命憲法】を日本語で書き上げてください。イデオロギーも刷新される可能性があります。"}
                ]
                new_constitution = chat_with_gods(rev_prompt)
                
                const_path = self.path / "Constitution.md"
                with open(const_path, "w", encoding="utf-8") as f:
                    f.write(new_constitution)
                
                # 資源をリセット
                self._save_social_state({"power": 40, "wealth": 40, "faith": 60})
                
                # 文化履歴に記録
                self._add_cultural_event(generation, "Revolution: Constitution was rewritten")
                return True
        return False

    def _get_social_state(self):
        state_path = self.path / "Social_State.json"
        if state_path.exists():
            with open(state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"power": 50, "wealth": 50, "faith": 50}

    def _save_social_state(self, state):
        state_path = self.path / "Social_State.json"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _update_social_state(self, updates):
        """議論の結果に基づいてリソースを更新"""
        state = self._get_social_state()
        for key in ["power", "wealth", "faith"]:
            if key in updates:
                state[key] = max(0, min(100, state[key] + updates[key]))
                print(f"📊 {self.name} {key}: {state[key]} ({updates[key]:+d})")
        self._save_social_state(state)

    def run_cycle(self, generation, knowledge_base=None):
        """サイクルの実行 (議論→記録→概念)"""
        # 1. 話題の選定
        topic, mode, category = TopicGenerator.generate_topic(self.ideology)
        print(f"\n🌀 Cycle Start: {self.name} (Gen {generation}) | Topic: {topic} ({category}/{mode})")
        
        # 2. THE ARENA (議論) - 日本語でのプロンプト構築
        system_prompt = (
            f"あなたは文明 '{self.name}' の記録係です。"
            f"絶対的イデオロギー '{self.ideology}' に基づき、住民たちの議論を日本語で記録してください。"
        )
        
        # 過去の知恵を注入
        wisdom_context = ""
        if knowledge_base:
            wisdom = knowledge_base.get_related_wisdom(category)
            if wisdom:
                wisdom_text = "\n".join([f"- {w['name']}: {w['definition']}" for w in wisdom])
                wisdom_context = f"\n【参考：過去の賢者たちの知見】\n{wisdom_text}\n"
        
        # 賢者のロードとコンテキスト構築
        sages_list = self._get_sages()
        for s in sages_list: s['role'] = 'SAGE'
        
        # 外部介入アバターのロード
        avatar_path = self.path / "Dropped_Avatars.json"
        if avatar_path.exists():
            with open(avatar_path, "r", encoding="utf-8") as f:
                avatars = json.load(f)
                for a in avatars: a['role'] = 'AVATAR'
                sages_list.extend(avatars)

        sages_text = "\n".join([f"- {s.get('icon', '👤')} {s['name']} ({s['trait']}): {s['bio']} [役割: {s['role']}, 特有の話し方: {s.get('speech_style', '標準的')}]" for s in sages_list])
        sages_context = f"\n【この文明の主要な賢者・アバターたち（発言者候補）】\n{sages_text}\n"
        
        # 文化的価値観のロードとコンテキスト構築
        culture = self._get_culture_values()
        culture_context = ""
        if culture:
            culture_text = ""
            if "colors" in culture:
                culture_text += f"\n色彩観: {', '.join([f'{k}={v}' for k, v in culture.get('colors', {}).items()])}"
            if "numbers" in culture:
                culture_text += f"\n数秘主義: {', '.join([f'{k}={v}' for k, v in culture.get('numbers', {}).items()])}"
            if "concepts" in culture:
                culture_text += f"\n核心概念: {', '.join([f'{k}={v}' for k, v in culture.get('concepts', {}).items()])}"
            
            if culture_text:
                culture_context = f"\n【文明の文化的価値観】{culture_text}\n※ 該論はこれらの価値観に治って展開すること。\n"

        # 社会状態のロード
        social_state = self._get_social_state()
        state_context = f"\n【現在の社会情勢】\n- 権力: {social_state['power']}\n- 富: {social_state['wealth']}\n- 信仰: {social_state['faith']}\n"

        if mode == "SERIOUS":
            user_prompt = f"第{generation}世代の激しい討論を記録せよ。テーマは『{topic}』。賢者たちがそれぞれの【動機】に基づき、社会の主導権を握るべく議論せよ。日本語で。"
        elif mode == "CASUAL":
            user_prompt = f"第{generation}世代の住民たちらによる、テーマ『{topic}』についての雑談。賢者たちの個人的な関係性や【動機】が垣間見える会話形式で。"
        elif mode == "OBSERVATIONAL":
            user_prompt = f"第{generation}世代における、『{topic}』への住民たちの反応。賢者たちが自身の【動機】に沿ってどう動いているかを中心に。"
        else: # SPECULATIVE
            user_prompt = f"第{generation}世代の賢者たちが『{topic}』に基づき、文明の将来を賭けた大胆な空想を繰り広げる。"

        prompt = [
            {"role": "system", "content": system_prompt + wisdom_context + sages_context + culture_context + state_context},
            {"role": "user", "content": (
                f"{user_prompt}\n\n"
                f"※ 記録は必ず **[アイコン] 名前: 「セリフ」** の形式の会話劇（ダイアログ）として描写してください。\n"
                f"※ 各賢者の【特有の話し方】や【動機】を反映し、誰が話しているか明確に区別できるようにしてください。\n"
                f"※ 出力は全て日本語でお願いします。\n"
                f"※ 議論の最後に、以下の形式で【最優秀賢者】と【社会への影響】（権力、富、信仰の変動合計±20以内）を出力してください。\n"
                f"【最優秀賢者: 賢者名】\n"
                f"【社会への影響: 権力(+5), 富(-10), 信仰(0)】"
            )}
        ]
        
        discussion_log = chat_with_gods(prompt, temperature=0.8)
        
        # 白熱度の計算
        heat = calculate_heat(discussion_log, category, mode)
        
        # 影響力のある賢者の特定と更新
        import re
        winner_match = re.search(r'【最優秀賢者: (.*)】', discussion_log)
        if winner_match:
            winner_name = winner_match.group(1).strip()
            self._update_sage_influence(winner_name)
            
            # 社会資源の更新
            impact_match = re.search(r'【社会への影響: (.*)】', discussion_log)
            if impact_match:
                impact_str = impact_match.group(1)
                updates = {}
                for part in impact_str.split(','):
                    m = re.search(r'(権力|富|信仰)\(([\+\-]?\d+)\)', part)
                    if m:
                        key_map = {"権力": "power", "富": "wealth", "信仰": "faith"}
                        updates[key_map[m.group(1)]] = int(m.group(2))
                self._update_social_state(updates)

        # プロフィール更新
        self._update_stats(heat)
        
        # 参加者の抽出 (Spotlight System)
        participants = []
        for s in sages_list:
            if s['name'] in discussion_log:
                participants.append(f"{s['name']}({s.get('icon', '👤')}:{s['role']})")
        participants_str = ", ".join(participants) if participants else "一般市民"

        # ログ保存 (メタデータ付き)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.path / "Archives" / f"Gen{generation}_{timestamp}.md"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"# 第{generation}世代 議事録\n\n")
            f.write(f"**話題**: {topic}\n")
            f.write(f"**属性**: {category} / {mode}\n")
            f.write(f"**参加者**: {participants_str}\n")
            f.write(f"**白熱度**: {'🔥' * (heat // 30 + 1)} ({heat})\n\n")
            f.write("---\n\n")
            f.write(discussion_log)

        # 3. THE PHILOSOPHER (概念抽出) - 日本語で 
        concept_prompt = [
            {"role": "system", "content": "あなたは抽象概念を抽出する哲学者です。"},
            {"role": "user", "content": f"以下の議論から、普遍的な『新しい概念』を一つ日本語で定義し、Markdown形式（# 概念名、## 定義、## 意義）で出力せよ。\n\n【議論内容】\n{discussion_log}"}
        ]
        new_concept = chat_with_gods(concept_prompt, temperature=0.5)
        
        # 概念保存
        concept_file = self.path / "Concepts" / f"Concept_Gen{generation}.md"
        with open(concept_file, "w", encoding="utf-8") as f:
            f.write(new_concept)
        
        # 知識ベースへ登録
        if knowledge_base:
            try:
                name = new_concept.split("#")[1].split("\n")[0].strip()
                defn = new_concept.split("## 定義")[1].split("##")[0].strip()
                knowledge_base.add_wisdom(category, name, defn, heat)
            except:
                pass
            
        print(f"✨ Concept Born: {self.name} | Heat: {heat}")
        
        # 4. THE GOVERNOR (分岐判定)
        self.dogma_level += 0.05
        
        # 革命チェック
        self._check_revolution(discussion_log, generation)
        
        # 免疫チェック (アバター審問)
        self._check_inquisition(generation)
        
        return self._check_schism(discussion_log, generation)
    
    def _check_inquisition(self, generation):
        """免疫システム: アバターの異端度を判定し、審問または適応を実行"""
        avatar_path = self.path / "Dropped_Avatars.json"
        if not avatar_path.exists():
            return
        
        with open(avatar_path, "r", encoding="utf-8") as f:
            avatars = json.load(f)
        
        if not avatars:
            return
        
        culture = self._get_culture_values()
        remaining_avatars = []
        
        for avatar in avatars:
            # 異端度スコアの計算
            heresy_score = self._calculate_heresy(avatar, culture)
            
            if heresy_score > 70:
                print(f"🛡️ INQUISITION: {avatar['name']} is being judged (heresy={heresy_score})")
                
                # LLMに審問を任せる
                verdict = self._ask_for_verdict(avatar, generation)
                
                if verdict == "REJECT":
                    print(f"⛓️ {avatar['name']} was rejected as heresy!")
                    self._banish_avatar(avatar, generation)
                elif verdict == "ADAPT":
                    print(f"✨ {avatar['name']} was sanctified as a prophet!")
                    self._sanctify_avatar(avatar, generation)
                    remaining_avatars.append(avatar)
                else:
                    remaining_avatars.append(avatar)
            else:
                # 低リスクなアバターは残す
                remaining_avatars.append(avatar)
        
        # 更新
        with open(avatar_path, "w", encoding="utf-8") as f:
            json.dump(remaining_avatars, f, ensure_ascii=False, indent=2)
    
    def _calculate_heresy(self, avatar, culture):
        """異端度スコアを計算"""
        score = 0
        
        # 介入者フラグで基社スコア
        if avatar.get("motivation") == "介入者":
            score += 50
        
        # 影響力が異常に高い
        if avatar.get("influence", 0) > 40:
            score += 20
        
        # 文化的価値観との乱離 (簡易的なキーワードチェック)
        bio_lower = avatar.get("bio", "").lower()
        if "fire" in bio_lower and culture.get("concepts", {}).get("fire") == "symbol_of_chaos":
            score += 15
        if "red" in bio_lower and culture.get("colors", {}).get("red") == "cursed":
            score += 15
        
        return score
    
    def _ask_for_verdict(self, avatar, generation):
        """アバターに対する審問結果をLLMに問う"""
        culture = self._get_culture_values()
        
        prompt = [
            {"role": "system", "content": "あなたは文明の審問官です。"},
            {"role": "user", "content": (
                f"異分子: {avatar['name']}\n"
                f"特徴: {avatar.get('bio', 'unknown')}\n"
                f"文明の文化: {json.dumps(culture, ensure_ascii=False)}\n\n"
                f"この人物は文明にとって 'REJECT'(拒絶/追放) か 'ADAPT'(受容/聖人化) かを判定してください。\n"
                f"※ 1ワードで答えてください: REJECT または ADAPT"
            )}
        ]
        
        result = chat_with_gods(prompt, temperature=0.6)
        if "REJECT" in result.upper():
            return "REJECT"
        elif "ADAPT" in result.upper():
            return "ADAPT"
        return "UNKNOWN"
    
    def _banish_avatar(self, avatar, generation):
        """アバターを追放し、伝説として記録"""
        legend_text = f"# 異端の追放: {avatar['name']}\n\n第{generation}世代、{avatar['name']}は異質な存在として文明に現れた。しかし、その思想は文明の根幹と相容れず、審問により追放された。\n\n**特徴**: {avatar.get('bio', 'unknown')}"
        
        legend_file = self.path / "Archives" / f"_Banished_{avatar['name']}_Gen{generation}.md"
        with open(legend_file, "w", encoding="utf-8") as f:
            f.write(legend_text)
        
        self._add_cultural_event(generation, f"Heretic {avatar['name']} was banished")
    
    def _sanctify_avatar(self, avatar, generation):
        """アバターを聖人として受入れ、文化に放射させる"""
        # 賢者に昇格
        self._add_sage(avatar)
        
        self._add_cultural_event(generation, f"Prophet {avatar['name']} was sanctified and became a sage")

    def _check_schism(self, log, generation):
        """分裂（Schism）の判定"""
        if random.random() < (0.2 + self.dogma_level * 0.1):
            sages = self._get_sages()
            if len(sages) < 2: return None
            
            # ランダムに2人の対立リーダーを選ぶ
            random.shuffle(sages)
            leader = sages[0]
            dissident = sages[1]
            
            print(f"⚡ SCHISM ALERT: {self.name} で {leader['name']} と {dissident['name']} が対立！")
            
            schism_prompt = [
                {"role": "system", "content": "あなたは社会学者です。"},
                {"role": "user", "content": f"議論の文脈から、{leader['name']}側と{dissident['name']}側で決定的に対立した『2つの相反する思想』を短い名称(10文字以内)で答えよ。\n形式: 思想A vs 思想B\n\n{log}"}
            ]
            schism_theme = chat_with_gods(schism_prompt)
            
            return {
                "theme": schism_theme,
                "leader_sage": leader,
                "dissident_sage": dissident
            }
        return None

# ==========================================
# 🌍 WORLD ENGINE (メインループ)
# ==========================================
def main():
    print("🚀 Project Genesis: Initializing Local Universe...")
    
    root_path = Path(OBSIDIAN_VAULT_PATH)
    root_path.mkdir(parents=True, exist_ok=True)
    
    # マネージャーの初期化
    reaper = EntropyManager(root_path, max_depth=MAX_DEPTH)
    archivist = ArchiveManager()
    oracle = KnowledgeBase(root_path)
    pado = WanderingBard(root_path)  # 流浪の詩人
    atlas = WorldMap(root_path)      # 世界地図
    chronicle = ChronicleCompiler(root_path) # 年代記
    
    # 最初の文明 (既存の文明がある場合はそれを引き継ぐ)
    civ_dir = root_path / "Civilizations"
    civs = []
    if civ_dir.exists():
        for item in civ_dir.iterdir():
            if not item.is_dir(): continue
            ideology = "不明な真理"
            const_path = item / "Constitution.md"
            if const_path.exists():
                with open(const_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if "絶対的イデオロギー:" in line:
                            ideology = line.split(":", 1)[1].strip()
            civs.append(Civilization(item.name, root_path, ideology))
    
    if not civs:
        print("🌌 創世開始... Seeds.mdから原初の文明を生成します。")
        # Seeds.mdから初期文明を生成
        initial_seeds = [
            {"name": "Seekers", "ideology": "真実は問いかけの中にこそ存在する"},
            {"name": "Harmonists", "ideology": "全ては循環の中で一つになる"},
            {"name": "Architects", "ideology": "世界は意志によって形作られる"}
        ]
        
        for seed in initial_seeds:
            civ = Civilization(seed["name"], root_path, seed["ideology"])
            civs.append(civ)
            print(f"✨ 文明誕生: {seed['name']} | イデオロギー: {seed['ideology']}")
    
    for gen in range(1, MAX_GENERATIONS + 1):
        print(f"\n⏳ --- YEAR {gen} ---")
        
        new_civs = []
        
        # 🚀 並列処理: 複数文明を同時実行
        def process_civilization(civ):
            """単一文明の1サイクルを処理"""
            schism_result = civ.run_cycle(gen, oracle)
            archivist.metabolize_archives(civ)
            return (civ, schism_result)
        
        # ThreadPoolExecutorで並列実行（最大2-3並列、GPU VRAMに応じて調整）
        max_workers = min(3, len(civs))  # 最大3文明まで同時処理
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 全文明を並列でキューに投入
            future_to_civ = {executor.submit(process_civilization, civ): civ for civ in civs}
            
            # 完了順に結果を取得
            for future in as_completed(future_to_civ):
                civ, schism_result = future.result()
                
                # 分裂が発生した場合
                if schism_result:
                    theme = schism_result["theme"]
                    l_sage = schism_result["leader_sage"]
                    d_sage = schism_result["dissident_sage"]
                    
                    print(f"⚠️ {civ.name} が分裂: {theme}")
                    new_name_a = f"{civ.name}_Orthodox_{gen}"
                    new_name_b = f"{civ.name}_Reformed_{gen}"
                    
                    civ_a = Civilization(new_name_a, root_path, f"{l_sage['name']}: {theme.split('vs')[0]}", civ.name)
                    civ_b = Civilization(new_name_b, root_path, f"{d_sage['name']}: {theme.split('vs')[-1]}", civ.name)
                    
                    # 創設者を各文明に追加
                    civ_a._add_sage(l_sage)
                    civ_b._add_sage(d_sage)
                    
                    new_civs.append(civ_a)
                    new_civs.append(civ_b)
                else:
                    new_civs.append(civ)  # 存続
                
                # 領土拡大の処理
                state = civ._get_social_state()
                atlas.expand(civ.name, state.get("power", 50), state.get("wealth", 50))
        
        # 地図の保存
        atlas.save()

        # 年代記の更新 (10年に1回、および初回)
        if gen % 10 == 0 or gen == 0:
            chronicle.compile()

        # 新陳代謝の実行（リストを更新）
        civs = reaper.perform_metabolism(new_civs)
        
        # パドの旅（1時間ごと）
        if pado.should_journey():
            pado.embark_on_journey(civs)
        
        if not civs:
            print("💀 全ての文明が滅びました。世界は静寂に包まれた...")
            print("✨ 再創世を開始します...")
            civs = [Civilization(f"New_Genesis_{gen}", root_path, "失われた伝説を超えて")]
            
        print(f"💤 Sleeping for {CYCLE_DURATION_SEC} seconds...")
        time.sleep(CYCLE_DURATION_SEC)

if __name__ == "__main__":
    main()
