# /ml_experiments/evaluation/evaluate_model_v3.py
"""
Phase 3 Evaluation Script: Qwen-2.5-Coder-7B QLoRA
================================================
Calculates EM and EX metrics against the 500-row test_v3_alpaca.json.
"""

import os
import json
import sqlite3
import torch
import logging
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

logging.basicConfig(level=logging.INFO)

def normalize_sql(sql):
    return " ".join(sql.strip().lower().replace(";", "").split())

def execute_sql(db_path, sql):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        return results, None
    except Exception as e:
        return None, str(e)

def main():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    TEST_DATA_PATH = os.path.join(BASE_DIR, "data", "test_v3_alpaca.json")
    DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "data_engineering", "queryvoice_local.db")
    MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "v3_qlora_model", "checkpoint-376"))
    BASE_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"

    # Load Model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True
    )

    print(f"Loading Base Model for Evaluation...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, quantization_config=bnb_config, device_map={"": 0}, torch_dtype=torch.bfloat16
    )
    print(f"Loading Adapter for Evaluation...")
    model = PeftModel.from_pretrained(model, MODEL_PATH)
    model.eval()

    with open(TEST_DATA_PATH, "r") as f:
        test_cases = json.load(f)

    em_count = 0
    ex_count = 0
    failures = []

    for tc in tqdm(test_cases, desc="Evaluating v3"):
        prompt = f"### Instruction:\n{tc['instruction']}\n\n### Input:\n{tc['input']}\n\n### Response:\n"
        gold_sql = tc["output"]

        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=128, 
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
            pred_sql = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
            pred_sql = pred_sql.split("###")[0].split(";")[0].strip() + ";"

        # EM
        if normalize_sql(pred_sql) == normalize_sql(gold_sql):
            em_count += 1
        
        # EX
        gold_res, gold_err = execute_sql(DB_PATH, gold_sql)
        pred_res, pred_err = execute_sql(DB_PATH, pred_sql)

        if gold_err is None and pred_err is None:
            if sorted(gold_res) == sorted(pred_res):
                ex_count += 1
            else:
                failures.append({"q": tc['input'], "gold": gold_sql, "pred": pred_sql, "reason": "Wrong results"})
        else:
            failures.append({"q": tc['input'], "gold": gold_sql, "pred": pred_sql, "reason": pred_err or "Gold SQL Error"})

    total = len(test_cases)
    print("\n" + "="*50)
    print("PHASE 3 (v3 QLoRA) FINAL RESULTS")
    print("="*50)
    print(f"Total Test Cases:    {total}")
    print(f"Exact Match (EM):    {em_count}/{total} ({(em_count/total)*100:.2f}%)")
    print(f"Execution Acc (EX):  {ex_count}/{total} ({(ex_count/total)*100:.2f}%)")
    print("="*50)

if __name__ == "__main__":
    main()
