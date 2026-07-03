from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig
import torch

print("Loading model and tokenizer...")

# 4-bit quantization config for RTX 3060 Ti (8GB VRAM)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# Load base model (using TinyLlama - no authentication required)
model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # 1.1Bモデル（認証不要、8GBで余裕で動く）
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# Prepare for LoRA
model = prepare_model_for_kbit_training(model)

# LoRA configuration
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# Load dataset
print("Loading dataset...")
dataset = load_dataset("json", data_files="genesis_training_alpaca.json", split="train")

# Formatting function
def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    inputs = examples["input"]
    outputs = examples["output"]
    texts = []
    for instruction, input_text, output in zip(instructions, inputs, outputs):
        if input_text:
            text = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"
        else:
            text = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"
        texts.append(text)
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)

# Training configuration (SFTConfig for 2025/2026 API)
sft_config = SFTConfig(
    output_dir="./genesis_model_output",
    num_train_epochs=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    save_steps=50,
    logging_steps=10,
    optim="paged_adamw_8bit",
    warmup_steps=5,
    max_steps=100,
    max_length=512,  # Rename from max_seq_length to max_length for TRL 0.12.2
    dataset_text_field="text", # Also move text field here
)

# Formatting function for SFTTrainer
def formatting_func(example):
    return [example["text"]]

# Trainer
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    processing_class=tokenizer,
    args=sft_config,
)

# Start training
print("Starting training...")
trainer.train()

# Save model
print("Saving model...")
model.save_pretrained("./genesis_lora_model")
tokenizer.save_pretrained("./genesis_lora_model")

print("Training complete!")
print("Model saved to: ./genesis_lora_model")
