-- PreStocks Database Schema
-- PostgreSQL 15+ with TimescaleDB extension
-- Run: CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    risk_tier VARCHAR(50) -- 'beginner', 'intermediate', 'advanced'
);

CREATE TABLE user_risk_profile (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    risk_tolerance_score INT, -- 0-100
    knowledge_level INT, -- 0-100
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- STOCKS
-- ============================================================

CREATE TABLE stock (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE stock_fundamentals (
    id SERIAL PRIMARY KEY,
    stock_id INT REFERENCES stock(id),
    quarter_date DATE,
    pe_ratio FLOAT,
    price_to_sales FLOAT,
    debt_to_equity FLOAT,
    current_ratio FLOAT,
    interest_coverage FLOAT,
    cash_runway_months INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, quarter_date)
);

-- Stock price history (time-series, using TimescaleDB hypertable)
CREATE TABLE stock_prices (
    time TIMESTAMP NOT NULL,
    stock_id INT NOT NULL,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    FOREIGN KEY (stock_id) REFERENCES stock(id)
);

-- Convert to hypertable:
SELECT create_hypertable('stock_prices', 'time', if_not_exists => TRUE);

-- ============================================================
-- RISK FLAGS
-- ============================================================

CREATE TABLE risk_flag (
    id SERIAL PRIMARY KEY,
    stock_id INT REFERENCES stock(id),
    flag_type VARCHAR(50), -- 'volatility', 'valuation', 'insider_activity', etc.
    severity_score INT, -- 0-100
    explanation TEXT,
    confidence_score FLOAT, -- 0-1
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, flag_type, calculated_at)
);

-- ============================================================
-- PORTFOLIOS & TRADING
-- ============================================================

CREATE TABLE portfolio (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    total_value FLOAT DEFAULT 10000.00,
    cash_available FLOAT DEFAULT 10000.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

CREATE TABLE holding (
    id SERIAL PRIMARY KEY,
    portfolio_id INT REFERENCES portfolio(id) ON DELETE CASCADE,
    stock_id INT REFERENCES stock(id),
    quantity FLOAT NOT NULL,
    average_buy_price FLOAT NOT NULL,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trade (
    id SERIAL PRIMARY KEY,
    portfolio_id INT REFERENCES portfolio(id),
    stock_id INT REFERENCES stock(id),
    order_type VARCHAR(10), -- 'buy', 'sell'
    quantity FLOAT NOT NULL,
    price_executed FLOAT NOT NULL,
    total_value FLOAT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_ticket_details JSONB -- store all order details for audit
);

-- ============================================================
-- LEARNING
-- ============================================================

CREATE TABLE learning_module (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    required_tier VARCHAR(50), -- 'beginner', 'intermediate', 'advanced'
    content_url TEXT,
    estimated_duration_minutes INT,
    quiz_questions JSONB, -- array of question objects
    created_at TIMESTAMP
);

CREATE TABLE user_module_progress (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    module_id INT REFERENCES learning_module(id),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    quiz_score INT, -- 0-100, NULL if not completed
    UNIQUE(user_id, module_id)
);

-- ============================================================
-- SOCIAL
-- ============================================================

CREATE TABLE social_post (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    content TEXT, -- user's reasoning, <300 chars
    tickers TEXT[], -- array of tickers mentioned
    trade_type VARCHAR(10), -- 'buy', 'sell', 'hold'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    engagement_count INT DEFAULT 0
);

CREATE TABLE social_comment (
    id SERIAL PRIMARY KEY,
    post_id INT REFERENCES social_post(id) ON DELETE CASCADE,
    user_id INT REFERENCES "user"(id),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE social_like (
    id SERIAL PRIMARY KEY,
    post_id INT REFERENCES social_post(id) ON DELETE CASCADE,
    user_id INT REFERENCES "user"(id),
    created_at TIMESTAMP,
    UNIQUE(post_id, user_id)
);

-- ============================================================
-- WATCHLIST
-- ============================================================

CREATE TABLE watchlist_item (
    id SERIAL PRIMARY KEY,
    portfolio_id INT REFERENCES portfolio(id) ON DELETE CASCADE,
    stock_id INT REFERENCES stock(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_id, stock_id)
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_stock_prices_stock_time ON stock_prices (stock_id, time DESC);
CREATE INDEX idx_risk_flag_stock ON risk_flag (stock_id, calculated_at DESC);
CREATE INDEX idx_holding_portfolio ON holding (portfolio_id);
CREATE INDEX idx_trade_portfolio ON trade (portfolio_id, executed_at DESC);
CREATE INDEX idx_social_post_user ON social_post (user_id, created_at DESC);
CREATE INDEX idx_social_post_tickers ON social_post USING GIN (tickers);
CREATE INDEX idx_user_email ON "user" (email);
CREATE INDEX idx_stock_ticker ON stock (ticker);
