-- ══════════════════════════════════════════════════════════════════════════════
-- PRESTOCKS DATABASE SCHEMA v2.0
-- PostgreSQL 15+ with TimescaleDB
-- Fully normalized, production-ready
-- ══════════════════════════════════════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy search
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- SECTORS & TAGS (Lookup tables)
-- ============================================================

CREATE TABLE sector (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_sector_id INT REFERENCES sector(id),
    color_hex VARCHAR(7),
    icon_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tag (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(50), -- 'theme', 'risk_type', 'market_cap', 'geography'
    color_hex VARCHAR(7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- USERS (Enhanced)
-- ============================================================

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    username VARCHAR(50) UNIQUE,
    avatar_url TEXT,
    age INT,
    risk_tier VARCHAR(50) DEFAULT 'beginner',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMP,
    preferences JSONB DEFAULT '{}',
    notification_settings JSONB DEFAULT '{"email": true, "push": true, "weekly_digest": true}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_risk_profile (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    risk_tolerance_score INT CHECK (risk_tolerance_score BETWEEN 0 AND 100),
    knowledge_level INT CHECK (knowledge_level BETWEEN 0 AND 100),
    investment_horizon VARCHAR(20), -- 'short', 'medium', 'long'
    income_stability VARCHAR(20), -- 'stable', 'variable', 'uncertain'
    loss_tolerance INT CHECK (loss_tolerance BETWEEN 0 AND 100),
    assessment_answers JSONB,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

CREATE TABLE user_session (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- COMPANIES (Enhanced from 'stock')
-- ============================================================

CREATE TABLE company (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE,
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    description TEXT,
    logo_url TEXT,
    website_url TEXT,
    sector_id INT REFERENCES sector(id),
    industry VARCHAR(150),
    sub_industry VARCHAR(150),
    founded_year INT,
    headquarters_city VARCHAR(100),
    headquarters_country VARCHAR(100),
    employee_count INT,
    ceo_name VARCHAR(255),
    market_cap BIGINT,
    company_type VARCHAR(30) DEFAULT 'public', -- 'public', 'private', 'pre_ipo'
    exchange VARCHAR(20), -- 'NYSE', 'NASDAQ', 'LSE'
    ipo_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE company_tag (
    company_id INT REFERENCES company(id) ON DELETE CASCADE,
    tag_id INT REFERENCES tag(id) ON DELETE CASCADE,
    PRIMARY KEY (company_id, tag_id)
);

CREATE TABLE company_fundamentals (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES company(id) ON DELETE CASCADE,
    period_end DATE NOT NULL,
    period_type VARCHAR(10) DEFAULT 'quarterly', -- 'quarterly', 'annual'
    revenue BIGINT,
    net_income BIGINT,
    ebitda BIGINT,
    gross_margin FLOAT,
    operating_margin FLOAT,
    net_margin FLOAT,
    pe_ratio FLOAT,
    price_to_sales FLOAT,
    price_to_book FLOAT,
    ev_to_ebitda FLOAT,
    debt_to_equity FLOAT,
    current_ratio FLOAT,
    quick_ratio FLOAT,
    interest_coverage FLOAT,
    free_cash_flow BIGINT,
    cash_and_equivalents BIGINT,
    total_debt BIGINT,
    shares_outstanding BIGINT,
    dividend_yield FLOAT,
    payout_ratio FLOAT,
    roe FLOAT,
    roa FLOAT,
    revenue_growth_yoy FLOAT,
    earnings_growth_yoy FLOAT,
    cash_runway_months INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, period_end, period_type)
);

-- Stock price time-series (TimescaleDB hypertable)
CREATE TABLE stock_prices (
    time TIMESTAMPTZ NOT NULL,
    company_id INT NOT NULL REFERENCES company(id),
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    adjusted_close FLOAT,
    volume BIGINT,
    vwap FLOAT
);
SELECT create_hypertable('stock_prices', 'time', if_not_exists => TRUE);

-- ============================================================
-- INVESTORS & FUNDING ROUNDS
-- ============================================================

CREATE TABLE investor (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50), -- 'vc', 'pe', 'angel', 'corporate', 'sovereign_fund', 'hedge_fund'
    description TEXT,
    logo_url TEXT,
    website_url TEXT,
    headquarters_city VARCHAR(100),
    headquarters_country VARCHAR(100),
    aum_usd BIGINT, -- Assets under management
    founded_year INT,
    notable_investments TEXT[], -- Array of well-known portfolio companies
    investment_stages TEXT[], -- ['seed', 'series_a', 'series_b', 'growth']
    sectors_focus INT[], -- References to sector ids
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE funding_round (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES company(id) ON DELETE CASCADE,
    round_type VARCHAR(50) NOT NULL, -- 'seed', 'series_a', 'series_b', ..., 'ipo', 'debt'
    amount_raised_usd BIGINT,
    pre_money_valuation BIGINT,
    post_money_valuation BIGINT,
    announced_date DATE,
    closed_date DATE,
    lead_investor_id INT REFERENCES investor(id),
    num_investors INT,
    equity_dilution FLOAT,
    source_url TEXT,
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE funding_round_investor (
    funding_round_id INT REFERENCES funding_round(id) ON DELETE CASCADE,
    investor_id INT REFERENCES investor(id) ON DELETE CASCADE,
    amount_invested_usd BIGINT,
    is_lead BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (funding_round_id, investor_id)
);

-- ============================================================
-- RISK FLAGS (Enhanced)
-- ============================================================

CREATE TABLE risk_flag (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES company(id) ON DELETE CASCADE,
    flag_type VARCHAR(50) NOT NULL,
    severity_score INT CHECK (severity_score BETWEEN 0 AND 100),
    title VARCHAR(255),
    explanation TEXT,
    ai_explanation TEXT,
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    data_sources TEXT[],
    raw_data JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, flag_type, calculated_at)
);

CREATE TABLE composite_risk_score (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES company(id) ON DELETE CASCADE,
    overall_score INT CHECK (overall_score BETWEEN 0 AND 100),
    volatility_component INT,
    valuation_component INT,
    financial_health_component INT,
    momentum_component INT,
    insider_component INT,
    sentiment_component INT,
    weights JSONB,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PORTFOLIOS & TRADING (Enhanced)
-- ============================================================

CREATE TABLE portfolio (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    name VARCHAR(100) DEFAULT 'Main Portfolio',
    total_value FLOAT DEFAULT 10000.00,
    cash_available FLOAT DEFAULT 10000.00,
    initial_capital FLOAT DEFAULT 10000.00,
    currency VARCHAR(3) DEFAULT 'USD',
    is_default BOOLEAN DEFAULT TRUE,
    strategy_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE holding (
    id SERIAL PRIMARY KEY,
    portfolio_id INT REFERENCES portfolio(id) ON DELETE CASCADE,
    company_id INT REFERENCES company(id),
    quantity FLOAT NOT NULL,
    average_buy_price FLOAT NOT NULL,
    current_price FLOAT,
    unrealized_pnl FLOAT,
    unrealized_pnl_pct FLOAT,
    weight_pct FLOAT,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_id, company_id)
);

CREATE TABLE trade (
    id SERIAL PRIMARY KEY,
    portfolio_id INT REFERENCES portfolio(id),
    company_id INT REFERENCES company(id),
    order_type VARCHAR(10) NOT NULL, -- 'buy', 'sell'
    order_method VARCHAR(20) DEFAULT 'market', -- 'market', 'limit', 'stop_loss'
    quantity FLOAT NOT NULL,
    price_executed FLOAT NOT NULL,
    total_value FLOAT NOT NULL,
    limit_price FLOAT,
    stop_price FLOAT,
    commission FLOAT DEFAULT 0,
    reasoning TEXT,
    risk_flags_at_trade JSONB,
    portfolio_snapshot JSONB,
    status VARCHAR(20) DEFAULT 'executed', -- 'pending', 'executed', 'cancelled', 'failed'
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- WATCHLISTS (Enhanced)
-- ============================================================

CREATE TABLE watchlist (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL DEFAULT 'My Watchlist',
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE watchlist_item (
    id SERIAL PRIMARY KEY,
    watchlist_id INT REFERENCES watchlist(id) ON DELETE CASCADE,
    company_id INT REFERENCES company(id) ON DELETE CASCADE,
    notes TEXT,
    target_price FLOAT,
    alert_above FLOAT,
    alert_below FLOAT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(watchlist_id, company_id)
);

-- ============================================================
-- ALERTS & NOTIFICATIONS
-- ============================================================

CREATE TABLE alert (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    company_id INT REFERENCES company(id),
    alert_type VARCHAR(50) NOT NULL, -- 'price_above', 'price_below', 'risk_flag', 'news', 'earnings', 'funding_round', 'portfolio_threshold'
    condition JSONB NOT NULL,
    title VARCHAR(255),
    message TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMP,
    cooldown_hours INT DEFAULT 24,
    last_notified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notification (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    alert_id INT REFERENCES alert(id),
    type VARCHAR(50) NOT NULL, -- 'price_alert', 'trade_executed', 'risk_update', 'ai_insight', 'system'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    channel VARCHAR(20) DEFAULT 'in_app', -- 'in_app', 'email', 'push'
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- NEWS
-- ============================================================

CREATE TABLE news_article (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content TEXT,
    source_name VARCHAR(100),
    source_url TEXT,
    article_url TEXT NOT NULL,
    image_url TEXT,
    author VARCHAR(255),
    published_at TIMESTAMP NOT NULL,
    category VARCHAR(50), -- 'earnings', 'merger', 'regulation', 'product', 'leadership', 'market'
    sentiment_score FLOAT, -- -1 to 1
    sentiment_label VARCHAR(20), -- 'positive', 'negative', 'neutral'
    relevance_score FLOAT,
    is_breaking BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE news_company (
    news_id INT REFERENCES news_article(id) ON DELETE CASCADE,
    company_id INT REFERENCES company(id) ON DELETE CASCADE,
    relevance FLOAT DEFAULT 1.0,
    PRIMARY KEY (news_id, company_id)
);

CREATE TABLE news_sector (
    news_id INT REFERENCES news_article(id) ON DELETE CASCADE,
    sector_id INT REFERENCES sector(id) ON DELETE CASCADE,
    PRIMARY KEY (news_id, sector_id)
);

-- ============================================================
-- AI PROMPTS & RESPONSES
-- ============================================================

CREATE TABLE ai_prompt_template (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50), -- 'research', 'portfolio_advice', 'flag_explanation', 'comparison', 'education'
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT NOT NULL,
    model VARCHAR(50) DEFAULT 'claude-sonnet-4-20250514',
    temperature FLOAT DEFAULT 0.3,
    max_tokens INT DEFAULT 2000,
    input_schema JSONB,
    output_schema JSONB,
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_conversation (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    company_id INT REFERENCES company(id),
    context_type VARCHAR(50), -- 'research', 'portfolio_advice', 'flag_explain', 'general'
    title VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_message (
    id SERIAL PRIMARY KEY,
    conversation_id UUID REFERENCES ai_conversation(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    prompt_template_id INT REFERENCES ai_prompt_template(id),
    model_used VARCHAR(50),
    tokens_input INT,
    tokens_output INT,
    latency_ms INT,
    cost_usd FLOAT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_research_report (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id),
    company_id INT REFERENCES company(id),
    report_type VARCHAR(50) NOT NULL, -- 'full_analysis', 'risk_assessment', 'competitor_map', 'ipo_probability', 'swot'
    summary TEXT,
    risks JSONB,
    opportunities JSONB,
    financial_health JSONB,
    funding_history JSONB,
    competitors JSONB,
    ipo_probability JSONB,
    swot_analysis JSONB,
    raw_response TEXT,
    model_used VARCHAR(50),
    data_sources TEXT[],
    confidence_score FLOAT,
    is_stale BOOLEAN DEFAULT FALSE,
    valid_until TIMESTAMP,
    generation_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_portfolio_advice (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    portfolio_id INT REFERENCES portfolio(id),
    advice_type VARCHAR(50) NOT NULL, -- 'weekly_review', 'rebalance', 'diversification', 'risk_alert'
    overall_health_score INT CHECK (overall_health_score BETWEEN 0 AND 100),
    diversification_score INT CHECK (diversification_score BETWEEN 0 AND 100),
    concentration_risk JSONB,
    missing_sectors JSONB,
    suggestions JSONB,
    portfolio_snapshot JSONB,
    model_used VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- API KEYS & EXTERNAL INTEGRATIONS
-- ============================================================

CREATE TABLE api_key (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(8) NOT NULL, -- First 8 chars for identification
    permissions JSONB DEFAULT '["read"]',
    rate_limit_per_minute INT DEFAULT 60,
    rate_limit_per_day INT DEFAULT 10000,
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_usage_log (
    id BIGSERIAL PRIMARY KEY,
    api_key_id INT REFERENCES api_key(id),
    user_id INT REFERENCES "user"(id),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INT,
    response_time_ms INT,
    request_size_bytes INT,
    response_size_bytes INT,
    ip_address INET,
    user_agent TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- LEARNING (Enhanced)
-- ============================================================

CREATE TABLE learning_module (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE,
    description TEXT,
    required_tier VARCHAR(50) DEFAULT 'beginner',
    category VARCHAR(50), -- 'fundamentals', 'technical', 'risk_management', 'psychology'
    difficulty_level INT DEFAULT 1, -- 1-5
    content_type VARCHAR(30), -- 'video', 'interactive', 'article', 'quiz_only'
    content_url TEXT,
    content_body TEXT,
    estimated_duration_minutes INT,
    quiz_questions JSONB,
    pass_threshold INT DEFAULT 80,
    prerequisites INT[], -- Array of module IDs
    order_index INT NOT NULL DEFAULT 0,
    xp_reward INT DEFAULT 100,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_module_progress (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    module_id INT REFERENCES learning_module(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed', 'failed'
    progress_pct INT DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    quiz_score INT,
    attempts INT DEFAULT 0,
    time_spent_seconds INT DEFAULT 0,
    UNIQUE(user_id, module_id)
);

-- ============================================================
-- SOCIAL (Enhanced)
-- ============================================================

CREATE TABLE social_post (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES "user"(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    tickers TEXT[],
    trade_type VARCHAR(10), -- 'buy', 'sell', 'hold'
    trade_id INT REFERENCES trade(id),
    sentiment VARCHAR(20), -- 'bullish', 'bearish', 'neutral'
    is_pinned BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    likes_count INT DEFAULT 0,
    comments_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE social_comment (
    id SERIAL PRIMARY KEY,
    post_id INT REFERENCES social_post(id) ON DELETE CASCADE,
    user_id INT REFERENCES "user"(id),
    parent_comment_id INT REFERENCES social_comment(id),
    content TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE social_like (
    id SERIAL PRIMARY KEY,
    post_id INT REFERENCES social_post(id) ON DELETE CASCADE,
    user_id INT REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id)
);

-- ============================================================
-- COMPETITOR MAP
-- ============================================================

CREATE TABLE competitor_relationship (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES company(id) ON DELETE CASCADE,
    competitor_id INT REFERENCES company(id) ON DELETE CASCADE,
    overlap_score FLOAT, -- 0-1, how much they overlap
    relationship_type VARCHAR(30), -- 'direct', 'indirect', 'adjacent'
    category VARCHAR(50), -- product area where they compete
    source VARCHAR(50), -- 'ai_generated', 'manual', 'sec_filing'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, competitor_id)
);

-- ============================================================
-- INDEXES (Performance)
-- ============================================================

-- Users
CREATE INDEX idx_user_email ON "user" (email);
CREATE INDEX idx_user_username ON "user" (username);
CREATE INDEX idx_user_session_user ON user_session (user_id, expires_at);

-- Companies
CREATE INDEX idx_company_ticker ON company (ticker);
CREATE INDEX idx_company_name_trgm ON company USING gin (name gin_trgm_ops);
CREATE INDEX idx_company_sector ON company (sector_id);
CREATE INDEX idx_company_type ON company (company_type);

-- Prices
CREATE INDEX idx_stock_prices_company_time ON stock_prices (company_id, time DESC);

-- Funding
CREATE INDEX idx_funding_round_company ON funding_round (company_id, announced_date DESC);
CREATE INDEX idx_funding_round_investor ON funding_round_investor (investor_id);

-- Risk Flags
CREATE INDEX idx_risk_flag_company ON risk_flag (company_id, calculated_at DESC);
CREATE INDEX idx_composite_risk_company ON composite_risk_score (company_id, calculated_at DESC);

-- Portfolio & Trading
CREATE INDEX idx_portfolio_user ON portfolio (user_id);
CREATE INDEX idx_holding_portfolio ON holding (portfolio_id);
CREATE INDEX idx_trade_portfolio ON trade (portfolio_id, executed_at DESC);
CREATE INDEX idx_trade_company ON trade (company_id, executed_at DESC);

-- Watchlists
CREATE INDEX idx_watchlist_user ON watchlist (user_id);
CREATE INDEX idx_watchlist_item_watchlist ON watchlist_item (watchlist_id);

-- Alerts & Notifications
CREATE INDEX idx_alert_user_active ON alert (user_id) WHERE is_active = TRUE;
CREATE INDEX idx_notification_user_unread ON notification (user_id, created_at DESC) WHERE is_read = FALSE;

-- News
CREATE INDEX idx_news_published ON news_article (published_at DESC);
CREATE INDEX idx_news_company ON news_company (company_id);
CREATE INDEX idx_news_sentiment ON news_article (sentiment_label, published_at DESC);

-- AI
CREATE INDEX idx_ai_conversation_user ON ai_conversation (user_id, created_at DESC);
CREATE INDEX idx_ai_research_company ON ai_research_report (company_id, created_at DESC);
CREATE INDEX idx_ai_portfolio_user ON ai_portfolio_advice (user_id, created_at DESC);

-- API
CREATE INDEX idx_api_key_user ON api_key (user_id) WHERE is_active = TRUE;
CREATE INDEX idx_api_usage_time ON api_usage_log (created_at DESC);
CREATE INDEX idx_api_usage_key ON api_usage_log (api_key_id, created_at DESC);

-- Social
CREATE INDEX idx_social_post_user ON social_post (user_id, created_at DESC);
CREATE INDEX idx_social_post_tickers ON social_post USING GIN (tickers);

-- Learning
CREATE INDEX idx_module_progress_user ON user_module_progress (user_id);
