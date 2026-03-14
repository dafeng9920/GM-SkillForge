"""
统一 CORS 配置中间件

APH-001: 统一 CORS 配置 - 消除 allow_origins=['*'] 安全风险

根据 SKILLFORGE_ENV 环境变量动态设置允许来源：
- production: 从配置读取允许的来源列表
- development: 允许本地开发来源
- test: 允许测试服务器
- 未知/默认: 空列表（fail-closed）
"""
from __future__ import annotations

import logging
import os
from typing import List

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

logger = logging.getLogger(__name__)


# 环境对应的允许来源配置
ENV_ORIGINS = {
    "production": [
        # 生产环境来源 - 需要从配置文件读取
        # 示例：["https://skillforge.example.com"]
    ],
    "development": [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    "test": [
        "http://test-server.example.com",
    ],
}


def get_allowed_origins() -> List[str]:
    """
    根据环境变量获取允许的来源列表

    Returns:
        允许的来源列表，未知环境返回空列表（fail-closed）
    """
    env = os.getenv("SKILLFORGE_ENV", "").lower()

    allowed = ENV_ORIGINS.get(env, [])

    # 从环境变量读取额外的允许来源
    additional_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if additional_origins:
        additional = [origin.strip() for origin in additional_origins.split(",") if origin.strip()]
        allowed.extend(additional)

    # 如果环境未知且没有配置来源，记录警告
    if not allowed:
        logger.warning(
            f"[CORS] SKILLFORGE_ENV='{env}' 未配置允许来源，使用 fail-closed 策略（空列表）"
        )
        logger.warning(
            f"[CORS] 请设置 CORS_ALLOWED_ORIGINS 环境变量或在 ENV_ORIGINS 中配置 '{env}' 环境"
        )

    return allowed


def setup_cors(app: FastAPI) -> None:
    """
    为 FastAPI 应用配置统一 CORS 中间件

    Args:
        app: FastAPI 应用实例
    """
    allowed_origins = get_allowed_origins()

    logger.info(f"[CORS] 配置允许来源: {allowed_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-RateLimit-Remaining"],
        max_age=600,  # 10 分钟预检缓存
    )


# 启动时验证
def validate_cors_config() -> bool:
    """
    验证 CORS 配置是否有效

    Returns:
        配置是否有效
    """
    env = os.getenv("SKILLFORGE_ENV", "").lower()

    if env == "production":
        allowed = get_allowed_origins()
        if not allowed:
            logger.error("[CORS] 生产环境必须配置允许来源！")
            return False
        logger.info(f"[CORS] 生产环境配置了 {len(allowed)} 个允许来源")

    return True
