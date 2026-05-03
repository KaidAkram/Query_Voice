# Phase 1, Step 2 — Star Schema Architecture
==========================================

## 🏗️ Design Philosophy
QueryVoice uses a **Star Schema** optimized for analytical Text-to-SQL tasks. This structure minimizes joins while maintaining clear relationships between users, products, and sales.

## 🗄️ Database Tables

### 1. `dim_users` (Dimension Table)
Stores user-specific metadata.
- `user_id` (PK)
- `name`
- `email`
- `country`
- `is_premium` (Boolean)
- `signup_date`

### 2. `dim_products` (Dimension Table)
Stores catalog information.
- `product_id` (PK)
- `product_name`
- `category`
- `unit_price`
- `unit_cost`

### 3. `fact_sales` (Fact Table)
The central table capturing transactional data.
- `sale_id` (PK)
- `user_id` (FK -> dim_users)
- `product_id` (FK -> dim_products)
- `sale_timestamp`
- `quantity`
- `revenue`
- `profit`

## 🔗 Relationships
- **Sales to Users:** Many-to-One
- **Sales to Products:** Many-to-One
