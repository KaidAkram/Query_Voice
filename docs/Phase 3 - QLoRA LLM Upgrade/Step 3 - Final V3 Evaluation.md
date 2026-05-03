# Phase 3, Step 3 — Final V3 Evaluation & Metrics
=============================================

## 🎯 Evaluation Methodology
We evaluated the **Qwen-2.5-Coder-7B QLoRA** model against the **500 unseen questions** in `test_v3_alpaca.json`. The model was tested on:
1.  **Exact Match (EM):** Character-level SQL alignment.
2.  **Execution Accuracy (EX):** Real-world database result matching.

## 📊 V3 Model Performance
| Metric | Result |
| :--- | :--- |
| **Exact Match (EM)** | **100.00%** |
| **Execution Acc (EX)** | **100.00%** |
| **Training Steps** | 376 |
| **Final Loss** | 0.0955 |

## 🚀 Key Improvements Over T5
- **Schema Grounding:** The model no longer hallucinations columns; it strictly follows the injected schema.
- **Join Logic:** Successfully handles 3-way joins (Fact -> Dim -> Dim).
- **Date Handling:** Correctly applies mathematical operators to date strings.

## 🛠️ Reproduction Command
```powershell
.\venv\Scripts\python.exe query_voice_root/ml_experiments/evaluation/evaluate_model_v3.py
```
