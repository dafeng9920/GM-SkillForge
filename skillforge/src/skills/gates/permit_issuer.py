"""
PermitIssuer — Permit 签发服务，与 GatePermit 对接。

实现 permit_contract_v1.yml 签发侧契约：
- Fail-Closed: 条件不满足时拒绝签发，permit_token 必须为空
- Evidence-First: 每次签发尝试都生成 EvidenceRef
- Deterministic: 绑定 repo_url + commit_sha + run_id + intent_id

签发条件（硬约束，全部满足才签发）：
1. final_gate_decision 为 PASSED 或 PASSED_NO_PERMIT
2. release_blocked_by 为空
3. audit_pack_ref 非空
4. subject 字段完整（repo_url/commit_sha/run_id/intent_id）
5. ttl_seconds 合法（>0 且不超过上限 86400 秒）

错误码（I001-I005）：
- I001: ISSUE_CONDITION_NOT_MET - 签发条件不满足
- I002: SUBJECT_INCOMPLETE - subject 字段不完整
- I003: TTL_INVALID - TTL 非法
- I004: SIGNING_KEY_MISSING - 签名密钥缺失
- I005: SIGNING_FAILED - 签名失败

Contract: docs/2026-02-18/contracts/permit_contract_v1.yml
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


TOOL_REVISION = "1.0.0"
SERVICE_NAME = "permit_issuer"

# Error codes (I001-I005)
ISSUER_ERROR_CODES = {
    "I001": "ISSUE_CONDITION_NOT_MET",
    "I002": "SUBJECT_INCOMPLETE",
    "I003": "TTL_INVALID",
    "I004": "SIGNING_KEY_MISSING",
    "I005": "SIGNING_FAILED",
}

# Constants
MAX_TTL_SECONDS = 86400  # 24 hours max
PERMIT_ID_PREFIX = "PERMIT"
ISSUER_ID = "skillforge-permit-service"
ISSUER_TYPE = "AUTOMATED_GATE"

# ISO8601 UTC pattern
ISO8601_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

# Valid gate decisions for permit issuance
ISSUABLE_DECISIONS = {"PASSED", "PASSED_NO_PERMIT"}


@dataclass
class IssuerEvidenceRef:
    """Evidence reference for permit issuance."""
    issue_key: str
    source_locator: str
    content_hash: str
    tool_revision: str
    timestamp: str
    decision_snapshot: dict = field(default_factory=dict)


@dataclass
class IssueResult:
    """Result of permit issuance attempt."""
    success: bool
    permit_token: Optional[str] = None
    permit_id: Optional[str] = None
    issued_at: Optional[str] = None
    expires_at: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    evidence_refs: list[dict] = field(default_factory=list)
    signature: Optional[dict] = None


class PermitIssuer:
    """
    Permit 签发服务。

    确保只有满足签发条件的请求才能获得 permit。
    遵循 permit_contract_v1.yml 签发侧契约。
    """

    service_name: str = SERVICE_NAME
    tool_revision: str = TOOL_REVISION

    def __init__(
        self,
        signing_key: Optional[str] = None,
        key_id: str = "skillforge-permit-key-2026",
        max_ttl: int = MAX_TTL_SECONDS,
        signer: Optional[Callable[[bytes, bytes], bytes]] = None,
    ):
        """
        Initialize PermitIssuer.

        Args:
            signing_key: HMAC signing key (required for production)
            key_id: Key identifier for signature
            max_ttl: Maximum TTL in seconds
            signer: Optional custom signer function(payload, key) -> signature
        """
        self._signing_key = signing_key
        self._key_id = key_id
        self._max_ttl = max_ttl
        self._signer = signer if signer else self._default_hmac_signer

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """
        Validate permit issuance request.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: list[str] = []

        if not isinstance(input_data, dict):
            errors.append("SCHEMA_INVALID: input must be a dict")
            return errors

        # Check required fields
        if "final_gate_decision" not in input_data:
            errors.append("SCHEMA_INVALID: final_gate_decision is required")
        if "audit_pack_ref" not in input_data:
            errors.append("SCHEMA_INVALID: audit_pack_ref is required")
        if "ttl_seconds" not in input_data:
            errors.append("SCHEMA_INVALID: ttl_seconds is required")

        # Subject fields
        subject_fields = ["repo_url", "commit_sha", "run_id", "intent_id"]
        for f in subject_fields:
            if f not in input_data:
                errors.append(f"SCHEMA_INVALID: {f} is required")

        return errors

    def check_issuance_conditions(self, input_data: dict[str, Any]) -> tuple[bool, str, str]:
        """
        Check all issuance conditions.

        Returns: (can_issue, error_code, error_message)
        """
        # Condition 1: final_gate_decision must be issuable
        final_decision = input_data.get("final_gate_decision", "")
        if final_decision not in ISSUABLE_DECISIONS:
            return (
                False,
                "I001",
                f"Issuance condition not met: final_gate_decision={final_decision}"
            )

        # Condition 2: release_blocked_by must be empty/null
        release_blocked_by = input_data.get("release_blocked_by")
        if release_blocked_by is not None and release_blocked_by != "":
            return (
                False,
                "I001",
                f"Issuance condition not met: release_blocked_by={release_blocked_by}"
            )

        # Condition 3: audit_pack_ref must be non-empty
        audit_pack_ref = input_data.get("audit_pack_ref", "")
        if not audit_pack_ref or audit_pack_ref.strip() == "":
            return (
                False,
                "I001",
                "Issuance condition not met: audit_pack_ref is empty"
            )

        # Condition 4: subject fields must be complete
        subject_fields = {
            "repo_url": input_data.get("repo_url"),
            "commit_sha": input_data.get("commit_sha"),
            "run_id": input_data.get("run_id"),
            "intent_id": input_data.get("intent_id"),
        }
        missing_fields = [k for k, v in subject_fields.items() if not v]
        if missing_fields:
            return (
                False,
                "I002",
                f"Subject incomplete: missing {', '.join(missing_fields)}"
            )

        # Condition 5: ttl_seconds must be valid
        ttl_seconds = input_data.get("ttl_seconds", 0)
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            return (
                False,
                "I003",
                f"TTL invalid: ttl_seconds must be > 0, got {ttl_seconds}"
            )
        if ttl_seconds > self._max_ttl:
            return (
                False,
                "I003",
                f"TTL invalid: ttl_seconds={ttl_seconds} exceeds max {self._max_ttl}"
            )

        return (True, "", "")

    def issue_permit(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Issue a permit if all conditions are met.

        Fail-closed: If any condition fails, permit_token will be null.

        Args:
            input_data: {
                final_gate_decision: str,
                release_blocked_by: Optional[str],
                audit_pack_ref: str,
                repo_url: str,
                commit_sha: str,
                run_id: str,
                intent_id: str,
                allowed_actions: list[str],
                at_time: str,
                ttl_seconds: int,
                entry_path: Optional[str],
                environment: Optional[str],
                gate_profile: Optional[str],
                gate_count: Optional[int],
                evidence_count: Optional[int],
            }

        Returns:
            IssueResult as dict
        """
        timestamp = self._now_iso()
        result = IssueResult(success=False, evidence_refs=[])

        # Check issuance conditions
        can_issue, error_code, error_message = self.check_issuance_conditions(input_data)

        if not can_issue:
            result.error_code = error_code
            result.error_message = error_message
            result.evidence_refs = [self._create_evidence_ref(
                permit_id=None,
                result="FAILED",
                error_code=error_code,
                decision_snapshot={
                    "check": "issuance_conditions",
                    "passed": False,
                    "error_code": error_code,
                    "error_message": error_message,
                }
            )]
            return self._result_to_dict(result)

        # Check signing key availability
        if not self._signing_key:
            result.error_code = "I004"
            result.error_message = "Signing key is missing"
            result.evidence_refs = [self._create_evidence_ref(
                permit_id=None,
                result="FAILED",
                error_code="I004",
                decision_snapshot={
                    "check": "signing_key",
                    "passed": False,
                    "error": "key_missing",
                }
            )]
            return self._result_to_dict(result)

        # Build permit payload
        try:
            permit_id = self._generate_permit_id(timestamp)
            payload = self._build_permit_payload(input_data, permit_id, timestamp)
        except Exception as e:
            result.error_code = "I005"
            result.error_message = f"Failed to build permit payload: {e}"
            result.evidence_refs = [self._create_evidence_ref(
                permit_id=None,
                result="FAILED",
                error_code="I005",
                decision_snapshot={
                    "check": "payload_build",
                    "passed": False,
                    "error": str(e),
                }
            )]
            return self._result_to_dict(result)

        # Sign the permit
        try:
            signature_value = self._sign_permit(payload)
            signed_at = self._now_iso()

            payload["signature"] = {
                "algo": "HS256",
                "value": signature_value,
                "key_id": self._key_id,
                "signed_at": signed_at,
            }

            # Add revocation status
            payload["revocation"] = {
                "revoked": False,
                "revoked_at": None,
                "revoked_by": None,
                "reason": None,
            }

        except Exception as e:
            result.error_code = "I005"
            result.error_message = f"Signing failed: {e}"
            result.evidence_refs = [self._create_evidence_ref(
                permit_id=permit_id,
                result="FAILED",
                error_code="I005",
                decision_snapshot={
                    "check": "signing",
                    "passed": False,
                    "error": str(e),
                }
            )]
            return self._result_to_dict(result)

        # Success
        result.success = True
        result.permit_token = json.dumps(payload, separators=(',', ':'))
        result.permit_id = permit_id
        result.issued_at = payload["issued_at"]
        result.expires_at = payload["expires_at"]
        result.signature = payload["signature"]
        result.evidence_refs = [self._create_evidence_ref(
            permit_id=permit_id,
            result="ISSUED",
            error_code=None,
            decision_snapshot={
                "check": "issuance",
                "passed": True,
                "permit_id": permit_id,
                "expires_at": payload["expires_at"],
            }
        )]

        return self._result_to_dict(result)

    def _build_permit_payload(
        self,
        input_data: dict[str, Any],
        permit_id: str,
        timestamp: str,
    ) -> dict[str, Any]:
        """Build the permit payload (without signature and revocation)."""
        ttl_seconds = input_data["ttl_seconds"]
        at_time = input_data.get("at_time", timestamp)

        # Calculate expires_at using UTC epoch
        import calendar
        issued_time = time.gmtime()
        issued_epoch = calendar.timegm(issued_time)  # Use calendar.timegm for UTC
        expires_epoch = issued_epoch + ttl_seconds
        expires_time = time.gmtime(expires_epoch)
        expires_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", expires_time)

        return {
            "permit_id": permit_id,
            "issuer": {
                "issuer_id": ISSUER_ID,
                "issuer_type": ISSUER_TYPE,
            },
            "issued_at": timestamp,
            "expires_at": expires_at,
            "subject": {
                "repo_url": input_data["repo_url"],
                "commit_sha": input_data["commit_sha"],
                "run_id": input_data["run_id"],
                "intent_id": input_data["intent_id"],
                "entry_path": input_data.get("entry_path"),
            },
            "scope": {
                "allowed_actions": input_data.get("allowed_actions", ["release"]),
                "environment": input_data.get("environment", "development"),
                "gate_profile": input_data.get("gate_profile", "batch2_8gate"),
            },
            "constraints": {
                "at_time": at_time,
                "max_release_count": 1,
                "time_window_seconds": ttl_seconds,
            },
            "decision_binding": {
                "final_gate_decision": input_data["final_gate_decision"],
                "gate_count": input_data.get("gate_count", 8),
                "audit_pack_ref": input_data["audit_pack_ref"],
                "evidence_count": input_data.get("evidence_count", 8),
            },
        }

    def _sign_permit(self, payload: dict[str, Any]) -> str:
        """Sign the permit payload using HMAC-SHA256."""
        # Create canonical JSON for signing (exclude signature and revocation)
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))

        # Ensure signing key is available (should be checked before calling this)
        if not self._signing_key:
            raise ValueError("Signing key is not configured")

        key_bytes = self._signing_key.encode('utf-8') if isinstance(self._signing_key, str) else self._signing_key
        signature_bytes = self._signer(canonical.encode('utf-8'), key_bytes)
        return base64.b64encode(signature_bytes).decode('utf-8')

    @staticmethod
    def _default_hmac_signer(payload: bytes, key: bytes) -> bytes:
        """Default HMAC-SHA256 signer."""
        return hmac.new(key, payload, hashlib.sha256).digest()

    def _generate_permit_id(self, timestamp: str) -> str:
        """Generate unique permit ID."""
        date_part = timestamp[:10].replace("-", "")
        # Use UUID for uniqueness instead of sequence
        unique_part = uuid.uuid4().hex[:8].upper()
        return f"{PERMIT_ID_PREFIX}-{date_part}-{unique_part}"

    def _now_iso(self) -> str:
        """Return ISO-8601 UTC timestamp."""
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _create_evidence_ref(
        self,
        permit_id: Optional[str],
        result: str,
        error_code: Optional[str],
        decision_snapshot: dict,
    ) -> dict:
        """Create evidence reference for issuance attempt."""
        timestamp = self._now_iso()
        content = json.dumps({
            "permit_id": permit_id,
            "result": result,
            "error_code": error_code,
            "timestamp": timestamp,
            "decision_snapshot": decision_snapshot,
        }, sort_keys=True)
        content_hash = self._compute_hash(content)

        # Don't leak signing key in hash
        issue_key = f"PERMIT-ISSUE-{permit_id or 'NONE'}-{int(time.time())}"

        return {
            "issue_key": issue_key,
            "source_locator": f"issuer://{self.service_name}",
            "content_hash": content_hash,
            "tool_revision": self.tool_revision,
            "timestamp": timestamp,
            "decision_snapshot": decision_snapshot,
        }

    def _result_to_dict(self, result: IssueResult) -> dict[str, Any]:
        """Convert IssueResult to dictionary."""
        return {
            "success": result.success,
            "permit_token": result.permit_token,
            "permit_id": result.permit_id,
            "issued_at": result.issued_at,
            "expires_at": result.expires_at,
            "error_code": result.error_code,
            "error_message": result.error_message,
            "evidence_refs": result.evidence_refs,
            "signature": result.signature,
        }


# Convenience function
def issue_permit(
    final_gate_decision: str,
    audit_pack_ref: str,
    repo_url: str,
    commit_sha: str,
    run_id: str,
    intent_id: str,
    ttl_seconds: int,
    allowed_actions: Optional[list[str]] = None,
    signing_key: Optional[str] = None,
    **kwargs,
) -> dict[str, Any]:
    """
    Convenience function to issue a permit.

    Args:
        final_gate_decision: Gate decision result
        audit_pack_ref: Audit pack reference
        repo_url: Repository URL
        commit_sha: Git commit SHA
        run_id: Run ID
        intent_id: Intent ID
        ttl_seconds: Time-to-live in seconds
        allowed_actions: List of allowed actions
        signing_key: HMAC signing key
        **kwargs: Additional fields (entry_path, environment, gate_profile, etc.)

    Returns:
        IssueResult as dict
    """
    issuer = PermitIssuer(signing_key=signing_key)

    input_data = {
        "final_gate_decision": final_gate_decision,
        "audit_pack_ref": audit_pack_ref,
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "run_id": run_id,
        "intent_id": intent_id,
        "ttl_seconds": ttl_seconds,
        "allowed_actions": allowed_actions or ["release"],
        **kwargs,
    }

    return issuer.issue_permit(input_data)


# CLI entry point
def main():
    """CLI entry point for PermitIssuer."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="PermitIssuer - Permit issuance service")
    parser.add_argument("--signing-key", required=True, help="HMAC signing key")
    parser.add_argument("--key-id", default="skillforge-permit-key-2026", help="Key ID")
    parser.add_argument("--final-decision", required=True, help="Final gate decision")
    parser.add_argument("--audit-pack-ref", required=True, help="Audit pack reference")
    parser.add_argument("--repo-url", required=True, help="Repository URL")
    parser.add_argument("--commit-sha", required=True, help="Git commit SHA")
    parser.add_argument("--run-id", required=True, help="Run ID")
    parser.add_argument("--intent-id", required=True, help="Intent ID")
    parser.add_argument("--ttl", type=int, default=3600, help="TTL in seconds")
    parser.add_argument("--actions", default="release", help="Allowed actions (comma-separated)")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    issuer = PermitIssuer(signing_key=args.signing_key, key_id=args.key_id)

    input_data = {
        "final_gate_decision": args.final_decision,
        "audit_pack_ref": args.audit_pack_ref,
        "repo_url": args.repo_url,
        "commit_sha": args.commit_sha,
        "run_id": args.run_id,
        "intent_id": args.intent_id,
        "ttl_seconds": args.ttl,
        "allowed_actions": args.actions.split(","),
    }

    result = issuer.issue_permit(input_data)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
