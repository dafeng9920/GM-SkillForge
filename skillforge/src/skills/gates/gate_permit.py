"""
GatePermit — Permit 校验 Gate，确保"无 permit 不可发布"。

Gate Group: delivery
Position: G9 (在 pack_audit_and_publish G8 之前执行)

实现 permit_contract_v1.yml 契约：
- Fail-Closed: permit 缺失/过期/签名无效/作用域不匹配/主体不匹配/已撤销 => 一律阻断
- Evidence-First: 每次校验生成 EvidenceRef
- Deterministic: 绑定 repo_url + commit_sha + run_id

错误码映射（7项）：
- E001: permit 缺失 -> PERMIT_REQUIRED
- E002: permit 格式无效 -> PERMIT_INVALID
- E003: 签名无效 -> PERMIT_INVALID
- E004: permit 过期 -> PERMIT_EXPIRED
- E005: scope 不匹配 -> PERMIT_SCOPE_MISMATCH
- E006: subject 不匹配 -> PERMIT_SUBJECT_MISMATCH
- E007: permit 已撤销 -> PERMIT_REVOKED

Contract: docs/2026-02-18/contracts/permit_contract_v1.yml
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import time
from dataclasses import dataclass, field
# Path import removed - not needed
from typing import Any, Callable, Optional

from ..experience_capture import FixKind, capture_gate_event

TOOL_REVISION = "1.0.0"
GATE_NAME = "permit_gate"

# Error codes (E001-E007)
ERROR_CODES = {
    "E001": "PERMIT_REQUIRED",
    "E002": "PERMIT_INVALID",
    "E003": "PERMIT_INVALID",
    "E004": "PERMIT_EXPIRED",
    "E005": "PERMIT_SCOPE_MISMATCH",
    "E006": "PERMIT_SUBJECT_MISMATCH",
    "E007": "PERMIT_REVOKED",
}

# ISO8601 UTC pattern
ISO8601_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')


@dataclass
class EvidenceRef:
    """Evidence reference following gate_interface_v1.yaml schema."""
    issue_key: str
    source_locator: str
    content_hash: str
    tool_revision: str
    timestamp: str
    decision_snapshot: dict = field(default_factory=dict)


@dataclass
class PermitValidationResult:
    """Permit validation result per permit_contract_v1.yml."""
    gate_name: str
    gate_decision: str  # ALLOW | BLOCK
    permit_validation_status: str  # VALID | INVALID
    release_allowed: bool
    release_blocked_by: Optional[str]
    error_code: Optional[str]
    evidence_refs: list[dict]
    validation_timestamp: str


# Signature verifier (可插拔)
def _stub_signature_verifier(permit: dict, public_key_id: Optional[str] = None) -> bool:
    """
    Signature verifier with fallback strategy.

    策略：
    1. 检查结构完整性（algo, value, key_id 必填）
    2. algo in {RS256, ES256}：按结构通过（兼容现有 fixtures）
    3. algo == HS256：
       - 若有 PERMIT_HS256_KEY，做真验签（能抓篡改）
       - 若无 key，退回结构校验（兼容历史单测）
    """
    sig = permit.get("signature", {})
    required_sig_fields = ["algo", "value", "key_id"]
    for f in required_sig_fields:
        if f not in sig or not sig.get(f):
            return False

    algo = sig.get("algo")
    if algo not in ("RS256", "ES256", "HS256"):
        return False

    # RS256/ES256: 结构校验通过即可（兼容现有 fixtures）
    if algo != "HS256":
        return False
    key = os.getenv("PERMIT_HS256_KEY")
    if not key:
        return False

    # 有 key 时做真验签
    payload = dict(permit)
    payload.pop("signature", None)
    payload.pop("revocation", None)
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    expected = base64.b64encode(
        hmac.new(key.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).digest()
    ).decode("utf-8")

    return hmac.compare_digest(expected, sig["value"])


class GatePermit:
    """
    Permit 校验 Gate。

    确保"无 permit 不可发布"的硬约束落地。
    遵循 permit_contract_v1.yml 契约。
    """

    node_id: str = "permit_gate"
    gate_name: str = GATE_NAME
    tool_revision: str = TOOL_REVISION

    # Evidence storage path
    evidence_base_path: str = "AuditPack/evidence"

    def __init__(
        self,
        evidence_base_path: Optional[str] = None,
        signature_verifier: Optional[Callable[[dict], bool]] = None,
    ):
        if evidence_base_path:
            self.evidence_base_path = evidence_base_path
        # Store signature verifier as instance attribute
        self._signature_verifier = signature_verifier if signature_verifier else _stub_signature_verifier

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """
        Validate permit validation request.

        Returns list of validation error strings. Empty list = valid.
        """
        errors: list[str] = []

        if not isinstance(input_data, dict):
            errors.append("SCHEMA_INVALID: input must be a dict")
            return errors

        # Required execution context fields
        required_context = ["repo_url", "commit_sha", "run_id", "requested_action"]
        for field in required_context:
            if field not in input_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        # permit_token can be null/empty (will trigger E001)
        # current_time is optional (defaults to now)

        return errors

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute permit validation gate.

        校验流程（按 permit_contract_v1_spec.md 3.1）：
        Step 1: 存在性检查 (E001)
        Step 2: 解析 Permit (E002)
        Step 3: 必填字段检查 (E002)
        Step 4: 签名校验 (E003)
        Step 5: 过期检查 (E004)
        Step 6: 主体匹配检查 (E006)
        Step 7: 作用域匹配检查 (E005)
        Step 8: 撤销检查 (E007)
        Step 9: 生成 Evidence
        Step 10: 返回结果
        """
        timestamp = self._now_iso()
        permit_token = input_data.get("permit_token")
        current_time = input_data.get("current_time") or timestamp

        # Extract execution context
        repo_url = input_data.get("repo_url", "")
        commit_sha = input_data.get("commit_sha", "")
        run_id = input_data.get("run_id", "")
        requested_action = input_data.get("requested_action", "release")

        # Step 1: 存在性检查 (E001)
        if permit_token is None or permit_token == "":
            return self._build_blocked_result(
                error_code="E001",
                timestamp=timestamp,
                reason="Permit token is missing",
                decision_snapshot={
                    "check": "existence",
                    "permit_token_present": False,
                }
            )

        # Step 2: 解析 Permit (E002)
        try:
            if isinstance(permit_token, str):
                permit = json.loads(permit_token)
            elif isinstance(permit_token, dict):
                permit = permit_token
            else:
                return self._build_blocked_result(
                    error_code="E002",
                    timestamp=timestamp,
                    reason="Permit token format invalid",
                    decision_snapshot={
                        "check": "parse",
                        "permit_token_type": type(permit_token).__name__,
                    }
                )
        except json.JSONDecodeError:
            return self._build_blocked_result(
                error_code="E002",
                timestamp=timestamp,
                reason="Permit token JSON parse failed",
                decision_snapshot={
                    "check": "parse",
                    "error": "JSONDecodeError",
                }
            )

        # Step 3: 必填字段检查 (E002)
        required_fields = [
            "permit_id",
            "expires_at",
            "subject.repo_url",
            "subject.commit_sha",
            "subject.run_id",
            "scope.allowed_actions",
            "revocation.revoked",
        ]
        for field_path in required_fields:
            if not self._has_nested_field(permit, field_path):
                return self._build_blocked_result(
                    error_code="E002",
                    timestamp=timestamp,
                    reason=f"Required field missing: {field_path}",
                    decision_snapshot={
                        "check": "required_fields",
                        "missing_field": field_path,
                    }
                )

        # Step 4: 签名校验 (E003)
        if not self._signature_verifier(permit):
            return self._build_blocked_result(
                error_code="E003",
                timestamp=timestamp,
                reason="Signature verification failed",
                decision_snapshot={
                    "check": "signature",
                    "algo": permit.get("signature", {}).get("algo"),
                    "key_id": permit.get("signature", {}).get("key_id"),
                }
            )

        # Step 5: 过期检查 (E004)
        expires_at = permit.get("expires_at", "")
        if not self._is_expired(expires_at, current_time):
            pass  # Not expired
        else:
            return self._build_blocked_result(
                error_code="E004",
                timestamp=timestamp,
                reason="Permit has expired",
                decision_snapshot={
                    "check": "expiry",
                    "expires_at": expires_at,
                    "current_time": current_time,
                }
            )

        # Step 6: 主体匹配检查 (E006)
        subject = permit.get("subject", {})
        subject_mismatches = []
        if subject.get("repo_url") != repo_url:
            subject_mismatches.append("repo_url")
        if subject.get("commit_sha") != commit_sha:
            subject_mismatches.append("commit_sha")
        if subject.get("run_id") != run_id:
            subject_mismatches.append("run_id")

        if subject_mismatches:
            return self._build_blocked_result(
                error_code="E006",
                timestamp=timestamp,
                reason=f"Subject mismatch: {', '.join(subject_mismatches)}",
                decision_snapshot={
                    "check": "subject_match",
                    "mismatches": subject_mismatches,
                    "permit_subject": subject,
                    "execution_context": {
                        "repo_url": repo_url,
                        "commit_sha": commit_sha,
                        "run_id": run_id,
                    }
                }
            )

        # Step 7: 作用域匹配检查 (E005)
        allowed_actions = permit.get("scope", {}).get("allowed_actions", [])
        if requested_action not in allowed_actions:
            return self._build_blocked_result(
                error_code="E005",
                timestamp=timestamp,
                reason=f"Action '{requested_action}' not in allowed_actions",
                decision_snapshot={
                    "check": "scope_match",
                    "requested_action": requested_action,
                    "allowed_actions": allowed_actions,
                }
            )

        # Step 8: 撤销检查 (E007)
        revoked = permit.get("revocation", {}).get("revoked", False)
        if revoked:
            return self._build_blocked_result(
                error_code="E007",
                timestamp=timestamp,
                reason="Permit has been revoked",
                decision_snapshot={
                    "check": "revocation",
                    "revoked": True,
                    "revoked_at": permit.get("revocation", {}).get("revoked_at"),
                    "reason": permit.get("revocation", {}).get("reason"),
                }
            )

        # Step 9: 生成 Evidence
        evidence_ref = self._create_evidence_ref(
            permit_id=permit.get("permit_id"),
            result="VALID",
            decision_snapshot={
                "check": "all_passed",
                "permit_id": permit.get("permit_id"),
                "subject_match": True,
                "scope_match": True,
                "not_expired": True,
                "not_revoked": True,
            }
        )

        # Step 10: 返回结果
        result = {
            "gate_name": self.gate_name,
            "gate_decision": "ALLOW",
            "permit_validation_status": "VALID",
            "release_allowed": True,
            "release_blocked_by": None,
            "error_code": None,
            "evidence_refs": [evidence_ref],
            "validation_timestamp": timestamp,
            "permit_id": permit.get("permit_id"),
        }
        capture_gate_event(
            gate_node=self.gate_name,
            gate_decision=result["gate_decision"],
            evidence_refs=result["evidence_refs"],
            fix_kind=FixKind.GATE_DECISION,
            summary="permit validation passed",
            metadata={"permit_id": permit.get("permit_id")},
        )
        return result

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate output against permit_contract_v1.yml schema."""
        errors: list[str] = []

        if not isinstance(output_data, dict):
            errors.append("SCHEMA_INVALID: output must be a dict")
            return errors

        required_fields = [
            "gate_name",
            "gate_decision",
            "permit_validation_status",
            "release_allowed",
            "evidence_refs",
            "validation_timestamp",
        ]
        for field in required_fields:
            if field not in output_data:
                errors.append(f"SCHEMA_INVALID: {field} is required")

        # gate_decision validation
        gate_decision = output_data.get("gate_decision")
        if gate_decision not in ("ALLOW", "BLOCK"):
            errors.append("SCHEMA_INVALID: gate_decision must be 'ALLOW' or 'BLOCK'")

        # permit_validation_status validation
        status = output_data.get("permit_validation_status")
        if status and status not in ("VALID", "INVALID"):
            errors.append("SCHEMA_INVALID: permit_validation_status must be 'VALID' or 'INVALID'")

        # release_allowed must be boolean
        release_allowed = output_data.get("release_allowed")
        if not isinstance(release_allowed, bool):
            errors.append("SCHEMA_INVALID: release_allowed must be a boolean")

        # evidence_refs validation
        evidence_refs = output_data.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            errors.append("SCHEMA_INVALID: evidence_refs must be an array")

        return errors

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _now_iso(self) -> str:
        """Return ISO-8601 UTC timestamp."""
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _has_nested_field(self, obj: dict, path: str) -> bool:
        """Check if nested field exists (e.g., 'subject.repo_url')."""
        parts = path.split(".")
        current = obj
        for part in parts:
            if not isinstance(current, dict):
                return False
            if part not in current:
                return False
            current = current[part]
        return True

    def _is_expired(self, expires_at: str, current_time: str) -> bool:
        """Check if permit is expired."""
        try:
            # Simple string comparison works for ISO8601 UTC format
            return current_time > expires_at
        except Exception:
            return True  # Fail-closed: treat invalid format as expired

    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _create_evidence_ref(
        self,
        permit_id: str,
        result: str,
        decision_snapshot: dict,
    ) -> dict:
        """Create evidence reference for permit validation."""
        timestamp = self._now_iso()
        content = json.dumps({
            "permit_id": permit_id,
            "result": result,
            "timestamp": timestamp,
            "decision_snapshot": decision_snapshot,
        }, sort_keys=True)
        content_hash = self._compute_hash(content)
        issue_key = f"PERMIT-VAL-{permit_id}-{int(time.time())}"

        return {
            "issue_key": issue_key,
            "source_locator": f"permit://{permit_id}",
            "content_hash": content_hash,
            "tool_revision": self.tool_revision,
            "timestamp": timestamp,
            "decision_snapshot": decision_snapshot,
        }

    def _build_blocked_result(
        self,
        error_code: str,
        timestamp: str,
        reason: str,
        decision_snapshot: dict,
    ) -> dict[str, Any]:
        """Build a BLOCKED result with release_allowed=false."""
        blocked_by = ERROR_CODES.get(error_code, "PERMIT_INVALID")

        evidence_ref = {
            "issue_key": f"PERMIT-BLOCK-{error_code}-{int(time.time())}",
            "source_locator": "permit://none",
            "content_hash": self._compute_hash(reason),
            "tool_revision": self.tool_revision,
            "timestamp": timestamp,
            "decision_snapshot": decision_snapshot,
        }

        result = {
            "gate_name": self.gate_name,
            "gate_decision": "BLOCK",
            "permit_validation_status": "INVALID",
            "release_allowed": False,
            "release_blocked_by": blocked_by,
            "error_code": error_code,
            "evidence_refs": [evidence_ref],
            "validation_timestamp": timestamp,
            "reason": reason,
        }
        capture_gate_event(
            gate_node=self.gate_name,
            gate_decision=result["gate_decision"],
            evidence_refs=result["evidence_refs"],
            error_code=error_code,
            fix_kind=FixKind.GATE_DECISION,
            summary=reason,
        )
        return result


# Convenience function
def validate_permit(
    permit_token: Optional[str | dict],
    repo_url: str,
    commit_sha: str,
    run_id: str,
    requested_action: str = "release",
    current_time: Optional[str] = None,
) -> dict[str, Any]:
    """
    Convenience function to validate a permit.

    Matches permit_contract_v1.yml signature.
    """
    gate = GatePermit()

    input_data = {
        "permit_token": permit_token,
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "run_id": run_id,
        "requested_action": requested_action,
        "current_time": current_time,
    }

    return gate.execute(input_data)


# CLI entry point
def main():
    """CLI entry point for GatePermit."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="GatePermit - Permit validation gate")
    parser.add_argument("--permit-file", help="JSON file containing permit token")
    parser.add_argument("--repo-url", required=True, help="Repository URL")
    parser.add_argument("--commit-sha", required=True, help="Git commit SHA")
    parser.add_argument("--run-id", required=True, help="Run ID")
    parser.add_argument("--action", default="release", help="Requested action")
    parser.add_argument("--current-time", help="Current time (ISO8601 UTC)")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    gate = GatePermit()

    # Load permit token
    permit_token = None
    if args.permit_file:
        try:
            with open(args.permit_file, "r", encoding="utf-8") as f:
                permit_token = json.load(f)
        except Exception as e:
            print(f"Error loading permit file: {e}", file=sys.stderr)
            sys.exit(1)

    input_data = {
        "permit_token": permit_token,
        "repo_url": args.repo_url,
        "commit_sha": args.commit_sha,
        "run_id": args.run_id,
        "requested_action": args.action,
        "current_time": args.current_time,
    }

    # Validate input
    validation_errors = gate.validate_input(input_data)
    if validation_errors:
        error_result = {
            "gate_name": gate.gate_name,
            "gate_decision": "BLOCK",
            "permit_validation_status": "INVALID",
            "release_allowed": False,
            "release_blocked_by": "PERMIT_INVALID",
            "error_code": "E002",
            "evidence_refs": [],
            "validation_timestamp": gate._now_iso(),
            "validation_errors": validation_errors,
        }
        output = error_result
    else:
        output = gate.execute(input_data)

    # Validate output
    output_errors = gate.validate_output(output)
    if output_errors:
        print(f"WARNING: Output validation errors: {output_errors}", file=sys.stderr)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
    else:
        print(json.dumps(output, indent=2))

    sys.exit(0 if output["release_allowed"] else 1)


if __name__ == "__main__":
    main()
