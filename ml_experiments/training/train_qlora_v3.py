# /ml_experiments/training/train_qlora_v3.py
"""
Phase 3: Overnight QLoRA Fine-tuning (v3)
=========================================
Upgrades the QueryVoice Text-to-SQL engine from T5 to Qwen-2.5-Coder-7B (Decoder-only).
Optimized for 8GB VRAM using 4-bit quantization and PEFT.

Requires: pip install transformers peft bitsandbytes trl accelerate datasets
"""

import os
import torch
import logging
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    set_seed
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# Configuration
MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"
DATASET_PATH = os.path.join(os.path.dirname(__file__), "../data/train_v3_alpaca.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../v3_qlora_model")

logging.basicConfig(level=logging.INFO)
set_seed(42)

def main():
    # 1. Quantization Config (MANDATORY for 8GB VRAM)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    # 2. Load Tokenizer & Model
    print(f"Loading model: {MODEL_ID} on GPU 0...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map={"": 0},           # Hard-fix for Windows bitsandbytes stability
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True,       # Prevents RAM spikes during sharding
    )

    # 3. Prepare for Training
    model.config.use_cache = False    # Mandatory for gradient checkpointing
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)

    # 4. LoRA Config
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    # 5. Load Dataset
    dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

    def formatting_prompts_func(example):
        return f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['output']}"

    # 6. Standard Training Arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,  # Effective batch size of 16
        optim="paged_adamw_32bit",
        save_steps=500,
        logging_steps=100,
        learning_rate=2e-4,
        max_grad_norm=0.3,
        num_train_epochs=2,
        warmup_ratio=0.03,
        lr_scheduler_type="constant",
        fp16=False,
        bf16=True,
        report_to="none",
        gradient_checkpointing=True,
    )

    # 7. SFT Trainer (Removed max_seq_length and updated for trl 1.x)
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        processing_class=tokenizer,  # Updated for trl 1.x compatibility
        args=training_args,
        formatting_func=formatting_prompts_func,
    )

    print("Starting v3 QLoRA Training...")
    trainer.train()

    # 8. Save Model
    trainer.save_model(OUTPUT_DIR)
    print(f"v3 QLoRA Model saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
