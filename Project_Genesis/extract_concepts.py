import os
import re

def extract_concepts(directory="."):
    """
    Markdownファイルを読み込み、条件に従ってTopicとConcept Bornを抽出する。
    """
    excluded_list = []
    extracted_data = []

    # 1. ファイル一覧を取得してフィルタリング
    for filename in os.listdir(directory):
        if not filename.endswith(".md"):
            continue

        # ファイル名が30文字以上（拡張子含む）なら除外
        if len(filename) >= 30:
            excluded_list.append(filename)
            continue

        # 2. 条件に合致するファイルの内容を解析
        filepath = os.path.join(directory, filename)
        topic = None
        concept_born = None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # "Topic:" で始まる行を抽出（大文字小文字を区別しない場合は re.IGNORECASE を検討）
                    if line.startswith("Topic:"):
                        topic = line.replace("Topic:", "").strip()
                    # "Concept Born:" で始まる行を抽出
                    elif line.startswith("Concept Born:"):
                        concept_born = line.replace("Concept Born:", "").strip()

                    # ペアが見つかったら保存して次へ（1ファイル1ペア想定）
                    if topic and concept_born:
                        extracted_data.append({
                            "file": filename,
                            "topic": topic,
                            "concept": concept_born
                        })
                        break # ペアが見つかったのでこのファイルの読み込みを終了
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    # 3. 結果の表示
    print("--- 除外リスト (30文字以上) ---")
    for f in excluded_list:
        print(f"- {f}")
    
    print("\n--- 抽出されたペア ---")
    for data in extracted_data:
        print(f"File: {data['file']}")
        print(f"  Topic: {data['topic']}")
        print(f"  Concept Born: {data['concept']}")
        print("-" * 20)

if __name__ == "__main__":
    # カレントディレクトリまたは指定のフォルダを対象にする
    target_dir = "." # 必要に応じて変更可能
    extract_concepts(target_dir)
