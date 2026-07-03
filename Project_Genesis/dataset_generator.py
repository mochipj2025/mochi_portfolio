import os
import json
from pathlib import Path

def generate_training_data():
    base_dir = Path(".")
    training_dir = base_dir / "training_data"
    training_dir.mkdir(exist_ok=True)

    # 1. Lore and Myth
    print("📜 Generating lore_and_myth.txt...")
    lore_files = [
        base_dir / "00_The_Origin" / "Genesis_Myth.md",
        base_dir / "00_The_Origin" / "Seeds.md"
    ]
    
    with open(training_dir / "lore_and_myth.txt", "w", encoding="utf-8") as out:
        for lf in lore_files:
            if lf.exists():
                with open(lf, "r", encoding="utf-8") as f:
                    out.write(f"--- SOURCE: {lf.name} ---\n")
                    out.write(f.read())
                    out.write("\n\n")
    
    # 2. Civilization Profiles and Sages
    print("👥 Extracting Civilization and Sage data...")
    profiles_out = open(training_dir / "civilization_profiles.jsonl", "w", encoding="utf-8")
    sages_out = open(training_dir / "sage_personalities.jsonl", "w", encoding="utf-8")

    civ_root = base_dir / "Civilizations"
    if civ_root.exists():
        for civ_dir in civ_root.iterdir():
            if civ_dir.is_dir():
                # Profile
                profile_path = civ_dir / "Profile.json"
                if profile_path.exists():
                    try:
                        with open(profile_path, "r", encoding="utf-8") as f:
                            profile = json.load(f)
                            profiles_out.write(json.dumps(profile, ensure_ascii=False) + "\n")
                    except Exception as e:
                        print(f"Error loading {profile_path}: {e}")

                # Sages
                sages_path = civ_dir / "Sages.json"
                if sages_path.exists():
                    try:
                        with open(sages_path, "r", encoding="utf-8") as f:
                            sages = json.load(f)
                            for sage in sages:
                                # Add civ context to sage trait
                                sage['civ_name'] = civ_dir.name
                                sages_out.write(json.dumps(sage, ensure_ascii=False) + "\n")
                    except Exception as e:
                        print(f"Error loading {sages_path}: {e}")

    profiles_out.close()
    sages_out.close()
    print("✅ Training data generation complete.")

if __name__ == "__main__":
    generate_training_data()
