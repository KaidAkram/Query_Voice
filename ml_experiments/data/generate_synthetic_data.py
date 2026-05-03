# /ml_experiments/data/generate_synthetic_data.py
import json
import random
import os
import datetime

# ==============================================================================
# SCHEMA STRINGS
# ==============================================================================
S_USERS = "Table: dim_users (user_id, name, email, country, is_premium, signup_date)"
S_PRODS = "Table: dim_products (product_id, product_name, category, unit_price, unit_cost)"
S_SALES = "Table: fact_sales (sale_id, user_id, product_id, sale_timestamp, quantity, revenue, profit)"
S_JOIN_ALL = f"{S_USERS} | {S_PRODS} | {S_SALES}"
S_JOIN_USERS_SALES = f"{S_USERS} | {S_SALES}"
S_JOIN_PRODS_SALES = f"{S_PRODS} | {S_SALES}"

# ==============================================================================
# DICTIONARIES FOR MASSIVE VARIATION (ENTROPY)
# ==============================================================================
# Expanding arrays massively to ensure >20,000 unique combinations
COUNTRIES = ["USA", "UK", "Germany", "France", "Japan", "Canada", "Australia", "India", "Brazil", "Algeria", "Mexico", "Spain", "Italy", "China", "South Korea"]
CATEGORIES = ["SaaS Subscription", "Enterprise License", "Consulting Hours", "Add-on Feature", "Premium Support", "Cloud Storage", "Hardware Router", "Implementation Fee", "Training Certification", "API Access"]
BOOLEANS = ["TRUE", "FALSE"]

# SYNONYMS
SYN_USERS = ["users", "customers", "clients", "subscribers", "accounts", "people", "members", "profiles"]
SYN_REVENUE = ["revenue", "sales", "money made", "income", "total sales value", "gross revenue", "top line"]
SYN_PROFIT = ["profit", "net income", "earnings", "bottom line", "net profit", "margins"]
SYN_PRODUCTS = ["products", "items", "offerings", "licenses", "services", "goods"]
SYN_BUY = ["bought", "purchased", "ordered", "acquired", "paid for"]
PREFIXES = ["Can you tell me ", "Show me ", "I need to know ", "Get ", "Fetch ", "What is ", "Calculate ", "Find ", "Query ", ""]

def rand_choice(lst):
    return random.choice(lst)

def get_random_date():
    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date(2025, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + datetime.timedelta(days=random_number_of_days)

def generate_dataset(num_samples=20000):
    dataset = []
    seen = set()
    attempts = 0
    
    while len(dataset) < num_samples and attempts < 200000:
        attempts += 1
        template_idx = random.randint(1, 15)
        prefix = rand_choice(PREFIXES)
        
        # 1. Count users by country
        if template_idx == 1:
            country = rand_choice(COUNTRIES)
            syn_u = rand_choice(SYN_USERS)
            q = f"{prefix}how many {syn_u} do we have from {country}?"
            sql = f"SELECT COUNT(user_id) FROM dim_users WHERE country = '{country}';"
            schema = S_USERS
            
        # 2. Count premium users by country
        elif template_idx == 2:
            country = rand_choice(COUNTRIES)
            is_prem = rand_choice(BOOLEANS)
            prem_word = "premium" if is_prem == "TRUE" else "free tier"
            syn_u = rand_choice(SYN_USERS)
            q = f"{prefix}the number of {prem_word} {syn_u} in {country}."
            sql = f"SELECT COUNT(user_id) FROM dim_users WHERE country = '{country}' AND is_premium = {is_prem};"
            schema = S_USERS
            
        # 3. Total revenue by category
        elif template_idx == 3:
            category = rand_choice(CATEGORIES)
            syn_rev = rand_choice(SYN_REVENUE)
            q = f"{prefix}the total {syn_rev} for the {category} category."
            sql = f"SELECT SUM(f.revenue) FROM fact_sales f JOIN dim_products p ON f.product_id = p.product_id WHERE p.category = '{category}';"
            schema = S_JOIN_PRODS_SALES
            
        # 4. Average profit margin by category
        elif template_idx == 4:
            category = rand_choice(CATEGORIES)
            q = f"{prefix}the average profit margin for {category}."
            sql = f"SELECT SUM(f.profit) / SUM(f.revenue) AS avg_profit_margin FROM fact_sales f JOIN dim_products p ON f.product_id = p.product_id WHERE p.category = '{category}';"
            schema = S_JOIN_PRODS_SALES

        # 5. Top N countries by revenue
        elif template_idx == 5:
            limit = random.randint(1, 50)
            syn_rev = rand_choice(SYN_REVENUE)
            q = f"{prefix}the top {limit} countries by {syn_rev}."
            sql = f"SELECT u.country, SUM(f.revenue) AS total_revenue FROM fact_sales f JOIN dim_users u ON f.user_id = u.user_id GROUP BY u.country ORDER BY total_revenue DESC LIMIT {limit};"
            schema = S_JOIN_USERS_SALES

        # 6. Best-selling product category (Quantity)
        elif template_idx == 6:
            limit = random.randint(1, 10)
            q = f"{prefix}the top {limit} product categories that sold the most units."
            sql = f"SELECT p.category, SUM(f.quantity) AS total_sold FROM fact_sales f JOIN dim_products p ON f.product_id = p.product_id GROUP BY p.category ORDER BY total_sold DESC LIMIT {limit};"
            schema = S_JOIN_PRODS_SALES

        # 7. Total sales for Premium Users
        elif template_idx == 7:
            syn_rev = rand_choice(SYN_REVENUE)
            is_prem = rand_choice(BOOLEANS)
            prem_word = "premium" if is_prem == "TRUE" else "non-premium"
            q = f"{prefix}how much {syn_rev} we generated from {prem_word} users."
            sql = f"SELECT SUM(f.revenue) FROM fact_sales f JOIN dim_users u ON f.user_id = u.user_id WHERE u.is_premium = {is_prem};"
            schema = S_JOIN_USERS_SALES

        # 8. Distinct users who bought a specific category
        elif template_idx == 8:
            category = rand_choice(CATEGORIES)
            syn_u = rand_choice(SYN_USERS)
            syn_b = rand_choice(SYN_BUY)
            q = f"{prefix}how many distinct {syn_u} {syn_b} {category}."
            sql = f"SELECT COUNT(DISTINCT f.user_id) FROM fact_sales f JOIN dim_products p ON f.product_id = p.product_id WHERE p.category = '{category}';"
            schema = S_JOIN_PRODS_SALES

        # 9. Triple JOIN - Revenue from Category by Country
        elif template_idx == 9:
            country = rand_choice(COUNTRIES)
            category = rand_choice(CATEGORIES)
            syn_rev = rand_choice(SYN_REVENUE)
            q = f"{prefix}the {syn_rev} from {category} sold to users in {country}."
            sql = f"SELECT SUM(f.revenue) FROM fact_sales f JOIN dim_users u ON f.user_id = u.user_id JOIN dim_products p ON f.product_id = p.product_id WHERE u.country = '{country}' AND p.category = '{category}';"
            schema = S_JOIN_ALL

        # 10. Email of top N users by profit
        elif template_idx == 10:
            limit = random.randint(3, 100)
            syn_u = rand_choice(SYN_USERS)
            syn_p = rand_choice(SYN_PROFIT)
            q = f"{prefix}the emails of the top {limit} {syn_u} by total {syn_p}."
            sql = f"SELECT u.email, SUM(f.profit) AS total_profit FROM fact_sales f JOIN dim_users u ON f.user_id = u.user_id GROUP BY u.email ORDER BY total_profit DESC LIMIT {limit};"
            schema = S_JOIN_USERS_SALES

        # 11. Price Filtering
        elif template_idx == 11:
            price = random.randint(10, 2000)
            operator = random.choice([">", "<", ">=", "<="])
            op_words = {">": "more than", "<": "less than", ">=": "at least", "<=": "at most"}
            syn_p = rand_choice(SYN_PRODUCTS)
            q = f"{prefix}the names of {syn_p} that cost {op_words[operator]} {price} dollars."
            sql = f"SELECT product_name FROM dim_products WHERE unit_price {operator} {price};"
            schema = S_PRODS

        # 12. Date filtering users
        elif template_idx == 12:
            d = get_random_date()
            operator = random.choice([">", "<"])
            op_words = {">": "after", "<": "before"}
            syn_u = rand_choice(SYN_USERS)
            q = f"{prefix}the {syn_u} who signed up {op_words[operator]} {d.strftime('%Y-%m-%d')}."
            sql = f"SELECT name, email FROM dim_users WHERE signup_date {operator} '{d.strftime('%Y-%m-%d')}';"
            schema = S_USERS
            
        # 13. Date filtering sales
        elif template_idx == 13:
            d = get_random_date()
            operator = random.choice([">", "<", ">=", "<="])
            op_words = {">": "after", "<": "before", ">=": "from", "<=": "up to"}
            syn_rev = rand_choice(SYN_REVENUE)
            q = f"{prefix}the total {syn_rev} generated {op_words[operator]} {d.strftime('%Y-%m-%d')}."
            sql = f"SELECT SUM(revenue) FROM fact_sales WHERE sale_timestamp {operator} '{d.strftime('%Y-%m-%d')}';"
            schema = S_SALES
            
        # 14. Complex Date and Category filtering
        elif template_idx == 14:
            d = get_random_date()
            category = rand_choice(CATEGORIES)
            syn_rev = rand_choice(SYN_REVENUE)
            q = f"{prefix}the {syn_rev} from {category} sales after {d.strftime('%Y-%m-%d')}."
            sql = f"SELECT SUM(f.revenue) FROM fact_sales f JOIN dim_products p ON f.product_id = p.product_id WHERE p.category = '{category}' AND f.sale_timestamp > '{d.strftime('%Y-%m-%d')}';"
            schema = S_JOIN_PRODS_SALES
            
        # 15. Complex Date, Country, Category filtering
        elif template_idx == 15:
            d = get_random_date()
            country = rand_choice(COUNTRIES)
            category = rand_choice(CATEGORIES)
            syn_rev = rand_choice(SYN_REVENUE)
            q = f"{prefix}the {syn_rev} from {category} sold to {country} before {d.strftime('%Y-%m-%d')}."
            sql = f"SELECT SUM(f.revenue) FROM fact_sales f JOIN dim_users u ON f.user_id = u.user_id JOIN dim_products p ON f.product_id = p.product_id WHERE u.country = '{country}' AND p.category = '{category}' AND f.sale_timestamp < '{d.strftime('%Y-%m-%d')}';"
            schema = S_JOIN_ALL

        # Add to dataset if unique
        # Clean up double spaces from empty prefixes
        q = q.replace("  ", " ").strip()
        # Capitalize first letter properly
        q = q[0].upper() + q[1:]
        
        key = (q, sql)
        if key not in seen:
            seen.add(key)
            dataset.append({
                "question": q,
                "schema": schema,
                "sql": sql
            })

    # Shuffle the dataset
    random.shuffle(dataset)
    return dataset

if __name__ == "__main__":
    print("Generating 20,000 unique Text-to-SQL pairs...")
    full_dataset = generate_dataset(20000)
    
    if len(full_dataset) < 20000:
        print(f"Warning: Only generated {len(full_dataset)} unique samples.")
        
    train_data = full_dataset[:19500]
    test_data = full_dataset[19500:]
    
    # Save train data
    train_path = os.path.join(os.path.dirname(__file__), "train_text_to_sql_large.json")
    with open(train_path, "w") as f:
        json.dump(train_data, f, indent=2)
        
    # Save test data
    test_path = os.path.join(os.path.dirname(__file__), "test_text_to_sql_large.json")
    with open(test_path, "w") as f:
        json.dump(test_data, f, indent=2)
        
    print(f"Success! Saved {len(train_data)} training pairs to train_text_to_sql_large.json")
    print(f"Success! Saved {len(test_data)} testing pairs to test_text_to_sql_large.json")
