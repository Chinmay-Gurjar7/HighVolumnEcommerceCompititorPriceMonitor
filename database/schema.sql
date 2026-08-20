-- ============================================================
-- E-Commerce Competitive Price Intelligence
-- PostgreSQL Database Schema
-- ============================================================


-- ============================================================
-- PRODUCTS
-- ============================================================

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(255) PRIMARY KEY,
    product_name TEXT NOT NULL,
    brand VARCHAR(255),
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- MERCHANTS
-- ============================================================

CREATE TABLE IF NOT EXISTS merchants (
    merchant_id SERIAL PRIMARY KEY,
    merchant_name VARCHAR(500) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- PRICE HISTORY
-- ============================================================

CREATE TABLE IF NOT EXISTS price_history (
    price_id BIGSERIAL PRIMARY KEY,

    product_id VARCHAR(255) NOT NULL,

    merchant_id INTEGER NOT NULL,

    price_min NUMERIC(12, 2) NOT NULL,

    price_max NUMERIC(12, 2) NOT NULL,

    price NUMERIC(12, 2) NOT NULL,

    currency VARCHAR(10),

    condition VARCHAR(100),

    observed_at TIMESTAMPTZ NOT NULL,

    observed_date DATE,

    observed_year INTEGER,

    observed_month INTEGER,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_price_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT fk_price_merchant
        FOREIGN KEY (merchant_id)
        REFERENCES merchants(merchant_id),

    CONSTRAINT chk_price_min
        CHECK (price_min >= 0),

    CONSTRAINT chk_price_max
        CHECK (price_max >= 0),

    CONSTRAINT chk_price
        CHECK (price >= 0),

    CONSTRAINT chk_price_range
        CHECK (price_min <= price_max)
);


-- ============================================================
-- PIPELINE RUNS
-- ============================================================

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id BIGSERIAL PRIMARY KEY,

    started_at TIMESTAMPTZ NOT NULL,

    completed_at TIMESTAMPTZ,

    status VARCHAR(50) NOT NULL,

    records_received INTEGER DEFAULT 0,

    records_validated INTEGER DEFAULT 0,

    records_transformed INTEGER DEFAULT 0,

    records_loaded INTEGER DEFAULT 0,

    error_message TEXT
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_price_history_product
ON price_history(product_id);


CREATE INDEX IF NOT EXISTS idx_price_history_merchant
ON price_history(merchant_id);


CREATE INDEX IF NOT EXISTS idx_price_history_observed_at
ON price_history(observed_at);


CREATE INDEX IF NOT EXISTS idx_price_history_product_date
ON price_history(product_id, observed_at);


CREATE INDEX IF NOT EXISTS idx_price_history_merchant_date
ON price_history(merchant_id, observed_at);