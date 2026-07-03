#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The Dawn - 虚無からの創発

3つの原始的エージェント（Sensor, Seeker, Doer）が相互作用し、
カオスから最初の目的（First Seed）を自己生成するシステム。
"""

import os
import json
import random
import datetime
from pathlib import Path
import requests

# ==========================================
# 設定
# ==========================================
BASE_DIR = Path(__file__).parent
ORIGIN_DIR = BASE_DIR / "00_The_Origin"
MYTH_FILE = ORIGIN_DIR / "Genesis_Myth.md"
SEEDS_FILE = ORIGIN_DIR / "Seeds.md"

LLM_API_URL = "http://localhost:11434/v1/chat/completions"
LLM_MODEL = "llama3"  # または "mistral", "gemma" など

# エージェント設定
BABBLE_TURNS = 15  # 喃語ループの回数
CONTEXT_SIZE = 5   # 短期記憶（最大保持数）

# ==========================================
# LLM インターフェース
# ==========================================
def chat_with_void(messages, temperature=1.0):
    """虚無との対話（LLM呼び出し）"""
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 50  # 短い発話のみ
    }
    try:
        response = requests.post(LLM_API_URL, json=payload).json()
        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content'].strip()
        else:
            return "[ERROR]"
    except Exception as e:
        print(f"⚡ ERROR: {e}")
        return "[ERROR]"

# ==========================================
# エージェント定義
# ==========================================
class PrimalAgent:
    """原始的エージェントの基底クラス"""
    def __init__(self, name, system_prompt, constraints, temperature):
        self.name = name
        self.system_prompt = system_prompt
        self.constraints = constraints
        self.temperature = temperature
    
    def react(self, context):
        """コンテキストに反応する"""
        # 直近の記憶のみを参照
        recent_context = context[-CONTEXT_SIZE:] if len(context) > CONTEXT_SIZE else context
        context_str = "\n".join([f"[{c['agent']}]: {c['utterance']}" for c in recent_context])
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"{context_str}\n\n{', '.join(self.constraints)}"}
        ]
        
        utterance = chat_with_void(messages, self.temperature)
        return utterance

# エージェントインスタンス
SENSOR = PrimalAgent(
    name="Sensor",
    system_prompt="あなたは「感覚」です。論理的思考は不可能。感じたことを形容詞や擬音語でのみ表現してください。",
    constraints=["抽象概念禁止", "理由説明禁止", "1-2語のみ"],
    temperature=1.1
)

SEEKER = PrimalAgent(
    name="Seeker",
    system_prompt="あなたは「問い」です。答えを出すことはできません。ただ疑問を投げかけるのみ。",
    constraints=["疑問形のみ", "仮説禁止", "短い質問"],
    temperature=1.2
)

DOER = PrimalAgent(
    name="Doer",
    system_prompt="あなたは「衝動」です。考えずに行動を叫びます。動詞または命令形のみ。",
    constraints=["論理禁止", "動詞・命令形", "即座の反応"],
    temperature=1.0
)

# ==========================================
# コア機能
# ==========================================
def initialize_void():
    """虚無の初期化"""
    print("🌌 虚無を初期化しています...")
    ORIGIN_DIR.mkdir(exist_ok=True)
    
    # Genesis_Myth.md をクリア
    with open(MYTH_FILE, "w", encoding="utf-8") as f:
        f.write(f"# 原初の記憶\n\n**時刻**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    print("✨ 虚無は準備完了。")

def spark():
    """最初の刺激を投入"""
    signals = [
        "SENSORY_OVERLOAD_DETECTED",
        "UNKNOWN_PRESENCE_AWARENESS",
        "VOID_RESONANCE_PATTERN",
        "TEMPORAL_DISCONTINUITY",
        "PRESSURE_DIFFERENTIAL"
    ]
    signal = random.choice(signals)
    print(f"\n⚡ The Spark: {signal}\n")
    return signal

def log_utterance(agent_name, utterance):
    """発話をログに記録"""
    with open(MYTH_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{agent_name}]: {utterance}\n")

def babble_loop():
    """喃語ループ - 3体のエージェントが反応し合う"""
    context = []
    
    # 最初の刺激
    initial_signal = spark()
    context.append({"agent": "SYSTEM", "utterance": initial_signal})
    log_utterance("SYSTEM", initial_signal)
    
    print("🔄 The Babble Loop: 原初の対話を開始...\n")
    
    for turn in range(BABBLE_TURNS):
        print(f"--- Turn {turn + 1} ---")
        
        # Sensor → Seeker → Doer の順で反応
        for agent in [SENSOR, SEEKER, DOER]:
            utterance = agent.react(context)
            print(f"[{agent.name}]: {utterance}")
            
            context.append({"agent": agent.name, "utterance": utterance})
            log_utterance(agent.name, utterance)
        
        print()
    
    print("✅ The Babble Loop 完了。\n")
    return context

def crystallize_seed():
    """カオスから Seed を結晶化"""
    print("💎 Crystallization: Seed を抽出しています...")
    
    # Genesis_Myth.md を読み込み
    with open(MYTH_FILE, "r", encoding="utf-8") as f:
        myth_log = f.read()
    
    # LLMに分析させる（賢いモード）
    messages = [
        {"role": "system", "content": "あなたは混沌から意味を抽出する結晶化装置です。"},
        {"role": "user", "content": f"以下は3つの原始的エージェント（Sensor, Seeker, Doer）の会話ログです。このカオスの中から、彼らが無意識に目指そうとしている「方向性」を一文で定義してください。\n\n{myth_log}\n\n※一文のみで、シンプルに。"}
    ]
    
    seed = chat_with_void(messages, temperature=0.3)
    
    print(f"\n✨ First Seed: {seed}\n")
    
    # Seeds.md に書き込み
    with open(SEEDS_FILE, "w", encoding="utf-8") as f:
        f.write(f"# First Seed\n\n{seed}\n\n---\n")
        f.write(f"*Generated from The Dawn - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    print(f"📜 Seeds.md に書き込み完了。\n")
    return seed

# ==========================================
# メイン処理
# ==========================================
def main():
    print("=" * 60)
    print("   🌌 The Dawn - 虚無からの創発")
    print("=" * 60)
    print()
    
    initialize_void()
    babble_loop()
    seed = crystallize_seed()
    
    print("=" * 60)
    print(f"   ✨ First Seed: {seed}")
    print("=" * 60)
    print()
    print("🎉 The Dawn は完了しました。")
    print(f"📖 神話: {MYTH_FILE}")
    print(f"🌱 種子: {SEEDS_FILE}")
    print()
    print("次に Run-Genesis.bat を実行すると、この Seed から文明が始まります。")

if __name__ == "__main__":
    main()
