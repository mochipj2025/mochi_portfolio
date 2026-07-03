from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import requests
import re
import time
from pathlib import Path

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(r"d:\00000\mochisura-lab\Project_Genesis")
CIV_DIR = BASE_DIR / "Civilizations"
LEGEND_DIR = BASE_DIR / "00_Legends"
LLM_API_URL = "http://localhost:11434/v1/chat/completions"
LLM_MODEL = "llama3"

@app.route('/api/civilizations', methods=['GET'])
def get_civilizations():
    civs = []
    if CIV_DIR.exists():
        for item in CIV_DIR.iterdir():
            if item.is_dir():
                # Get basic info
                const_path = item / "Constitution.md"
                ideology = "Unknown"
                parent_name = None
                if const_path.exists():
                    with open(const_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for line in lines:
                            if "絶対的イデオロギー:" in line:
                                ideology = line.split(":", 1)[1].strip()
                
                # Get parent name from profile if available
                profile_path = item / "Profile.json"
                if profile_path.exists():
                    with open(profile_path, "r", encoding="utf-8") as f:
                        profile = json.load(f)
                        parent_name = profile.get("parent_name")

                # Get sages count
                sages_count = 0
                sages_path = item / "Sages.json"
                if sages_path.exists():
                    try:
                        with open(sages_path, "r", encoding="utf-8") as f:
                            sages_count = len(json.load(f))
                    except: pass

                civs.append({
                    "name": item.name,
                    "ideology": ideology,
                    "parent": parent_name,
                    "sages_count": sages_count
                })
    return jsonify(civs)

@app.route('/api/genealogy')
def get_genealogy():
    """全文明の親子関係をMermaid形式のデータとして返す"""
    nodes = []
    edges = []
    if CIV_DIR.exists():
        for item in CIV_DIR.iterdir():
            if not item.is_dir(): continue
            
            # 親の名前を取得
            parent = None
            profile_path = item / "Profile.json"
            if profile_path.exists():
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    parent = profile.get("parent_name")
            
            nodes.append({"id": item.name, "label": item.name})
            if parent:
                edges.append({"from": parent, "to": item.name})
    
    return jsonify({"nodes": nodes, "edges": edges})

@app.route('/api/civilization/<civ_name>/files')
def get_files(civ_name):
    civ_path = CIV_DIR / civ_name
    archives = []
    if (civ_path / "Archives").exists():
        archives = [f.name for f in (civ_path / "Archives").glob("*.md")]
    
    concepts = []
    if (civ_path / "Concepts").exists():
        concepts = [f.name for f in (civ_path / "Concepts").glob("*.md")]
    
    return jsonify({
        "archives": sorted(archives, reverse=True),
        "concepts": sorted(concepts, reverse=True)
    })

@app.route('/api/profile/<civ_name>')
def get_profile(civ_name):
    profile_path = CIV_DIR / civ_name / "Profile.json"
    sages_path = CIV_DIR / civ_name / "Sages.json"
    
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        
        # 賢者情報を追加
        if sages_path.exists():
            with open(sages_path, "r", encoding="utf-8") as f:
                profile["sages"] = json.load(f)
        else:
            profile["sages"] = []
            
        # 社会情勢を追加
        state_path = CIV_DIR / civ_name / "Social_State.json"
        if state_path.exists():
            with open(state_path, "r", encoding="utf-8") as f:
                profile["social_state"] = json.load(f)
        else:
            profile["social_state"] = {"power": 50, "wealth": 50, "faith": 50}
        
        # 文化的価値観を追加
        culture_path = CIV_DIR / civ_name / "Culture_Values.json"
        if culture_path.exists():
            with open(culture_path, "r", encoding="utf-8") as f:
                profile["culture_values"] = json.load(f)

        return jsonify(profile)
    return jsonify({"error": "Profile not found"}), 404

@app.route('/api/timeline')
def get_timeline():
    """全文明から最新の議論を集めてheat順に返す"""
    all_discussions = []
    if CIV_DIR.exists():
        for civ_dir in CIV_DIR.iterdir():
            if not civ_dir.is_dir(): continue
            
            # 最新のArchiveを取得
            archive_dir = civ_dir / "Archives"
            if archive_dir.exists():
                files = sorted(archive_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
                for f in files[:3]: # 文明ごとに最新3件まで
                    if f.name.startswith("_"): continue
                    
                    try:
                        with open(f, "r", encoding="utf-8") as content_file:
                            lines = content_file.readlines()
                        
                        # メタ解析
                        topic = "不明"
                        heat = 0
                        category = "不明"
                        leading_sage = None
                        participants = []
                        
                        full_content = "".join(lines)
                        import re
                        sage_match = re.search(r'【最優秀賢者: (.*)】', full_content)
                        if sage_match:
                            leading_sage = sage_match.group(1).strip()

                        for line in lines[:12]:
                            if "**話題**:" in line: topic = line.split(":")[1].strip()
                            if "**白熱度**:" in line: 
                                parts = line.split("(")
                                if len(parts) > 1: heat = int(parts[1].split(")")[0])
                            if "**属性**:" in line: category = line.split(":")[1].split("/")[0].strip()
                            if "**参加者**:" in line:
                                p_list = line.split(":", 1)[1].strip()
                                if p_list != "一般市民":
                                    for p in p_list.split(", "):
                                        m = re.search(r'(.*?)\((.*?):(.*?)\)', p)
                                        if m:
                                            participants.append({
                                                "name": m.group(1),
                                                "icon": m.group(2),
                                                "role": m.group(3)
                                            })
                        
                        # 抜粋の抽出: '---' 以降の最初の数行
                        excerpt_lines = []
                        start_reading = False
                        for line in lines:
                            if "---" in line.strip():
                                start_reading = True
                                continue
                            if start_reading and line.strip():
                                excerpt_lines.append(line.strip())
                                if len(excerpt_lines) >= 3:
                                    break
                        
                        all_discussions.append({
                            "civ_name": civ_dir.name,
                            "filename": f.name,
                            "topic": topic,
                            "heat": heat,
                            "category": category,
                            "leading_sage": leading_sage,
                            "participants": participants,
                            "timestamp": f.stat().st_mtime,
                            "excerpt": " / ".join(excerpt_lines) # 抜粋
                        })
                    except:
                        continue
    
    # Heat順（盛り上がっている順）にソート
    return jsonify(sorted(all_discussions, key=lambda x: x['heat'], reverse=True))

@app.route('/api/pados_tales')
def get_pados_tales():
    """パドの見聞録リストを取得"""
    tales_dir = BASE_DIR / "00_The_Origin" / "Pados_Tales"
    if not tales_dir.exists():
        return jsonify([])
    
    files = [f.name for f in tales_dir.glob("*.md")]
    return jsonify(sorted(files, reverse=True))

@app.route('/api/pado_tale_content')
def get_pado_tale_content():
    """パドの物語の内容を取得"""
    filename = request.args.get('filename')
    tales_dir = BASE_DIR / "00_The_Origin" / "Pados_Tales"
    file_path = tales_dir / filename
    
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return jsonify({"content": f.read()})
    return jsonify({"error": "File not found"}), 404

@app.route('/api/file-content')
def get_file_content():
    path = request.args.get('path')
    full_path = BASE_DIR / path
    if full_path.exists():
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return "File not found", 404

@app.route('/api/legends', methods=['GET'])
def get_legends():
    legends = []
    if LEGEND_DIR.exists():
        legends = sorted([f.name for f in LEGEND_DIR.glob("*.md")], reverse=True)
    return jsonify(legends)

@app.route('/api/legend_content', methods=['GET'])
def get_legend_content():
    filename = request.args.get('filename')
    path = LEGEND_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"content": content})
    return jsonify({"error": "Legend not found"}), 404

@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text')
    
    prompt = [
        {"role": "system", "content": "あなたは優秀な翻訳家です。以下の文明の記録を、そのニュアンスを保ったまま美しく自然な日本語に翻訳してください。"},
        {"role": "user", "content": f"以下の英文を日本語に翻訳せよ:\n\n{text}"}
    ]
    
    payload = {
        "model": LLM_MODEL,
        "messages": prompt,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(LLM_API_URL, json=payload).json()
        translated_text = response['choices'][0]['message']['content']
        return jsonify({"translated": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

def get_speaker_meta(speaker, civ_name):
    """
    話者のアイコンとロールを特定する
    """
    # 賢者のリストをチェック
    sages_path = CIV_DIR / civ_name / "Sages.json"
    if sages_path.exists():
        with open(sages_path, "r", encoding="utf-8") as f:
            sages = json.load(f)
            for s in sages:
                if s['name'] == speaker:
                    return s.get('icon', '🧘'), 'SAGE'
    
    # プロフィールをチェック（アバターかどうか）
    profile_path = CIV_DIR / civ_name / "Profile.json"
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)
            # 簡易的にチェック
            if speaker in profile.get('display_name', ''):
                return profile.get('icon', '👤'), 'AVATAR'
    
    return '👤', 'CITIZEN'

def parse_discussion_to_thread(content, civ_name):
    """
    MD形式の議論をスレッド構造に変換
    """
    lines = content.split('\n')
    topic = "Unknown Topic"
    heat = 0
    
    for line in lines[:15]:
        if "**話題**:" in line: topic = line.split(":", 1)[1].strip()
        if "**白熱度**:" in line:
            m = re.search(r'\((\d+)\)', line)
            if m: heat = int(m.group(1))
            
    replies = []
    start_parsing = False
    current_id = 0
    
    for line in lines:
        if "---" in line:
            start_parsing = True
            continue
        if start_parsing and line.strip():
            # 形式: 賢者A「発言内容」
            match = re.search(r'(.+?)「(.+?)」', line)
            if match:
                speaker = match.group(1).strip()
                text = match.group(2).strip()
                icon, role = get_speaker_meta(speaker, civ_name)
                
                replies.append({
                    "id": current_id,
                    "parent_id": current_id - 1 if current_id > 0 else None,
                    "speaker": speaker,
                    "text": text,
                    "icon": icon,
                    "role": role
                })
                current_id += 1
                
    return {
        "topic": topic,
        "heat": heat,
        "replies": replies
    }

@app.route('/api/discussion/<civ>/<filename>')
def get_discussion_thread(civ, filename):
    path = CIV_DIR / civ / "Archives" / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            thread = parse_discussion_to_thread(content, civ)
            return jsonify(thread)
    return jsonify({"error": "Discussion not found"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
