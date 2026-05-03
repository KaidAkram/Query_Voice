# Phase 1, Step 4 — Execution & Verification
==========================================

## 🚀 Running the Pipeline
```powershell
python query_voice_root/data_engineering/run_etl.py
```

## 🔍 Verification Strategy
We use two methods to ensure data integrity:
1.  **File Check:** Verify `queryvoice_local.db` exists and is ~5-6MB.
2.  **Visual Audit:** Use DBeaver or VS Code SQLite Viewer to check for "Silent Failures" (e.g., zero quantity, orphaned user IDs).

## 📊 Data Integrity Queries
```sql
-- Ensure revenue matches quantity * price
SELECT COUNT(*) FROM fact_sales s
JOIN dim_products p ON s.product_id = p.product_id
WHERE ABS(s.revenue - (s.quantity * p.unit_price)) > 0.01;
```
*Expected Result: 0 rows.*
