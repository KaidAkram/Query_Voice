# /ml_experiments/evaluation/live_test.py
"""
Live Test Script for QueryVoice T5 (v2) and QLoRA (v3)
=====================================================
Supports both Phase 2 (T5) and Phase 3 (QLoRA) models.
"""

import os
import sys
import sqlite3
import torch
from transformers import (
    T5Tokenizer, T5ForConditionalGeneration,
    AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
)
from peft import PeftModel

def execute_sql(db_path, sql):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        return columns, results, None
    except Exception as e:
        return None, None, str(e)

def main():
    if len(sys.argv) < 2:
        print("Usage: python live_test.py \"Your question\" [v2/v3]")
        return

    question = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "v3"
    
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "data_engineering", "queryvoice_local.db")
    SCHEMA = (
        "Table: dim_users (user_id, name, email, country, is_premium, signup_date)\n"
        "Table: dim_products (product_id, product_name, category, unit_price, unit_cost)\n"
        "Table: fact_sales (sale_id, user_id, product_id, sale_timestamp, quantity, revenue, profit)"
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[1] Question: {question} (Testing {version})")

    if version == "v2":
        MODEL_PATH = os.path.join(BASE_DIR, "t5_sql_finetuned_v2")
        tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH, legacy=False)
        model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH).to(device)
        
        PREFIX = "generate SQL: "
        input_text = f"{PREFIX}Question: {question} Context: {SCHEMA.replace('\\n', ' | ')}"
        input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(device)
        
        with torch.no_grad():
            output_ids = model.generate(input_ids, max_length=128)
            pred_sql = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    else: # v3 QLoRA
        # Correct path to the final checkpoint folder
        MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "v3_qlora_model", "checkpoint-376"))
        BASE_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
        
        print(f"Loading v3 Base Model ({BASE_MODEL}) on GPU 0...")
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL, 
            quantization_config=bnb_config, 
            device_map={"": 0},
            torch_dtype=torch.bfloat16
        )
        
        print(f"Applying QLoRA Adapter from {MODEL_PATH}...")
        model = PeftModel.from_pretrained(model, MODEL_PATH)
        model.eval()
        
        prompt = (
            "### Instruction:\nYou are an expert Text-to-SQL assistant. Generate a precise SQL query based on the provided schema.\n\n"
            f"### Input:\nSchema:\n{SCHEMA}\n\nQuestion: {question}\n\n"
            "### Response:\n"
        )
        
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=128, 
                do_sample=False, # Use greedy decoding for SQL
                pad_token_id=tokenizer.eos_token_id
            )
            pred_sql = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
            # Clean up potential extra markers from Qwen
            pred_sql = pred_sql.split("###")[0].split(";")[0].strip() + ";"

    print(f"[2] Generated SQL:\n    {pred_sql}")

    # Execute
    columns, results, error = execute_sql(DB_PATH, pred_sql)

    print(f"\n[3] Database Results:")
    if error:
        print(f"    Error: {error}")
    else:
        if not results:
            print("    (No results found)")
        else:
            header = " | ".join(columns)
            print(f"    {header}")
            print(f"    {'-' * len(header)}")
            for row in results[:10]:
                print(f"    {' | '.join(map(str, row))}")

if __name__ == "__main__":
    main()
