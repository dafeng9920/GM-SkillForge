"""
API 输入验证和清洗工具

APH-004: API 输入验证和清洗 - 防止注入攻击

实现：
- 字符串长度限制
- SQL 注入检测
- XSS 防护
- 敏感词过滤
"""
from __future__ import annotations

import re
import logging
from typing import Any, List, Optional

from pydantic import field_validator, model_validator
from pydantic.types import constr

logger = logging.getLogger(__name__)


# SQL 注入检测模式
SQL_INJECTION_PATTERNS = [
    r"(\bunion\b.*\bselect\b)",
    r"(\bselect\b.*\bfrom\b)",
    r"(\binsert\b.*\binto\b)",
    r"(\bupdate\b.*\bset\b)",
    r"(\bdelete\b.*\bfrom\b)",
    r"(\bdrop\b.*\btable\b)",
    r"(\bexec\b|\bexecute\b)",
    r"(;.*\bexec\b)",
    r"('.*--)",
    r"(/\*.*\*/)",
    r"(\bor\b.*=.*\bor\b)",
    r"(\band\b.*=.*\band\b)",
]

# XSS 检测模式
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",  # onclick=, onload=, etc.
    r"<iframe[^>]*>",
    r"<object[^>]*>",
    r"<embed[^>]*>",
]

# 敏感词列表
SENSITIVE_WORDS = [
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "private_key", "credential", "auth",
]


class SecurityValidator:
    """安全验证器"""

    @classmethod
    def check_sql_injection(cls, value: str) -> bool:
        """
        检测 SQL 注入

        Args:
            value: 待检测字符串

        Returns:
            是否检测到 SQL 注入
        """
        value_lower = value.lower()
        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"[Security] 检测到 SQL 注入: {value[:50]}...")
                return True
        return False

    @classmethod
    def check_xss(cls, value: str) -> bool:
        """
        检测 XSS 攻击

        Args:
            value: 待检测字符串

        Returns:
            是否检测到 XSS
        """
        for pattern in XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"[Security] 检测到 XSS: {value[:50]}...")
                return True
        return False

    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """
        清理字符串输入

        Args:
            value: 待清理字符串
            max_length: 最大长度

        Returns:
            清理后的字符串
        """
        # 截断长度
        if len(value) > max_length:
            logger.warning(f"[Security] 字符串超长，截断到 {max_length}")
            value = value[:max_length]

        # 移除危险字符
        # TODO: 根据实际需求实现

        return value.strip()

    @classmethod
    def validate_field_name(cls, value: str) -> bool:
        """
        验证字段名是否安全（防止敏感词泄露）

        Args:
            value: 字段名

        Returns:
            是否安全
        """
        value_lower = value.lower()
        for word in SENSITIVE_WORDS:
            if word in value_lower:
                logger.warning(f"[Security] 字段名包含敏感词: {value}")
                return False
        return True


# Pydantic 验证器
def validate_safe_string(max_length: int = 1000):
    """
    创建安全字符串验证器

    Args:
        max_length: 最大长度
    """
    @field_validator("*")
    @classmethod
    def validate_string_field(cls, v: Any) -> Any:
        if isinstance(v, str):
            # 检查长度
            if len(v) > max_length:
                raise ValueError(f"字符串长度超过限制 ({max_length})")

            # 检查 SQL 注入
            if SecurityValidator.check_sql_injection(v):
                raise ValueError("检测到潜在的 SQL 注入")

            # 检查 XSS
            if SecurityValidator.check_xss(v):
                raise ValueError("检测到潜在的 XSS 攻击")

        return v
    return validate_string_field


# 常用长度限制
MAX_SHORT_STRING = 100
MAX_MEDIUM_STRING = 500
MAX_LONG_STRING = 2000
MAX_TEXT_LENGTH = 10000
