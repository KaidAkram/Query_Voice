# /ml_experiments/evaluation/evaluate_model.py
"""
Professional-Grade Evaluation Script for QueryVoice T5 (v2)
==========================================================
Calculates Exact Match (EM) and Execution Accuracy (EX) against the 
hold-out validation set of 500 rows.

Features:
- Execution against queryvoice_local.db
- Failure Pattern Identification (3-5 examples)
- EM/EX Metric Reporting
"""

import os
import json
import sqlite3
import torch
import logging
from tqdm import tqdm
from transformers import T5Tokenizer, T5ForConditionalGeneration

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def normalize_sql(sql):
    """Normalize SQL for comparison: lowercase, remove semicolons, normalize whitespace."""
    return " ".join(sql.strip().lower().replace(";", "").split())

def execute_sql(db_path, sql):
    """Execute SQL against SQLite and return results."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        return results, None
    except Exception as e:
        return None, str(e)

def run_evaluation(model_path, test_data_path, db_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Loading model from {model_path} on {device}...")
    
    tokenizer = T5Tokenizer.from_pretrained(model_path, legacy=False)
    model = T5ForConditionalGeneration.from_pretrained(model_path).to(device)
    model.eval()

    with open(test_data_path, "r") as f:
        test_cases = json.load(f)
    
    logging.info(f"Loaded {len(test_cases)} test cases.")
    
    em_count = 0
    ex_count = 0
    failures = []
    
    PREFIX = "generate SQL: "
    
    for tc in tqdm(test_cases, desc="Evaluating"):
        question = tc["question"]
        schema = tc["schema"]
        gold_sql = tc["sql"]
        
        # 1. Generate SQL
        input_text = f"{PREFIX}Question: {question} Context: {schema}"
        input_ids = tokenizer(input_text, return_tensors="pt", max_length=256, truncation=True).input_ids.to(device)
        
        with torch.no_grad():
            output_ids = model.generate(input_ids, max_length=128, num_beams=4, early_stopping=True)
            pred_sql = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        # 2. Exact Match (EM)
        is_em = normalize_sql(pred_sql) == normalize_sql(gold_sql)
        if is_em:
            em_count += 1
            
        # 3. Execution Accuracy (EX)
        gold_res, gold_err = execute_sql(db_path, gold_sql)
        pred_res, pred_err = execute_sql(db_path, pred_sql)
        
        is_ex = False
        if gold_err is None and pred_err is None:
            # We compare results. Order doesn't matter for basic accuracy unless specified.
            # But for set equality, we sort results.
            is_ex = sorted(gold_res) == sorted(pred_res)
        
        if is_ex:
            ex_count += 1
        else:
            # Capture failure for pattern analysis
            if len(failures) < 10:
                failures.append({
                    "question": question,
                    "gold_sql": gold_sql,
                    "pred_sql": pred_sql,
                    "gold_err": gold_err,
                    "pred_err": pred_err,
                    "reason": "Wrong results" if pred_err is None else f"SQL Error: {pred_err}"
                })
                
    total = len(test_cases)
    em_pct = (em_count / total) * 100
    ex_pct = (ex_count / total) * 100
    
    print("\n" + "="*50)
    print("FINAL EVALUATION RESULTS (v2)")
    print("="*50)
    print(f"Total Test Cases:    {total}")
    print(f"Exact Match (EM):    {em_count}/{total} ({em_pct:.2f}%)")
    print(f"Execution Acc (EX):  {ex_count}/{total} ({ex_pct:.2f}%)")
    print("="*50)
    
    print("\n### TOP FAILURE EXAMPLES ###")
    for i, f in enumerate(failures[:5]):
        print(f"\nFailure {i+1}:")
        print(f"  Question: {f['question']}")
        print(f"  Gold SQL: {f['gold_sql']}")
        print(f"  Pred SQL: {f['pred_sql']}")
        print(f"  Reason:   {f['reason']}")
        
    return {
        "em": em_pct,
        "ex": ex_pct,
        "total": total,
        "failures": failures[:5]
    }

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "t5_sql_finetuned_v2")
    TEST_DATA = os.path.join(BASE_DIR, "data", "test_text_to_sql_large.json")
    DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "data_engineering", "queryvoice_local.db")
    
    run_evaluation(MODEL_PATH, TEST_DATA, DB_PATH)
