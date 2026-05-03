# Phase 2, Step 3 — V2 Evaluation & Failure Analysis
=================================================

## 📊 Performance Metrics
We ran the T5-Small model against a 500-row hold-out set.
- **Exact Match (EM):** 73.4%
- **Execution Accuracy (EX):** 75.4%

## 🔍 Root Cause Analysis (The "Date Bug")
During evaluation, we identified a critical failure pattern in the T5 model. When asked questions involving time ranges, the model generated invalid SQL:

### ❌ Failed SQL (T5):
```sql
SELECT SUM(revenue) FROM fact_sales WHERE sale_timestamp > 2023-01-01
```
*Issue: The model treated the date as a mathematical subtraction (2023 minus 1 minus 1) instead of a string `'2023-01-01'`.*

### 🎓 Lessons Learned
This failure proved that the 60M parameter T5 model lacked the semantic grounding to understand data types (Strings vs Dates). This finding was the primary driver for our move to the **7B parameter Qwen model** in Phase 3.
