"""
IntakeRequest - Unified intake request handler for SkillForge audit pipeline.

This module enforces the T1 requirements:
- intent_id MUST be from approved whitelist
- repo_url MUST be provided (no branch-only inputs)
- commit_sha MUST be provided (minimum 7 characters)

Usage:
    from skillforge.src.contracts.intake_request import IntakeRequest, validate_intake_request

    # Create and validate
    request = IntakeRequest(
        intent_id="AUDIT_REPO_SKILL",
        repo_url="https://github.com/user/repo",
        commit_sha="abc123def456"
    )
    result = request.validate()

    # Or use convenience function
    result = validate_intake_request({
        "intent_id": "AUDIT_REPO_SKILL",
        "repo_url": "https://github.com/user/repo",
        "commit_sha": "abc123def456"
    })

Evidence paths:
    - run/<run_id>/intake_request.json
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal


# ============================================================================
# Error Codes
# ============================================================================
class ErrorCode:
    """Standard error codes for intake request validation."""

    INTENT_ID_MISSING = "E001_INTENT_ID_MISSING"
    INTENT_ID_INVALID = "E002_INTENT_ID_INVALID"
    INTENT_ID_NOT_APPROVED = "E003_INTENT_ID_NOT_APPROVED"
    REPO_URL_MISSING = "E004_REPO_URL_MISSING"
    REPO_URL_INVALID = "E005_REPO_URL_INVALID"
    COMMIT_SHA_MISSING = "E006_COMMIT_SHA_MISSING"
    COMMIT_SHA_INVALID = "E007_COMMIT_SHA_INVALID"
    BRANCH_ONLY_INPUT = "E008_BRANCH_ONLY_INPUT"


# ============================================================================
# Approved Intent Whitelist
# ============================================================================
APPROVED_INTENTS: set[str] = {
    "AUDIT_REPO_SKILL",
    "AUDIT_CONTRACT_COMPLIANCE",
    "AUDIT_SECURITY_SCAN",
    "AUDIT_PERFORMANCE_ANALYSIS",
}


# ============================================================================
# Validation Result
# ============================================================================
@dataclass(frozen=True)
class ValidationResult:
    """Result of intake request validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


# ============================================================================
# Intake Request
# ============================================================================
@dataclass
class IntakeRequest:
    """
    Unified intake request for SkillForge audit pipeline.

    Enforces T1 requirements:
    - intent_id MUST be from approved whitelist
    - repo_url MUST be provided
    - commit_sha MUST be provided (min 7 chars)
    """

    intent_id: str
    repo_url: str
    commit_sha: str
    at_time: str | None = None
    issue_key: str | None = None
    options: dict[str, Any] = field(default_factory=dict)

    # Compiled patterns
    _INTENT_ID_PATTERN = re.compile(r"^[A-Z]+_[A-Z0-9_]+$")
    _COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{7,40}$")
    _REPO_URL_PATTERN = re.compile(r"^https://.*|git://.*")
    _ISSUE_KEY_PATTERN = re.compile(r"^[A-Z]+-[A-Z0-9]+$")

    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        # Normalize commit_sha to lowercase
        if self.commit_sha:
            object.__setattr__(self, "commit_sha", self.commit_sha.lower())

        # Auto-generate at_time if not provided
        if not self.at_time:
            object.__setattr__(
                self,
                "at_time",
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        # Auto-generate issue_key if not provided
        if not self.issue_key:
            from time import gmtime, strftime

            object.__setattr__(
                self, "issue_key", f"REQ-{strftime('%Y%m%d%H%M%S', gmtime())}"
            )

    def validate(self) -> ValidationResult:
        """
        Validate the intake request against T1 requirements.

        Returns:
            ValidationResult with valid flag and any errors/warnings.
        """
        errors: list[str] = []
        warnings: list[str] = []

        # 1. Validate intent_id
        if not self.intent_id:
            errors.append(f"{ErrorCode.INTENT_ID_MISSING}: intent_id is required")
        elif not isinstance(self.intent_id, str):
            errors.append(
                f"{ErrorCode.INTENT_ID_INVALID}: intent_id must be a string"
            )
        elif not self._INTENT_ID_PATTERN.match(self.intent_id):
            errors.append(
                f"{ErrorCode.INTENT_ID_INVALID}: intent_id must match pattern "
                "^[A-Z]+_[A-Z0-9_]+$"
            )
        elif self.intent_id not in APPROVED_INTENTS:
            errors.append(
                f"{ErrorCode.INTENT_ID_NOT_APPROVED}: intent_id '{self.intent_id}' "
                f"is not in approved whitelist. Approved: {sorted(APPROVED_INTENTS)}"
            )

        # 2. Validate repo_url
        if not self.repo_url:
            errors.append(f"{ErrorCode.REPO_URL_MISSING}: repo_url is required")
        elif not isinstance(self.repo_url, str):
            errors.append(f"{ErrorCode.REPO_URL_INVALID}: repo_url must be a string")
        elif not self._REPO_URL_PATTERN.match(self.repo_url):
            errors.append(
                f"{ErrorCode.REPO_URL_INVALID}: repo_url must start with 'https://' or 'git://'"
            )

        # 3. Validate commit_sha
        if not self.commit_sha:
            errors.append(
                f"{ErrorCode.COMMIT_SHA_MISSING}: commit_sha is required for reproducible audit"
            )
        elif not isinstance(self.commit_sha, str):
            errors.append(f"{ErrorCode.COMMIT_SHA_INVALID}: commit_sha must be a string")
        elif not self._COMMIT_SHA_PATTERN.match(self.commit_sha):
            errors.append(
                f"{ErrorCode.COMMIT_SHA_INVALID}: commit_sha must be 7-40 character hex string"
            )
        elif len(self.commit_sha) < 40:
            warnings.append(
                f"commit_sha is {len(self.commit_sha)} chars (short SHA). "
                "Full 40-char SHA recommended for production."
            )

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of the canonical request (for deduplication)."""
        canonical = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def save(self, output_path: str | Path) -> None:
        """
        Save the intake request to a JSON file.

        Args:
            output_path: Path to save the intake request JSON.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write atomically via temp file
        temp_path = output_path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(self.to_json())
            temp_path.replace(output_path)
        except OSError as e:
            raise IOError(f"Failed to save intake request to {output_path}: {e}")


# ============================================================================
# Convenience Functions
# ============================================================================
def validate_intake_request(data: dict[str, Any]) -> ValidationResult:
    """
    Validate a dictionary as an intake request.

    Args:
        data: Dictionary containing intake request fields.

    Returns:
        ValidationResult with validation outcome.
    """
    # Check for branch-only input (T1 violation)
    if "branch" in data and "commit_sha" not in data:
        return ValidationResult(
            valid=False,
            errors=[
                f"{ErrorCode.BRANCH_ONLY_INPUT}: Branch-only input is not allowed. "
                "commit_sha is required for reproducible audit."
            ],
        )

    try:
        request = IntakeRequest(
            intent_id=data.get("intent_id", ""),
            repo_url=data.get("repo_url", ""),
            commit_sha=data.get("commit_sha", ""),
            at_time=data.get("at_time"),
            issue_key=data.get("issue_key"),
            options=data.get("options", {}),
        )
        return request.validate()
    except Exception as e:
        return ValidationResult(
            valid=False, errors=[f"Failed to create IntakeRequest: {e}"]
        )


def create_intake_request(
    intent_id: str,
    repo_url: str,
    commit_sha: str,
    at_time: str | None = None,
    issue_key: str | None = None,
    options: dict[str, Any] | None = None,
) -> IntakeRequest:
    """
    Create and validate an intake request.

    Args:
        intent_id: Approved intent identifier.
        repo_url: Git repository URL.
        commit_sha: Git commit SHA.
        at_time: Optional point-in-time timestamp.
        issue_key: Optional unique request ID.
        options: Optional execution parameters.

    Returns:
        Validated IntakeRequest instance.

    Raises:
        ValueError: If validation fails.
    """
    request = IntakeRequest(
        intent_id=intent_id,
        repo_url=repo_url,
        commit_sha=commit_sha,
        at_time=at_time,
        issue_key=issue_key,
        options=options or {},
    )

    result = request.validate()
    if not result.valid:
        raise ValueError(
            f"Intake request validation failed:\n" + "\n".join(result.errors)
        )

    return request


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for intake request validation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate and generate intake_request.json"
    )
    parser.add_argument(
        "--intent-id", required=True, help="Intent identifier (e.g., AUDIT_REPO_SKILL)"
    )
    parser.add_argument("--repo-url", required=True, help="Git repository URL")
    parser.add_argument("--commit-sha", required=True, help="Git commit SHA")
    parser.add_argument("--at-time", help="Point-in-time checkout (ISO-8601)")
    parser.add_argument("--issue-key", help="Unique request ID")
    parser.add_argument(
        "--output",
        default="run/latest/intake_request.json",
        help="Output path for intake_request.json",
    )
    args = parser.parse_args()

    # Create and validate
    try:
        request = create_intake_request(
            intent_id=args.intent_id,
            repo_url=args.repo_url,
            commit_sha=args.commit_sha,
            at_time=args.at_time,
            issue_key=args.issue_key,
        )
    except ValueError as e:
        print(f"Validation failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Save
    try:
        request.save(args.output)
        print(f"Intake request saved to: {args.output}")
        print(f"  Hash: {request.compute_hash()}")
        print(f"  Issue Key: {request.issue_key}")
    except IOError as e:
        print(f"Failed to save: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
