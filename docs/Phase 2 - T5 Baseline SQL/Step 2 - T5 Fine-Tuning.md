# Phase 2, Step 2 — T5 Baseline Fine-Tuning
========================================

## 🎯 Objective
Establish a functional Text-to-SQL baseline using the **T5-Small** (60M parameters) architecture.

## ⚙️ Process
We fine-tuned the model on a 20,000-row synthetic dataset using a simple prefix-based instruction format:
- **Prompt:** `generate SQL: Question: {question} Context: {schema}`
- **Training Tool:** HuggingFace `Trainer` API.

## 📊 V2 Results
- **Execution Accuracy:** ~75.4%
- **Strengths:** Fast inference, good at simple one-table queries.
- **Weaknesses:** 
    - Hallucinated columns that didn't exist in the schema.
    - Omitted mathematical operators in `WHERE` clauses.
    - Failed on queries requiring more than two JOINs.

## 🛑 Why we moved to Phase 3
The T5 model lacked the "reasoning" capacity to strictly follow the injected schema. We realized that a larger **Decoder-only LLM** (Qwen) with **QLoRA** would provide the grounding needed for production accuracy.
