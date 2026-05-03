# QueryVoice 🎤📊

> **A State-of-the-Art Voice-Driven Business Intelligence Engine**

QueryVoice is a high-performance, agentic AI platform that transforms natural language voice commands into executable SQL queries. Designed for seamless Business Intelligence (BI), it enables non-technical users to query complex databases and receive instant visual insights through a sophisticated Neuro-Symbolic pipeline.

---

## 🧠 Theoretical Foundation

QueryVoice operates on the frontier of **Neuro-Symbolic AI**, bridging the gap between neural perception and symbolic reasoning:

1.  **Natural Language Understanding (NLU)**: Converting unstructured audio signals into structured semantic intent.
2.  **Code Synthesis**: Generating deterministic logic (SQL) from ambiguous human speech.
3.  **Symbolic Execution**: Running generated code in a secure sandbox with automated error correction (Reflexion pattern).
4.  **Schema Grounding**: Using Retrieval-Augmented Generation (RAG) to ground the LLM's knowledge in a specific database schema, eliminating hallucinations.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **LLM (Best Version)** | **Qwen2.5-Coder-7B-Instruct** (Fine-tuned via **QLoRA**) |
| **Orchestration** | **LangGraph / LangChain** (Agentic Workflow) |
| **ASR (Speech)** | **OpenAI Whisper** (via Hugging Face Transformers) |
| **Vector Engine** | **ChromaDB** with `BGE-Small-v1.5` Embeddings |
| **Database** | **PostgreSQL** (Production) / SQLite (Local Sandbox) |
| **Backend** | **FastAPI** (Python 3.12) |
| **Frontend** | **Flutter** (Premium UI with real-time visualization) |
| **Infrastructure** | **Docker Compose** / BitsAndBytes (4-bit Quantization) |

---

## 🧬 The Pipeline: From Voice to Insight

The QueryVoice engine utilizes a **LangGraph-driven agentic loop** to ensure 99% query accuracy:

### 1. Voice-to-Intent (ASR & Rewriting)
The process begins with the **Flutter** app capturing audio. This is processed by **Whisper**, converting speech to text. A custom **Rewriter Node** then cleans the transcript, correcting "speech artifacts" and normalizing terms for SQL generation.

### 2. Semantic Routing & Guardrails
A **Semantic Gatekeeper** analyzes the intent. If the query is out-of-scope (e.g., "What's the weather?"), the agent politely refuses. If in-scope, it determines which tables are needed.

### 3. Hierarchical RAG & Chunking
To handle complex schemas, we use a **Hierarchical Chunking Strategy**:
*   **Table-Level**: Descriptions of tables and their business purposes.
*   **Column-Level**: Metadata for each field (Type, Description, Constraints).
*   **Business Definitions**: Custom logic mappings (e.g., defining "Churn Rate" or "Active User" in SQL).
*   **Golden Queries**: A library of "perfect" NL-to-SQL pairs for few-shot grounding.

### 4. Semantic Cache
Before hitting the LLM, the system checks a **Semantic Cache**. If a similar query was answered recently (95%+ similarity), it returns the cached result, reducing latency and cost.

### 5. Generation & Auto-Correction (The Reflexion Loop)
The **Qwen2.5-Coder** model generates the SQL. The query is then sent to an **Evaluator Node** which:
*   **Auto-Patches**: Corrects common LLM biases (e.g., confusing "Profit" with "Revenue").
*   **Security Check**: Blocks destructive operations (DROP, DELETE).
*   **Self-Corrects**: If execution fails, the error message is fed back into the LLM for an immediate retry (up to 3 times).

### 6. Natural Language Summarization
Raw data results are converted back into a natural, human-readable summary using the LLM, which is then pushed to the Flutter dashboard alongside dynamic charts.

---

## 🚀 Getting Started

### 1. Environment Setup
```bash
# Clone and enter
git clone https://github.com/KaidAkram/Query_Voice.git
cd Query_Voice

# Start infrastructure (Postgres, ChromaDB)
docker-compose -f infrastructure/docker-compose.yml up -d
```

### 2. Ingest Data & Schema
```bash
# Initialize the Vector DB with Schema Metadata
python data_engineering/init_vector_db.py

# Run the ETL pipeline
python data_engineering/run_etl.py
```

### 3. Launch the Backend
```bash
cd backend_fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 📊 Sample Visualization
*Query: "Show me the top 5 countries by total profit in 2024"*
> **Output**: A clean bar chart showing profit distribution across regions, generated entirely from a voice command.

---

## 👨‍💻 Author
**Kaid Akram** - *AI Engineer / NLP Specialist*
Building the future of Voice-Driven Analytics.
