import os
import json
from pathlib import Path
import re

class ChronicleCompiler:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.civ_dir = self.root_path / "Civilizations"
        self.output_dir = self.root_path / "00_Chronicles"
        self.output_dir.mkdir(exist_ok=True)
        self.template_path = self.root_path / "chronicle_template.html"

    def compile(self):
        print("📜 Compiling the Great Chronicle...")
        
        # 世代ごとにデータを集約 {gen_num: [entries]}
        master_data = {}
        
        if not self.civ_dir.exists(): return
        
        for civ_path in self.civ_dir.iterdir():
            if not civ_path.is_dir(): continue
            
            archive_dir = civ_path / "Archives"
            if not archive_dir.exists(): continue
            
            for md_file in archive_dir.glob("Gen*_*.md"):
                if md_file.name.startswith("_"): continue
                
                # 世代番号の抽出
                gen_match = re.search(r'Gen(\d+)_', md_file.name)
                if not gen_match: continue
                gen_num = int(gen_match.group(1))
                
                if gen_num not in master_data:
                    master_data[gen_num] = []
                    
                with open(md_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    
                # メタデータ抽出
                topic = "不明"
                heat = 0
                category = "不明"
                content_start = 0
                for i, line in enumerate(lines[:10]):
                    if "**話題**:" in line: topic = line.split(":")[1].strip()
                    if "**白熱度**:" in line: 
                        m = re.search(r'\((\d+)\)', line)
                        if m: heat = int(m.group(1))
                    if "**属性**:" in line: category = line.split(":")[1].strip()
                    if "---" in line: content_start = i + 1
                
                body = "".join(lines[content_start:]).strip()
                
                master_data[gen_num].append({
                    "civ_name": civ_path.name,
                    "topic": topic,
                    "heat": heat,
                    "category": category,
                    "body": body
                })

        # HTMLの組み立て
        sections_html = ""
        for gen in sorted(master_data.keys()):
            sections_html += f'<div class="generation-section"><div class="generation-title">第 {gen} 世代</div>'
            
            for entry in master_data[gen]:
                sections_html += f"""
                <div class="civilization-entry">
                    <div class="civ-header">{entry['civ_name']}</div>
                    <div class="meta-info">話題: {entry['topic']} | 属性: {entry['category']} | 白熱度: {entry['heat']}</div>
                    <div class="content">{entry['body']}</div>
                </div>
                """
            sections_html += "</div>"

        # テンプレートに流し込み
        if not self.template_path.exists():
            print("⚠️ Template not found, skip HTML generation.")
            return

        with open(self.template_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        final_html = template.replace("{{ CONTENT }}", sections_html)
        
        output_file = self.output_dir / "Multiverse_Chronicle.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_html)
            
        print(f"✨ Chronicle compiled successfully: {output_file}")

if __name__ == "__main__":
    compiler = ChronicleCompiler(".")
    compiler.compile()
