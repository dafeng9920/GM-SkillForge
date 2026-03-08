"""
Skills Gates module - Logic Layer gates for SkillForge.

This module implements the Logic Layer gates:
- gate_intake: Intake repo gate (G1)
- gate_scan: Repo scan fit score gate (G3)
- gate_draft_spec: Draft skill specification from scan report
- gate_risk: Constitution risk assessment gate (G5)
- gate_permit: Permit validation gate (G9) - 无 permit 不可发布
- permit_issuer: Permit issuance service - 与 GatePermit 对接
- batch_permit_issuer: N-Target batch permit issuance (2→5 targets)

Gate Interface Contract: gate_interface_v1.yaml (FROZEN)
"""

from .gate_intake import GateIntakeRepo, IntakeGate, intake_repo
from .gate_scan import GateRepoScanFitScore, ScanGate, repo_scan_fit_score
from .gate_draft_spec import DraftSpecGate, draft_skill_spec
from .gate_risk import ConstitutionRiskGate, constitution_risk_gate
from .gate_permit import GatePermit, validate_permit
from .permit_issuer import PermitIssuer, issue_permit
from .batch_permit_issuer import (
    BatchPermitIssuer,
    FailureStrategy,
    BatchDecision,
    issue_batch_permits,
)

__all__ = [
    # Entrance gates
    "GateIntakeRepo",
    "IntakeGate",
    "intake_repo",
    "GateRepoScanFitScore",
    "ScanGate",
    "repo_scan_fit_score",
    # Logic gates
    "DraftSpecGate",
    "draft_skill_spec",
    "ConstitutionRiskGate",
    "constitution_risk_gate",
    # Delivery gates
    "GatePermit",
    "validate_permit",
    # Permit issuance
    "PermitIssuer",
    "issue_permit",
    # Batch permit issuance
    "BatchPermitIssuer",
    "FailureStrategy",
    "BatchDecision",
    "issue_batch_permits",
]
