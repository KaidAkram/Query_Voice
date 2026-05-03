# Phase 4, Step 2 — The Voice-Intent Rewriter
===========================================

## Overview
Because QueryVoice is designed for voice interaction, the input is often messy, fragmented, and filled with "human noise." The **Rewriter Node** acts as a semantic filter, transforming this noise into a machine-ready instruction.

## 🎙️ The Challenge of "Human Noise"
A typical user might say:
> *"Uhm, hey QueryVoice, can you, like, pull up the... wait, no, just show me the total revenue for the computer category last month?"*

Traditional NLP systems would get confused by the "wait, no" correction. Our rewriter uses **Temporal Signal Priority**.

## 🎙️ Whisper ASR Integration
Before rewriting begins, the raw audio must be converted to text. We utilize the **OpenAI Whisper (Small)** model via the Hugging Face Transformers pipeline for high-speed, local inference.

### 1. Audio Pre-processing & Resampling
Mobile devices often capture audio at 44.1kHz or 48kHz. Since Whisper is trained on 16kHz audio, we implemented a custom server-side resampling layer to prevent "chipmunk" distortion:
```python
# Pass both audio data and its real sample rate to Whisper
res = asr_pipeline({"raw": audio_data, "sampling_rate": samplerate})
```

### 2. Hallucination Protective Measures
To prevent the common "Whisper Loop" (where the model repeats phrases during silence), we enforced strict generation parameters:
- **Repetition Penalty (1.2):** Penalizes tokens that have already appeared.
- **No-Repeat N-Gram Size (3):** Hard-blocks the model from repeating a 3-word sequence more than once.
- **Volume Normalization:** Automatically boosts the amplitude of quiet speech to ensure the signal is clear.


---

## 🧠 ChatML Prompt Engineering

### 1. Stripping Filler
The model is instructed to aggressively delete:
- Greetings ("Hey", "Hello")
- Hesitations ("Um", "Uh", "Like")
- System calls ("QueryVoice", "Computer")

### 2. Handling Mid-Sentence Corrections
If the model detects phrases like *"actually"* or *"no, wait"*, it is trained to **discard everything before the pivot** and only process the final intent.

### 3. Structured JSON Enforcement
To ensure the orchestrator can read the output, we use LangChain's `JsonOutputParser`. The model must return:
- `core_intent`: The cleaned, professional version of the question.
- `inferred_tables`: A prioritized list of tables (`dim_users`, `dim_products`, `fact_sales`) suspected to be involved.

## 🚀 Example Transformation
- **Input:** *"Uhm, show me premium... wait, just show me sales from Morocco."*
- **Output:**
  ```json
  {
    "core_intent": "Show me the total sales from Morocco.",
    "inferred_tables": ["fact_sales", "dim_users"]
  }
  ```

---
**Next Step:** [Step 3 — LangGraph Orchestration](file:///d:/NLP_MINI_Project/query_voice_root/docs/Phase%204%20-%20Agentic%20RAG%20Blueprint/Step%203%20-%20LangGraph%20Orchestration.md)
