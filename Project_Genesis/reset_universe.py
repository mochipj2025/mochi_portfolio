import os
import shutil
import datetime
from pathlib import Path

def reset_multiverse():
    root = Path(".")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"Multiverse_Archive_{timestamp}"
    archive_path = root / "Archives" / archive_name
    
    print(f"🌌 Archiving current Multiverse to: {archive_path}")
    archive_path.mkdir(parents=True, exist_ok=True)
    
    # Folders to archive and reset
    targets = ["Civilizations", "00_Knowledge_Base", "00_Legends", "00_Pado_Tales"]
    
    for target in targets:
        target_path = root / target
        if target_path.exists():
            print(f"📦 Moving {target}...")
            shutil.move(str(target_path), str(archive_path / target))
            # Recreate empty folders for the next run
            target_path.mkdir(exist_ok=True)
            
    print("\n✨ Multiverse has been reset.")
    print("🚀 You can now start the simulation to birth a new world.")

if __name__ == "__main__":
    confirm = input("Are you sure you want to reset the universe? All current civilizations will be archived. (y/n): ")
    if confirm.lower() == 'y':
        reset_multiverse()
    else:
        print("Reset cancelled.")
