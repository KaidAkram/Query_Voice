# /data_engineering/data_dictionary.py

# ==========================================
# 1. SCHEMA DEFINITIONS (The "What")
# ==========================================
# These describe the tables and columns in business terms.
# When the user asks a question, ChromaDB will retrieve the most relevant schemas.
SCHEMA_DOCS = [
    {
        "id": "table_dim_users",
        "type": "table_schema",
        "content": """Table: dim_users
        Description: Contains demographic and account information for all registered users.
        Columns:
        - user_id (UUID): Primary key. Unique identifier for the user.
        - name (VARCHAR): Full name of the user.
        - email (VARCHAR): User email address.
        - country (VARCHAR): Country of residence (e.g., 'United States', 'Algeria').
        - is_premium (BOOLEAN): True if the user pays for a premium subscription. False if they are on the free tier.
        - signup_date (DATE): When the user joined.""",
        "metadata": {"table": "dim_users"}
    },
    {
        "id": "table_dim_products",
        "type": "table_schema",
        "content": """Table: dim_products
        Description: Contains details about the software, licenses, and services we sell.
        Columns:
        - product_id (UUID): Primary key. Unique identifier for the product.
        - product_name (VARCHAR): Name of the item.
        - category (VARCHAR): Can be 'SaaS Subscription', 'Enterprise License', 'Consulting Hours', or 'Add-on Feature'.
        - unit_price (DECIMAL): How much we charge the customer per unit.
        - unit_cost (DECIMAL): How much it costs us to provide.""",
        "metadata": {"table": "dim_products"}
    },
    {
        "id": "table_fact_sales",
        "type": "table_schema",
        "content": """Table: fact_sales
        Description: The core transaction table. Every row is a completed purchase. Connects users to products.
        Columns:
        - sale_id (UUID): Primary key. Unique identifier for the transaction.
        - user_id (UUID): Foreign key to dim_users.
        - product_id (UUID): Foreign key to dim_products.
        - sale_timestamp (TIMESTAMP): When the transaction occurred.
        - quantity (INT): Number of units bought.
        - revenue (DECIMAL): Total money made for this sale (quantity * unit_price).
        - profit (DECIMAL): Money kept after costs (revenue - (quantity * unit_cost)).""",
        "metadata": {"table": "fact_sales"}
    }
]

# ==========================================
# 2. GOLDEN QUERIES (The "How")
# ==========================================
# These are pre-verified, perfect SQL examples for common questions.
# Providing examples is the #1 way to improve LLM accuracy (Few-Shot Prompting).
GOLDEN_QUERIES = [
    {
        "id": "golden_1_premium_revenue",
        "type": "golden_query",
        "content": """Question: How much revenue did we make from premium users?
        SQL: SELECT SUM(f.revenue) AS total_revenue FROM fact_sales f JOIN dim_users u ON f.user_id = u.user_id WHERE u.is_premium = TRUE;""",
        "metadata": {"query_type": "revenue_calculation"}
    },
    {
        "id": "golden_2_category_sales",
        "type": "golden_query",
        "content": """Question: What are our best selling product categories by total quantity?
        SQL: SELECT p.category, SUM(f.quantity) as total_sold FROM fact_sales f JOIN dim_products p ON f.product_id = p.product_id GROUP BY p.category ORDER BY total_sold DESC;""",
        "metadata": {"query_type": "category_aggregation"}
    },
    {
        "id": "golden_3_profit_margin",
        "type": "golden_query",
        "content": """Question: Which product has the highest profit margin?
        SQL: SELECT p.product_name, SUM(f.profit) / SUM(f.revenue) AS profit_margin FROM fact_sales f JOIN dim_products p ON f.product_id = p.product_id GROUP BY p.product_name ORDER BY profit_margin DESC LIMIT 1;""",
        "metadata": {"query_type": "profitability"}
    },
    {
        "id": "golden_4_country_users",
        "type": "golden_query",
        "content": """Question: How many free-tier users do we have in the United States?
        SQL: SELECT COUNT(user_id) AS user_count FROM dim_users WHERE is_premium = FALSE AND country = 'United States';""",
        "metadata": {"query_type": "user_demographics"}
    }
]
