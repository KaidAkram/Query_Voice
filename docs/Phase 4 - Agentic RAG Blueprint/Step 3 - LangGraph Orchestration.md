# Phase 4, Step 3 — The LangGraph Orchestrator
===========================================

## Overview
The **Orchestrator** is the "Central Nervous System" of QueryVoice. It manages the **GraphState**, routes data between nodes, and ensures the entire pipeline remains 100% offline.

## 🏗️ The Graph Architecture
We use `langgraph` to build a **Directed Acyclic Graph (DAG)** that evolves into a **Cyclical Graph** during Step 4.

### The Linear Flow:
1.  **START ⮕ Rewriter:** Cleans the voice input.
2.  **Rewriter ⮕ Router:** Analyzes the cleaned intent to decide on retrieval strategy.
3.  **Router ⮕ Retriever:** Fetches schema docs and golden queries from ChromaDB.
4.  **Retriever ⮕ Generator:** Injects context into the Qwen model for SQL generation.
5.  **Generator ⮕ Evaluator:** (See Step 4) Verifies the SQL against the database.

## 💾 GraphState: The Memory Layer
The orchestrator maintains a `TypedDict` called `GraphState`. Every node has access to this state and can update specific fields:
- `raw_voice_input`: The original noisy transcript.
- `core_intent`: The filtered instruction.
- `retrieved_context`: The combined schema and example data.
- `generated_sql`: The final candidate query.
- `error_traceback`: Used for the reflexion loop.

## ⚡ Enterprise Memory Management
Running a 7B parameter LLM alongside an ASR model on a consumer machine with only 16GB RAM and 8GB VRAM requires extreme memory orchestration. We implemented several "Enterprise-grade" strategies in `graph.py`:

### 1. 4-Bit Quantization (BNB)
We utilize `BitsAndBytesConfig` to load the Qwen model in **4-bit mode**. This reduces the model's footprint from ~28GB to ~5.5GB, allowing it to fit into VRAM with room for the ASR model.

### 2. Manual GPU Mapping (`device_map`)
To avoid the overhead of the `accelerate` library's automatic mapping (which can use too much system RAM on Windows), we use a direct mapping:
```python
device_map={"": 0}  # Forces everything onto GPU 0 immediately
```

### 3. VRAM Guardrails & Disk Offloading
We implemented strict memory limits to prevent "Out of Memory" (OOM) crashes:
- **Max Memory:** `{0: "7GiB", "cpu": "500MiB"}` — Forces the model to stay within 7GB of VRAM.
- **Disk Offloading:** When VRAM is full, weights are temporarily offloaded to a local `offload_cache` folder on the D: drive instead of crashing.

---

## 🚦 Semantic Routing
Unlike a standard chain, our orchestrator uses a **Router Node** to optimize token usage.
- If the query is simple (e.g., "Show users"), it only fetches **Table Definitions**.
- If the query is complex (e.g., "revenue growth"), it fetches **Business Logic** and **Golden Queries** to provide the LLM with enough reasoning context.

## 🚀 Implementation
The orchestrator is implemented in `query_voice_root/agentic_pipeline/graph.py` and uses a **4-bit quantized local Qwen model** to perform all logic nodes, keeping data entirely on the D: drive.

## ⚠️ Model Limitations: Nested Logic Flattening
While the orchestrator handles simple queries flawlessly, we identified a critical architectural limitation when relying on a single Generator node.

Small models (7B-8B) struggle with nested temporal or relational logic. They usually 'flatten' the instruction and just do an `ORDER BY revenue DESC LIMIT 3`, missing the intermediate logical step. In enterprise systems, we solve this by chaining agents (Agent A finds the products, Agent B writes the revenue query), but for a single-pass 7B model, this is a very natural failure point.

---
**Next Step:** [Step 4 — Sandbox Evaluation & Reflexion](file:///d:/NLP_MINI_Project/query_voice_root/docs/Phase%204%20-%20Agentic%20RAG%20Blueprint/Step%204%20-%20Sandbox%20Evaluation%20%26%20Reflexion.md)
