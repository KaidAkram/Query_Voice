# Phase 4, Step 4 — Sandbox Evaluation & Reflexion
================================================

## Overview
Even a highly-trained LLM can make syntactic mistakes, especially when dealing with dialect differences (e.g., using MySQL's `DATE_SUB` in an SQLite database). **Step 4** adds a "Self-Correction" layer that allows the agent to debug itself.

## 🔄 The Reflexion Loop
Instead of showing a user a SQL error, QueryVoice performs an internal **Reflexion Cycle**:

1.  **Execution Node:** The agent attempts to run the `generated_sql` against a read-only instance of the local database located at `query_voice_root/data_engineering/queryvoice_local.db`.
2.  **Error Catching:** If the database throws a `sqlite3.OperationalError` or a syntax error, the system captures the **exact error message**.
3.  **The Re-Prompt:** The agent routes the flow **back to the Generator**. The prompt is dynamically updated to include the failure:
    > *"CRITICAL: Your last SQL query failed with this error: [Traceback]. Please fix the syntax (remember this is SQLite) and try again."*
4.  **Self-Correction:** The LLM "reflects" on the mistake and produces a corrected query.

## 🛡️ Safety Constraints: The Retry Cap
To prevent the agent from getting stuck in an infinite loop (e.g., if it keeps making the same mistake), we implemented a **Retry Counter**.
- **Limit:** 3 Attempts.
- **Outcome:** If the model fails after 3 tries, it stops and returns a graceful error message to the user rather than crashing the system.

## 🔍 Technical Implementation
This is implemented as a **Conditional Edge** in LangGraph:
```python
workflow.add_conditional_edges(
    "evaluator", 
    should_retry # Routes back to 'generator' or to END
)
```

## 🎯 Result
This mechanism provides the "missing piece" for production-grade reliability, ensuring that the 100% execution accuracy we achieved in training is maintained even for complex, unpredictable user requests.

## ⚠️ Model Limitations: Pre-Training Bias & The Auto-Patcher
During validation, we encountered a severe limitation: the **Pre-Training Bias (The Revenue Black Hole)**. Because the token sequence `SUM(f.revenue)` is statistically dominant in the model's training data, the 7B model stubbornly defaulted to the `revenue` column even when the user explicitly asked for "total profit," completely ignoring strict prompt instructions.

Worse, when the Reflexion loop caught this semantic error and told the model to fix it, the model ignored the feedback and repeated the exact same `SUM(f.revenue)` query across all three retries.

**The Engineering Workaround: The Deterministic Auto-Patcher**
Instead of continuing to rely on Prompt Engineering, we bypassed the LLM's stubbornness entirely. We implemented a programmatic intercept in the Evaluator node using Python:
* If the user asked for "profit" but the LLM output contained "revenue", the Auto-Patcher silently executes a deterministic string swap (`replace("revenue", "profit")`) *before* executing the SQL.
* This treats the semantic bias as a known, predictable system error rather than asking an incapable model to fix itself.

---
**Next Step:** [Step 5 — Pro Enterprise Features](file:///d:/NLP_MINI_Project/query_voice_root/docs/Phase%204%20-%20Agentic%20RAG%20Blueprint/Step%205%20-%20Pro%20Enterprise%20Features.md)
