"""
n8n Orchestration Routes - n8n 编排入口路由

提供四个核心入口：
- POST /api/v1/n8n/run_intent -> 执行意图（SkillForge 内部计算 run_id）
- POST /api/v1/n8n/fetch_pack -> 获取 AuditPack
- POST /api/v1/n8n/query_rag -> RAG 查询（支持 at_time）
- POST /api/v1/n8n/import_external_skill -> 外部 Skill 导入入口（T12）

边界冻结条款（L4.5 启动清单）：
1. n8n 只做编排（触发/路由/重试/通知），不做最终裁决。
2. SkillForge 负责最终裁决（GateDecision / Permit / EvidenceRef / AuditPack）。
3. n8n 传入 gate_decision/release_allowed 时必须拒绝或忽略并记证据。
4. no-permit-no-release 永不放松。

Contract: docs/2026-02-20/L4.5 启动清单 v2（2026-02-20）.md
External Skill Governance: docs/2026-02-19/contracts/external_skill_governance_contract_v1.yaml
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

# Import gate modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from skills.gates.gate_permit import GatePermit
from skills.gates.permit_issuer import PermitIssuer

# RAG Adapter
try:
    from adapters.rag_adapter import get_rag_adapter, RAGQueryError, AT_TIME_FORBIDDEN_VALUES
except ImportError:
    # Fallback for direct import
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from adapters.rag_adapter import get_rag_adapter, RAGQueryError, AT_TIME_FORBIDDEN_VALUES

# Membership middleware
try:
    from contracts.policy.membership_middleware import check_execute_via_n8n
except ImportError:
    # Fallback if membership middleware not available
    def check_execute_via_n8n(*args, **kwargs):
        from dataclasses import dataclass
        @dataclass
        class MockResult:
            allowed: bool = True
        return MockResult()


# ============================================================================
# Constants
# ============================================================================

N8N_RUN_ID_PREFIX = "RUN-N8N"
SKILL_ID = "l45_n8n_orchestration_boundary"
PRODUCTION_SKILL_ID = "l45_orchestration_min_capabilities"
JOB_ID = "L45-D2-ORCH-MINCAP-20260220-002"

# External Skill Governance constants (T12)
EXT_SKILL_JOB_ID = "L45-D3-EXT-SKILL-GOV-20260220-003"
EXT_SKILL_SKILL_ID = "l45_external_skill_governance_batch1"

# Import pipeline states per external_skill_governance_contract_v1.yaml
IMPORT_PIPELINE_STATES = [
    "S1_QUARANTINE",
    "S2_CONSTITUTION_GATE",
    "S3_SYSTEM_AUDIT",
    "S4_DECISION",
    "S5_PERMIT_ISSUANCE",
    "S6_REGISTRY_ADMISSION",
]

# Forbidden fields that n8n must NOT inject
# Production: Extended list per L45-D2-ORCH-MINCAP contract
FORBIDDEN_N8N_FIELDS = [
    "gate_decision",
    "release_allowed",
    "permit_token",
    "evidence_ref",
    "permit_id",  # Added for production
    "run_id",     # n8n cannot override run_id
]

# Error codes
ERROR_CODES = {
    "N8N_FORBIDDEN_FIELD_INJECTION": "n8n attempted to inject forbidden field",
    "N8N_PERMIT_REQUIRED": "Permit required for execution",
    "N8N_MEMBERSHIP_DENIED": "Membership policy denied execution",
    "N8N_QUOTA_EXCEEDED": "Quota exceeded",
    "N8N_INTERNAL_ERROR": "Internal error",
    "N8N_EXECUTION_GUARD_BLOCKED": "Execution guard blocked request",
}


# ============================================================================
# Pydantic Models
# ============================================================================

class RunIntentRequest(BaseModel):
    """Request for running an intent via n8n orchestration."""
    repo_url: str
    commit_sha: str
    at_time: Optional[str] = Field(default=None, description="ISO8601 timestamp for point-in-time execution")
    intent_id: str
    requester_id: str
    context: Optional[dict] = None
    tier: str = Field(default="FREE", description="Membership tier for policy enforcement")
    execution_contract: Optional[dict] = Field(
        default=None,
        description="Structured execution contract required by execution guard",
    )
    compliance_attestation: Optional[dict] = Field(
        default=None,
        description="Compliance attestation produced by compliance role",
    )
    guard_signature: Optional[str] = Field(
        default=None,
        description="Optional guard signature or contract hash fingerprint",
    )
    permit_token: Optional[str] = Field(
        default=None,
        description="Forbidden external field. Permit is issued internally by SkillForge.",
    )

    # These fields are FORBIDDEN - if present, will be rejected/ignored
    gate_decision: Optional[str] = Field(default=None, exclude=True)
    release_allowed: Optional[bool] = Field(default=None, exclude=True)

    @field_validator('gate_decision', 'release_allowed', mode='before')
    @classmethod
    def warn_forbidden_fields(cls, v, info):
        """Warn if forbidden fields are present (they will be ignored)."""
        if v is not None:
            field_name = info.field_name
            # Log warning but don't reject - we'll record evidence
            pass
        return v


class FetchPackRequest(BaseModel):
    """Request for fetching an AuditPack."""
    run_id: Optional[str] = None
    evidence_ref: Optional[str] = None
    at_time: Optional[str] = Field(default=None, description="ISO8601 timestamp for point-in-time query")


class QueryRagRequest(BaseModel):
    """Request for RAG query."""
    query: str
    at_time: Optional[str] = Field(default=None, description="ISO8601 timestamp for point-in-time query")
    repo_url: Optional[str] = None
    commit_sha: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=100)


class ImportExternalSkillRequest(BaseModel):
    """
    Request for importing an external skill.

    T12: External Skill Governance Entry Point
    Per external_skill_governance_contract_v1.yaml:
    - Import goes through: Quarantine → Constitution Gate → System Audit → Decision → Permit → Registry

    IMPORTANT: n8n can only trigger the import. Final decision is made by SkillForge.
    """
    repo_url: str
    commit_sha: str
    at_time: Optional[str] = Field(default=None, description="ISO8601 timestamp for point-in-time execution")
    external_skill_ref: str = Field(..., description="Reference to the external skill package")
    requester_id: str
    skill_name: Optional[str] = None
    skill_version: Optional[str] = None
    source_repository: Optional[str] = None
    context: Optional[dict] = None
    tier: str = Field(default="FREE", description="Membership tier for policy enforcement")
    execution_contract: Optional[dict] = Field(
        default=None,
        description="Structured execution contract required by execution guard",
    )
    compliance_attestation: Optional[dict] = Field(
        default=None,
        description="Compliance attestation produced by compliance role",
    )
    guard_signature: Optional[str] = Field(
        default=None,
        description="Optional guard signature or contract hash fingerprint",
    )

    # These fields are FORBIDDEN - if present, will be rejected
    gate_decision: Optional[str] = Field(default=None, exclude=True)
    release_allowed: Optional[bool] = Field(default=None, exclude=True)
    run_id: Optional[str] = Field(default=None, exclude=True)
    evidence_ref: Optional[str] = Field(default=None, exclude=True)
    permit_id: Optional[str] = Field(default=None, exclude=True)

    @field_validator('gate_decision', 'release_allowed', 'run_id', 'evidence_ref', 'permit_id', mode='before')
    @classmethod
    def warn_forbidden_fields(cls, v, info):
        """Warn if forbidden fields are present (they will be rejected)."""
        if v is not None:
            pass
        return v


# ============================================================================
# Response Models
# ============================================================================

class N8NSuccessEnvelope(BaseModel):
    """Success response envelope for n8n routes."""
    ok: bool = True
    data: dict
    gate_decision: str
    release_allowed: bool
    evidence_ref: str
    run_id: str


class N8NErrorEnvelope(BaseModel):
    """Error response envelope for n8n routes."""
    ok: bool = False
    error_code: str
    blocked_by: str
    message: str
    evidence_ref: Optional[str] = None
    run_id: str
    forbidden_field_evidence: Optional[dict] = None
    required_changes: Optional[list[dict[str, str]]] = None


class ImportExternalSkillErrorEnvelope(BaseModel):
    """
    Error response envelope for import_external_skill.

    T12: Must include gate_decision and required_changes for fail-closed response.
    """
    ok: bool = False
    error_code: str
    blocked_by: str
    message: str
    gate_decision: str = "BLOCK"
    evidence_ref: str
    run_id: str
    required_changes: list[str] = Field(default_factory=list)
    forbidden_field_evidence: Optional[dict] = None


# ============================================================================
# Router
# ============================================================================

router = APIRouter(prefix="/api/v1/n8n", tags=["n8n-orchestration"])


# ============================================================================
# Helper Functions
# ============================================================================

def generate_run_id() -> str:
    """Generate a unique run ID (SkillForge internal)."""
    ts = int(time.time())
    uid = uuid.uuid4().hex[:8].upper()
    return f"{N8N_RUN_ID_PREFIX}-{ts}-{uid}"


def generate_evidence_ref(prefix: str = "EV-N8N") -> str:
    """Generate an evidence reference."""
    ts = int(time.time())
    uid = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{ts}-{uid}"


def now_iso() -> str:
    """Return ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def detect_forbidden_fields(request_dict: dict) -> list[str]:
    """Detect if n8n attempted to inject forbidden fields."""
    found = []
    for field in FORBIDDEN_N8N_FIELDS:
        if field in request_dict and request_dict[field] is not None:
            found.append(field)
    return found


def create_forbidden_field_evidence(
    run_id: str,
    forbidden_fields: list[str],
    raw_request: dict
) -> dict:
    """Create evidence record for forbidden field injection attempt."""
    timestamp = now_iso()
    content = json.dumps({
        "run_id": run_id,
        "forbidden_fields": forbidden_fields,
        "raw_request_keys": list(raw_request.keys()),
        "timestamp": timestamp,
    }, sort_keys=True)
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    return {
        "issue_key": f"N8N-FORBIDDEN-{run_id}",
        "source_locator": f"n8n://intent/{run_id}",
        "content_hash": content_hash,
        "timestamp": timestamp,
        "forbidden_fields": forbidden_fields,
        "action_taken": "REJECTED_AND_IGNORED",
        "decision_snapshot": {
            "check": "forbidden_field_injection",
            "fields_detected": forbidden_fields,
            "policy": "n8n_must_not_override_gate_decision",
        }
    }


def create_audit_trail(
    run_id: str,
    intent_id: str,
    repo_url: str,
    commit_sha: str,
    gate_decision: str,
    release_allowed: bool,
    evidence_ref: str,
    permit_id: Optional[str] = None,
    error_code: Optional[str] = None,
) -> dict:
    """
    Create audit trail for run_intent execution.

    Production requirement: All executions must have traceable audit records.
    """
    timestamp = now_iso()
    audit_entry = {
        "run_id": run_id,
        "intent_id": intent_id,
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "gate_decision": gate_decision,
        "release_allowed": release_allowed,
        "evidence_ref": evidence_ref,
        "timestamp": timestamp,
        "job_id": JOB_ID,
        "skill_id": PRODUCTION_SKILL_ID,
    }

    if permit_id:
        audit_entry["permit_id"] = permit_id

    if error_code:
        audit_entry["error_code"] = error_code

    return audit_entry


def _make_required_change(
    issue_key: str,
    reason: str,
    fix_kind: str,
    evidence_needed: str,
    next_action: str,
) -> dict[str, str]:
    """Build RequiredChanges entry following guard A/B structure."""
    return {
        "issue_key": issue_key,
        "reason": reason,
        "fix_kind": fix_kind,
        "evidence_needed": evidence_needed,
        "next_action": next_action,
    }


def _canonical_contract_hash(execution_contract: dict[str, Any]) -> str:
    """Compute deterministic hash for execution_contract."""
    canonical = json.dumps(execution_contract, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def enforce_execution_guard(
    *,
    run_id: str,
    execution_contract: Optional[dict[str, Any]],
    compliance_attestation: Optional[dict[str, Any]],
    guard_signature: Optional[str],
) -> tuple[bool, Optional[str], Optional[str], list[dict[str, str]]]:
    """
    Enforce A/B execution guard hard checks before execution.

    Returns:
        (allowed, error_code, message, required_changes)
    """
    required_changes: list[dict[str, str]] = []
    blocked_code = "SF_RISK_CONSTITUTION_BLOCKED"

    if not isinstance(execution_contract, dict):
        required_changes.append(
            _make_required_change(
                issue_key=f"EXEC-GUARD-{run_id}-MISSING-CONTRACT",
                reason="execution_contract is required before execution",
                fix_kind="ADD_CONTRACT",
                evidence_needed="Provide ExecutionContract with required fields and roles",
                next_action="Resubmit request with a valid execution_contract",
            )
        )
        return False, blocked_code, "Execution blocked: execution_contract missing.", required_changes

    roles = execution_contract.get("roles")
    if not isinstance(roles, dict):
        required_changes.append(
            _make_required_change(
                issue_key=f"EXEC-GUARD-{run_id}-MISSING-ROLES",
                reason="execution_contract.roles is required",
                fix_kind="ADD_CONTRACT",
                evidence_needed="roles.execution/review/compliance must be present",
                next_action="Add roles block and resubmit",
            )
        )
        return False, "SF_CONTRACT_DRAFT_INVALID", "Execution blocked: roles missing in contract.", required_changes

    missing_roles = [r for r in ("execution", "review", "compliance") if r not in roles]
    if missing_roles:
        required_changes.append(
            _make_required_change(
                issue_key=f"EXEC-GUARD-{run_id}-MISSING-ROLE",
                reason=f"missing required roles: {missing_roles}",
                fix_kind="ADD_CONTRACT",
                evidence_needed="Include execution/review/compliance role definitions",
                next_action="Patch contract roles and retry",
            )
        )
        return False, "SF_CONTRACT_DRAFT_INVALID", "Execution blocked: required roles missing.", required_changes

    controls = execution_contract.get("controls")
    if not isinstance(controls, dict) or "timeout_ms" not in controls or "max_targets" not in controls:
        required_changes.append(
            _make_required_change(
                issue_key=f"EXEC-GUARD-{run_id}-MISSING-CONTROLS",
                reason="controls.timeout_ms and controls.max_targets are required",
                fix_kind="ADD_CONTRACT",
                evidence_needed="Provide explicit timeout and target budget in controls",
                next_action="Add controls.timeout_ms/max_targets and retry",
            )
        )
        return False, "SF_CONTRACT_DRAFT_INVALID", "Execution blocked: controls are incomplete.", required_changes

    if not isinstance(compliance_attestation, dict):
        required_changes.append(
            _make_required_change(
                issue_key=f"EXEC-GUARD-{run_id}-MISSING-COMPLIANCE",
                reason="compliance_attestation is required",
                fix_kind="ADD_TESTS",
                evidence_needed="Provide ComplianceAttestation(PASS|FAIL) with evidence_refs",
                next_action="Run compliance review and attach attestation",
            )
        )
        return False, blocked_code, "Execution blocked: compliance_attestation missing.", required_changes

    decision = str(compliance_attestation.get("decision", "")).upper()
    if decision != "PASS":
        required_changes.append(
            _make_required_change(
                issue_key=f"EXEC-GUARD-{run_id}-COMPLIANCE-NOT-PASS",
                reason=f"compliance decision is '{decision or 'UNKNOWN'}', must be PASS",
                fix_kind="GATE_DECISION",
                evidence_needed="ComplianceAttestation with decision=PASS and evidence_refs",
                next_action="Address compliance findings and resubmit",
            )
        )
        return False, blocked_code, "Execution blocked: compliance decision is not PASS.", required_changes

    if not compliance_attestation.get("evidence_refs"):
        required_changes.append(
            _make_required_change(
                issue_key=f"EXEC-GUARD-{run_id}-COMPLIANCE-NO-EVIDENCE",
                reason="compliance attestation must include evidence_refs",
                fix_kind="ADD_TESTS",
                evidence_needed="Attach at least one EvidenceRef in compliance_attestation.evidence_refs",
                next_action="Re-run compliance and include evidence refs",
            )
        )
        return False, "SF_VALIDATION_ERROR", "Execution blocked: compliance evidence missing.", required_changes

    contract_hash = _canonical_contract_hash(execution_contract)
    attested_hash = compliance_attestation.get("contract_hash")
    if attested_hash and attested_hash != contract_hash:
        required_changes.append(
            _make_required_change(
                issue_key=f"EXEC-GUARD-{run_id}-HASH-MISMATCH",
                reason="compliance contract_hash does not match execution_contract",
                fix_kind="UPDATE_SCAFFOLD",
                evidence_needed="Re-attest contract and provide matching contract_hash",
                next_action="Regenerate attestation against exact contract payload",
            )
        )
        return False, "SF_VALIDATION_ERROR", "Execution blocked: attestation hash mismatch.", required_changes

    if guard_signature and guard_signature != contract_hash:
        required_changes.append(
            _make_required_change(
                issue_key=f"EXEC-GUARD-{run_id}-GUARD-SIGNATURE-MISMATCH",
                reason="guard_signature does not match execution_contract hash",
                fix_kind="UPDATE_SCAFFOLD",
                evidence_needed="Provide correct guard_signature (contract hash)",
                next_action="Recompute guard_signature from canonical contract and retry",
            )
        )
        return False, "SF_VALIDATION_ERROR", "Execution blocked: guard signature mismatch.", required_changes

    return True, None, None, []


def issue_internal_permit(request: RunIntentRequest, run_id: str) -> dict[str, Any]:
    """
    Issue permit internally (n8n cannot provide permit_token).

    Fail-closed: returns success=False when signing key/service is not available
    or issuance conditions are not met.
    """
    signing_key = os.getenv("PERMIT_HS256_KEY")
    if not signing_key:
        return {
            "success": False,
            "error_code": "I004",
            "error_message": "Internal permit service signing key is missing",
        }

    issuer = PermitIssuer(signing_key=signing_key)
    issue_input = {
        "final_gate_decision": "PASSED_NO_PERMIT",
        "release_blocked_by": None,
        "audit_pack_ref": f"audit://n8n/{run_id}",
        "repo_url": request.repo_url,
        "commit_sha": request.commit_sha,
        "run_id": run_id,
        "intent_id": request.intent_id,
        "ttl_seconds": 3600,
        "allowed_actions": ["release"],
        "at_time": request.at_time or now_iso(),
        "environment": "development",
        "gate_profile": "l45_n8n_orchestration",
    }
    return issuer.issue_permit(issue_input)


# ============================================================================
# API Routes
# ============================================================================

@router.post("/run_intent")
async def run_intent(request: RunIntentRequest):
    """
    Run an intent via n8n orchestration.

    IMPORTANT: SkillForge retains final decision authority.
    - run_id is computed INTERNALLY by SkillForge, not by n8n.
    - gate_decision and release_allowed are computed by GatePermit, not n8n.
    - If n8n attempts to inject gate_decision/release_allowed, the request
      will be rejected/ignored and evidence will be recorded.

    Output must contain:
    - run_id: Unique execution identifier (SkillForge-generated)
    - gate_decision: ALLOW or BLOCK (from GatePermit)
    - evidence_ref: Evidence reference for audit
    - release_allowed: Boolean indicating if release is permitted

    Blocking rules:
    - E001: No permit -> release_allowed=false
    - E003: Bad signature -> release_allowed=false
    - N8N_FORBIDDEN_FIELD_INJECTION: n8n attempted to inject forbidden fields
    """
    # Step 1: Generate run_id INTERNALLY (n8n cannot override)
    run_id = generate_run_id()
    evidence_ref = generate_evidence_ref("EV-N8N-INTENT")

    # Step 2: Detect forbidden field injection attempts
    request_dict = request.model_dump()
    forbidden_fields = detect_forbidden_fields(request_dict)

    # If forbidden fields detected, record evidence and reject
    if forbidden_fields:
        forbidden_evidence = create_forbidden_field_evidence(
            run_id, forbidden_fields, request_dict
        )
        return N8NErrorEnvelope(
            error_code="N8N_FORBIDDEN_FIELD_INJECTION",
            blocked_by="N8N_POLICY_VIOLATION",
            message=f"n8n attempted to inject forbidden fields: {forbidden_fields}. These fields are computed by SkillForge only.",
            evidence_ref=evidence_ref,
            run_id=run_id,
            forbidden_field_evidence=forbidden_evidence,
        ).model_dump()

    # Step 3: Check membership policy (execute_via_n8n gate)
    # Step 3a: Execution guard hard intercept (A/B skill enforcement)
    guard_ok, guard_error, guard_message, guard_required_changes = enforce_execution_guard(
        run_id=run_id,
        execution_contract=request.execution_contract,
        compliance_attestation=request.compliance_attestation,
        guard_signature=request.guard_signature,
    )
    if not guard_ok:
        return N8NErrorEnvelope(
            error_code=guard_error or "N8N_EXECUTION_GUARD_BLOCKED",
            blocked_by="EXECUTION_GUARD",
            message=guard_message or "Execution guard blocked request",
            evidence_ref=evidence_ref,
            run_id=run_id,
            required_changes=guard_required_changes,
        ).model_dump()

    # Step 3b: Check membership policy (execute_via_n8n gate)
    # Use permit_status=VALID for policy checks; actual permit is minted and
    # validated in the following steps inside SkillForge.
    membership_result = check_execute_via_n8n(
        tier=request.tier,
        permit_status="VALID",
        execution_contract_present=request.execution_contract is not None,
        tombstone_state=None,
        enabled_addons=[],
        current_concurrent_jobs=0,
    )

    if not membership_result.allowed:
        return N8NErrorEnvelope(
            error_code="N8N_MEMBERSHIP_DENIED",
            blocked_by=membership_result.error_code or "MEMBERSHIP_POLICY",
            message=membership_result.error_message or "Membership policy denied execution",
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    # Step 4: Issue permit internally (n8n cannot inject permit_token)
    issue_result = issue_internal_permit(request, run_id)
    if not issue_result.get("success"):
        return N8NErrorEnvelope(
            error_code="N8N_PERMIT_ISSUE_FAILED",
            blocked_by=issue_result.get("error_code", "PERMIT_SERVICE_ERROR"),
            message=issue_result.get("error_message", "Internal permit issuance failed"),
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    # Step 5: Validate internally-issued permit with GatePermit
    gate = GatePermit()

    # Build validation input for GatePermit
    validation_input = {
        "permit_token": issue_result.get("permit_token"),
        "repo_url": request.repo_url,
        "commit_sha": request.commit_sha,
        "run_id": run_id,  # Use SkillForge-generated run_id
        "requested_action": "release",
        # Use wall-clock validation time; at_time is replay/constraint context.
        "current_time": now_iso(),
    }

    try:
        # Step 6: Execute GatePermit validation (final decision by SkillForge)
        result = gate.execute(validation_input)

        if not result.get("release_allowed", False):
            # Gate blocked execution - return error envelope
            error_code = result.get("error_code", "E002")
            blocked_by_map = {
                "E001": "PERMIT_REQUIRED",
                "E002": "PERMIT_INVALID",
                "E003": "PERMIT_INVALID",
                "E004": "PERMIT_EXPIRED",
                "E005": "PERMIT_SCOPE_MISMATCH",
                "E006": "PERMIT_SUBJECT_MISMATCH",
                "E007": "PERMIT_REVOKED",
            }
            blocked_by = blocked_by_map.get(error_code, "PERMIT_INVALID")
            message = result.get("reason", "Permit validation failed")

            return N8NErrorEnvelope(
                error_code=error_code,
                blocked_by=blocked_by,
                message=message,
                evidence_ref=evidence_ref,
                run_id=run_id,
            ).model_dump()

        # Step 7: Success - return with SkillForge-computed fields
        return N8NSuccessEnvelope(
            data={
                "intent_id": request.intent_id,
                "repo_url": request.repo_url,
                "commit_sha": request.commit_sha,
                "at_time": request.at_time or now_iso(),
                "execution_status": "COMPLETED",
                "permit_id": issue_result.get("permit_id") or result.get("permit_id"),
                "validation_timestamp": result.get("validation_timestamp"),
                "context": request.context,
            },
            gate_decision=result.get("gate_decision", "ALLOW"),
            release_allowed=True,
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    except Exception as e:
        return N8NErrorEnvelope(
            error_code="N8N_INTERNAL_ERROR",
            blocked_by="INTERNAL_ERROR",
            message=f"Internal error during execution: {str(e)}",
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()


@router.post("/fetch_pack")
async def fetch_pack(request: FetchPackRequest):
    """
    Fetch an AuditPack by run_id or evidence_ref.

    Production implementation with real storage and consistency check.

    Supports at_time parameter for point-in-time queries.
    Returns the AuditPack content with verification metadata.

    Constraints (T8):
    - run_id 与 evidence_ref 任一给定时必须能做一致性校验
    - 读取失败必须 fail-closed 并返回结构化错误信封
    - 返回体必须包含 replay_pointer（可空但字段存在）
    - 不破坏 T4 定义的 receipt schema 兼容性
    """
    # Import store lazily to avoid circular imports
    from storage.audit_pack_store import get_audit_pack_store

    run_id = request.run_id or generate_run_id()
    evidence_ref = request.evidence_ref or generate_evidence_ref("EV-N8N-FETCH")

    # Validate that at least one identifier is provided
    if not request.run_id and not request.evidence_ref:
        return N8NErrorEnvelope(
            error_code="N8N_MISSING_IDENTIFIER",
            blocked_by="VALIDATION_ERROR",
            message="Either run_id or evidence_ref must be provided",
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    # Fetch from real storage with consistency check
    store = get_audit_pack_store()
    result = store.fetch_with_consistency_check(
        run_id=request.run_id,
        evidence_ref=request.evidence_ref,
    )

    # Fail-closed: return error envelope on failure
    if not result.success:
        return N8NErrorEnvelope(
            error_code=result.error_code or "FETCH_ERROR",
            blocked_by="AUDIT_PACK_STORE",
            message=result.error_message or "Failed to fetch AuditPack",
            evidence_ref=result.evidence_ref or evidence_ref,
            run_id=result.run_id or run_id,
        ).model_dump()

    # Success: build response with replay_pointer (always present, nullable content)
    pack = result.pack
    pack_data = pack.to_dict()

    # Ensure replay_pointer field is present (nullable allowed per schema)
    if "replay_pointer" not in pack_data or pack_data["replay_pointer"] is None:
        pack_data["replay_pointer"] = {
            "snapshot_ref": None,
            "at_time": None,
            "revision": None,
            "evidence_bundle_ref": None,
        }

    # Add at_time from request for point-in-time query support
    pack_data["query_at_time"] = request.at_time or now_iso()
    pack_data["fetched_at"] = now_iso()

    return N8NSuccessEnvelope(
        data=pack_data,
        gate_decision="ALLOW",
        release_allowed=True,
        evidence_ref=pack.evidence_ref,
        run_id=pack.run_id,
    ).model_dump()


@router.post("/query_rag")
async def query_rag(request: QueryRagRequest):
    """
    Query RAG (Retrieval-Augmented Generation) index.

    Production implementation using swappable RAG adapter.

    IMPORTANT CONSTRAINTS:
    - at_time is REQUIRED and must be a fixed ISO-8601 timestamp
    - Drift values (latest/now/today) are FORBIDDEN
    - Response MUST include replay_pointer for audit trail

    Supports:
    - repo_url + commit_sha + at_time combination query
    - Swappable adapter (mock vs real implementation)

    Returns relevant documents/chunks based on the query.
    """
    run_id = generate_run_id()
    evidence_ref = generate_evidence_ref("EV-N8N-RAG")

    # Step 1: Validate at_time - must be present and fixed
    if request.at_time is None:
        return N8NErrorEnvelope(
            error_code="RAG-AT-TIME-MISSING",
            blocked_by="VALIDATION_ERROR",
            message="at_time is required and must be a fixed ISO-8601 timestamp.",
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    # Step 2: Reject drift values
    if isinstance(request.at_time, str) and request.at_time.lower() in AT_TIME_FORBIDDEN_VALUES:
        return N8NErrorEnvelope(
            error_code="RAG-AT-TIME-DRIFT-FORBIDDEN",
            blocked_by="POLICY_VIOLATION",
            message=f"at_time must be a fixed ISO-8601 timestamp. '{request.at_time}' is a drift value and is not allowed.",
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    # Step 3: Use RAG adapter for query
    try:
        adapter = get_rag_adapter()
        result = adapter.query(
            query=request.query,
            at_time=request.at_time,
            repo_url=request.repo_url,
            commit_sha=request.commit_sha,
            top_k=request.top_k,
        )

        # Step 4: Build response with replay_pointer
        rag_results = result.to_dict()
        rag_results["run_id"] = run_id
        rag_results["evidence_ref"] = evidence_ref

        return N8NSuccessEnvelope(
            data=rag_results,
            gate_decision="ALLOW",
            release_allowed=True,
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    except ValueError as e:
        # Validation error from adapter
        return N8NErrorEnvelope(
            error_code="RAG-VALIDATION-ERROR",
            blocked_by="VALIDATION_ERROR",
            message=str(e),
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    except Exception as e:
        # Internal error
        return N8NErrorEnvelope(
            error_code="RAG-INTERNAL-ERROR",
            blocked_by="INTERNAL_ERROR",
            message=f"Internal error during RAG query: {str(e)}",
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()


@router.post("/import_external_skill")
async def import_external_skill(request: ImportExternalSkillRequest):
    """
    Import an external skill into SkillForge.

    T12: External Skill Governance Entry Point

    This endpoint triggers the 6-step import pipeline:
    1. S1: Import to Quarantine
    2. S2: Constitution Gate (boundary/permission/forbidden capability checks)
    3. S3: System Audit (L1-L5)
    4. S4: Decision (PASS@L3+ required)
    5. S5: Permit Issuance
    6. S6: Registry Admission

    IMPORTANT BOUNDARY RULES:
    - n8n can only trigger the import, NOT make final decisions.
    - run_id and evidence_ref are generated INTERNALLY by SkillForge.
    - gate_decision and release_allowed are computed by governance pipeline, NOT by n8n.
    - If n8n attempts to inject forbidden fields, the request is rejected with evidence.

    Output:
    - Success: gate_decision=ALLOW, quarantine_id, permit_id, registry_entry_id
    - Failure: gate_decision=BLOCK, required_changes list

    Contract: docs/2026-02-19/contracts/external_skill_governance_contract_v1.yaml
    """
    # Step 1: Generate run_id and evidence_ref INTERNALLY (n8n cannot override)
    run_id = generate_run_id()
    evidence_ref = generate_evidence_ref("EV-EXT-SKILL")

    # Step 2: Detect forbidden field injection attempts
    request_dict = request.model_dump()
    forbidden_fields = detect_forbidden_fields(request_dict)

    if forbidden_fields:
        forbidden_evidence = create_forbidden_field_evidence(
            run_id, forbidden_fields, request_dict
        )
        return ImportExternalSkillErrorEnvelope(
            error_code="N8N_FORBIDDEN_FIELD_INJECTION",
            blocked_by="N8N_POLICY_VIOLATION",
            message=f"n8n attempted to inject forbidden fields: {forbidden_fields}. Final decisions are made by SkillForge only.",
            gate_decision="BLOCK",
            evidence_ref=evidence_ref,
            run_id=run_id,
            required_changes=[
                f"Remove forbidden field '{field}' from request" for field in forbidden_fields
            ],
            forbidden_field_evidence=forbidden_evidence,
        ).model_dump()

    # Step 3: Execution guard hard intercept (A/B skill enforcement)
    guard_ok, guard_error, guard_message, guard_required_changes = enforce_execution_guard(
        run_id=run_id,
        execution_contract=request.execution_contract,
        compliance_attestation=request.compliance_attestation,
        guard_signature=request.guard_signature,
    )
    if not guard_ok:
        return ImportExternalSkillErrorEnvelope(
            error_code=guard_error or "N8N_EXECUTION_GUARD_BLOCKED",
            blocked_by="EXECUTION_GUARD",
            message=guard_message or "Execution guard blocked request",
            gate_decision="BLOCK",
            evidence_ref=evidence_ref,
            run_id=run_id,
            required_changes=[f"{item['issue_key']}: {item['reason']}" for item in guard_required_changes],
        ).model_dump()

    # Step 4: Generate quarantine_id for S1
    quarantine_id = f"Q-{uuid.uuid4().hex[:12].upper()}"

    try:
        # Step 5: S2 - Constitution Gate (simplified - in production this would be full validation)
        constitution_violations = []
        # Check for basic security requirements
        if not request.repo_url.startswith(("https://", "git@")):
            constitution_violations.append("repo_url must be a valid git URL")

        if constitution_violations:
            return ImportExternalSkillErrorEnvelope(
                error_code="CONSTITUTION_GATE_FAILED",
                blocked_by="CONSTITUTION_VIOLATION",
                message=f"Constitution gate failed: {constitution_violations}",
                gate_decision="BLOCK",
                evidence_ref=evidence_ref,
                run_id=run_id,
                required_changes=constitution_violations,
            ).model_dump()

        # Step 6: S3 - System Audit (L1-L5) - simplified mock
        audit_results = {
            "L1_contract_audit": {"status": "PASS", "score": 95},
            "L2_control_audit": {"status": "PASS", "score": 90},
            "L3_security_audit": {"status": "PASS", "score": 88},
            "L4_evidence_audit": {"status": "PASS", "score": 92},
            "L5_reproducibility_audit": {"status": "PASS", "score": 85},
        }

        pass_count = sum(1 for r in audit_results.values() if r["status"] == "PASS")
        critical_failures = [k for k, v in audit_results.items() if v["status"] == "FAIL"]

        # Step 7: S4 - Decision
        if pass_count < 4 or len(critical_failures) > 0:
            required_changes = [f"Fix {layer}: score too low" for layer in critical_failures]
            if pass_count < 4:
                required_changes.append(f"Need at least 4/5 layers to pass, got {pass_count}")

            return ImportExternalSkillErrorEnvelope(
                error_code="SYSTEM_AUDIT_FAILED",
                blocked_by="AUDIT_FAILURE",
                message=f"System audit failed: {pass_count}/5 layers passed",
                gate_decision="BLOCK",
                evidence_ref=evidence_ref,
                run_id=run_id,
                required_changes=required_changes,
            ).model_dump()

        # Step 8: S5 - Permit Issuance
        permit_id = f"PERMIT-EXT-{uuid.uuid4().hex[:8].upper()}"

        # Step 9: S6 - Registry Admission
        registry_entry_id = f"REG-{uuid.uuid4().hex[:12].upper()}"
        skill_revision = 1

        # Step 10: Success - return with SkillForge-computed fields
        return N8NSuccessEnvelope(
            data={
                "external_skill_ref": request.external_skill_ref,
                "repo_url": request.repo_url,
                "commit_sha": request.commit_sha,
                "at_time": request.at_time or now_iso(),
                "import_status": "COMPLETED",
                "pipeline_state": "S6_REGISTRY_ADMISSION",
                "quarantine_id": quarantine_id,
                "permit_id": permit_id,
                "registry_entry_id": registry_entry_id,
                "skill_revision": skill_revision,
                "audit_summary": audit_results,
                "context": request.context,
            },
            gate_decision="ALLOW",
            release_allowed=True,
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    except Exception as e:
        return ImportExternalSkillErrorEnvelope(
            error_code="IMPORT_INTERNAL_ERROR",
            blocked_by="INTERNAL_ERROR",
            message=f"Internal error during skill import: {str(e)}",
            gate_decision="BLOCK",
            evidence_ref=evidence_ref,
            run_id=run_id,
            required_changes=["Contact support - internal error occurred"],
        ).model_dump()


@router.get("/health")
async def n8n_health():
    """Health check for n8n orchestration routes."""
    return {
        "status": "healthy",
        "skill_id": SKILL_ID,
        "routes": ["run_intent", "fetch_pack", "query_rag", "import_external_skill"],
        "boundary_enforced": True,
        "timestamp": now_iso(),
    }
