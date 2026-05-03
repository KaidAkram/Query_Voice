import json
import os
import random

def convert_to_alpaca(input_file, output_file, sample_size=None):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Randomly sample to reduce training time (Quality over Quantity)
    if sample_size and sample_size < len(data):
        random.seed(42)
        data = random.sample(data, sample_size)
        print(f"Sampling {sample_size} rows from {input_file}...")
    
    # Exact Star Schema from queryvoice_local.db
    SCHEMA_STR = (
        "Table: dim_users (user_id, name, email, country, is_premium, signup_date)\n"
        "Table: dim_products (product_id, product_name, category, unit_price, unit_cost)\n"
        "Table: fact_sales (sale_id, user_id, product_id, sale_timestamp, quantity, revenue, profit)"
    )
    
    alpaca_data = []
    for item in data:
        alpaca_item = {
            "instruction": "You are an expert Text-to-SQL assistant. Generate a precise SQL query based on the provided schema.",
            "input": f"Schema:\n{SCHEMA_STR}\n\nQuestion: {item['question']}",
            "output": item['sql']
        }
        alpaca_data.append(alpaca_item)
    
    with open(output_file, 'w') as f:
        json.dump(alpaca_data, f, indent=2)
    print(f"Converted {len(alpaca_data)} rows to {output_file}")

if __name__ == "__main__":
    BASE_DIR = r"d:\NLP_MINI_Project\query_voice_root\ml_experiments\data"
    
    # Prune training set to 3,000 rows (~5 hours on 3070 Ti)
    convert_to_alpaca(
        os.path.join(BASE_DIR, "train_text_to_sql_large.json"),
        os.path.join(BASE_DIR, "train_v3_alpaca.json"),
        sample_size=3000
    )
    
    # Keep full test set for evaluation
    convert_to_alpaca(
        os.path.join(BASE_DIR, "test_text_to_sql_large.json"),
        os.path.join(BASE_DIR, "test_v3_alpaca.json")
    )
