"""
External Action Policy - 外部动作策略

定义关键动作/非关键动作分类、Permit 校验、Evidence 搬运规则。

Task ID: E4
Executor: Kior-B
Date: 2026-03-19
"""

from .classification import (
    ActionCategory,
    classify_action,
    is_critical_action as _is_critical_action,
    is_non_critical_action,
    get_known_critical_actions,
    get_known_non_critical_actions,
)

from .external_action_policy import (
    CRITICAL_ACTIONS,
    ExternalActionPolicy,
    ActionPolicyDecision,
    ExecutionBlockReason,
    get_policy,
    evaluate_action,
    is_critical_action,
    requires_permit,
)

from .permit_check import (
    PermitCheckResult,
    check_permit_for_action,
    check_permit_or_raise,
)

from .evidence_transport import (
    EvidenceRef,
    AuditPackRef,
    EvidenceTransportRule,
    get_transport_rule,
    transport_evidence_ref,
    transport_audit_pack_ref,
)

__all__ = [
    # Classification
    "ActionCategory",
    "classify_action",
    "is_non_critical_action",
    "get_known_critical_actions",
    "get_known_non_critical_actions",
    # Policy
    "CRITICAL_ACTIONS",
    "ExternalActionPolicy",
    "ActionPolicyDecision",
    "ExecutionBlockReason",
    "get_policy",
    "evaluate_action",
    "is_critical_action",
    "requires_permit",
    # Permit Check
    "PermitCheckResult",
    "check_permit_for_action",
    "check_permit_or_raise",
    # Evidence Transport
    "EvidenceRef",
    "AuditPackRef",
    "EvidenceTransportRule",
    "get_transport_rule",
    "transport_evidence_ref",
    "transport_audit_pack_ref",
]
