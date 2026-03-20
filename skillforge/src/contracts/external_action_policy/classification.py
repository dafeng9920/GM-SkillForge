"""
Action Classification - 动作分类

定义关键动作和非关键动作的分类规则。

Task ID: E4
Executor: Kior-B
Date: 2026-03-19
"""

from enum import Enum
from re import compile
from typing import Literal


class ActionCategory(Enum):
    """动作类别"""
    CRITICAL = "critical"       # 关键动作：产生外部副作用
    NON_CRITICAL = "non_critical"  # 非关键动作：只读操作
    UNKNOWN = "unknown"         # 未知动作


# 关键动作模式列表
CRITICAL_PATTERNS = [
    compile(r"^PUBLISH_"),
    compile(r"^EXECUTE_"),
    compile(r"^EXPORT_"),
    compile(r"^UPGRADE_"),
    compile(r"^REPLACE_"),
    compile(r"^TRIGGER_"),
    compile(r"^WRITE_"),
    compile(r"^MODIFY_"),
    compile(r"^DELETE_"),
    compile(r".*_EXTERNAL_"),
]

# 非关键动作模式列表
NON_CRITICAL_PATTERNS = [
    compile(r"^GET_"),
    compile(r"^READ_"),
    compile(r"^QUERY_"),
    compile(r"^VALIDATE_"),
    compile(r"^CHECK_"),
    compile(r"^VERIFY_"),
    compile(r"^INSPECT_"),
    compile(r"^LIST_"),
    compile(r"^FIND_"),
    compile(r"^SEARCH_"),
]

# 已知关键动作白名单
KNOWN_CRITICAL_ACTIONS = {
    "PUBLISH_LISTING",
    "EXECUTE_VIA_N8N",
    "EXPORT_WHITELIST",
    "UPGRADE_REPLACE_ACTIVE",
    "TRIGGER_EXTERNAL_CONNECTOR",
    "WRITE_EXTERNAL_STATE",
    "MODIFY_EXTERNAL_RESOURCE",
    "DELETE_EXTERNAL_RESOURCE",
}

# 已知非关键动作白名单
KNOWN_NON_CRITICAL_ACTIONS = {
    "GET_SKILL_INFO",
    "READ_SKILL_SPEC",
    "QUERY_STATUS",
    "VALIDATE_INPUT",
    "CHECK_PERMIT",
    "VERIFY_SIGNATURE",
    "INSPECT_LOGS",
    "LIST_SKILLS",
    "FIND_DEPENDENCIES",
    "SEARCH_CACHE",
}


def classify_action(action: str) -> ActionCategory:
    """
    分类动作

    优先级：
    1. 已知白名单（精确匹配）
    2. 关键动作模式
    3. 非关键动作模式
    4. UNKNOWN

    Args:
        action: 动作名称

    Returns:
        动作类别
    """
    # 1. 检查已知关键动作
    if action in KNOWN_CRITICAL_ACTIONS:
        return ActionCategory.CRITICAL

    # 2. 检查已知非关键动作
    if action in KNOWN_NON_CRITICAL_ACTIONS:
        return ActionCategory.NON_CRITICAL

    # 3. 检查关键动作模式
    for pattern in CRITICAL_PATTERNS:
        if pattern.match(action):
            return ActionCategory.CRITICAL

    # 4. 检查非关键动作模式
    for pattern in NON_CRITICAL_PATTERNS:
        if pattern.match(action):
            return ActionCategory.NON_CRITICAL

    # 5. 未知动作
    return ActionCategory.UNKNOWN


def is_critical_action(action: str) -> bool:
    """
    判断是否为关键动作

    Args:
        action: 动作名称

    Returns:
        True if critical
    """
    category = classify_action(action)
    return category == ActionCategory.CRITICAL


def is_non_critical_action(action: str) -> bool:
    """
    判断是否为非关键动作

    Args:
        action: 动作名称

    Returns:
        True if non-critical
    """
    category = classify_action(action)
    return category == ActionCategory.NON_CRITICAL


def get_known_critical_actions() -> set[str]:
    """获取已知关键动作集合"""
    return KNOWN_CRITICAL_ACTIONS.copy()


def get_known_non_critical_actions() -> set[str]:
    """获取已知非关键动作集合"""
    return KNOWN_NON_CRITICAL_ACTIONS.copy()


__all__ = [
    "ActionCategory",
    "classify_action",
    "is_critical_action",
    "is_non_critical_action",
    "get_known_critical_actions",
    "get_known_non_critical_actions",
]
