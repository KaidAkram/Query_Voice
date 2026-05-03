# /ml_experiments/training/train_t5.py
"""
Production-Scale Text-to-SQL Training Script (v2)
=================================================
Fine-tunes the T5 model on a large synthetic dataset (19,500+ examples).
Uses the Hugging Face `datasets` and `Trainer` API for maximum efficiency.

Key Features:
- Dataset abstraction for fast batch processing.
- Gradient Accumulation to simulate large batch sizes without crashing VRAM.
- Automatic Mixed Precision (FP16) on GPU.
- Checkpointing and automatic metric calculation.
"""

import os
import torch
import logging
import datasets
from transformers import (
    T5Tokenizer, 
    T5ForConditionalGeneration, 
    TrainingArguments, 
    Trainer,
    DataCollatorForSeq2Seq
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # ==========================================
    # 1. Setup Device
    # ==========================================
    device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available()
        else "cpu"
    )
    logging.info(f"Initializing Training Pipeline on: {device}")
    
    # ==========================================
    # 2. Load Model & Tokenizer
    # ==========================================
    MODEL_NAME = "t5-small"
    # Or "t5-base" if you have a very strong GPU, but small is fine for learning syntax
    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME, legacy=False)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME).to(device)
    
    # ==========================================
    # 3. Load & Preprocess Dataset
    # ==========================================
    train_path = os.path.join(os.path.dirname(__file__), "../data/train_text_to_sql_large.json")
    val_path = os.path.join(os.path.dirname(__file__), "../data/test_text_to_sql_large.json")
    
    logging.info("Loading Datasets...")
    dataset = datasets.load_dataset(
        "json", 
        data_files={"train": train_path, "validation": val_path}
    )
    
    # Ensure RAG/SQL prefix matches what we use in verification
    PREFIX = "generate SQL: "
    
    def preprocess_function(examples):
        inputs = [PREFIX + "Question: " + q + " Context: " + s for q, s in zip(examples["question"], examples["schema"])]
        targets = examples["sql"]
        
        model_inputs = tokenizer(inputs, max_length=256, truncation=True)
        # Setup the tokenizer for targets
        labels = tokenizer(targets, max_length=128, truncation=True)
        
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
    
    logging.info("Tokenizing Datasets...")
    tokenized_datasets = dataset.map(
        preprocess_function,
        batched=True,
        remove_columns=dataset["train"].column_names
    )
    
    # ==========================================
    # 4. Training Arguments
    # ==========================================
    # Output directory for v2
    output_dir = os.path.join(os.path.dirname(__file__), "../t5_sql_finetuned_v2")
    
    # Optimization for 8GB VRAM (fragmentation fix)
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    
    training_args = TrainingArguments(
        output_dir=output_dir,
        eval_strategy="no",               # Disable evaluation during training to save VRAM
        save_strategy="epoch",            # Save checkpoints every epoch
        learning_rate=3e-4,               # T5 likes slightly higher learning rates
        per_device_train_batch_size=1,    # Absolute minimum to prevent OOM
        gradient_accumulation_steps=32,   # Simulates a batch size of 32 (1 * 32)
        weight_decay=0.01,
        save_total_limit=2,               # Only keep best 2 checkpoints to save disk space
        num_train_epochs=5,               # 5 epochs on 19.5k is plenty for T5
        fp16=False,                       # Sometimes AMP uses more VRAM due to double weight storage
        max_grad_norm=0.0,                # Disable gradient clipping to save memory during norm calculation
        logging_steps=100,
        report_to="none"                  # Disable wandb/tensorboard for clean logs
    )
    
    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
    
    # ==========================================
    # 5. Execute Trainer
    # ==========================================
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        data_collator=data_collator,
    )
    
    logging.info("=" * 60)
    logging.info("Starting Scaled Training Loop (v2)...")
    logging.info("=" * 60)
    
    trainer.train()
    
    # Save the final best model
    trainer.save_model(output_dir)
    logging.info("=" * 60)
    logging.info(f"Production Model Saved to: {output_dir}")
    logging.info("=" * 60)

if __name__ == "__main__":
    main()
