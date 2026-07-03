from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# 1. Configuration for RTX 3060 Ti (8GB VRAM)
max_seq_length = 2048 # 8GB VRAMを考慮
dtype = None # Noneなら自動検出
load_in_4bit = True # メモリ節約のため必須

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/llama-3-8b-Instruct-bnb-4bit", # ベースモデル
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# 2. Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # Rank
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth", # 非常に重要
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)

# 3. Load Dataset
# 先ほど作成した genesis_training_alpaca.json を読み込み
dataset = load_dataset("json", data_files="genesis_training_alpaca.json", split="train")

# 4. Formatting function (Alpaca style)
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

EOS_TOKEN = tokenizer.eos_token
def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs       = examples["input"]
    outputs      = examples["output"]
    texts = []
    for instruction, input, output in zip(instructions, inputs, outputs):
        text = alpaca_prompt.format(instruction, input, output) + EOS_TOKEN
        texts.append(text)
    return { "text" : texts, }

dataset = dataset.map(formatting_prompts_func, batched = True,)

# 5. Trainer setup
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False, # 短いテキストが多い場合はFalse
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # テスト用に少なめに設定（必要に応じて増やしてください）
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)

# 6. Training execution
print("Starting training...")
trainer_stats = trainer.train()

# 7. Save and Export to GGUF (for Ollama)
print("Saving model and exporting to GGUF...")
model.save_pretrained_gguf("model_gguf", tokenizer, quantization_method = "q4_k_m")

# Ollama用のModelfileのヒントを表示
print("\n--- Training Complete ---")
print("To use with Ollama:")
print("1. cd model_gguf")
print("2. ollama create genesis-model -f Modelfile")
print("3. ollama run genesis-model")
