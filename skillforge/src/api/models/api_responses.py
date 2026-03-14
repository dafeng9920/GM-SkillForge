"""
API Response Models - 统一的 API 响应格式

APH-007: 统一 API 响应格式
"""
from __future__ import annotations

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field


T = TypeVar("T")


class SuccessEnvelope(BaseModel, Generic[T]):
    """API 成功响应信封"""
    success: bool = True
    data: T
    message: str | None = None
    version: str = "1.0"


class ErrorDetail(BaseModel):
    """错误详情"""
    code: str
    message: str
    field: str | None = None


class ErrorEnvelope(BaseModel):
    """API 错误响应信封"""
    success: bool = False
    error: ErrorDetail
    version: str = "1.0"


class PaginationMeta(BaseModel):
    """分页元数据"""
    total: int
    page: int = 1
    page_size: int = 10
    total_pages: int | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    success: bool = True
    data: list[T]
    meta: PaginationMeta
    version: str = "1.0"


# 常用错误码
class ErrorCode:
    """标准错误码"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INVALID_API_KEY = "INVALID_API_KEY"
