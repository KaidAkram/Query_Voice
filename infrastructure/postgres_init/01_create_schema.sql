-- ============================================
-- PostgreSQL Initialization Script
-- ============================================
-- This script runs automatically when the
-- PostgreSQL container starts for the first time.
-- It creates the QueryVoice database schema.
-- ============================================

-- Create the business intelligence schema
\echo 'Creating QueryVoice database schema...'

-- Departments
CREATE TABLE IF NOT EXISTS departments (
    department_id   SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    location        VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employees
CREATE TABLE IF NOT EXISTS employees (
    employee_id     SERIAL PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(100) UNIQUE,
    department_id   INTEGER REFERENCES departments(department_id),
    hire_date       DATE NOT NULL,
    salary          DECIMAL(10, 2),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    product_id      SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    category        VARCHAR(100),
    price           DECIMAL(10, 2) NOT NULL,
    stock_quantity  INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id     SERIAL PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(100) UNIQUE,
    region          VARCHAR(100),
    registered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales
CREATE TABLE IF NOT EXISTS sales (
    sale_id         SERIAL PRIMARY KEY,
    product_id      INTEGER REFERENCES products(product_id),
    customer_id     INTEGER REFERENCES customers(customer_id),
    employee_id     INTEGER REFERENCES employees(employee_id),
    quantity        INTEGER NOT NULL,
    total_amount    DECIMAL(12, 2) NOT NULL,
    sale_date       DATE NOT NULL,
    region          VARCHAR(100),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_region ON sales(region);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees(department_id);

\echo 'Schema created successfully.'
