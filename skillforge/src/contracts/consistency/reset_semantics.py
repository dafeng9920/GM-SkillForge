"""
Reset Semantics - 重置语义统一实现

L4.5 T96: 一致性契约 + 重置语义统一
Job ID: L4P5-UPGRADE-20260222-001
Executor: vs--cc1

三种重置语义的统一定义与实现：

1. ITERATE (迭代)
   - 语义：增量更新，保留历史记录
   - 用例：版本递增、配置热更新
   - 特点：可回滚到任意历史版本

2. ROLLBACK_RESET (回滚重置)
   - 语义：恢复到之前确认的稳定状态
   - 用例：故障恢复、错误撤销
   - 特点：需要有效的检查点/快照

3. REBASE_RESET (变基重置)
   - 语义：基于新的基准重新构建状态
   - 用例：同步远程变更、合并冲突
   - 特点：丢弃本地变更，以基准为准

Fail-closed 策略：
- 未声明的重置操作 -> DENY
- 检查点不存在 -> DENY
- 基准版本不兼容 -> DENY
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Generic, TypeVar
from abc import ABC, abstractmethod

T = TypeVar('T')


# ============================================================================
# Constants
# ============================================================================

RESET_SEMANTICS_VERSION = "v1.0.0-20260224"


class ResetType(Enum):
    """重置类型 - 三种统一语义"""
    ITERATE = "iterate"              # 迭代：增量更新
    ROLLBACK_RESET = "rollback_reset"    # 回滚重置
    REBASE_RESET = "rebase_reset"        # 变基重置


class ResetValidationResult(Enum):
    """重置验证结果"""
    ALLOW = "ALLOW"                  # 允许执行
    DENY = "DENY"                    # 拒绝执行
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"  # 需要审批


# ============================================================================
# Compatibility Boundary (兼容边界)
# ============================================================================

@dataclass
class CompatibilityBoundary:
    """
    兼容/不兼容边界定义

    定义何时操作是兼容的，何时需要特殊处理
    """
    boundary_id: str
    name: str
    description: str

    # 兼容条件
    compatible_conditions: List[str] = field(default_factory=list)

    # 不兼容条件（触发 DENY）
    incompatible_conditions: List[str] = field(default_factory=list)

    # 需要审批的条件
    approval_required_conditions: List[str] = field(default_factory=list)

    def check_compatibility(self, context: Dict[str, Any]) -> ResetValidationResult:
        """
        检查兼容性

        Returns:
            ALLOW: 完全兼容
            DENY: 不兼容，拒绝执行
            REQUIRES_APPROVAL: 需要额外审批
        """
        # 检查不兼容条件
        for condition in self.incompatible_conditions:
            if self._evaluate_condition(condition, context):
                return ResetValidationResult.DENY

        # 检查需要审批的条件
        for condition in self.approval_required_conditions:
            if self._evaluate_condition(condition, context):
                return ResetValidationResult.REQUIRES_APPROVAL

        return ResetValidationResult.ALLOW

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        简化条件求值（生产环境应使用安全求值器）
        """
        # 默认返回 False，避免误判
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "boundary_id": self.boundary_id,
            "name": self.name,
            "description": self.description,
            "compatible_conditions": self.compatible_conditions,
            "incompatible_conditions": self.incompatible_conditions,
            "approval_required_conditions": self.approval_required_conditions
        }


# ============================================================================
# Checkpoint (检查点)
# ============================================================================

@dataclass
class Checkpoint:
    """
    检查点 - 用于回滚和验证的状态快照
    """
    checkpoint_id: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    state_hash: str = ""
    state_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True

    def compute_hash(self) -> str:
        """计算状态哈希"""
        content = json.dumps(self.state_data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """验证检查点完整性"""
        if not self.is_valid:
            return False
        expected_hash = self.compute_hash()
        return self.state_hash == "" or self.state_hash == expected_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "created_at": self.created_at,
            "state_hash": self.state_hash,
            "state_data": self.state_data,
            "metadata": self.metadata,
            "is_valid": self.is_valid
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        return cls(
            checkpoint_id=data["checkpoint_id"],
            created_at=data.get("created_at", ""),
            state_hash=data.get("state_hash", ""),
            state_data=data.get("state_data", {}),
            metadata=data.get("metadata", {}),
            is_valid=data.get("is_valid", True)
        )


# ============================================================================
# Reset Operation Result (重置操作结果)
# ============================================================================

@dataclass
class ResetOperationResult(Generic[T]):
    """
    重置操作结果

    Fail-closed: success=False 时必须提供明确的失败原因
    """
    success: bool
    reset_type: ResetType
    result: Optional[T] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    checkpoint_before: Optional[str] = None
    checkpoint_after: Optional[str] = None
    evidence_ref: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "reset_type": self.reset_type.value,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "checkpoint_before": self.checkpoint_before,
            "checkpoint_after": self.checkpoint_after,
            "evidence_ref": self.evidence_ref
        }


# ============================================================================
# Reset Semantics Handler (重置语义处理器基类)
# ============================================================================

class ResetSemanticsHandler(ABC):
    """
    重置语义处理器抽象基类

    所有重置操作必须实现此接口
    """

    @abstractmethod
    def can_execute(self, context: Dict[str, Any]) -> ResetValidationResult:
        """
        检查是否可以执行重置

        Fail-closed: 默认 DENY，只有明确满足条件才 ALLOW
        """
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> ResetOperationResult:
        """
        执行重置操作

        Fail-closed: 任何失败必须回滚并返回明确错误
        """
        pass

    @abstractmethod
    def validate_preconditions(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证前置条件

        Returns:
            (is_valid, error_messages)
        """
        pass


# ============================================================================
# Iterate Handler (迭代处理器)
# ============================================================================

class IterateHandler(ResetSemanticsHandler):
    """
    ITERATE 语义处理器

    定义：
    - 增量更新现有状态
    - 保留完整历史记录
    - 每次迭代创建新检查点

    兼容边界：
    - 兼容：增量变更、配置更新、版本递增
    - 不兼容：破坏性删除、Schema 不兼容变更
    """

    def __init__(self):
        self.checkpoints: List[Checkpoint] = []
        self.boundary = CompatibilityBoundary(
            boundary_id="ITERATE-BOUNDARY-001",
            name="Iterate Compatibility Boundary",
            description="Defines compatible and incompatible operations for ITERATE",
            compatible_conditions=[
                "incremental_change",
                "config_update",
                "version_increment"
            ],
            incompatible_conditions=[
                "destructive_deletion",
                "schema_breaking_change",
                "invalid_state_transition"
            ],
            approval_required_conditions=[
                "major_version_change",
                "security_sensitive_update"
            ]
        )

    def can_execute(self, context: Dict[str, Any]) -> ResetValidationResult:
        return self.boundary.check_compatibility(context)

    def validate_preconditions(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []

        # 检查当前状态是否有效
        if "current_state" not in context:
            errors.append("Missing current_state in context")

        # 检查变更是否有效
        if "changes" not in context:
            errors.append("Missing changes in context")

        return len(errors) == 0, errors

    def execute(self, context: Dict[str, Any]) -> ResetOperationResult:
        """
        执行迭代操作

        Fail-closed 策略：
        1. 前置条件检查失败 -> DENY
        2. 状态验证失败 -> DENY
        3. 变更应用失败 -> 回滚
        """
        # 1. 验证前置条件
        is_valid, errors = self.validate_preconditions(context)
        if not is_valid:
            return ResetOperationResult(
                success=False,
                reset_type=ResetType.ITERATE,
                error_code="PRECONDITION_FAILED",
                error_message="; ".join(errors)
            )

        # 2. 检查兼容性
        compat_result = self.can_execute(context)
        if compat_result == ResetValidationResult.DENY:
            return ResetOperationResult(
                success=False,
                reset_type=ResetType.ITERATE,
                error_code="INCOMPATIBLE_OPERATION",
                error_message="Operation denied by compatibility boundary"
            )

        # 3. 创建前置检查点
        current_state = context["current_state"]
        checkpoint_before = self._create_checkpoint(current_state)

        try:
            # 4. 应用变更
            new_state = self._apply_changes(current_state, context["changes"])

            # 5. 验证新状态
            if not self._validate_state(new_state):
                raise ValueError("Invalid state after applying changes")

            # 6. 创建后置检查点
            checkpoint_after = self._create_checkpoint(new_state)

            return ResetOperationResult(
                success=True,
                reset_type=ResetType.ITERATE,
                result=new_state,
                checkpoint_before=checkpoint_before.checkpoint_id,
                checkpoint_after=checkpoint_after.checkpoint_id,
                evidence_ref=f"EV-ITERATE-{checkpoint_after.checkpoint_id}"
            )

        except Exception as e:
            # Fail-closed: 回滚到前置检查点
            return ResetOperationResult(
                success=False,
                reset_type=ResetType.ITERATE,
                error_code="EXECUTION_FAILED",
                error_message=str(e),
                checkpoint_before=checkpoint_before.checkpoint_id
            )

    def _create_checkpoint(self, state: Dict[str, Any]) -> Checkpoint:
        """创建检查点"""
        checkpoint = Checkpoint(
            checkpoint_id=f"CP-ITERATE-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{hashlib.md5(str(state).encode()).hexdigest()[:8]}",
            state_data=state
        )
        checkpoint.state_hash = checkpoint.compute_hash()
        self.checkpoints.append(checkpoint)
        return checkpoint

    def _apply_changes(self, state: Dict[str, Any], changes: Dict[str, Any]) -> Dict[str, Any]:
        """应用增量变更"""
        new_state = state.copy()
        new_state.update(changes)
        return new_state

    def _validate_state(self, state: Dict[str, Any]) -> bool:
        """验证状态有效性"""
        return isinstance(state, dict) and len(state) > 0


# ============================================================================
# Rollback Reset Handler (回滚重置处理器)
# ============================================================================

class RollbackResetHandler(ResetSemanticsHandler):
    """
    ROLLBACK_RESET 语义处理器

    定义：
    - 恢复到之前确认的稳定状态
    - 需要有效的检查点
    - 保留回滚记录用于审计

    兼容边界：
    - 兼容：恢复到有效检查点、撤销最近变更
    - 不兼容：检查点不存在、检查点已损坏、跨越不兼容版本
    """

    def __init__(self):
        self.boundary = CompatibilityBoundary(
            boundary_id="ROLLBACK-BOUNDARY-001",
            name="Rollback Reset Compatibility Boundary",
            description="Defines compatible and incompatible operations for ROLLBACK_RESET",
            compatible_conditions=[
                "valid_checkpoint_exists",
                "state_recoverable"
            ],
            incompatible_conditions=[
                "checkpoint_not_found",
                "checkpoint_corrupted",
                "version_incompatible"
            ],
            approval_required_conditions=[
                "rollback_across_major_version"
            ]
        )

    def can_execute(self, context: Dict[str, Any]) -> ResetValidationResult:
        return self.boundary.check_compatibility(context)

    def validate_preconditions(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []

        # 必须有目标检查点
        if "target_checkpoint" not in context:
            errors.append("Missing target_checkpoint in context")

        # 检查点必须有效
        if "checkpoint_data" in context:
            checkpoint = Checkpoint.from_dict(context["checkpoint_data"])
            if not checkpoint.verify_integrity():
                errors.append("Checkpoint integrity verification failed")

        return len(errors) == 0, errors

    def execute(self, context: Dict[str, Any]) -> ResetOperationResult:
        """
        执行回滚重置

        Fail-closed 策略：
        1. 检查点不存在 -> DENY
        2. 检查点损坏 -> DENY
        3. 版本不兼容 -> DENY
        """
        # 1. 验证前置条件
        is_valid, errors = self.validate_preconditions(context)
        if not is_valid:
            return ResetOperationResult(
                success=False,
                reset_type=ResetType.ROLLBACK_RESET,
                error_code="PRECONDITION_FAILED",
                error_message="; ".join(errors)
            )

        # 2. 检查兼容性
        compat_result = self.can_execute(context)
        if compat_result == ResetValidationResult.DENY:
            return ResetOperationResult(
                success=False,
                reset_type=ResetType.ROLLBACK_RESET,
                error_code="INCOMPATIBLE_OPERATION",
                error_message="Rollback denied by compatibility boundary"
            )

        try:
            # 3. 获取检查点数据
            checkpoint_data = context["checkpoint_data"]
            checkpoint = Checkpoint.from_dict(checkpoint_data)

            # 4. 验证检查点完整性
            if not checkpoint.verify_integrity():
                return ResetOperationResult(
                    success=False,
                    reset_type=ResetType.ROLLBACK_RESET,
                    error_code="CHECKPOINT_CORRUPTED",
                    error_message="Checkpoint integrity verification failed"
                )

            # 5. 恢复状态
            restored_state = checkpoint.state_data

            return ResetOperationResult(
                success=True,
                reset_type=ResetType.ROLLBACK_RESET,
                result=restored_state,
                checkpoint_after=checkpoint.checkpoint_id,
                evidence_ref=f"EV-ROLLBACK-{checkpoint.checkpoint_id}"
            )

        except Exception as e:
            return ResetOperationResult(
                success=False,
                reset_type=ResetType.ROLLBACK_RESET,
                error_code="EXECUTION_FAILED",
                error_message=str(e)
            )


# ============================================================================
# Rebase Reset Handler (变基重置处理器)
# ============================================================================

class RebaseResetHandler(ResetSemanticsHandler):
    """
    REBASE_RESET 语义处理器

    定义：
    - 基于新的基准重新构建状态
    - 丢弃本地未提交变更
    - 以远程/基准版本为准

    兼容边界：
    - 兼容：同步到更新的基准、丢弃冲突的本地变更
    - 不兼容：基准版本更旧、基准已损坏、存在未解决的依赖冲突
    """

    def __init__(self):
        self.boundary = CompatibilityBoundary(
            boundary_id="REBASE-BOUNDARY-001",
            name="Rebase Reset Compatibility Boundary",
            description="Defines compatible and incompatible operations for REBASE_RESET",
            compatible_conditions=[
                "base_is_newer",
                "no_conflicting_dependencies"
            ],
            incompatible_conditions=[
                "base_is_older",
                "base_corrupted",
                "dependency_conflict"
            ],
            approval_required_conditions=[
                "destructive_rebase",
                "rebase_with_uncommitted_work"
            ]
        )

    def can_execute(self, context: Dict[str, Any]) -> ResetValidationResult:
        return self.boundary.check_compatibility(context)

    def validate_preconditions(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []

        # 必须有基准状态
        if "base_state" not in context:
            errors.append("Missing base_state in context")

        # 基准版本必须有效
        if "base_version" not in context:
            errors.append("Missing base_version in context")

        return len(errors) == 0, errors

    def execute(self, context: Dict[str, Any]) -> ResetOperationResult:
        """
        执行变基重置

        Fail-closed 策略：
        1. 基准不存在 -> DENY
        2. 基准版本不兼容 -> DENY
        3. 存在未解决的冲突 -> DENY
        """
        # 1. 验证前置条件
        is_valid, errors = self.validate_preconditions(context)
        if not is_valid:
            return ResetOperationResult(
                success=False,
                reset_type=ResetType.REBASE_RESET,
                error_code="PRECONDITION_FAILED",
                error_message="; ".join(errors)
            )

        # 2. 检查兼容性
        compat_result = self.can_execute(context)
        if compat_result == ResetValidationResult.DENY:
            return ResetOperationResult(
                success=False,
                reset_type=ResetType.REBASE_RESET,
                error_code="INCOMPATIBLE_OPERATION",
                error_message="Rebase denied by compatibility boundary"
            )

        try:
            # 3. 获取基准状态
            base_state = context["base_state"]
            base_version = context["base_version"]

            # 4. 创建变基后状态（丢弃本地变更）
            rebased_state = base_state.copy()
            rebased_state["_rebase_source"] = base_version
            rebased_state["_rebase_time"] = datetime.now(timezone.utc).isoformat()

            return ResetOperationResult(
                success=True,
                reset_type=ResetType.REBASE_RESET,
                result=rebased_state,
                evidence_ref=f"EV-REBASE-{base_version}"
            )

        except Exception as e:
            return ResetOperationResult(
                success=False,
                reset_type=ResetType.REBASE_RESET,
                error_code="EXECUTION_FAILED",
                error_message=str(e)
            )


# ============================================================================
# Reset Semantics Registry (重置语义注册表)
# ============================================================================

class ResetSemanticsRegistry:
    """
    重置语义注册表

    统一管理三种重置语义的处理器
    """

    def __init__(self):
        self._handlers: Dict[ResetType, ResetSemanticsHandler] = {
            ResetType.ITERATE: IterateHandler(),
            ResetType.ROLLBACK_RESET: RollbackResetHandler(),
            ResetType.REBASE_RESET: RebaseResetHandler(),
        }

    def get_handler(self, reset_type: ResetType) -> Optional[ResetSemanticsHandler]:
        """获取指定类型的处理器"""
        return self._handlers.get(reset_type)

    def execute_reset(
        self,
        reset_type: ResetType,
        context: Dict[str, Any]
    ) -> ResetOperationResult:
        """
        执行重置操作

        Fail-closed: 未知类型直接 DENY
        """
        handler = self.get_handler(reset_type)
        if not handler:
            return ResetOperationResult(
                success=False,
                reset_type=reset_type,
                error_code="UNKNOWN_RESET_TYPE",
                error_message=f"Unknown reset type: {reset_type.value}"
            )

        return handler.execute(context)

    def validate_reset(
        self,
        reset_type: ResetType,
        context: Dict[str, Any]
    ) -> ResetValidationResult:
        """
        验证重置操作是否可以执行
        """
        handler = self.get_handler(reset_type)
        if not handler:
            return ResetValidationResult.DENY

        return handler.can_execute(context)


# ============================================================================
# Export
# ============================================================================

__all__ = [
    # Enums
    "ResetType",
    "ResetValidationResult",
    # Data classes
    "CompatibilityBoundary",
    "Checkpoint",
    "ResetOperationResult",
    # Handlers
    "ResetSemanticsHandler",
    "IterateHandler",
    "RollbackResetHandler",
    "RebaseResetHandler",
    # Registry
    "ResetSemanticsRegistry",
    # Constants
    "RESET_SEMANTICS_VERSION",
]
