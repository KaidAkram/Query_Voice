# /ml_experiments/evaluation/verify_model.py
"""
Text-to-SQL Semantic Evaluation Suite
=======================================
Evaluates a fine-tuned T5 model against a test dataset of 500 unseen queries.
Replaces brittle Exact Match (EM) with robust Execution Accuracy (EX) as the
primary evaluation metric by physically running both queries against SQLite.

Usage:
  python verify_model.py                          # Evaluates v1 baseline
  python verify_model.py --model ../t5_sql_finetuned_v2  # Evaluates v2
"""

import os
import json
import argparse
import sqlite3
import torch
import logging
from transformers import T5Tokenizer, T5ForConditionalGeneration

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_test_data(data_path):
    with open(data_path, "r") as f:
        return json.load(f)

def load_model(model_path):
    """Load a fine-tuned T5 model and tokenizer."""
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    tokenizer = T5Tokenizer.from_pretrained(model_path, legacy=False)
    model = T5ForConditionalGeneration.from_pretrained(model_path).to(device)
    model.eval()
    return model, tokenizer, device

def generate_sql(model, tokenizer, device, question, schema):
    """Generate SQL from a natural language question using the fine-tuned model."""
    input_text = f"generate SQL: Question: {question} Context: {schema}"
    input_ids = tokenizer(
        input_text, return_tensors="pt",
        max_length=256, truncation=True
    ).input_ids.to(device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_length=128,
            num_beams=4,
            early_stopping=True
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def execute_sql(db_path, sql):
    """Execute SQL against the SQLite database and return the result set as a list of tuples."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        return results, None
    except Exception as e:
        return None, str(e)

def normalize_sql(sql):
    """Normalize SQL for Exact Match comparison (ignore case and spacing)."""
    return " ".join(sql.strip().lower().replace(";", "").split())

def evaluate(model_path, db_path, data_path):
    logging.info(f"Loading model from: {model_path}")
    model, tokenizer, device = load_model(model_path)

    logging.info(f"Loading test data from: {data_path}")
    test_cases = load_test_data(data_path)
    
    total = len(test_cases)
    logging.info(f"Database: {db_path}")
    logging.info(f"Running evaluation on {total} test cases. This may take a few minutes...\n")

    em_correct = 0
    ex_correct = 0
    errors = 0

    for idx, tc in enumerate(test_cases):
        if idx > 0 and idx % 50 == 0:
            logging.info(f"Processed {idx}/{total} test cases...")
            
        generated_sql = generate_sql(model, tokenizer, device, tc["question"], tc["schema"])
        expected_sql = tc["sql"]

        # --- Exact Match (EM) ---
        em_match = normalize_sql(generated_sql) == normalize_sql(expected_sql)
        if em_match:
            em_correct += 1

        # --- Execution Accuracy (EX) ---
        expected_result, expected_err = execute_sql(db_path, expected_sql)
        generated_result, generated_err = execute_sql(db_path, generated_sql)

        ex_match = False
        if expected_err is None and generated_err is None:
            # Semantic equality: Do the queries return the exact same data tuples?
            # We sort them to ignore row order differences unless an ORDER BY was explicitly missed,
            # though sorting can sometimes hide ORDER BY failures, it's safer for sets.
            # For strictness, we compare exact output order here.
            ex_match = expected_result == generated_result
        elif generated_err is not None:
            ex_match = False
            errors += 1

        if ex_match:
            ex_correct += 1

    # --- Final Metrics ---
    em_pct = (em_correct / total) * 100
    ex_pct = (ex_correct / total) * 100
    err_pct = (errors / total) * 100

    logging.info("=" * 70)
    logging.info("EVALUATION SUMMARY")
    logging.info("=" * 70)
    logging.info(f"Total Test Cases:     {total}")
    logging.info(f"Exact Match (EM):     {em_correct}/{total} ({em_pct:.1f}%)")
    logging.info(f"Execution Acc (EX):   {ex_correct}/{total} ({ex_pct:.1f}%)")
    logging.info(f"Execution Errors:     {errors}/{total} ({err_pct:.1f}%)")
    logging.info("=" * 70)

    return em_pct, ex_pct

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a fine-tuned Text-to-SQL model.")
    parser.add_argument("--model", type=str,
                        default=os.path.join(os.path.dirname(__file__), "../t5_sql_finetuned"),
                        help="Path to the fine-tuned model directory.")
    parser.add_argument("--db", type=str,
                        default=os.path.join(os.path.dirname(__file__), "../../data_engineering/queryvoice_local.db"),
                        help="Path to the SQLite database.")
    parser.add_argument("--data", type=str,
                        default=os.path.join(os.path.dirname(__file__), "../data/test_text_to_sql_large.json"),
                        help="Path to the test JSON file.")
    args = parser.parse_args()

    evaluate(args.model, args.db, args.data)
