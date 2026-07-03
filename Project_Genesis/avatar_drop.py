import os
import json
from pathlib import Path

def list_civilizations(root_path):
    civ_dir = Path(root_path) / "Civilizations"
    if not civ_dir.exists():
        return []
    return [d.name for d in civ_dir.iterdir() if d.is_dir()]

def drop_avatar():
    print("=" * 60)
    print("   🌌 Avatar Drop: 手動介入プロトコル")
    print("=" * 60)
    
    root_path = "."
    civs = list_civilizations(root_path)
    
    if not civs:
        print("❌ 文明が見つかりません。")
        return

    print("\n対象の文明を選択してください:")
    for i, civ in enumerate(civs):
        print(f"[{i}] {civ}")
        
    try:
        choice = int(input("\n選択 (番号): "))
        target_civ = civs[choice]
    except:
        print("❌ 無効な選択です。")
        return

    print(f"\n--- {target_civ} への降臨 ---")
    name = input("名前 (例: 神の使者、反逆者ゼロ): ")
    icon = input("アイコン絵文字 (例: 👼, 😈, 🤖): ")
    trait = input("気質 (例: 破壊的、導き、皮肉屋): ")
    style = input("話し方の特徴 (例: 語尾に『…なのだ』を付ける、古風な喋り、熱血): ")
    bio = input("詳細 (性格や目的): ")
    
    avatar = {
        "name": name,
        "icon": icon or "👤",
        "trait": trait,
        "speech_style": style or "標準的",
        "bio": bio,
        "motivation": "介入者",
        "influence": 50, # 介入者は最初から影響力が高い
        "manual": True
    }
    
    # Civilization/Dropped_Avatars.json に保存
    avatar_path = Path(root_path) / "Civilizations" / target_civ / "Dropped_Avatars.json"
    
    existing = []
    if avatar_path.exists():
        with open(avatar_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
            
    existing.append(avatar)
    
    with open(avatar_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
        
    print(f"\n✨ {name} が {target_civ} に降臨しました。")
    print("次回の議論サイクルからこのアバターが参加します。")

if __name__ == "__main__":
    drop_avatar()
