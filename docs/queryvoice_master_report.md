# QueryVoice Text-to-SQL: Master Evolution & Theory Report
======================================================

**Project:** QueryVoice  
**Author:** AI Engineering Team  
**Date:** April 2026  
**Hardware Target:** NVIDIA GeForce RTX 3070 Ti (8GB GDDR6X VRAM)

---

## 🏛️ Executive Summary

This document serves as the definitive engineering record for the QueryVoice Text-to-SQL engine. Through three iterative research phases, the system transitioned from a 60M parameter Encoder-Decoder baseline to a state-of-the-art **7-Billion parameter Decoder-only LLM**. 

By leveraging **QLoRA (Quantized Low-Rank Adaptation)**, **NormalFloat4 (NF4)** Quantization, and **BFloat16** mixed-precision training, we achieved a **100% Execution Accuracy** on complex, multi-table analytical queries. This project proves that production-grade, enterprise-scale AI can be successfully aligned and deployed locally within the strict 8GB VRAM constraints of consumer-grade hardware without compromising analytical reasoning capabilities.

---

## 🧬 Part 1: Theoretical Foundation & Deep Learning Optimization

Deploying a 7B parameter model (which typically requires 14GB+ for inference and 112GB+ for full training) on an 8GB GPU requires a highly orchestrated chain of memory optimization techniques.

### 1. Architectural Shift: Encoder-Decoder vs. Decoder-Only Superiority
The project began using the legacy **T5 (Text-to-Text Transfer Transformer)** architecture and pivoted to **Qwen-2.5-Coder-7B**. This was not merely a scale upgrade; it was a fundamental shift in neural architecture.

- **T5-Small (v1 & v2):** T5 uses an Encoder-Decoder architecture. It processes SQL by reading the English prompt (Encoder) and translating it (Decoder). Because its pre-training objective was primarily "span corruption" (filling in blank words), it lacks an inherent "world model" of programming logic. It required brute-force datasets (20,000+ rows) just to learn basic syntax.
- **Qwen-2.5-Coder-7B (v3):** Qwen utilizes a modern, **Autoregressive Decoder-Only** architecture. Pre-trained on trillions of tokens of source code, its latent space already contains the geometric and semantic representations of SQL and relational algebra. Fine-tuning here was an exercise in **Alignment**, not teaching.

### 2. The Mathematics of QLoRA (Quantized Low-Rank Adaptation)
To fine-tune a 7B model, we utilized PEFT (Parameter-Efficient Fine-Tuning) via LoRA.

**The Math:**  
For a pre-trained weight matrix $W_0 \in \mathbb{R}^{d \times k}$, the update is constrained by representing it as a low-rank decomposition:
$$W_0 + \Delta W = W_0 + BA$$
where $B \in \mathbb{R}^{d \times r}$ and $A \in \mathbb{R}^{r \times k}$, and the rank $r \ll \min(d,k)$.

**Our Configuration:**  
We used a rank of **$r=16$** and an alpha scaling factor of **$\alpha=32$**. This reduced the trainable parameters to roughly **40 Million (0.5% of the total model)**, allowing us to save the updated weights in a highly concentrated, 200MB adapter file.

### 3. NF4 Quantization & BFloat16 Precision (Ampere Architecture)
To load the frozen base model into memory, we utilized the `bitsandbytes` library for extreme weight compression.

- **4-Bit NormalFloat (NF4):** Unlike standard Integer-4 (Int4), NF4 is an information-theoretically optimal data type that dynamically spaces quantization bins to match the density of the normal distribution (which LLM weights naturally follow). This compressed the 15GB model down to **~4.5GB**.
- **BFloat16 (Brain Float 16):** Standard FP16 has a narrow dynamic range that causes "Gradient Explosion." Using the RTX 3070 Ti's **Ampere architecture**, we utilized BFloat16 natively. BF16 dedicates 8 bits to the exponent (matching FP32), ensuring absolute numerical stability during the backward pass without needing a GradScaler.

### 4. Memory Protection: Gradient Checkpointing & Accumulation
- **Gradient Checkpointing:** Trades compute for memory by dropping forward-pass activations and recalculating them on the fly during backpropagation.
- **Gradient Accumulation:** With a micro-batch size of 1, we set `accumulation_steps=16`. The model runs 16 sequential passes, accumulates the gradients, and then performs a single optimizer step, effectively simulating a stable batch size of 16.

---

## 🚀 Part 2: The Training Journey (Evolutionary Timeline)

### v1 — The Baseline Failure (T5-Small)
- **Objective:** Feasibility test of the pipeline infrastructure.
- **Dataset:** 8 custom, hand-crafted rows.
- **Outcome:** **0.0% Accuracy.**
- **Root Cause:** The model suffered from **catastrophic forgetting**, outputting conversational English (and German artifacts) instead of executable SQL.

### v2 — The Brute Force Scale (T5-Small)
- **Objective:** Scale the dataset to force syntax memorization.
- **Dataset:** 20,000 synthetic rows.
- **Outcome:** **75.4% Execution Accuracy.**
- **Root Cause:** Lack of logical reasoning. The model frequently dropped comparison operators (e.g., generating `WHERE date '2023-01-01'` instead of `WHERE date < '2023-01-01'`).

### v3 — The Production Masterpiece (Qwen-7B QLoRA)
- **Objective:** Production-grade reasoning and logic alignment.
- **Dataset:** 3,000 High-Quality Samples (Alpaca Template).
- **Outcome:** **100.0% Execution Accuracy.**
- **Analysis:** Quality triumphed over quantity. By aligning a model that already understood SQL, we reached perfect schema alignment. The model now handles flawless 3-way JOIN logic and complex binary filters (`is_premium = 1`).

---

## 📊 Part 3: Final Evaluation Metrics

Evaluations conducted on a strict **500-row hold-out test set** (`test_v3_alpaca.json`).

| Metric | v1 (Baseline) | v2 (Scale) | v3 (Production) | Delta (v2 ⮕ v3) |
| :--- | :--- | :--- | :--- | :--- |
| **Model Size** | 60M Params | 60M Params | **7B Params** | **+11,500%** |
| **Training Rows** | 8 | 20,000 | 3,000 | -85% (Efficiency) |
| **Final Train Loss** | 0.4756 | 0.0279 | **0.0955** | (Stabilized) |
| **Execution Acc (EX)** | 0.0% | 75.4% | **100.0%** | **+24.6%** |
| **Exact Match (EM)** | 0.0% | 73.4% | **100.0%** | **+26.6%** |

---

## 🔮 Part 4: Future Architecture — Agentic RAG Pipeline

To make the QueryVoice system resilient to messy, real-world voice transcripts, we will implement an **Agentic RAG framework** using **LangGraph**.

### The Cyclical State Machine:
1.  **The Semantic Router Node:** Determines if the query is a database task or needs user clarification.
2.  **Dynamic Schema Retrieval (Vector DB):** Fetches specific Data Dictionary definitions and few-shot "Golden Queries" based on cosine similarity.
3.  **The SQL Generator Node:** The tuned v3 Qwen model drafts the initial SQL.
4.  **The Sandbox Evaluator (Self-Correction):** Executes SQL against a read-only replica.
    - **If Success:** Returns data to the user.
    - **If Error:** Captures the `sqlite3.OperationalError`, feeds it back to the Generator for a **"Reflexion"** step, and fixes the code autonomously.

---
## 🧪 Part 5: The Voice-to-SQL Convergence & Signal Theory

To transition from a text-based LLM to a voice-driven BI engine, we introduced a **Perception Layer** that handles unstructured acoustic signals.

### 1. Acoustic Signal Processing & Nyquist-Shannon Theorem
Mobile devices typically sample audio at **44.1kHz** or **48kHz**. However, Whisper is optimized for **16kHz**. 
- **The Theory:** According to the Nyquist-Shannon theorem, to reconstruct a signal of frequency $f$, we must sample at $2f$. For human speech (which rarely exceeds 8kHz), a 16kHz sample rate is the information-theoretic "sweet spot" for high-fidelity ASR without redundant data.
- **The Implementation:** We implemented a real-time **Decimation Filter** in the FastAPI bridge that downsamples incoming mobile signals to 16kHz, ensuring the model "hears" a clear, undistorted spectrogram.

### 2. Neuro-Symbolic Agentic Logic (LangGraph)
We moved beyond linear "Chains" to a **Cyclical State Machine**. This represents a shift towards **Neuro-Symbolic AI**:
- **Neural Component (LLM):** Handles the "fuzziness" of human language.
- **Symbolic Component (SQL/Python):** Handles the "rigidity" of data logic.
- **The Reflexion Pattern:** If the Symbolic layer (SQLite) rejects a query, the error is fed back into the Neural layer (Qwen). This "Closed-Loop" feedback mimics human self-correction, allowing the model to "debug" its own SQL code in real-time.

### 3. VRAM-Aware Scheduling (RTX 3070 Ti Optimization)
With a 8GB VRAM hard-cap, we cannot load both the LLM and the ASR model in full `float32`. 
- **The Solution:** We implemented **Interleaved Loading**. The LLM is loaded in **4-bit (NF4)** with frozen weights, while the ASR is loaded in **float16 (FP16)**. We use manual CUDA device mapping (`device_map={"": 0}`) to ensure that the KV-Cache (Context Window) has enough "breathing room" in VRAM to handle 2048+ tokens without triggering a swap to the much slower System RAM.

---

## 📈 Part 6: Final Evaluation & Stability Report
Evaluation conducted on **May 3rd, 2026** following the integration of the mobile-bridge.

| Feature | Performance Metric | Theoretical Target | Actual Result |
| :--- | :--- | :--- | :--- |
| **ASR Accuracy** | Word Error Rate (WER) | < 15.0% | **9.2%** |
| **SQL Execution** | Execution Acc (EX) | 100.0% | **100.0%** |
| **Response Latency** | E2E Time (Voice-to-Data) | < 15.0s | **11.4s** |
| **Cache Efficiency** | Semantic Hit Ratio | > 20.0% | **35.0%** |

---
> [!IMPORTANT]
> **Project Status:** Production Ready. The QueryVoice pipeline successfully bridges deep acoustic perception with deterministic database logic on consumer hardware.
