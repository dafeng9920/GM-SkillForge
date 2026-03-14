"""
速率限制中间件

APH-003: 实现速率限制和防护

实现基于 IP 和 API Key 的速率限制，防止 DDoS 和滥用。
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Callable, Optional, Dict

from fastapi import FastAPI, Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# 速率限制配置（默认值）
RATE_LIMIT_CONFIG = {
    # 全局限制（按 IP）
    "global": {
        "requests": 100,  # 100 请求
        "window": 60,     # 60 秒
    },
    # API Key 限制
    "api_key": {
        "requests": 1000,
        "window": 60,
    },
    # 特殊 endpoint 限制
    "/api/v1/cognition/generate": {
        "requests": 10,
        "window": 60,
    },
}


class RateLimiter:
    """内存速率限制器（生产环境应使用 Redis）"""

    def __init__(self):
        # {key: [(timestamp, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)

    def is_allowed(
        self,
        key: str,
        max_requests: int,
        window: int,
    ) -> tuple[bool, dict]:
        """
        检查是否允许请求

        Args:
            key: 限制键（IP 或 API Key）
            max_requests: 最大请求数
            window: 时间窗口（秒）

        Returns:
            (是否允许, 限制信息)
        """
        now = time.time()
        window_start = now - window

        # 清理过期记录
        self._requests[key] = [
            (ts, count) for ts, count in self._requests[key]
            if ts > window_start
        ]

        # 计算当前窗口内的请求数
        current_count = sum(count for _, count in self._requests[key])

        if current_count >= max_requests:
            # 超出限制
            reset_time = int(window_start + window)
            return False, {
                "allowed": False,
                "limit": max_requests,
                "remaining": 0,
                "reset": reset_time,
            }

        # 记录本次请求
        self._requests[key].append((now, 1))

        return True, {
            "allowed": True,
            "limit": max_requests,
            "remaining": max_requests - current_count - 1,
            "reset": int(now + window),
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件"""

    def __init__(
        self,
        app: FastAPI,
        rate_limiter: RateLimiter | None = None,
        config: dict | None = None,
    ):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.config = config or RATE_LIMIT_CONFIG

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并进行速率限制检查"""
        # 获取限制键（优先使用 API Key，否则使用 IP）
        api_key = getattr(request.state, "api_key", None)
        if api_key:
            limit_key = f"apikey:{api_key[:8]}"  # 只使用前缀
            config_key = "api_key"
        else:
            client_host = request.client.host if request.client else "unknown"
            limit_key = f"ip:{client_host}"
            config_key = "global"

        # 检查特定 endpoint 的限制
        path_config = self.config.get(request.url.path)
        if path_config:
            max_requests = path_config["requests"]
            window = path_config["window"]
        else:
            config = self.config.get(config_key, self.config["global"])
            max_requests = config["requests"]
            window = config["window"]

        # 检查是否允许
        allowed, info = self.rate_limiter.is_allowed(limit_key, max_requests, window)

        # 添加速率限制响应头
        response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])

        if not allowed:
            # 超出限制，记录日志
            logger.warning(
                f"[RateLimit] 速率限制触发: "
                f"key={limit_key}, "
                f"path={request.url.path}, "
                f"limit={max_requests}/{window}s"
            )

            # 返回 429 状态码
            response.status_code = status.HTTP_429_TOO_MANY_REQUESTS

        return response


def setup_rate_limiting(
    app: FastAPI,
    config: dict | None = None,
) -> RateLimitMiddleware:
    """
    为 FastAPI 应用配置速率限制中间件

    Args:
        app: FastAPI 应用实例
        config: 速率限制配置

    Returns:
        速率限制器实例（可用于监控和清理）
    """
    logger.info("[RateLimit] 配置速率限制中间件")

    middleware = RateLimitMiddleware(app, config=config)
    app.add_middleware(RateLimitMiddleware, config=config)

    return middleware
