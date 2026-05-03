-- ============================================================
-- QueryVoice — Star Schema DDL (Data Definition Language)
-- ============================================================
-- Architecture: OLAP Star Schema
--   • dim_* tables  → Dimension tables (context: who, what, when)
--   • fact_* tables  → Fact tables (measurable business events)
--
-- This script is auto-executed by PostgreSQL on first container
-- startup via docker-entrypoint-initdb.d mount.
-- ============================================================

-- 1. DIMENSION TABLES (The context of our data)

CREATE TABLE IF NOT EXISTS dim_users (
    user_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    country VARCHAR(100),
    is_premium BOOLEAN DEFAULT FALSE,
    signup_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_products (
    product_id UUID PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL,
    -- Check constraint ensures data integrity (can't have negative prices)
    CONSTRAINT check_price_positive CHECK (unit_price >= 0),
    CONSTRAINT check_cost_positive CHECK (unit_cost >= 0)
);

-- 2. FACT TABLE (The measurable events)

CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id UUID PRIMARY KEY,
    user_id UUID REFERENCES dim_users(user_id),
    product_id UUID REFERENCES dim_products(product_id),
    sale_timestamp TIMESTAMP NOT NULL,
    quantity INT NOT NULL,
    revenue DECIMAL(10, 2) NOT NULL,
    profit DECIMAL(10, 2) NOT NULL
);

-- 3. PERFORMANCE INDEXING (Crucial for fast AI queries)
-- We index Foreign Keys and columns that PMs will frequently filter by.
CREATE INDEX idx_sales_user ON fact_sales(user_id);
CREATE INDEX idx_sales_product ON fact_sales(product_id);
CREATE INDEX idx_sales_date ON fact_sales(sale_timestamp);
CREATE INDEX idx_products_category ON dim_products(category);
