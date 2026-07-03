import os
import json
import random
from pathlib import Path
from PIL import Image, ImageDraw

class WorldMap:
    def __init__(self, root_path, size=100):
        self.root_path = Path(root_path)
        self.map_dir = self.root_path / "00_World_Atlas"
        self.map_dir.mkdir(exist_ok=True)
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.civ_colors = {} # {civ_name: (r, g, b)}
        self.load()

    def load(self):
        map_file = self.map_dir / "Map_Data.json"
        if map_file.exists():
            with open(map_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.grid = data.get("grid", self.grid)
                self.civ_colors = {k: tuple(v) for k, v in data.get("colors", {}).items()}

    def save(self):
        map_file = self.map_dir / "Map_Data.json"
        with open(map_file, "w", encoding="utf-8") as f:
            json.dump({
                "grid": self.grid,
                "colors": {k: list(v) for k, v in self.civ_colors.items()}
            }, f, ensure_ascii=False, indent=2)
        self.render()

    def register_civilization(self, civ_name):
        if civ_name not in self.civ_colors:
            # Generate a bright, distinct color
            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
            self.civ_colors[civ_name] = color
            
            # Place initial 'Capital' at a random empty spot
            attempts = 0
            while attempts < 100:
                x, y = random.randint(0, self.size-1), random.randint(0, self.size-1)
                if self.grid[y][x] is None:
                    self.grid[y][x] = civ_name
                    break
                attempts += 1

    def expand(self, civ_name, power, wealth):
        """領土拡大ロジック"""
        if civ_name not in self.civ_colors:
            self.register_civilization(civ_name)
            
        # 拡大回数は Power と Wealth に依存 (最低1回)
        expansion_attempts = max(1, int((power + wealth) / 20))
        
        owned_cells = []
        for y in range(self.size):
            for x in range(self.size):
                if self.grid[y][x] == civ_name:
                    owned_cells.append((x, y))
                    
        if not owned_cells: return

        for _ in range(expansion_attempts):
            source_x, source_y = random.choice(owned_cells)
            # 隣接4方向
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            tx, ty = source_x + dx, source_y + dy
            
            if 0 <= tx < self.size and 0 <= ty < self.size:
                target = self.grid[ty][tx]
                if target is None:
                    self.grid[ty][tx] = civ_name
                    owned_cells.append((tx, ty))
                elif target != civ_name:
                    # 将来的にはここで戦争ロジック（Power比較）
                    pass

    def render(self):
        """現在の世界地図を画像として保存"""
        img = Image.new("RGB", (self.size * 5, self.size * 5), color=(5, 5, 8)) # bg-deep
        draw = ImageDraw.Draw(img)
        
        for y in range(self.size):
            for x in range(self.size):
                civ = self.grid[y][x]
                if civ:
                    color = self.civ_colors.get(civ, (125, 95, 255))
                    draw.rectangle(
                        [x * 5, y * 5, (x + 1) * 5 - 1, (y + 1) * 5 - 1],
                        fill=color
                    )
        
        img.save(self.map_dir / "World_Map.png")
        # UIから見れるように static フォルダ等にもコピーしたいが、まずはプロジェクトルートの00_World_Atlas

if __name__ == "__main__":
    # テスト実行
    atlas = WorldMap(".")
    atlas.register_civilization("Seekers")
    atlas.expand("Seekers", 80, 50)
    atlas.save()
    print("Map generated at 00_World_Atlas/World_Map.png")
