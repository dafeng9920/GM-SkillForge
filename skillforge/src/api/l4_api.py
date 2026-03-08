"""
L4 API - FastAPI application for L4 frontend-backend integration.

Exposes three core endpoints:
- POST /cognition/generate -> 10d cognition assessment
- POST /work/adopt -> adopt reason card as work item
- POST /work/execute -> execute work item with permit validation

Unified error envelope format:
- Success: {"ok": true, "data": {...}, "gate_decision": "...", "release_allowed": bool, "evidence_ref": "...", "run_id": "..."}
- Failure: {"ok": false, "error_code": "...", "blocked_by": "...", "message": "...", "evidence_ref": "...", "run_id": "..."}
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import n8n orchestration routes
from .routes.n8n_orchestration import router as n8n_router

# Import existing gate modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.gates.gate_permit import GatePermit

# LLM client imports
from llm.client import generate_10d, LLMConfigError, LLMCallError, check_llm_config

# ============================================================================
# Constants
# ============================================================================

API_VERSION = "v1"
RUN_ID_PREFIX = "RUN-L4"

ERROR_CODE_MAP = {
    "E001": "PERMIT_REQUIRED",
    "E002": "PERMIT_INVALID",
    "E003": "PERMIT_INVALID",
    "E004": "PERMIT_EXPIRED",
    "E005": "PERMIT_SCOPE_MISMATCH",
    "E006": "PERMIT_SUBJECT_MISMATCH",
    "E007": "PERMIT_REVOKED",
}

# LLM-specific error codes
LLM_ERROR_CODES = {
    "L4_LLM_CONFIG_MISSING": "LLM configuration is missing or incomplete",
    "L4_LLM_CALL_FAILED": "LLM API call failed",
}

# ============================================================================
# Pydantic Models
# ============================================================================

class CognitionGenerateRequest(BaseModel):
    """Request for cognition generation."""
    repo_url: str
    commit_sha: str
    at_time: Optional[str] = None
    rubric_version: str = "1.0.0"
    requester_id: str
    context: Optional[dict] = None


class WorkAdoptRequest(BaseModel):
    """Request for adopting a reason card as work item."""
    reason_card_id: str
    requester_id: str
    context: Optional[dict] = None
    options: Optional[dict] = None


class ExecutionContext(BaseModel):
    """Execution context for work execution."""
    repo_url: str
    commit_sha: str
    run_id: str
    requested_action: str = "release"


class WorkExecuteRequest(BaseModel):
    """Request for executing a work item."""
    work_item_id: str
    permit_token: Optional[str] = None
    execution_context: ExecutionContext


# ============================================================================
# Response Models
# ============================================================================

class SuccessEnvelope(BaseModel):
    """Success response envelope."""
    ok: bool = True
    data: dict
    gate_decision: str
    release_allowed: bool
    evidence_ref: str
    run_id: str


class ErrorEnvelope(BaseModel):
    """Error response envelope."""
    ok: bool = False
    error_code: str
    blocked_by: str
    message: str
    evidence_ref: Optional[str] = None
    run_id: str


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="SkillForge L4 API",
    description="L4 Governance API for frontend-backend integration",
    version=API_VERSION,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include n8n orchestration routes
app.include_router(n8n_router)


# ============================================================================
# Helper Functions
# ============================================================================

def generate_run_id() -> str:
    """Generate a unique run ID."""
    ts = int(time.time())
    uid = uuid.uuid4().hex[:8].upper()
    return f"{RUN_ID_PREFIX}-{ts}-{uid}"


def generate_evidence_ref(prefix: str = "EV") -> str:
    """Generate an evidence reference."""
    ts = int(time.time())
    uid = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-L4-{ts}-{uid}"


def generate_work_item_id() -> str:
    """Generate a work item ID."""
    uid = uuid.uuid4().hex[:8].upper()
    return f"WI-{uid}"


def now_iso() -> str:
    """Return ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ============================================================================
# API Routes
# ============================================================================

@app.post("/api/v1/cognition/generate")
async def cognition_generate(request: CognitionGenerateRequest):
    """
    Link A: Generate 10-dimensional cognition assessment.

    Input: Free text + context
    Output: 10d_result conforming to 10d_schema.json

    Error handling:
    - L4_LLM_CONFIG_MISSING: LLM configuration incomplete (fail-closed)
    - L4_LLM_CALL_FAILED: LLM API call failed (fail-closed)
    """
    run_id = generate_run_id()
    evidence_ref = generate_evidence_ref("EV-COG")

    # Build input for LLM
    user_input = f"Repository: {request.repo_url}\nCommit: {request.commit_sha}"
    if request.context:
        user_input += f"\nContext: {request.context}"

    context = {
        "repo_url": request.repo_url,
        "commit_sha": request.commit_sha,
        "requester_id": request.requester_id,
        "rubric_version": request.rubric_version,
    }

    # Try to generate using LLM
    try:
        llm_result = generate_10d(user_input, context=context)

        # Convert LLM dimensions to API format
        dimensions = []
        for dim in llm_result["dimensions"]:
            threshold = 60
            score = dim["score"]
            verdict = "PASS" if score >= threshold else "FAIL"
            dimensions.append({
                "dim_id": dim["dim_id"],
                "label": dim["name"],
                "summary": dim.get("summary", ""),
                "score": score,
                "threshold": threshold,
                "verdict": verdict,
                "evidence_hint": dim.get("evidence_hint", ""),
                "evidence_ref": f"AuditPack/cognition/{evidence_ref}/{dim['dim_id']}.md"
            })

        # Add LLM metadata to result
        llm_metadata = {
            "model": llm_result.get("model", "unknown"),
            "provider": llm_result.get("provider", "unknown"),
            "latency_ms": llm_result.get("latency_ms", 0),
            "trace_id": llm_result.get("trace_id", ""),
        }

    except LLMConfigError as e:
        # Configuration missing - return error envelope (fail-closed)
        return ErrorEnvelope(
            error_code="L4_LLM_CONFIG_MISSING",
            blocked_by="LLM_UNAVAILABLE",
            message=f"LLM configuration incomplete: {e.message}",
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    except LLMCallError as e:
        # LLM call failed - return error envelope (fail-closed)
        return ErrorEnvelope(
            error_code="L4_LLM_CALL_FAILED",
            blocked_by="LLM_UNAVAILABLE",
            message=f"LLM API call failed: {e.message}",
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    # Calculate pass/fail status
    pass_count = sum(1 for d in dimensions if d["verdict"] == "PASS")
    critical_passed = all(
        d["verdict"] == "PASS"
        for d in dimensions
        if d["dim_id"] in ["L1", "L3", "L5", "L10"]
    )

    status = "PASSED" if pass_count >= 8 and critical_passed else "REJECTED"
    rejection_reasons = []
    if status == "REJECTED":
        if pass_count < 8:
            rejection_reasons.append(f"Insufficient pass count: {pass_count}/8")
        failed_critical = [d["dim_id"] for d in dimensions if d["dim_id"] in ["L1", "L3", "L5", "L10"] and d["verdict"] == "FAIL"]
        if failed_critical:
            rejection_reasons.append(f"Critical dimension failures: {', '.join(failed_critical)}")

    result = {
        "intent_id": "cognition_10d",
        "status": status,
        "repo_url": request.repo_url,
        "commit_sha": request.commit_sha,
        "at_time": request.at_time or now_iso(),
        "rubric_version": request.rubric_version,
        "dimensions": dimensions,
        "overall_pass_count": pass_count,
        "rejection_reasons": rejection_reasons,
        "audit_pack_ref": f"AuditPack/cognition/{evidence_ref}/",
        "generated_at": now_iso(),
        "llm_metadata": llm_metadata,
    }

    return SuccessEnvelope(
        data=result,
        gate_decision="ALLOW",
        release_allowed=True,
        evidence_ref=evidence_ref,
        run_id=run_id,
    ).model_dump()


@app.post("/api/v1/work/adopt")
async def work_adopt(request: WorkAdoptRequest):
    """
    Link B: Adopt a reason card as work item.

    Input: 10d_result (or subset)
    Output: work_item conforming to work_item_schema.json or blocking error
    """
    run_id = generate_run_id()
    evidence_ref = generate_evidence_ref("EV-ADOPT")
    work_item_id = generate_work_item_id()

    # Validate reason_card_id format
    if not request.reason_card_id.startswith("RC-"):
        return ErrorEnvelope(
            error_code="E002",
            blocked_by="PERMIT_INVALID",
            message="Invalid reason_card_id format, must start with RC-",
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    # Create work item from adoption
    work_item = {
        "work_item_id": work_item_id,
        "intent": f"Migrated from {request.reason_card_id}",
        "inputs": {
            "repo_url": {
                "type": "string",
                "required": True,
                "description": "Repository URL"
            }
        },
        "constraints": {
            "timeout_seconds": 3600,
            "max_retries": 3,
            "fail_mode": "CLOSED",
            "blocking": True
        },
        "acceptance": {
            "criteria": [
                {
                    "criterion_id": "AC-01",
                    "description": "Work item must be executed with valid permit",
                    "validation": {"type": "schema", "schema_ref": "permit_contract_v1"},
                    "mandatory": True
                }
            ]
        },
        "evidence": {
            "evidence_refs": [
                {
                    "ref_id": evidence_ref,
                    "type": "audit_pack",
                    "path": f"AuditPack/adoptions/{work_item_id}/"
                }
            ]
        },
        "adopted_from": {
            "reason_card_id": request.reason_card_id,
            "migration_timestamp": now_iso(),
            "migration_version": "1.0.0",
            "verified": True,
            "verified_by": "system",
            "verified_at": now_iso()
        }
    }

    return SuccessEnvelope(
        data={
            "work_item_id": work_item_id,
            "status": "ADOPTED",
            "work_item": work_item,
            "adopted_from": work_item["adopted_from"],
            "evidence_refs": work_item["evidence"]["evidence_refs"],
            "created_at": now_iso()
        },
        gate_decision="ALLOW",
        release_allowed=True,
        evidence_ref=evidence_ref,
        run_id=run_id,
    ).model_dump()


@app.post("/api/v1/work/execute")
async def work_execute(request: WorkExecuteRequest):
    """
    Link C: Execute work item with permit validation.

    Input: work_item + permit_token + execution_context
    Output: gate_decision + release_allowed + receipt + evidence_ref

    Blocking rules:
    - E001: No permit -> release_allowed=false
    - E003: Bad signature -> release_allowed=false
    """
    run_id = generate_run_id()
    evidence_ref = generate_evidence_ref("EV-EXEC")

    # Get execution context
    ctx = request.execution_context

    # Step 1: Check permit existence (E001)
    if request.permit_token is None or request.permit_token == "":
        return ErrorEnvelope(
            error_code="E001",
            blocked_by="PERMIT_REQUIRED",
            message="Permit token is required for execution",
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    # Step 2: Validate permit with GatePermit
    gate = GatePermit()

    validation_input = {
        "permit_token": request.permit_token,
        "repo_url": ctx.repo_url,
        "commit_sha": ctx.commit_sha,
        "run_id": ctx.run_id,
        "requested_action": ctx.requested_action,
        "current_time": now_iso(),
    }

    try:
        result = gate.execute(validation_input)

        if not result.get("release_allowed", False):
            error_code = result.get("error_code", "E002")
            blocked_by = ERROR_CODE_MAP.get(error_code, "PERMIT_INVALID")
            message = result.get("reason", "Permit validation failed")

            return ErrorEnvelope(
                error_code=error_code,
                blocked_by=blocked_by,
                message=message,
                evidence_ref=evidence_ref,
                run_id=run_id,
            ).model_dump()

        # Success case
        return SuccessEnvelope(
            data={
                "work_item_id": request.work_item_id,
                "execution_status": "COMPLETED",
                "receipt": {
                    "gate_decision": result.get("gate_decision"),
                    "permit_id": result.get("permit_id"),
                    "validation_timestamp": result.get("validation_timestamp"),
                }
            },
            gate_decision=result.get("gate_decision", "ALLOW"),
            release_allowed=True,
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()

    except Exception as e:
        return ErrorEnvelope(
            error_code="E002",
            blocked_by="PERMIT_INVALID",
            message=f"Permit validation error: {str(e)}",
            evidence_ref=evidence_ref,
            run_id=run_id,
        ).model_dump()


# ============================================================================
# Health Check
# ============================================================================

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": API_VERSION,
        "timestamp": now_iso()
    }


# ============================================================================
# Main Entry
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
