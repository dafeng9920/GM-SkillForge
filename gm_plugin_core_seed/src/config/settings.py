"""
GMOS 配置中心
所有 env 读取必须通过此处
"""
import os
from typing import Optional


class Settings:
    """配置类"""

    # ==================== Beidou ====================
    BEIDOU_ENABLED: bool = os.getenv("GM_OS_BEIDOU_ENABLED", "0") == "1"
    BEIDOU_STORE: str = os.getenv("GM_OS_BEIDOU_STORE", "inmem")
    BEIDOU_STORE_TYPE: str = os.getenv("BEIDOU_STORE_TYPE", "redis")

    # ==================== Tasks ====================
    TASKS_ENABLED: bool = os.getenv("GM_OS_TASKS_ENABLED", "0") == "1"
    TASKS_DB: str = os.getenv("GM_OS_TASKS_DB", "step4/out/tasks.db")
    TASKS_STORE_TYPE: str = os.getenv("GM_OS_TASKS_STORE_TYPE", "sqlite")

    # ==================== Concurrency Guard ====================
    CONCURRENCY_GUARD_ENABLED: bool = os.getenv("GM_OS_CONCURRENCY_GUARD_ENABLED", "0") == "1"

    # ==================== Replay ====================
    REPLAY_ENABLED: bool = os.getenv("GM_OS_REPLAY_ENABLED", "0") == "1"
    REPLAY_STORE_DIR: str = os.getenv("GM_OS_REPLAY_STORE_DIR", "step4/out/replays")

    # ==================== CORS ====================
    CORS_ALLOWED_ORIGINS: str = os.getenv("CORS_ALLOWED_ORIGINS", "")

    # ==================== Gateway ====================
    GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
    GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8000"))
    INNER_GATEWAY_PORT: int = int(os.getenv("INNER_GATEWAY_PORT", "4002"))

    # ==================== UI ====================
    UI_ENABLED: bool = os.getenv("GM_OS_UI_ENABLED", "0") == "1"

    # ==================== Light ====================
    LIGHT_ENABLED: bool = os.getenv("GM_OS_LIGHT_ENABLED", "0") == "1"

    # ==================== Guard ====================
    GUARD_ENABLED: bool = os.getenv("GM_OS_GUARD_ENABLED", "0") == "1"

    # ==================== WAVE15: ALG3D 配置 ====================
    GM_OS_RAG_FUSION_STRATEGY: str = os.getenv("GM_OS_RAG_FUSION_STRATEGY", "COMPOSITE")
    GM_OS_RAG_TIME_TRIAD: bool = os.getenv("GM_OS_RAG_TIME_TRIAD", "0") == "1"
    GM_OS_RAG_SEMANTIC_RERANK: bool = os.getenv("GM_OS_RAG_SEMANTIC_RERANK", "0") == "1"
    GM_OS_RAG_HYDE_OVERLAY: bool = os.getenv("GM_OS_RAG_HYDE_OVERLAY", "0") == "1"

    # ==================== WAVE16: Algorithmic Ops 配置 ====================
    GM_OS_RAG_ROLLBACK_DEGRADE_THRESHOLD: int = int(
        os.getenv("GM_OS_RAG_ROLLBACK_DEGRADE_THRESHOLD", "2")
    )
    GM_OS_RAG_ROLLBACK_TOPK_THRESHOLD: float = float(
        os.getenv("GM_OS_RAG_ROLLBACK_TOPK_THRESHOLD", "0.3")
    )
    GM_OS_RAG_ROLLBACK_TIMEOUT_MS: int = int(
        os.getenv("GM_OS_RAG_ROLLBACK_TIMEOUT_MS", "5000")
    )
    GM_OS_RAG_AUTO_ROLLBACK_ENABLED: bool = os.getenv("GM_OS_RAG_AUTO_ROLLBACK_ENABLED", "1") == "1"

    # ==================== WAVE18: Auto-tuning 配置 ====================
    AUTO_TUNE_ENABLED: bool = os.getenv("AUTO_TUNE_ENABLED", "0") == "1"  # 默认关闭
    AUTO_TUNE_LOOKBACK_HOURS: int = int(os.getenv("AUTO_TUNE_LOOKBACK_HOURS", "24"))
    AUTO_TUNE_MIN_SAMPLES: int = int(os.getenv("AUTO_TUNE_MIN_SAMPLES", "30"))
    AUTO_TUNE_MAX_POLICY_CHANGES: int = int(os.getenv("AUTO_TUNE_MAX_POLICY_CHANGES", "2"))
    AUTO_TUNE_REASON_THRESHOLD_TOPK_HIT: float = float(
        os.getenv("AUTO_TUNE_REASON_THRESHOLD_TOPK_HIT", "0.3")
    )



    # ==================== WAVE21: PaperGuardian First-Show Ready Settings ====================
    PAPERGUARDIAN_INTERNAL_BYPASS_ENABLED: bool = os.getenv("PAPERGUARDIAN_INTERNAL_BYPASS_ENABLED", "0") == "1"
    PAPERGUARDIAN_SHARE_TOKEN_DEFAULT_EXPIRY_SEC: int = int(os.getenv("PAPERGUARDIAN_SHARE_TOKEN_DEFAULT_EXPIRY_SEC", "604800"))
    PAPERGUARDIAN_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("PAPERGUARDIAN_RATE_LIMIT_PER_MINUTE", "60"))
    PAPERGUARDIAN_EXPORT_REQUIRE_TOKEN: bool = os.getenv("PAPERGUARDIAN_EXPORT_REQUIRE_TOKEN", "1") == "1"

# 单例
settings = Settings()
