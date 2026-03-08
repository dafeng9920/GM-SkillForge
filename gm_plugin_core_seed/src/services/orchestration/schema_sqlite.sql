-- C3 Orchestration 存储层 v1
-- 默认路径：step4/out/mini_db/orchestration.db

-- 会话表
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_hash TEXT,  -- 用户标识（脱敏）
    client_meta_json TEXT  -- 客户端元数据（JSON）
);

-- 轮次表
CREATE TABLE IF NOT EXISTS turns (
    turn_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level_before INTEGER NOT NULL,
    level_after INTEGER NOT NULL,
    turn_json TEXT NOT NULL,  -- OrchestrationTurn 完整 JSON
    policy_summary_json TEXT,  -- policy_checks 摘要
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- 产物表
CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    turn_id TEXT,
    artifact_type TEXT NOT NULL,  -- intent_map/plan/contract/canvas
    summary TEXT,
    content_json TEXT NOT NULL,  -- 产物内容（JSON）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (turn_id) REFERENCES turns(turn_id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_session ON artifacts(session_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_turn ON artifacts(turn_id);

-- Wave 2 replay fields for turns are added via store_sqlite.py migration
