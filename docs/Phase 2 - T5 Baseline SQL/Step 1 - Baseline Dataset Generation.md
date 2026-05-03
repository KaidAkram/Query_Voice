# Phase 2, Step 1 — Baseline Dataset Generation
============================================

## Overview
To train the first generation of QueryVoice (T5-Small), we needed a large-scale training set that mapped natural language to SQL queries.

## ⚙️ Generation Logic
We built a script that programmatically combined:
1.  **Templates:** "Show me all users from {country}", "What is the revenue for {product}?"
2.  **Values:** Randomly sampled countries and product names from our database.
3.  **SQL:** Corresponding query logic for each template.

## 📊 Scale
- **Training Set:** 20,000 rows.
- **Format:** `generate SQL: Question: {question} Context: {schema}`.

## 🛑 Limitations
The synthetic generation at this phase used a "flat" context string rather than the structured Alpaca format we later adopted for Phase 3. This contributed to the T5 model's difficulty with complex JOINs.
