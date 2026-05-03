import os
import uuid
import logging
import numpy as np
import pandas as pd
from faker import Faker
from datetime import timedelta
from sqlalchemy import create_engine

# 1. Setup Professional Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
fake = Faker()

DATABASE_URL = "sqlite:///queryvoice_local.db"
engine = create_engine(DATABASE_URL)

def run_etl_pipeline(num_users=2000, num_products=100, num_sales=15000):
    logging.info("Starting Data Generation Phase...")

    # --- EXTRACT/GENERATE PHASE ---

    # Generate Dimension: Users
    users = [{
        'user_id': str(uuid.uuid4()),
        'name': fake.name(),
        'email': fake.unique.email(),
        'country': fake.country(),
        # 30% chance to be premium
        'is_premium': np.random.choice([True, False], p=[0.3, 0.7]),
        'signup_date': fake.date_between(start_date='-3y', end_date='today')
    } for _ in range(num_users)]
    df_users = pd.DataFrame(users)

    # Generate Dimension: Products
    categories = ['SaaS Subscription', 'Enterprise License', 'Consulting Hours', 'Add-on Feature']
    products = []
    for _ in range(num_products):
        price = round(np.random.uniform(50.0, 1500.0), 2)
        products.append({
            'product_id': str(uuid.uuid4()),
            'product_name': fake.catch_phrase(),
            'category': np.random.choice(categories),
            'unit_price': price,
            'unit_cost': round(price * np.random.uniform(0.1, 0.4), 2)
        })
    df_products = pd.DataFrame(products)

    # Generate Fact: Sales (With realistic distributions)
    logging.info("Generating realistic sales relationships...")
    user_ids = df_users['user_id'].values
    premium_mask = df_users['is_premium'] == True
    weights = np.where(premium_mask, 5.0, 1.0)
    weights /= weights.sum()

    sales = []
    product_dict = df_products.set_index('product_id').to_dict('index')
    product_ids = df_products['product_id'].values

    for _ in range(num_sales):
        p_id = np.random.choice(product_ids)
        u_id = np.random.choice(user_ids, p=weights)
        qty = np.random.randint(1, 4)
        
        price = product_dict[p_id]['unit_price']
        cost = product_dict[p_id]['unit_cost']
        revenue = qty * price
        
        sales.append({
            'sale_id': str(uuid.uuid4()),
            'user_id': u_id,
            'product_id': p_id,
            'sale_timestamp': fake.date_time_between(start_date='-2y', end_date='now'),
            'quantity': qty,
            'revenue': revenue,
            'profit': revenue - (qty * cost)
        })
    df_sales = pd.DataFrame(sales)

    # --- LOAD PHASE ---
    logging.info("Loading Data into Local SQLite Data Warehouse...")
    try:
        df_users.to_sql('dim_users', engine, if_exists='append', index=False, chunksize=1000)
        df_products.to_sql('dim_products', engine, if_exists='append', index=False, chunksize=1000)
        df_sales.to_sql('fact_sales', engine, if_exists='append', index=False, chunksize=1000)
        logging.info("ETL Pipeline Completed Successfully! Database is primed.")
    except Exception as e:
        logging.error(f"Database insertion failed: {e}")

if __name__ == "__main__":
    run_etl_pipeline()
