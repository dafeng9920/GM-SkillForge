"""
Consistency Contract - 一致性契约定义与验证

L4.5 T96: 一致性契约 + 重置语义统一
Job ID: L4P5-UPGRADE-20260222-001
Executor: vs--cc1

契约三要素：
1. invariants (不变量): 必须始终保持为真的断言
2. allowed_changes (允许变化): 可安全变更的字段和范围
3. breaking_change_triggers (重大变更触发条件): 需要特殊处理的变更模式

Fail-closed: 契约验证失败时必须阻断执行，不允许部分放行
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
from abc import ABC, abstractmethod


# ============================================================================
# Constants
# ============================================================================

CONTRACT_VERSION = "v1.0.0-20260224"
DENY_ERROR_CODE = "CONTRACT_VIOLATION"


class ContractViolationSeverity(Enum):
    """契约违规严重级别"""
    WARNING = "WARNING"       # 警告，不阻断
    ERROR = "ERROR"           # 错误，阻断当前操作
    CRITICAL = "CRITICAL"     # 严重，阻断并回滚


class ResetSemantics(Enum):
    """重置语义类型 - 统一定义"""
    ITERATE = "iterate"           # 迭代：增量更新，保留历史
    ROLLBACK_RESET = "rollback_reset"  # 回滚重置：恢复到之前状态
    REBASE_RESET = "rebase_reset"      # 变基重置：基于新基准重建


# ============================================================================
# Invariant Definition (不变量)
# ============================================================================

@dataclass
class Invariant:
    """
    不变量定义 - 必须始终保持为真的断言

    特性：
    - 一旦声明，任何变更不得违反
    - 违反时触发 fail-closed 阻断
    - 支持自定义验证函数
    """
    id: str
    name: str
    description: str
    validator: Optional[Callable[[Dict[str, Any]], bool]] = None
    assertion: str = ""  # 用于序列化的断言表达式
    severity: ContractViolationSeverity = ContractViolationSeverity.CRITICAL

    def validate(self, state: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证不变量是否满足

        Returns:
            (is_valid, error_message)
        """
        if self.validator:
            try:
                result = self.validator(state)
                if result:
                    return True, None
                return False, f"Invariant '{self.name}' violated"
            except Exception as e:
                return False, f"Invariant '{self.name}' validation error: {str(e)}"

        # 如果没有验证器，仅作为文档声明
        return True, None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "assertion": self.assertion,
            "severity": self.severity.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Invariant":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            assertion=data.get("assertion", ""),
            severity=ContractViolationSeverity(data.get("severity", "CRITICAL"))
        )


# ============================================================================
# Allowed Change Definition (允许变化)
# ============================================================================

@dataclass
class AllowedChange:
    """
    允许变化定义 - 可安全变更的字段和范围

    特性：
    - 定义字段级别的变更边界
    - 支持类型约束和值域约束
    - 变更必须在允许范围内
    """
    field_path: str          # 字段路径，支持点分隔符如 "config.max_workers"
    change_type: str         # 变更类型: "any" | "increment" | "set" | "append"
    constraints: Dict[str, Any] = field(default_factory=dict)  # 约束条件
    requires_approval: bool = False  # 是否需要审批

    def validate_change(self, old_value: Any, new_value: Any) -> Tuple[bool, Optional[str]]:
        """
        验证变更是否在允许范围内
        """
        # 检查类型约束
        if "type" in self.constraints:
            expected_type = self.constraints["type"]
            if not isinstance(new_value, eval(expected_type)):
                return False, f"Type mismatch: expected {expected_type}"

        # 检查值域约束
        if "min" in self.constraints and new_value < self.constraints["min"]:
            return False, f"Value below minimum: {self.constraints['min']}"
        if "max" in self.constraints and new_value > self.constraints["max"]:
            return False, f"Value above maximum: {self.constraints['max']}"

        # 检查枚举约束
        if "enum" in self.constraints:
            if new_value not in self.constraints["enum"]:
                return False, f"Value not in allowed enum: {self.constraints['enum']}"

        # 检查增量约束
        if self.change_type == "increment" and "max_delta" in self.constraints:
            delta = abs(new_value - old_value) if isinstance(new_value, (int, float)) else 0
            if delta > self.constraints["max_delta"]:
                return False, f"Delta exceeds maximum: {self.constraints['max_delta']}"

        return True, None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_path": self.field_path,
            "change_type": self.change_type,
            "constraints": self.constraints,
            "requires_approval": self.requires_approval
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AllowedChange":
        return cls(
            field_path=data["field_path"],
            change_type=data.get("change_type", "any"),
            constraints=data.get("constraints", {}),
            requires_approval=data.get("requires_approval", False)
        )


# ============================================================================
# Breaking Change Trigger (重大变更触发条件)
# ============================================================================

@dataclass
class BreakingChangeTrigger:
    """
    重大变更触发条件 - 需要特殊处理的变更模式

    特性：
    - 定义触发重大变更的条件
    - 触发时需要额外验证或审批
    - 可能触发回滚或阻断
    """
    id: str
    name: str
    description: str
    trigger_condition: str   # 触发条件表达式
    required_action: str     # 触发后必须采取的行动
    auto_rollback: bool = False  # 是否自动回滚

    def check_trigger(self, change_context: Dict[str, Any]) -> bool:
        """
        检查是否触发重大变更条件
        """
        # 简化实现：检查关键字段匹配
        # 生产环境应使用安全的表达式求值
        return False  # 默认不触发

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "trigger_condition": self.trigger_condition,
            "required_action": self.required_action,
            "auto_rollback": self.auto_rollback
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BreakingChangeTrigger":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            trigger_condition=data["trigger_condition"],
            required_action=data["required_action"],
            auto_rollback=data.get("auto_rollback", False)
        )


# ============================================================================
# Consistency Contract (一致性契约)
# ============================================================================

@dataclass
class ConsistencyContract:
    """
    一致性契约 - 每次变更必须声明的三要素

    用途：
    - 定义变更边界
    - 确保系统一致性
    - 作为 fail-closed 验证依据

    Fail-closed 策略：
    - 任何不变量违反 -> CRITICAL -> 阻断
    - 任何未声明的变更 -> ERROR -> 阻断
    - 任何重大变更触发 -> 需要额外验证
    """
    contract_id: str
    version: str = CONTRACT_VERSION
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # 契约三要素
    invariants: List[Invariant] = field(default_factory=list)
    allowed_changes: List[AllowedChange] = field(default_factory=list)
    breaking_change_triggers: List[BreakingChangeTrigger] = field(default_factory=list)

    # 元数据
    scope: str = ""  # 契约适用范围
    owner: str = ""  # 契约所有者

    def add_invariant(self, invariant: Invariant) -> None:
        """添加不变量"""
        self.invariants.append(invariant)

    def add_allowed_change(self, change: AllowedChange) -> None:
        """添加允许变化"""
        self.allowed_changes.append(change)

    def add_breaking_change_trigger(self, trigger: BreakingChangeTrigger) -> None:
        """添加重大变更触发条件"""
        self.breaking_change_triggers.append(trigger)

    def validate_state(self, state: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证状态是否满足所有不变量

        Fail-closed: 任何不变量违反即失败
        """
        errors = []

        for invariant in self.invariants:
            is_valid, error = invariant.validate(state)
            if not is_valid:
                errors.append(f"[{invariant.severity.value}] {error}")
                if invariant.severity == ContractViolationSeverity.CRITICAL:
                    return False, errors  # 立即返回

        return len(errors) == 0, errors

    def validate_change(
        self,
        field_path: str,
        old_value: Any,
        new_value: Any
    ) -> Tuple[bool, Optional[str]]:
        """
        验证变更是否被允许

        Fail-closed: 未声明的变更默认拒绝
        """
        # 查找匹配的允许变化规则
        for allowed in self.allowed_changes:
            if allowed.field_path == field_path or allowed.field_path == "*":
                return allowed.validate_change(old_value, new_value)

        # 未找到匹配规则 -> 拒绝
        return False, f"Change to '{field_path}' not declared in allowed_changes"

    def check_breaking_changes(
        self,
        change_context: Dict[str, Any]
    ) -> List[BreakingChangeTrigger]:
        """
        检查是否触发任何重大变更条件
        """
        triggered = []
        for trigger in self.breaking_change_triggers:
            if trigger.check_trigger(change_context):
                triggered.append(trigger)
        return triggered

    def compute_hash(self) -> str:
        """计算契约内容哈希"""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "version": self.version,
            "created_at": self.created_at,
            "scope": self.scope,
            "owner": self.owner,
            "invariants": [i.to_dict() for i in self.invariants],
            "allowed_changes": [c.to_dict() for c in self.allowed_changes],
            "breaking_change_triggers": [t.to_dict() for t in self.breaking_change_triggers]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConsistencyContract":
        return cls(
            contract_id=data["contract_id"],
            version=data.get("version", CONTRACT_VERSION),
            created_at=data.get("created_at", ""),
            scope=data.get("scope", ""),
            owner=data.get("owner", ""),
            invariants=[Invariant.from_dict(i) for i in data.get("invariants", [])],
            allowed_changes=[AllowedChange.from_dict(c) for c in data.get("allowed_changes", [])],
            breaking_change_triggers=[
                BreakingChangeTrigger.from_dict(t) for t in data.get("breaking_change_triggers", [])
            ]
        )


# ============================================================================
# Contract Validator (契约验证器)
# ============================================================================

class ContractViolationError(Exception):
    """契约违反异常 - Fail-closed"""
    code: str = DENY_ERROR_CODE

    def __init__(self, message: str, contract_id: str, violations: List[str]):
        self.message = message
        self.contract_id = contract_id
        self.violations = violations
        super().__init__(self.message)


class ConsistencyContractValidator:
    """
    一致性契约验证器

    Fail-closed 策略实现：
    1. 任何验证失败 -> 抛出 ContractViolationError
    2. 不允许部分通过
    3. 必须提供明确的违规原因
    """

    def __init__(self, contract: ConsistencyContract):
        self.contract = contract

    def validate_before_change(
        self,
        current_state: Dict[str, Any],
        proposed_changes: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        变更前验证

        Returns:
            (can_proceed, violations)
        """
        violations = []

        # 1. 验证当前状态满足所有不变量
        state_valid, state_errors = self.contract.validate_state(current_state)
        if not state_valid:
            violations.extend(state_errors)
            return False, violations  # 当前状态无效，不允许任何变更

        # 2. 验证每个变更是否被允许
        for field_path, (old_val, new_val) in self._extract_changes(
            current_state, proposed_changes
        ).items():
            change_valid, change_error = self.contract.validate_change(
                field_path, old_val, new_val
            )
            if not change_valid:
                violations.append(f"Disallowed change: {change_error}")

        # 3. 检查重大变更触发条件
        triggered = self.contract.check_breaking_changes({
            "current_state": current_state,
            "proposed_changes": proposed_changes
        })
        for trigger in triggered:
            violations.append(
                f"Breaking change triggered: {trigger.name} - Action required: {trigger.required_action}"
            )

        return len(violations) == 0, violations

    def validate_after_change(
        self,
        new_state: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        变更后验证

        Fail-closed: 变更后状态必须满足所有不变量
        """
        return self.contract.validate_state(new_state)

    def _extract_changes(
        self,
        current: Dict[str, Any],
        proposed: Dict[str, Any],
        prefix: str = ""
    ) -> Dict[str, Tuple[Any, Any]]:
        """
        提取变更字段
        """
        changes = {}

        for key, new_val in proposed.items():
            field_path = f"{prefix}.{key}" if prefix else key
            old_val = current.get(key)

            if isinstance(new_val, dict) and isinstance(old_val, dict):
                # 递归处理嵌套字典
                nested_changes = self._extract_changes(old_val, new_val, field_path)
                changes.update(nested_changes)
            elif old_val != new_val:
                changes[field_path] = (old_val, new_val)

        return changes

    def enforce_or_fail(
        self,
        current_state: Dict[str, Any],
        proposed_changes: Dict[str, Any]
    ) -> None:
        """
        强制验证，失败抛出异常

        Fail-closed: 验证失败直接抛出异常，不允许绕过
        """
        can_proceed, violations = self.validate_before_change(
            current_state, proposed_changes
        )

        if not can_proceed:
            raise ContractViolationError(
                message=f"Contract validation failed with {len(violations)} violations",
                contract_id=self.contract.contract_id,
                violations=violations
            )


# ============================================================================
# Export
# ============================================================================

__all__ = [
    # Enums
    "ContractViolationSeverity",
    "ResetSemantics",
    # Data classes
    "Invariant",
    "AllowedChange",
    "BreakingChangeTrigger",
    "ConsistencyContract",
    # Exceptions
    "ContractViolationError",
    # Validators
    "ConsistencyContractValidator",
    # Constants
    "CONTRACT_VERSION",
    "DENY_ERROR_CODE",
]
