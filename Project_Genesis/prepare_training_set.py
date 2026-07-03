import json
import os
from pathlib import Path

def prepare_dataset():
    training_data_dir = Path("training_data")
    output_file = Path("genesis_training_alpaca.json")
    dataset = []

    # 1. Lore and Myth
    lore_file = training_data_dir / "lore_and_myth.txt"
    if lore_file.exists():
        with open(lore_file, "r", encoding="utf-8") as f:
            content = f.read()
            # 分割して登録（簡易的にセクションごと）
            sections = content.split("--- SOURCE:")
            for section in sections:
                if not section.strip():
                    continue
                lines = section.split("\n")
                source = lines[0].strip()
                text = "\n".join(lines[1:]).strip()
                
                dataset.append({
                    "instruction": "Project Genesisの伝承や背景、神話について説明してください。",
                    "input": f"ソースコード: {source}",
                    "output": text
                })

    # 2. Civilization Profiles
    civ_file = training_data_dir / "civilization_profiles.jsonl"
    if civ_file.exists():
        with open(civ_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                name = data.get("display_name", data.get("name"))
                dataset.append({
                    "instruction": f"文明「{name}」の詳細な情報を教えてください。",
                    "input": "",
                    "output": (
                        f"文明名: {name}\n"
                        f"性格特性: {', '.join(data.get('personality_traits', []))}\n"
                        f"トーン: {data.get('tone')}\n"
                        f"バイオグラフィ: {data.get('bio')}\n"
                        f"イデオロギー: {data.get('ideology')}\n"
                        f"統計: 第{data.get('stats', {}).get('generation')}世代, 総議論数 {data.get('stats', {}).get('total_discussions')}"
                    )
                })

    # 3. Sage Personalities
    sage_file = training_data_dir / "sage_personalities.jsonl"
    if sage_file.exists():
        with open(sage_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                name = data.get("name")
                civ_name = data.get("civ_name")
                dataset.append({
                    "instruction": f"賢者「{name}」の性格や話し方、背景を教えてください。",
                    "input": f"所属文明: {civ_name}",
                    "output": (
                        f"名前: {name}\n"
                        f"特性: {data.get('trait')}\n"
                        f"バイオグラフィ: {data.get('bio')}\n"
                        f"話し方のスタイル: {data.get('speech_style')}\n"
                        f"アイコン: {data.get('icon')}\n"
                        f"モチベーション: {data.get('motivation')}"
                    )
                })

    # Save as JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(dataset)} items in {output_file}")

if __name__ == "__main__":
    prepare_dataset()
