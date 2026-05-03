# Phase 3, Step 1 — Alpaca Instruction Tuning & Dataset Rebuild
============================================================

## 📝 The Move to Alpaca
In Phase 3, we transitioned from the T5 "prefix" format to the **Alpaca/ChatML** instruction format. This format explicitly separates the system role, the user context, and the expected output.

## 🏗️ The Template
Each training row follows this character-identical format:
```text
### Instruction:
You are an expert Text-to-SQL assistant. Generate a precise SQL query based on the provided schema.

### Input:
Schema:
Table: dim_users (user_id, name, email, country, is_premium, signup_date)
Table: dim_products (product_id, product_name, category, unit_price, unit_cost)
Table: fact_sales (sale_id, user_id, product_id, sale_timestamp, quantity, revenue, profit)

Question: [USER QUESTION HERE]

### Response:
[SQL QUERY HERE]
```

## 📉 Dataset Optimization
To ensure a successful overnight run on the 3070 Ti, we applied two critical optimizations:
1.  **Strict Schema Injection:** Every row includes the full star schema to prevent hallucinations.
2.  **Sampling:** We randomly sampled **3,000 high-quality rows** from our 20,000-row synthetic bank, reducing training time from 34 hours to **5.5 hours**.
