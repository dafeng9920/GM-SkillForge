"""
n8n Boundary Adapter - n8n 编排边界适配层

提供 n8n -> SkillForge 边界适配：
- 参数白名单过滤
- 禁止字段拦截
- 结构化错误信封

Job ID: L45-D1-N8N-BOUNDARY-20260220-001
Skill ID: l45_n8n_orchestration_boundary

Usage:
    from .n8n_boundary_adapter import (
        N8nBoundaryAdapter,
        N8nBoundaryError,
        validate_n8n_request,
    )
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import uuid


# ============================================================================
# Constants
# ============================================================================

# Allowed input fields from n8n (whitelist)
N8N_ALLOWED_FIELDS = frozenset([
    "repo_url",
    "commit_sha",
    "at_time",
    "requester_id",
    "intent_id",
    "n8n_execution_id",
])

# Forbidden fields - n8n cannot set these (privilege escalation prevention)
N8N_FORBIDDEN_FIELDS = frozenset([
    "gate_decision",
    "release_allowed",
    "evidence_ref",
    "permit_id",
])

# Required fields for n8n intent request
N8N_REQUIRED_FIELDS = frozenset([
    "repo_url",
    "commit_sha",
    "at_time",
    "requester_id",
    "intent_id",
])


# ============================================================================
# Error Definitions
# ============================================================================

class N8nErrorCode(str, Enum):
    """n8n boundary error codes."""
    FORBIDDEN_FIELD = "N8N-FORBIDDEN-FIELD"
    WHITELIST_VIOLATION = "N8N-WHITELIST-VIOLATION"
    AT_TIME_FIXED_REQUIRED = "N8N-AT-TIME-FIXED-REQUIRED"
    MISSING_REQUIRED_FIELD = "N8N-MISSING-REQUIRED-FIELD"
    MEMBERSHIP_CAPABILITY_DENIED = "MEMBERSHIP-CAPABILITY-DENIED"
    MEMBERSHIP_QUOTA_EXCEEDED = "MEMBERSHIP-QUOTA-EXCEEDED"
    MEMBERSHIP_RATE_LIMITED = "MEMBERSHIP-RATE-LIMITED"
    INTERNAL_ERROR = "INTERNAL-ERROR"


@dataclass
class N8nBoundaryError:
    """
    Structured error envelope for n8n boundary violations.

    All rejection branches MUST return this structure (fail-closed).
    """
    error_code: N8nErrorCode
    error_message: str
    timestamp: str
    forbidden_fields: list[str] = field(default_factory=list)
    unknown_fields: list[str] = field(default_factory=list)
    allowed_fields: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    tier: Optional[str] = None
    action: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON response."""
        result = {
            "error_code": self.error_code.value,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
        }

        # Add optional details
        details = {}
        if self.forbidden_fields:
            details["forbidden_fields"] = self.forbidden_fields
        if self.unknown_fields:
            details["unknown_fields"] = self.unknown_fields
        if self.allowed_fields:
            details["allowed_fields"] = self.allowed_fields
        if self.missing_fields:
            details["missing_fields"] = self.missing_fields
        if self.tier:
            details["tier"] = self.tier
        if self.action:
            details["action"] = self.action

        if details:
            result["details"] = details

        return result


class N8nBoundaryValidationError(Exception):
    """Exception raised when n8n request violates boundary rules."""

    def __init__(self, error: N8nBoundaryError):
        self.error = error
        super().__init__(error.error_message)


# ============================================================================
# Validation Result
# ============================================================================

@dataclass
class N8nValidationResult:
    """Result of n8n boundary validation."""
    valid: bool
    sanitized_payload: dict[str, Any]
    error: Optional[N8nBoundaryError] = None


# ============================================================================
# Boundary Adapter
# ============================================================================

class N8nBoundaryAdapter:
    """
    n8n Boundary Adapter - 白名单过滤 + forbidden fields deny

    Enforces strict input/output boundaries between n8n and SkillForge:
    1. Only whitelisted fields are accepted
    2. Forbidden fields trigger immediate rejection (fail-closed)
    3. at_time must be fixed, no "latest" auto-drift
    4. All rejections return structured error envelope
    """

    def __init__(
        self,
        allowed_fields: frozenset[str] = N8N_ALLOWED_FIELDS,
        forbidden_fields: frozenset[str] = N8N_FORBIDDEN_FIELDS,
        required_fields: frozenset[str] = N8N_REQUIRED_FIELDS,
    ):
        self.allowed_fields = allowed_fields
        self.forbidden_fields = forbidden_fields
        self.required_fields = required_fields

    def validate_request(self, payload: dict[str, Any]) -> N8nValidationResult:
        """
        Validate n8n request against boundary rules.

        Args:
            payload: Raw request payload from n8n

        Returns:
            N8nValidationResult with valid=True and sanitized payload,
            or valid=False with error details
        """
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # 1. Check for forbidden fields (fail-closed)
        forbidden_detected = [
            field for field in self.forbidden_fields
            if field in payload
        ]
        if forbidden_detected:
            error = N8nBoundaryError(
                error_code=N8nErrorCode.FORBIDDEN_FIELD,
                error_message=self._format_forbidden_field_message(forbidden_detected),
                timestamp=timestamp,
                forbidden_fields=forbidden_detected,
                allowed_fields=list(self.allowed_fields),
            )
            return N8nValidationResult(valid=False, sanitized_payload={}, error=error)

        # 2. Check for unknown fields (whitelist violation)
        unknown_fields = [
            field for field in payload.keys()
            if field not in self.allowed_fields
        ]
        if unknown_fields:
            error = N8nBoundaryError(
                error_code=N8nErrorCode.WHITELIST_VIOLATION,
                error_message=self._format_unknown_field_message(unknown_fields),
                timestamp=timestamp,
                unknown_fields=unknown_fields,
                allowed_fields=list(self.allowed_fields),
            )
            return N8nValidationResult(valid=False, sanitized_payload={}, error=error)

        # 3. Check required fields
        missing_fields = [
            field for field in self.required_fields
            if field not in payload or payload[field] is None
        ]
        if missing_fields:
            error = N8nBoundaryError(
                error_code=N8nErrorCode.MISSING_REQUIRED_FIELD,
                error_message=f"Missing required fields: {', '.join(missing_fields)}",
                timestamp=timestamp,
                missing_fields=missing_fields,
                allowed_fields=list(self.allowed_fields),
            )
            return N8nValidationResult(valid=False, sanitized_payload={}, error=error)

        # 4. Validate at_time is not "latest" or auto-drift
        at_time = payload.get("at_time")
        if at_time is not None:
            at_time_error = self._validate_at_time(at_time, timestamp)
            if at_time_error:
                return N8nValidationResult(valid=False, sanitized_payload={}, error=at_time_error)

        # 5. Validate commit_sha format
        commit_sha = payload.get("commit_sha")
        if commit_sha is not None:
            sha_error = self._validate_commit_sha(commit_sha, timestamp)
            if sha_error:
                return N8nValidationResult(valid=False, sanitized_payload={}, error=sha_error)

        # 6. Sanitize payload (only include allowed fields)
        sanitized = {
            key: value for key, value in payload.items()
            if key in self.allowed_fields
        }

        return N8nValidationResult(valid=True, sanitized_payload=sanitized)

    def _format_forbidden_field_message(self, forbidden_fields: list[str]) -> str:
        """Format error message for forbidden fields."""
        if len(forbidden_fields) == 1:
            field = forbidden_fields[0]
            return f"Forbidden field detected: {field}. n8n cannot set {field}."
        else:
            fields_str = ", ".join(forbidden_fields)
            return f"Forbidden fields detected: {fields_str}. n8n cannot set these fields."

    def _format_unknown_field_message(self, unknown_fields: list[str]) -> str:
        """Format error message for unknown fields."""
        if len(unknown_fields) == 1:
            field = unknown_fields[0]
            return f"Unknown field detected: {field}. Only whitelisted fields are allowed."
        else:
            fields_str = ", ".join(unknown_fields)
            return f"Unknown fields detected: {fields_str}. Only whitelisted fields are allowed."

    def _validate_at_time(self, at_time: Any, timestamp: str) -> Optional[N8nBoundaryError]:
        """
        Validate that at_time is a fixed timestamp, not "latest".

        Constraint: at_time must be fixed, no "latest" auto-drift is allowed.
        """
        if isinstance(at_time, str):
            # Check for forbidden values
            forbidden_values = ["latest", "now", "current", "today"]
            if at_time.lower() in forbidden_values:
                return N8nBoundaryError(
                    error_code=N8nErrorCode.AT_TIME_FIXED_REQUIRED,
                    error_message=f"at_time must be a fixed ISO-8601 timestamp. '{at_time}' auto-drift is not allowed.",
                    timestamp=timestamp,
                    allowed_fields=list(self.allowed_fields),
                )

            # Try to parse as ISO-8601
            try:
                datetime.fromisoformat(at_time.replace("Z", "+00:00"))
            except ValueError:
                return N8nBoundaryError(
                    error_code=N8nErrorCode.AT_TIME_FIXED_REQUIRED,
                    error_message="at_time must be a valid ISO-8601 timestamp.",
                    timestamp=timestamp,
                    allowed_fields=list(self.allowed_fields),
                )

        return None

    def _validate_commit_sha(self, commit_sha: Any, timestamp: str) -> Optional[N8nBoundaryError]:
        """Validate commit_sha is a 40-character hex string."""
        if not isinstance(commit_sha, str):
            return N8nBoundaryError(
                error_code=N8nErrorCode.WHITELIST_VIOLATION,
                error_message="commit_sha must be a string.",
                timestamp=timestamp,
            )

        if len(commit_sha) != 40 or not all(c in "0123456789abcdef" for c in commit_sha.lower()):
            return N8nBoundaryError(
                error_code=N8nErrorCode.WHITELIST_VIOLATION,
                error_message="commit_sha must be a 40-character hexadecimal string.",
                timestamp=timestamp,
            )

        return None


# ============================================================================
# Convenience Functions
# ============================================================================

# Default adapter instance
_default_adapter = N8nBoundaryAdapter()


def validate_n8n_request(payload: dict[str, Any]) -> N8nValidationResult:
    """
    Validate n8n request using the default adapter.

    Args:
        payload: Raw request payload from n8n

    Returns:
        N8nValidationResult
    """
    return _default_adapter.validate_request(payload)


def generate_run_id() -> str:
    """Generate a unique run ID for n8n execution."""
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"RUN-N8N-{date_part}-{unique_part}"


def create_success_response(
    intent_id: str,
    n8n_execution_id: Optional[str] = None,
) -> dict[str, Any]:
    """Create a success response for n8n run_intent."""
    return {
        "run_id": generate_run_id(),
        "status": "ACCEPTED",
        "intent_id": intent_id,
        "n8n_execution_id": n8n_execution_id,
        "boundary_validated": True,
        "forbidden_fields_detected": [],
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


# ============================================================================
# Membership Middleware Integration
# ============================================================================

def check_n8n_capability(
    tier: str,
    permit_status: str,
    execution_contract_present: bool,
    tombstone_state: Optional[str] = None,
    enabled_addons: Optional[list[str]] = None,
    current_concurrent_jobs: int = 0,
) -> tuple[bool, Optional[N8nBoundaryError]]:
    """
    Check n8n execution capability via membership middleware.

    Args:
        tier: User membership tier
        permit_status: Current permit status
        execution_contract_present: Whether execution contract exists
        tombstone_state: Tombstone state if applicable
        enabled_addons: List of enabled add-ons
        current_concurrent_jobs: Current concurrent job count

    Returns:
        Tuple of (allowed, error_if_not_allowed)
    """
    from contracts.policy.membership_middleware import check_execute_via_n8n

    result = check_execute_via_n8n(
        tier=tier,
        permit_status=permit_status,
        execution_contract_present=execution_contract_present,
        tombstone_state=tombstone_state,
        enabled_addons=enabled_addons,
        current_concurrent_jobs=current_concurrent_jobs,
    )

    if result.allowed:
        return True, None

    # Map middleware error to boundary error
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    if result.error_code and "CAPABILITY" in result.error_code:
        error_code = N8nErrorCode.MEMBERSHIP_CAPABILITY_DENIED
    elif result.error_code and "QUOTA" in result.error_code:
        error_code = N8nErrorCode.MEMBERSHIP_QUOTA_EXCEEDED
    elif result.error_code and "RATE" in result.error_code:
        error_code = N8nErrorCode.MEMBERSHIP_RATE_LIMITED
    else:
        error_code = N8nErrorCode.INTERNAL_ERROR

    error = N8nBoundaryError(
        error_code=error_code,
        error_message=result.error_message or "Membership policy denied",
        timestamp=timestamp,
        tier=result.tier,
        action=result.action,
    )

    return False, error
