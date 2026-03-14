"""
统一 API 认证中间件

APH-002: 添加统一 API 认证中间件

实现 API Key 认证，配置公共 endpoint 白名单，添加认证失败审计日志。
"""
from __future__ import annotations

import logging
import os
from typing import Callable, List, Optional

from fastapi import FastAPI, Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# 公共 endpoint 白名单（不需要认证）
PUBLIC_ENDPOINTS = {
    "/health",
    "/api/v1/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """API 认证中间件"""

    def __init__(
        self,
        app: FastAPI,
        public_endpoints: set | None = None,
        api_key_header: str = "X-API-Key",
        require_auth: bool = True,
    ):
        super().__init__(app)
        self.public_endpoints = public_endpoints or PUBLIC_ENDPOINTS
        self.api_key_header = api_key_header
        self.require_auth = require_auth

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并进行认证检查"""
        # 跳过公共 endpoint
        if request.url.path in self.public_endpoints:
            return await call_next(request)

        # 跳过 OPTIONS 预检请求
        if request.method == "OPTIONS":
            return await call_next(request)

        # 如果不要求认证，直接放行（开发模式）
        if not self.require_auth:
            return await call_next(request)

        # 检查 API Key
        api_key = request.headers.get(self.api_key_header)

        if not api_key:
            # 认证失败：缺少 API Key
            await self._log_auth_failure(request, "missing_api_key")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key",
                headers={"WWW-Authenticate": f'ApiKey realm="API"'},
            )

        # 验证 API Key
        if not await self._validate_api_key(api_key):
            # 认证失败：无效 API Key
            await self._log_auth_failure(request, "invalid_api_key", api_key=api_key)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": f'ApiKey realm="API" error="invalid_key"'},
            )

        # 认证成功，记录日志
        await self._log_auth_success(request, api_key)

        # 将 API Key 添加到请求状态（供后续使用）
        request.state.api_key = api_key

        return await call_next(request)

    async def _validate_api_key(self, api_key: str) -> bool:
        """
        验证 API Key 是否有效

        Args:
            api_key: API Key

        Returns:
            是否有效
        """
        # TODO: 实现 API Key 验证逻辑
        # 1. 检查 API Key 格式
        # 2. 查询数据库或缓存
        # 3. 检查是否被撤销或过期

        # 临时实现：接受任何非空 key（生产环境必须修改）
        return bool(api_key and len(api_key) >= 16)

    async def _log_auth_success(self, request: Request, api_key: str) -> None:
        """记录认证成功日志"""
        logger.info(
            f"[Auth] API Key 认证成功: "
            f"path={request.url.path}, "
            f"method={request.method}, "
            f"api_key_prefix={api_key[:8]}..."
        )

    async def _log_auth_failure(
        self, request: Request, reason: str, api_key: Optional[str] = None
    ) -> None:
        """记录认证失败日志"""
        logger.warning(
            f"[Auth] API Key 认证失败: "
            f"path={request.url.path}, "
            f"method={request.method}, "
            f"reason={reason}, "
            f"client={request.client.host if request.client else 'unknown'}"
        )


def setup_auth_middleware(
    app: FastAPI,
    public_endpoints: set | None = None,
    require_auth: bool | None = None,
) -> None:
    """
    为 FastAPI 应用配置认证中间件

    Args:
        app: FastAPI 应用实例
        public_endpoints: 公共 endpoint 白名单
        require_auth: 是否要求认证（None 则根据环境变量决定）
    """
    # 从环境变量读取是否要求认证
    if require_auth is None:
        env = os.getenv("SKILLFORGE_ENV", "development").lower()
        require_auth = (env == "production")

    logger.info(f"[Auth] 配置认证中间件: require_auth={require_auth}")

    app.add_middleware(
        AuthMiddleware,
        public_endpoints=public_endpoints,
        require_auth=require_auth,
    )
