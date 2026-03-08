"""
Consistency Contracts Package

L4.5 T96: 一致性契约 + 重置语义统一
Job ID: L4P5-UPGRADE-20260222-001
Executor: vs--cc1

This package provides:
1. ConsistencyContract - 一致性契约定义与验证
2. ResetSemantics - 重置语义统一实现 (iterate/rollback_reset/rebase_reset)
3. Fail-closed 策略 - 任何验证失败必须阻断执行

Usage:
    from contracts.consistency import (
        ConsistencyContract,
        ConsistencyContractValidator,
        ContractViolationError,
        ResetSemanticsRegistry,
        ResetType,
    )

    # 创建契约
    contract = ConsistencyContract(contract_id="MY-CONTRACT-001")
    contract.add_invariant(Invariant(...))
    contract.add_allowed_change(AllowedChange(...))

    # 验证变更
    validator = ConsistencyContractValidator(contract)
    validator.enforce_or_fail(current_state, proposed_changes)

    # 执行重置
    registry = ResetSemanticsRegistry()
    result = registry.execute_reset(ResetType.ITERATE, context)
"""

from .consistency_contract import (
    # Enums
    ContractViolationSeverity,
    # Data classes
    Invariant,
    AllowedChange,
    BreakingChangeTrigger,
    ConsistencyContract,
    # Exceptions
    ContractViolationError,
    # Validators
    ConsistencyContractValidator,
    # Constants
    CONTRACT_VERSION,
    DENY_ERROR_CODE,
)

from .reset_semantics import (
    # Enums
    ResetType,
    ResetValidationResult,
    # Data classes
    CompatibilityBoundary,
    Checkpoint,
    ResetOperationResult,
    # Handlers
    ResetSemanticsHandler,
    IterateHandler,
    RollbackResetHandler,
    RebaseResetHandler,
    # Registry
    ResetSemanticsRegistry,
    # Constants
    RESET_SEMANTICS_VERSION,
)

__all__ = [
    # Consistency Contract
    "ContractViolationSeverity",
    "Invariant",
    "AllowedChange",
    "BreakingChangeTrigger",
    "ConsistencyContract",
    "ContractViolationError",
    "ConsistencyContractValidator",
    "CONTRACT_VERSION",
    "DENY_ERROR_CODE",
    # Reset Semantics
    "ResetType",
    "ResetValidationResult",
    "CompatibilityBoundary",
    "Checkpoint",
    "ResetOperationResult",
    "ResetSemanticsHandler",
    "IterateHandler",
    "RollbackResetHandler",
    "RebaseResetHandler",
    "ResetSemanticsRegistry",
    "RESET_SEMANTICS_VERSION",
]

__version__ = "v1.0.0-20260224"
