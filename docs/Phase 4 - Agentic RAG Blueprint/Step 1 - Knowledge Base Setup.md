# Phase 4, Step 1 — The Knowledge Base & "Smart" Chunking
======================================================

## Overview
Phase 4 transitions QueryVoice from a static Text-to-SQL generator into a **Self-Healing Agentic System**. The foundation of this system is a high-fidelity Knowledge Base built on **ChromaDB**.

## 🧠 The "Schema-Aware" Chunking Strategy
Standard RAG systems often chunk text by character count (e.g., every 500 characters). This is destructive for database documentation because it splits tables and columns mid-sentence, losing the relational context.

We have implemented **Entity-Relationship Chunking**:
1.  **Table Objects:** Each table (e.g., `fact_sales`) is indexed as a discrete document containing its purpose and metadata.
2.  **Column Objects:** Every column (e.g., `is_premium`) is indexed as a separate chunk, meta-tagged with its parent table. This allows the retriever to fetch only the specific columns relevant to a query, saving context tokens.
3.  **Business Logic Objects:** Concepts like "High-Value Sale" or "Premium Segment" are defined as standalone chunks. This allows the LLM to map slang to specific SQL filters (e.g., `revenue > 500`).
4.  **Golden Query Objects:** Real Question-to-SQL pairs are indexed to enable **Few-Shot Prompting**.

## 🏗️ Dual-Collection Architecture
We use two specialized collections to maximize retrieval precision:

### 1. `queryvoice_schema`
- **Purpose:** Semantic mapping of user intent to database entities.
- **Embedding Model:** `BAAI/bge-small-en-v1.5` (State-of-the-art for technical retrieval).
- **Metadata:** Includes `type` (table/column/logic), `table_name`, and `entity_id`.

### 2. `queryvoice_golden_queries`
- **Purpose:** Providing the LLM with "Perfect Examples."
- **Content:** The user's natural language question is the "document" (embedded), while the validated SQL is stored in the **metadata**.
- **Usage:** When a user asks a complex question, we fetch the 2-3 most similar historical examples and inject them into the prompt.

## 🚀 Initialization
The Knowledge Base is initialized via `query_voice_root/data_engineering/init_vector_db.py`, which parses the `schema_description.yaml` and populates the collections.

## ⚠️ Model Limitations: The 7B Attention Ceiling
During development, we discovered a hard limitation with the 7B model's attention budget. When we injected too many "Golden Queries" (Few-Shot examples) alongside the schema context and strict system instructions, the model experienced **Instruction Overload**. 

Instead of generating valid SQL, it began producing **template hallucinations** (e.g., outputting placeholder text like `[Country]` and `$[Revenue]`). 
* **The Takeaway:** For small models (7B-8B), you cannot solve every problem by stuffing the context window with examples. Prompts must remain lean, and complex logic must be handled via orchestration or deterministic code rather than pure Prompt Engineering.

---
**Next Step:** [Step 2 — Voice-Intent Rewriting](file:///d:/NLP_MINI_Project/query_voice_root/docs/Phase%204%20-%20Agentic%20RAG%20Blueprint/Step%202%20-%20Voice-Intent%20Rewriting.md)
