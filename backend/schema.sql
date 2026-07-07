-- ═══════════════════════════════════════════════════════════════════════════
-- PRESTOCKS DATABASE SCHEMA v3.0
-- Comprehensive normalized schema for a pre-IPO / paper trading platform
-- PostgreSQL 15+ with pg_trgm, TimescaleDB extensions
-- ═══════════════════════════════════════════════════════════════════════════

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── ENUM TYPES ───
CREATE TYPE risk_tier AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE company_type AS ENUM ('public', 'private', 'pre_ipo', 'spac');
CREATE TYPE order_type AS ENUM ('market', 'limit', 'stop_loss', 'stop_limit');
CREATE TYPE order_side AS ENUM ('buy', 'sell');
CREATE TYPE order_status AS ENUM ('pending', 'filled', 'partially_filled', 'cancelled', 'rejected');
CREATE TYPE alert_type AS ENUM ('price_above', 'price_below', 'risk_flag', 'earnings', 'news', 'portfolio', 'ipo_update');
CREATE TYPE notification_channel AS ENUM ('in_app', 'email', 'push');
CREATE TYPE funding_stage AS ENUM ('pre_seed', 'seed', 'series_a', 'series_b', 'series_c', 'series_d', 'series_e', 'growth', 'ipo', 'debt', 'secondary');
CREATE TYPE sentiment_label AS ENUM ('very_positive', 'positive', 'neutral', 'negative', 'very_negative');
CREATE TYPE ai_role AS ENUM ('system', 'user', 'assistant');

-- ═══════════════════════════════════════════════════════════════
-- 1. USERS & AUTHENTICATION
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE "user" (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    username        VARCHAR(50) UNIQUE,
    avatar_url      TEXT,
    age             INTEGER,
    risk_tier       risk_tier DEFAULT 'beginner',
    is_active       BOOLEAN DEFAULT TRUE,
    is_verified     BOOLEAN DEFAULT FALSE,
    last_login_at   TIMESTAMPTZ,
    preferences     JSONB DEFAULT '{}',
    notification_settings JSONB DEFAULT '{"email": true, "push": true, "weekly_digest": true}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_user_email ON "user" USING btree(email);
CREATE INDEX idx_user_username ON "user" USING btree(username);
CREATE INDEX idx_user_email_trgm ON "user" USING gin(email gin_trgm_ops);

CREATE TABLE user_risk_profile (
    id                    SERIAL PRIMARY KEY,
    user_id               INTEGER NOT NULL UNIQUE REFERENCES "user"(id) ON DELETE CASCADE,
    risk_tolerance_score  INTEGER CHECK (risk_tolerance_score BETWEEN 0 AND 100),
    knowledge_level       INTEGER CHECK (knowledge_level BETWEEN 1 AND 5),
    investment_horizon    VARCHAR(20),
    income_stability      VARCHAR(20),
    loss_tolerance        INTEGER CHECK (loss_tolerance BETWEEN 0 AND 100),
    assessment_answers    JSONB,
    assessed_at           TIMESTAMPTZ DEFAULT NOW(),
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_session (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    refresh_token_hash  VARCHAR(255) NOT NULL,
    device_info         JSONB,
    ip_address          VARCHAR(45),
    user_agent          TEXT,
    expires_at          TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_session_user ON user_session(user_id);
CREATE INDEX idx_session_expires ON user_session(expires_at);

-- ═══════════════════════════════════════════════════════════════
-- 2. SECTORS & TAGS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE sector (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    slug        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon_url    TEXT,
    color       VARCHAR(7),
    parent_id   INTEGER REFERENCES sector(id),
    sort_order  INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tag (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    slug        VARCHAR(100) NOT NULL UNIQUE,
    category    VARCHAR(50) NOT NULL DEFAULT 'general',
    description TEXT,
    color       VARCHAR(7),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_tag_category ON tag(category);

-- ═══════════════════════════════════════════════════════════════
-- 3. COMPANIES
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE company (
    id                      SERIAL PRIMARY KEY,
    ticker                  VARCHAR(10) UNIQUE,
    name                    VARCHAR(255) NOT NULL,
    legal_name              VARCHAR(255),
    description             TEXT,
    logo_url                TEXT,
    website_url             TEXT,
    sector_id               INTEGER REFERENCES sector(id),
    industry                VARCHAR(150),
    sub_industry            VARCHAR(150),
    founded_year            INTEGER,
    headquarters_city       VARCHAR(100),
    headquarters_country    VARCHAR(100) DEFAULT 'US',
    employee_count          INTEGER,
    ceo_name                VARCHAR(255),
    market_cap              BIGINT,
    company_type            company_type DEFAULT 'public',
    exchange                VARCHAR(20),
    ipo_date                DATE,
    estimated_ipo_date      VARCHAR(50),
    latest_valuation        BIGINT,
    is_active               BOOLEAN DEFAULT TRUE,
    metadata                JSONB DEFAULT '{}',
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_company_ticker ON company(ticker);
CREATE INDEX idx_company_name_trgm ON company USING gin(name gin_trgm_ops);
CREATE INDEX idx_company_sector ON company(sector_id);
CREATE INDEX idx_company_type ON company(company_type);

CREATE TABLE company_tag (
    company_id  INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    tag_id      INTEGER NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
    PRIMARY KEY (company_id, tag_id)
);

CREATE TABLE company_fundamentals (
    id                  SERIAL PRIMARY KEY,
    company_id          INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    period_end          DATE NOT NULL,
    period_type         VARCHAR(10) DEFAULT 'quarterly',
    revenue             BIGINT,
    net_income          BIGINT,
    ebitda              BIGINT,
    gross_margin        NUMERIC(5,4),
    operating_margin    NUMERIC(5,4),
    net_margin          NUMERIC(5,4),
    pe_ratio            NUMERIC(10,2),
    price_to_sales      NUMERIC(10,2),
    price_to_book       NUMERIC(10,2),
    ev_to_ebitda        NUMERIC(10,2),
    debt_to_equity      NUMERIC(10,2),
    current_ratio       NUMERIC(10,2),
    quick_ratio         NUMERIC(10,2),
    interest_coverage   NUMERIC(10,2),
    free_cash_flow      BIGINT,
    cash_and_equivalents BIGINT,
    total_debt          BIGINT,
    shares_outstanding  BIGINT,
    dividend_yield      NUMERIC(5,4),
    payout_ratio        NUMERIC(5,4),
    roe                 NUMERIC(5,4),
    roa                 NUMERIC(5,4),
    revenue_growth_yoy  NUMERIC(5,4),
    earnings_growth_yoy NUMERIC(5,4),
    cash_runway_months  INTEGER,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id, period_end, period_type)
);
CREATE INDEX idx_fundamentals_company ON company_fundamentals(company_id, period_end DESC);

CREATE TABLE competitor_relationship (
    id                  SERIAL PRIMARY KEY,
    company_id          INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    competitor_id       INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    overlap_score       NUMERIC(3,2) CHECK (overlap_score BETWEEN 0 AND 1),
    relationship_type   VARCHAR(30),
    category            VARCHAR(50),
    source              VARCHAR(50),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id, competitor_id)
);

-- Price history (TimescaleDB hypertable candidate)
CREATE TABLE price_history (
    id          BIGSERIAL PRIMARY KEY,
    company_id  INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    timestamp   TIMESTAMPTZ NOT NULL,
    open        NUMERIC(12,4),
    high        NUMERIC(12,4),
    low         NUMERIC(12,4),
    close       NUMERIC(12,4) NOT NULL,
    volume      BIGINT,
    adjusted_close NUMERIC(12,4)
);
CREATE INDEX idx_price_company_time ON price_history(company_id, timestamp DESC);

-- ═══════════════════════════════════════════════════════════════
-- 4. INVESTORS & FUNDING ROUNDS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE investor (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(255) NOT NULL,
    slug                VARCHAR(255) UNIQUE,
    type                VARCHAR(30) NOT NULL DEFAULT 'vc',
    website_url         TEXT,
    logo_url            TEXT,
    description         TEXT,
    headquarters_city   VARCHAR(100),
    headquarters_country VARCHAR(100),
    founded_year        INTEGER,
    aum_usd             BIGINT,
    total_investments   INTEGER DEFAULT 0,
    notable_exits       JSONB DEFAULT '[]',
    focus_sectors       JSONB DEFAULT '[]',
    focus_stages        JSONB DEFAULT '[]',
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_investor_name_trgm ON investor USING gin(name gin_trgm_ops);

CREATE TABLE funding_round (
    id                  SERIAL PRIMARY KEY,
    company_id          INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    round_name          VARCHAR(100),
    stage               funding_stage,
    amount_usd          BIGINT,
    pre_money_valuation BIGINT,
    post_money_valuation BIGINT,
    announced_date      DATE,
    closed_date         DATE,
    lead_investor_id    INTEGER REFERENCES investor(id),
    is_confirmed        BOOLEAN DEFAULT TRUE,
    source_url          TEXT,
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_funding_company ON funding_round(company_id, announced_date DESC);

CREATE TABLE funding_round_investor (
    id              SERIAL PRIMARY KEY,
    funding_round_id INTEGER NOT NULL REFERENCES funding_round(id) ON DELETE CASCADE,
    investor_id     INTEGER NOT NULL REFERENCES investor(id) ON DELETE CASCADE,
    is_lead         BOOLEAN DEFAULT FALSE,
    amount_usd      BIGINT,
    UNIQUE(funding_round_id, investor_id)
);

-- ═══════════════════════════════════════════════════════════════
-- 5. PORTFOLIOS & TRADING
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE portfolio (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    name            VARCHAR(100) DEFAULT 'My Portfolio',
    initial_capital NUMERIC(12,2) DEFAULT 10000.00,
    cash            NUMERIC(12,2) DEFAULT 10000.00,
    currency        VARCHAR(3) DEFAULT 'USD',
    is_default      BOOLEAN DEFAULT TRUE,
    strategy_notes  TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_portfolio_user ON portfolio(user_id);

CREATE TABLE holding (
    id              SERIAL PRIMARY KEY,
    portfolio_id    INTEGER NOT NULL REFERENCES portfolio(id) ON DELETE CASCADE,
    company_id      INTEGER NOT NULL REFERENCES company(id),
    shares          NUMERIC(12,4) NOT NULL CHECK (shares > 0),
    avg_buy_price   NUMERIC(12,4) NOT NULL,
    current_price   NUMERIC(12,4),
    unrealized_pnl  NUMERIC(12,2),
    unrealized_pnl_pct NUMERIC(8,4),
    weight_pct      NUMERIC(5,2),
    first_bought_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(portfolio_id, company_id)
);
CREATE INDEX idx_holding_portfolio ON holding(portfolio_id);

CREATE TABLE trade (
    id              SERIAL PRIMARY KEY,
    portfolio_id    INTEGER NOT NULL REFERENCES portfolio(id) ON DELETE CASCADE,
    company_id      INTEGER NOT NULL REFERENCES company(id),
    order_type      order_type DEFAULT 'market',
    side            order_side NOT NULL,
    status          order_status DEFAULT 'filled',
    shares          NUMERIC(12,4) NOT NULL,
    price           NUMERIC(12,4) NOT NULL,
    total_amount    NUMERIC(14,2) NOT NULL,
    limit_price     NUMERIC(12,4),
    stop_price      NUMERIC(12,4),
    risk_flags_at_trade JSONB DEFAULT '[]',
    risk_acknowledged BOOLEAN DEFAULT FALSE,
    executed_at     TIMESTAMPTZ DEFAULT NOW(),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_trade_portfolio ON trade(portfolio_id, executed_at DESC);

-- ═══════════════════════════════════════════════════════════════
-- 6. WATCHLISTS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE watchlist (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    is_default  BOOLEAN DEFAULT FALSE,
    color       VARCHAR(7),
    sort_order  INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_watchlist_user ON watchlist(user_id);

CREATE TABLE watchlist_item (
    id              SERIAL PRIMARY KEY,
    watchlist_id    INTEGER NOT NULL REFERENCES watchlist(id) ON DELETE CASCADE,
    company_id      INTEGER NOT NULL REFERENCES company(id),
    notes           TEXT,
    target_price    NUMERIC(12,4),
    alert_above     NUMERIC(12,4),
    alert_below     NUMERIC(12,4),
    added_at        TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(watchlist_id, company_id)
);

-- ═══════════════════════════════════════════════════════════════
-- 7. RISK FLAGS & COMPOSITE SCORES
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE risk_flag (
    id              SERIAL PRIMARY KEY,
    company_id      INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    flag_type       VARCHAR(50) NOT NULL,
    title           VARCHAR(200),
    severity        VARCHAR(10) NOT NULL DEFAULT 'medium',
    severity_score  INTEGER CHECK (severity_score BETWEEN 0 AND 100),
    description     TEXT,
    ai_explanation  TEXT,
    data_sources    JSONB DEFAULT '[]',
    raw_data        JSONB DEFAULT '{}',
    is_active       BOOLEAN DEFAULT TRUE,
    expires_at      TIMESTAMPTZ,
    calculated_at   TIMESTAMPTZ DEFAULT NOW(),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_risk_flag_company ON risk_flag(company_id, is_active);
CREATE INDEX idx_risk_flag_type ON risk_flag(flag_type);

CREATE TABLE composite_risk_score (
    id                  SERIAL PRIMARY KEY,
    company_id          INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    overall_score       INTEGER CHECK (overall_score BETWEEN 0 AND 100),
    volatility_score    INTEGER,
    valuation_score     INTEGER,
    momentum_score      INTEGER,
    financial_score     INTEGER,
    insider_score       INTEGER,
    sentiment_score     INTEGER,
    components          JSONB DEFAULT '{}',
    calculated_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id)
);

-- ═══════════════════════════════════════════════════════════════
-- 8. ALERTS & NOTIFICATIONS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE alert (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    company_id      INTEGER REFERENCES company(id),
    alert_type      alert_type NOT NULL,
    condition_value NUMERIC(12,4),
    condition_json  JSONB DEFAULT '{}',
    is_active       BOOLEAN DEFAULT TRUE,
    is_triggered    BOOLEAN DEFAULT FALSE,
    triggered_at    TIMESTAMPTZ,
    title           VARCHAR(200),
    message         TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_alert_user_active ON alert(user_id, is_active);

CREATE TABLE notification (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    alert_id    INTEGER REFERENCES alert(id),
    channel     notification_channel DEFAULT 'in_app',
    title       VARCHAR(255) NOT NULL,
    body        TEXT,
    action_url  TEXT,
    is_read     BOOLEAN DEFAULT FALSE,
    read_at     TIMESTAMPTZ,
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_notification_user_unread ON notification(user_id, is_read, created_at DESC);

-- ═══════════════════════════════════════════════════════════════
-- 9. NEWS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE news_article (
    id              SERIAL PRIMARY KEY,
    title           TEXT NOT NULL,
    summary         TEXT,
    content         TEXT,
    source_name     VARCHAR(100),
    source_url      TEXT,
    author          VARCHAR(200),
    published_at    TIMESTAMPTZ,
    category        VARCHAR(50),
    sentiment_label sentiment_label,
    sentiment_score NUMERIC(4,3),
    relevance_score NUMERIC(4,3),
    is_breaking     BOOLEAN DEFAULT FALSE,
    image_url       TEXT,
    external_id     VARCHAR(255) UNIQUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_news_published ON news_article(published_at DESC);
CREATE INDEX idx_news_sentiment ON news_article(sentiment_label);
CREATE INDEX idx_news_title_trgm ON news_article USING gin(title gin_trgm_ops);

CREATE TABLE news_company (
    news_id     INTEGER NOT NULL REFERENCES news_article(id) ON DELETE CASCADE,
    company_id  INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    relevance   NUMERIC(3,2) DEFAULT 1.0,
    PRIMARY KEY (news_id, company_id)
);

CREATE TABLE news_sector (
    news_id     INTEGER NOT NULL REFERENCES news_article(id) ON DELETE CASCADE,
    sector_id   INTEGER NOT NULL REFERENCES sector(id) ON DELETE CASCADE,
    PRIMARY KEY (news_id, sector_id)
);

-- ═══════════════════════════════════════════════════════════════
-- 10. AI PROMPTS & RESPONSES
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE ai_prompt_template (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    category        VARCHAR(50) NOT NULL,
    system_prompt   TEXT NOT NULL,
    user_template   TEXT,
    model           VARCHAR(50) DEFAULT 'claude-sonnet-4-20250514',
    temperature     NUMERIC(3,2) DEFAULT 0.3,
    max_tokens      INTEGER DEFAULT 2000,
    is_active       BOOLEAN DEFAULT TRUE,
    version         INTEGER DEFAULT 1,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ai_conversation (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title           VARCHAR(255),
    context_type    VARCHAR(50),
    context_id      INTEGER,
    model_used      VARCHAR(50),
    total_tokens    INTEGER DEFAULT 0,
    is_archived     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_ai_conversation_user ON ai_conversation(user_id, created_at DESC);

CREATE TABLE ai_message (
    id                  SERIAL PRIMARY KEY,
    conversation_id     INTEGER NOT NULL REFERENCES ai_conversation(id) ON DELETE CASCADE,
    role                ai_role NOT NULL,
    content             TEXT NOT NULL,
    tokens_used         INTEGER,
    model               VARCHAR(50),
    metadata            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_ai_message_conv ON ai_message(conversation_id, created_at);

CREATE TABLE ai_research_report (
    id              SERIAL PRIMARY KEY,
    company_id      INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    user_id         INTEGER REFERENCES "user"(id),
    report_type     VARCHAR(50) DEFAULT 'full_analysis',
    summary         TEXT,
    opportunities   JSONB DEFAULT '[]',
    risks           JSONB DEFAULT '[]',
    financial_health JSONB DEFAULT '{}',
    competitive_position JSONB DEFAULT '{}',
    ipo_probability NUMERIC(3,2),
    overall_rating  VARCHAR(20),
    confidence_score NUMERIC(3,2),
    model_used      VARCHAR(50),
    tokens_used     INTEGER,
    is_stale        BOOLEAN DEFAULT FALSE,
    generated_at    TIMESTAMPTZ DEFAULT NOW(),
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_ai_report_company ON ai_research_report(company_id, generated_at DESC);

CREATE TABLE ai_portfolio_advice (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    portfolio_id        INTEGER REFERENCES portfolio(id),
    diversification_score INTEGER,
    concentration_risk  JSONB DEFAULT '{}',
    missing_sectors     JSONB DEFAULT '[]',
    suggestions         JSONB DEFAULT '[]',
    overall_health      INTEGER,
    analysis_summary    TEXT,
    model_used          VARCHAR(50),
    generated_at        TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_ai_advice_user ON ai_portfolio_advice(user_id, generated_at DESC);

-- ═══════════════════════════════════════════════════════════════
-- 11. API KEYS & USAGE LOGGING
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE api_key (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    key_hash        VARCHAR(255) NOT NULL UNIQUE,
    key_prefix      VARCHAR(10) NOT NULL,
    name            VARCHAR(100),
    scopes          JSONB DEFAULT '["read"]',
    rate_limit      INTEGER DEFAULT 100,
    is_active       BOOLEAN DEFAULT TRUE,
    last_used_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_api_key_hash ON api_key(key_hash);

CREATE TABLE api_usage_log (
    id          BIGSERIAL PRIMARY KEY,
    api_key_id  INTEGER REFERENCES api_key(id),
    user_id     INTEGER REFERENCES "user"(id),
    endpoint    VARCHAR(255) NOT NULL,
    method      VARCHAR(10) NOT NULL,
    status_code INTEGER,
    latency_ms  INTEGER,
    ip_address  VARCHAR(45),
    user_agent  TEXT,
    request_body_size INTEGER,
    response_body_size INTEGER,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_usage_log_key ON api_usage_log(api_key_id, created_at DESC);
CREATE INDEX idx_usage_log_user ON api_usage_log(user_id, created_at DESC);

-- ═══════════════════════════════════════════════════════════════
-- 12. LEARNING MODULES
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE learning_module (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    slug            VARCHAR(200) NOT NULL UNIQUE,
    description     TEXT,
    tier_required   risk_tier DEFAULT 'beginner',
    category        VARCHAR(50),
    duration_minutes INTEGER,
    content_type    VARCHAR(30) DEFAULT 'lesson',
    content_url     TEXT,
    content_json    JSONB,
    quiz_questions  JSONB DEFAULT '[]',
    pass_threshold  INTEGER DEFAULT 80,
    sort_order      INTEGER DEFAULT 0,
    prerequisites   JSONB DEFAULT '[]',
    xp_reward       INTEGER DEFAULT 50,
    is_published    BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_module_progress (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    module_id       INTEGER NOT NULL REFERENCES learning_module(id),
    status          VARCHAR(20) DEFAULT 'not_started',
    score           INTEGER,
    attempts        INTEGER DEFAULT 0,
    time_spent_sec  INTEGER DEFAULT 0,
    completed_at    TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, module_id)
);

-- ═══════════════════════════════════════════════════════════════
-- 13. SOCIAL FEATURES
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE social_post (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    company_id      INTEGER REFERENCES company(id),
    trade_id        INTEGER REFERENCES trade(id),
    content         TEXT NOT NULL,
    reasoning       TEXT,
    thesis_type     VARCHAR(30),
    attachments     JSONB DEFAULT '[]',
    likes_count     INTEGER DEFAULT 0,
    comments_count  INTEGER DEFAULT 0,
    is_flagged      BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_social_post_user ON social_post(user_id, created_at DESC);
CREATE INDEX idx_social_post_company ON social_post(company_id, created_at DESC);

CREATE TABLE social_comment (
    id          SERIAL PRIMARY KEY,
    post_id     INTEGER NOT NULL REFERENCES social_post(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    parent_id   INTEGER REFERENCES social_comment(id),
    content     TEXT NOT NULL,
    is_flagged  BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE social_like (
    id          SERIAL PRIMARY KEY,
    post_id     INTEGER NOT NULL REFERENCES social_post(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(post_id, user_id)
);

-- ═══════════════════════════════════════════════════════════════
-- 14. BACKGROUND JOB TRACKING
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE background_job (
    id              SERIAL PRIMARY KEY,
    job_type        VARCHAR(100) NOT NULL,
    status          VARCHAR(20) DEFAULT 'queued',
    payload         JSONB DEFAULT '{}',
    result          JSONB,
    error_message   TEXT,
    attempts        INTEGER DEFAULT 0,
    max_attempts    INTEGER DEFAULT 3,
    scheduled_at    TIMESTAMPTZ,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_job_status ON background_job(status, scheduled_at);

-- ═══════════════════════════════════════════════════════════════
-- 15. AUDIT LOG
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE audit_log (
    id          BIGSERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES "user"(id),
    action      VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    old_values  JSONB,
    new_values  JSONB,
    ip_address  VARCHAR(45),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_audit_user ON audit_log(user_id, created_at DESC);
CREATE INDEX idx_audit_resource ON audit_log(resource_type, resource_id);

-- ═══════════════════════════════════════════════════════════════
-- TRIGGERS
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_user_updated BEFORE UPDATE ON "user" FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_company_updated BEFORE UPDATE ON company FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_portfolio_updated BEFORE UPDATE ON portfolio FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_watchlist_updated BEFORE UPDATE ON watchlist FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_holding_updated BEFORE UPDATE ON holding FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tr_risk_flag_updated BEFORE UPDATE ON risk_flag FOR EACH ROW EXECUTE FUNCTION update_updated_at();
