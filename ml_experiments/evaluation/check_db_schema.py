import sqlite3
import os

db_path = r"d:\NLP_MINI_Project\query_voice_root\data_engineering\queryvoice_local.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables: {tables}")

for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print(f"Table: {table_name}, Columns: {[c[1] for c in columns]}")
conn.close()
