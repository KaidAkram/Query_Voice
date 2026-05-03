# Archive: Legacy RAG Experiments
==============================

## Step 1 — RAG Dependencies
Installed `chromadb` and `sentence-transformers` to build a vector-based knowledge base.

## Step 2 — Data Dictionary
Created semantic definitions for the database schema (e.g., defining `is_premium` as subscription status) to provide the LLM with business context.

## Step 3 — Vectorization
Built `build_rag.py` using the `all-MiniLM-L6-v2` model to embed schema definitions into a 384-dimensional vector space.

## Step 4 — Verification
Verified that semantic search correctly retrieves relevant tables (e.g., questioning "SaaS subscriptions" retrieves `dim_products`).

---
**Note:** This phase was archived in favor of direct **Text-to-SQL Instruction Tuning** (Phase 3), which provides higher accuracy and lower latency for our specific star schema.
