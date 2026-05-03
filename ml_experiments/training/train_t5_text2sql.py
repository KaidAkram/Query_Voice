"""
train_t5_text2sql.py
======================
Fine-tuning script for T5 on the Text-to-SQL task.

Uses the Spider dataset to train a T5 model to convert
natural language questions into SQL queries.

Usage:
    python train_t5_text2sql.py --epochs 10 --batch_size 8 --lr 3e-4
"""

import argparse
# import torch
# from torch.utils.data import DataLoader
# from transformers import T5Tokenizer, T5ForConditionalGeneration


def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune T5 for Text-to-SQL")
    parser.add_argument("--model_name", type=str, default="t5-base", help="Pretrained model name")
    parser.add_argument("--data_path", type=str, default="../data/spider_train.json", help="Training data path")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=8, help="Training batch size")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--output_dir", type=str, default="./checkpoints", help="Model checkpoint output directory")
    return parser.parse_args()


def load_dataset(data_path: str):
    """Load and preprocess the Spider dataset for T5 training."""
    # TODO: Load JSON, create input-output pairs
    #   Input:  "translate to SQL: {question} | schema: {schema_info}"
    #   Output: "{sql_query}"
    raise NotImplementedError


def train(args):
    """Main training loop."""
    print(f"Training {args.model_name} for {args.epochs} epochs...")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Learning rate: {args.lr}")
    print(f"  Data: {args.data_path}")
    print(f"  Output: {args.output_dir}")

    # TODO: Implement PyTorch training loop
    #   1. Load tokenizer and model
    #   2. Prepare DataLoader
    #   3. Training loop with loss logging
    #   4. Save best checkpoint
    raise NotImplementedError


if __name__ == "__main__":
    args = parse_args()
    train(args)
