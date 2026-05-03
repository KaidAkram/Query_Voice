# Phase 1, Step 3 — ETL Pipeline & Data Generation
================================================

## 🔄 The ETL Process
- **Extract:** Generate synthetic business data using `Faker`.
- **Transform:** Compute derived fields (`revenue`, `profit`) and apply weighted probabilities.
- **Load:** Bulk insert into `queryvoice_local.db` using pandas `.to_sql()`.

## 🎓 Design Decision: Weighted Probabilities
We used `numpy` to implement the **Pareto Principle** (80/20 rule).
- **Premium Users (30%):** Weighted 5x more likely to appear in sales.
- **Free Users (70%):** Standard weight.
This creates a realistic revenue distribution where a minority of users drive the majority of sales, allowing the AI to learn meaningful business patterns.

## 🎓 Design Decision: Derived Fields
Instead of forcing the LLM to calculate math at runtime, we pre-calculated `profit` in the ETL:
```python
revenue = quantity * unit_price
profit = revenue - (quantity * unit_cost)
```
This simplifies the SQL the AI needs to generate, improving **Execution Accuracy (EX)**.
