-- Quant System 元数据库初始化脚本
-- 创建数据库schema、表结构、初始数据

-- ============================================
-- 系统配置表
-- ============================================

CREATE SCHEMA IF NOT EXISTS quant_config;
CREATE SCHEMA IF NOT EXISTS quant_data;
CREATE SCHEMA IF NOT EXISTS quant_audit;

-- ============================================
-- 策略配置表
-- ============================================

CREATE TABLE quant_config.strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    version VARCHAR(20),
    status VARCHAR(20) DEFAULT 'draft',  -- draft, active, archived
    config JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(50)
);

CREATE INDEX idx_strategies_status ON quant_config.strategies(status);
CREATE INDEX idx_strategies_name ON quant_config.strategies(name);

-- ============================================
-- Skill 注册表
-- ============================================

CREATE TABLE quant_config.skills (
    id SERIAL PRIMARY KEY,
    skill_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    version VARCHAR(20),
    module VARCHAR(100),
    layer VARCHAR(50),  -- data, research, portfolio, execution, risk, governance
    status VARCHAR(20) DEFAULT 'active',  -- active, deprecated, experimental
    config_schema JSONB,
    input_contract JSONB,
    output_contract JSONB,
    dependencies TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_skills_layer ON quant_config.skills(layer);
CREATE INDEX idx_skills_status ON quant_config.skills(status);

-- ============================================
-- Gate 规则表
-- ============================================

CREATE TABLE quant_config.gate_rules (
    id SERIAL PRIMARY KEY,
    rule_id VARCHAR(100) UNIQUE NOT NULL,
    level VARCHAR(50) NOT NULL,  -- pre_trade, in_flight, post_trade
    name VARCHAR(200) NOT NULL,
    description TEXT,
    check_expression TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,  -- critical, warning, info
    on_fail VARCHAR(20) NOT NULL,  -- DENY, WARN, ALERT, ALLOW
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_gate_rules_level ON quant_config.gate_rules(level);
CREATE INDEX idx_gate_rules_enabled ON quant_config.gate_rules(enabled);

-- ============================================
-- 用户权限表
-- ============================================

CREATE TABLE quant_config.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'analyst',  -- admin, trader, analyst, viewer
    permissions JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- ============================================
-- 数据表 (quant_data schema)
-- ============================================

-- 市场数据元信息
CREATE TABLE quant_data.market_info (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200),
    type VARCHAR(20),  -- stock, etf, index, futures, crypto
    exchange VARCHAR(20),
    currency VARCHAR(10),
    tick_size NUMERIC,
    lot_size INTEGER,
    trading_hours JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 因子定义
CREATE TABLE quant_data.factors (
    id SERIAL PRIMARY KEY,
    factor_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),  -- value, momentum, quality, volatility
    description TEXT,
    formula TEXT,
    parameters JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 审计日志表 (quant_audit schema)
-- ============================================

-- 交易日志
CREATE TABLE quant_audit.trade_log (
    id BIGSERIAL PRIMARY KEY,
    trade_id VARCHAR(100) UNIQUE NOT NULL,
    strategy_id VARCHAR(100),
    symbol VARCHAR(20),
    direction VARCHAR(10),  -- BUY, SELL
    quantity INTEGER,
    price NUMERIC,
    order_time TIMESTAMPTZ,
    fill_time TIMESTAMPTZ,
    order_type VARCHAR(20),  -- MARKET, LIMIT, STOP
    status VARCHAR(20),  -- PENDING, FILLED, PARTIAL, CANCELLED, REJECTED
    gateway VARCHAR(50),  -- veighna, sim
    execution_venue VARCHAR(50),
    commission NUMERIC,
    slippage NUMERIC,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trade_log_symbol ON quant_audit.trade_log(symbol);
CREATE INDEX idx_trade_log_time ON quant_audit.trade_log(order_time);
CREATE INDEX idx_trade_log_strategy ON quant_audit.trade_log(strategy_id);

-- Gate 决策日志
CREATE TABLE quant_audit.gate_decisions (
    id BIGSERIAL PRIMARY KEY,
    decision_id VARCHAR(100) UNIQUE NOT NULL,
    gate_level VARCHAR(50),  -- pre_trade, in_flight, post_trade
    request_id VARCHAR(100),
    verdict VARCHAR(20),  -- ALLOW, DENY, WARN
    rules_checked TEXT[],
    rules_passed TEXT[],
    rules_failed TEXT[],
    violations JSONB,
    decision_time TIMESTAMPTZ DEFAULT NOW(),
    processing_time_ms INTEGER,
    metadata JSONB
);

CREATE INDEX idx_gate_decisions_time ON quant_audit.gate_decisions(decision_time);
CREATE INDEX idx_gate_decisions_verdict ON quant_audit.gate_decisions(verdict);

-- 风控事件
CREATE TABLE quant_audit.risk_events (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(100) UNIQUE NOT NULL,
    event_type VARCHAR(50),  -- drawdown_breach, position_limit, etc
    severity VARCHAR(20),  -- critical, warning, info
    message TEXT,
    metrics JSONB,
    triggered_rules TEXT[],
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_risk_events_time ON quant_audit.risk_events(triggered_at);
CREATE INDEX idx_risk_events_resolved ON quant_audit.risk_events(resolved);

-- 系统性能指标
CREATE TABLE quant_audit.performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC,
    labels JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_perf_metrics_name ON quant_audit.performance_metrics(metric_name);
CREATE INDEX idx_perf_metrics_time ON quant_audit.performance_metrics(timestamp);

-- ============================================
-- 初始化数据
-- ============================================

-- 插入默认Gate规则
INSERT INTO quant_config.gate_rules (rule_id, level, name, description, check_expression, severity, on_fail) VALUES
-- Pre-trade rules
('POSITION_LIMIT', 'pre_trade', '单标的仓位上限', '单个标的持仓不超过总资金的30%', 'position_size <= total_capital * 0.3', 'critical', 'DENY'),
('DAILY_LOSS_LIMIT', 'pre_trade', '单日亏损上限', '单日亏损不超过总资金的5%', 'daily_pnl >= -total_capital * 0.05', 'critical', 'DENY'),
('DRAWDOWN_LIMIT', 'pre_trade', '最大回撤限制', '当前回撤不超过最大回撤阈值', 'current_drawdown <= max_drawdown', 'critical', 'DENY'),
('LIQUIDITY_CHECK', 'pre_trade', '流动性检查', '订单量不超过日均成交量的5%', 'order_size <= avg_daily_volume * 0.05', 'warning', 'WARN'),
('CONCENTRATION_LIMIT', 'pre_trade', '持仓集中度', '单板块持仓不超过30%', 'single_sector_weight <= 0.3', 'warning', 'WARN'),

-- In-flight rules
('SLIPPAGE_ALERT', 'in_flight', '滑点告警', '实际滑点不超过预期滑点的1.5倍', 'actual_slippage <= expected_slippage * 1.5', 'warning', 'ALERT'),
('EXECUTION_TIMEOUT', 'in_flight', '执行超时', '订单执行不超过最大时间', 'execution_time <= max_execution_time', 'warning', 'ALERT'),

-- Post-trade rules
('AUDIT_TRAIL_COMPLETE', 'post_trade', '审计轨迹完整', '所有交易必须有完整审计链', 'evidence_chain_complete == true', 'critical', 'ALERT_HUMAN'),
('RECONCILIATION', 'post_trade', '持仓对账', '预期持仓与实际持仓一致', 'expected_position == actual_position', 'critical', 'ALERT_HUMAN');

-- 插入系统用户
INSERT INTO quant_config.users (username, email, role, permissions) VALUES
('admin', 'admin@quant.local', 'admin', '{"all": true}'),
('trader', 'trader@quant.local', 'trader', '{"trade": true, "view": true}'),
('analyst', 'analyst@quant.local', 'analyst', '{"view": true, "research": true}'),
('viewer', 'viewer@quant.local', 'viewer', '{"view": true}');

-- ============================================
-- 创建更新时间触发器
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON quant_config.strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON quant_config.skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gate_rules_updated_at BEFORE UPDATE ON quant_config.gate_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 创建视图
-- ============================================

-- 活跃策略视图
CREATE OR REPLACE VIEW quant_config.active_strategies AS
SELECT id, name, version, status, config, created_at, updated_at
FROM quant_config.strategies
WHERE status = 'active';

-- Gate规则统计视图
CREATE OR REPLACE VIEW quant_config.gate_rules_stats AS
SELECT
    level,
    COUNT(*) as total_rules,
    SUM(CASE WHEN enabled THEN 1 ELSE 0 END) as enabled_rules,
    SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_rules
FROM quant_config.gate_rules
GROUP BY level;

-- 今日交易统计视图
CREATE OR REPLACE VIEW quant_audit.today_trade_stats AS
SELECT
    DATE(order_time) as trade_date,
    COUNT(*) as total_trades,
    COUNT(DISTINCT symbol) as symbols_traded,
    SUM(CASE WHEN direction = 'BUY' THEN 1 ELSE 0 END) as buy_trades,
    SUM(CASE WHEN direction = 'SELL' THEN 1 ELSE 0 END) as sell_trades,
    AVG(quantity) as avg_quantity,
    AVG(price) as avg_price
FROM quant_audit.trade_log
GROUP BY DATE(order_time);

-- ============================================
-- 授权
-- ============================================

GRANT ALL PRIVILEGES ON SCHEMA quant_config TO quant_admin;
GRANT ALL PRIVILEGES ON SCHEMA quant_data TO quant_admin;
GRANT ALL PRIVILEGES ON SCHEMA quant_audit TO quant_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA quant_config TO quant_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA quant_data TO quant_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA quant_audit TO quant_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA quant_config TO quant_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA quant_data TO quant_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA quant_audit TO quant_admin;

-- ============================================
-- 完成
-- ============================================

-- 输出初始化完成信息
DO $$
BEGIN
    RAISE NOTICE '===========================================';
    RAISE NOTICE 'Quant System 元数据库初始化完成';
    RAISE NOTICE '===========================================';
    RAISE NOTICE 'Schemas: quant_config, quant_data, quant_audit';
    RAISE NOTICE 'Tables: strategies, skills, gate_rules, users, market_info, factors, trade_log, gate_decisions, risk_events, performance_metrics';
    RAISE NOTICE 'Views: active_strategies, gate_rules_stats, today_trade_stats';
    RAISE NOTICE 'Default users: admin, trader, analyst, viewer';
    RAISE NOTICE 'Default gate rules: 10 rules loaded';
    RAISE NOTICE '===========================================';
END $$;
