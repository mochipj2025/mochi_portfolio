import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os

base_model_path = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
adapter_path = "d:/00000/mochisura-lab/Project_Genesis/genesis_lora_model"
save_path = "d:/00000/mochisura-lab/Project_Genesis/genesis_merged_model"

print(f"Loading base model: {base_model_path}")
model = AutoModelForCausalLM.from_pretrained(
    base_model_path, 
    torch_dtype=torch.float16, 
    low_cpu_mem_usage=True
)
tokenizer = AutoTokenizer.from_pretrained(base_model_path)

print(f"Loading adapter from: {adapter_path}")
model = PeftModel.from_pretrained(model, adapter_path)

print("Merging weights (this may take a moment)...")
model = model.merge_and_unload()

print(f"Saving merged model to: {save_path}")
os.makedirs(save_path, exist_ok=True)
model.save_pretrained(save_path, safe_serialization=True)
tokenizer.save_pretrained(save_path)

print("Success! Integrated model is ready.")
