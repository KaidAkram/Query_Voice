import sqlite3
import os

db_path = r"d:\NLP_MINI_Project\query_voice_root\data_engineering\queryvoice_local.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- Valid Countries ---")
cursor.execute("SELECT DISTINCT country FROM dim_users LIMIT 5")
print([r[0] for r in cursor.fetchall()])

print("\n--- Valid Categories ---")
cursor.execute("SELECT DISTINCT category FROM dim_products LIMIT 5")
print([r[0] for r in cursor.fetchall()])

print("\n--- Sales with Results (Join Example) ---")
cursor.execute("""
    SELECT u.country, p.category, COUNT(*) 
    FROM fact_sales f 
    JOIN dim_users u ON f.user_id = u.user_id 
    JOIN dim_products p ON f.product_id = p.product_id 
    GROUP BY u.country, p.category 
    LIMIT 5
""")
for row in cursor.fetchall():
    print(f"Country: {row[0]} | Category: {row[1]} | Sales Count: {row[2]}")

conn.close()
