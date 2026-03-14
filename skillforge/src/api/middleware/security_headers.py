"""
安全头配置中间件

APH-009: 安全头配置 - 添加标准安全响应头

实现的安全头：
- Content-Security-Policy (CSP)
- X-Content-Type-Options
- X-Frame-Options
- Strict-Transport-Security (HSTS)
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy
"""
from __future__ import annotations

import logging
import os
from fastapi import FastAPI, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""

    def __init__(self, app: FastAPI, env: str = "production"):
        super().__init__(app)
        self.env = env

    async def dispatch(self, request: Request, call_next) -> Response:
        """处理请求并添加安全头"""
        response = await call_next(request)

        # X-Content-Type-Options: 防止 MIME 类型嗅探
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: 防止点击劫持
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: 启用浏览器 XSS 保护
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: 控制 Referer 信息
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: 控制浏览器功能
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=()"
        )

        # Content-Security-Policy (CSP)
        if self.env == "production":
            # 生产环境：严格的 CSP
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
        else:
            # 开发/测试环境：宽松的 CSP
            response.headers["Content-Security-Policy"] = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https: http:; "
                "connect-src 'self' http: https: ws: wss:;"
            )

        # Strict-Transport-Security (HSTS) - 仅 HTTPS
        if self.env == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


def setup_security_headers(app: FastAPI) -> None:
    """
    为 FastAPI 应用配置安全头中间件

    Args:
        app: FastAPI 应用实例
    """
    env = os.getenv("SKILLFORGE_ENV", "development").lower()

    logger.info(f"[SecurityHeaders] 配置环境: {env}")

    app.add_middleware(SecurityHeadersMiddleware, env=env)
