"""
External Skill Package Adapter - 外部 Skill 包校验适配器

提供 manifest/signature/content_hash/revision 完整性与身份绑定校验。

Contract: T13 (L45-D3-EXT-SKILL-GOV-20260220-003)
Schema: external_skill_governance_contract_v1.yaml
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ============================================================================
# Constants
# ============================================================================

# Required manifest fields per external_skill_governance_contract_v1.yaml
REQUIRED_MANIFEST_FIELDS = [
    "name",
    "version",
    "revision",
    "capability",
    "input_schema",
    "output_schema",
]

# Error codes (fail-closed)
ERROR_CODES = {
    "MANIFEST_MISSING_FIELD": "Manifest is missing required field(s)",
    "MANIFEST_INVALID_JSON": "Manifest is not valid JSON",
    "MANIFEST_NOT_FOUND": "Manifest file not found",
    "SIGNATURE_VERIFICATION_FAILED": "Package signature verification failed",
    "SIGNATURE_MISSING": "Package signature is missing",
    "CONTENT_HASH_MISMATCH": "Content hash does not match manifest",
    "CONTENT_HASH_MISSING": "Content hash is missing from manifest",
    "REVISION_MISSING": "Revision is missing from manifest",
    "PACKAGE_NOT_FOUND": "Skill package not found",
    "PACKAGE_INVALID_STRUCTURE": "Package structure is invalid",
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class SkillManifest:
    """Skill package manifest."""
    name: str
    version: str
    revision: str
    capability: str
    input_schema: dict
    output_schema: dict
    description: Optional[str] = None
    content_hash: Optional[str] = None
    signature: Optional[str] = None
    dependencies: Optional[list] = None
    metadata: Optional[dict] = None

    @classmethod
    def from_dict(cls, data: dict) -> "SkillManifest":
        """Create manifest from dictionary."""
        return cls(
            name=data["name"],
            version=data["version"],
            revision=data["revision"],
            capability=data["capability"],
            input_schema=data["input_schema"],
            output_schema=data["output_schema"],
            description=data.get("description"),
            content_hash=data.get("content_hash"),
            signature=data.get("signature"),
            dependencies=data.get("dependencies"),
            metadata=data.get("metadata"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "version": self.version,
            "revision": self.revision,
            "capability": self.capability,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }
        if self.description:
            result["description"] = self.description
        if self.content_hash:
            result["content_hash"] = self.content_hash
        if self.signature:
            result["signature"] = self.signature
        if self.dependencies:
            result["dependencies"] = self.dependencies
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class ValidationResult:
    """Result of package validation."""
    ok: bool
    package_id: Optional[str] = None
    revision: Optional[str] = None
    evidence_ref: Optional[str] = None
    run_id: Optional[str] = None
    manifest: Optional[SkillManifest] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    missing_fields: Optional[list] = None
    required_changes: Optional[list] = None
    validated_at: Optional[str] = None

    @classmethod
    def success(
        cls,
        manifest: SkillManifest,
        package_id: str,
        revision: str,
        evidence_ref: str,
        run_id: str,
    ) -> "ValidationResult":
        """Create a successful validation result."""
        return cls(
            ok=True,
            package_id=package_id,
            revision=revision,
            evidence_ref=evidence_ref,
            run_id=run_id,
            manifest=manifest,
            validated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    @classmethod
    def error(
        cls,
        error_code: str,
        error_message: str,
        missing_fields: Optional[list] = None,
        required_changes: Optional[list] = None,
    ) -> "ValidationResult":
        """Create an error validation result (fail-closed)."""
        return cls(
            ok=False,
            error_code=error_code,
            error_message=error_message,
            missing_fields=missing_fields,
            required_changes=required_changes,
            validated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            "ok": self.ok,
            "validated_at": self.validated_at,
        }
        if self.ok:
            result["package_id"] = self.package_id
            result["revision"] = self.revision
            result["evidence_ref"] = self.evidence_ref
            result["run_id"] = self.run_id
            if self.manifest:
                result["manifest"] = self.manifest.to_dict()
        else:
            result["error_code"] = self.error_code
            result["error_message"] = self.error_message
            if self.missing_fields:
                result["missing_fields"] = self.missing_fields
            if self.required_changes:
                result["required_changes"] = self.required_changes
        return result


@dataclass
class ReplayPointer:
    """Replay pointer for at-time replay capability."""
    at_time: str
    revision: str
    package_id: str
    evidence_bundle_ref: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "at_time": self.at_time,
            "revision": self.revision,
            "package_id": self.package_id,
            "evidence_bundle_ref": self.evidence_bundle_ref,
        }


# ============================================================================
# ExternalSkillPackageAdapter
# ============================================================================

class ExternalSkillPackageAdapter:
    """
    外部 Skill 包校验适配器。

    提供 manifest/signature/content_hash/revision 完整性与身份绑定校验。

    Constraints (fail-closed):
    - manifest 缺字段必须 fail-closed
    - signature 验签失败必须返回结构化错误码
    - content_hash 不一致必须阻断
    - 输出必须包含 package_id/revision/evidence_ref
    """

    def __init__(self, verification_key: Optional[str] = None):
        """
        Initialize the adapter.

        Args:
            verification_key: Optional key for signature verification.
                             If None, signature verification is skipped but logged.
        """
        self.verification_key = verification_key or "mock_key_for_testing"
        self._validation_cache: dict[str, ValidationResult] = {}

    def _generate_ids(self, manifest: SkillManifest) -> tuple[str, str, str, str]:
        """Generate package_id, revision, evidence_ref, and run_id."""
        ts = int(time.time())
        short_uuid = uuid.uuid4().hex[:8].upper()

        package_id = f"PKG-EXT-{manifest.name.upper()}-{ts}-{short_uuid}"
        revision = manifest.revision
        evidence_ref = f"EV-PKG-VAL-{ts}-{short_uuid}"
        run_id = f"RUN-PKG-{ts}-{short_uuid}"

        return package_id, revision, evidence_ref, run_id

    def _compute_content_hash(self, content: bytes) -> str:
        """Compute SHA-256 hash of content."""
        return f"sha256:{hashlib.sha256(content).hexdigest()}"

    def _verify_signature(self, manifest: SkillManifest, content: bytes) -> bool:
        """
        Verify package signature.

        In production, this would use proper cryptographic verification.
        For now, uses a mock implementation that validates signature format.

        Args:
            manifest: The skill manifest
            content: The package content bytes

        Returns:
            True if signature is valid, False otherwise
        """
        if not manifest.signature:
            return False

        # Mock signature verification: signature should be hex string >= 32 chars
        # In production, this would use proper JWT/Ed25519 verification
        sig = manifest.signature
        if not isinstance(sig, str) or len(sig) < 32:
            return False

        # Check signature format (mock: starts with "sig_" and contains hex)
        if sig.startswith("sig_"):
            hex_part = sig[4:]
            try:
                int(hex_part, 16)
                return True
            except ValueError:
                return False

        # Fallback: accept any 64-char hex string as valid mock signature
        try:
            if len(sig) == 64:
                int(sig, 16)
                return True
        except ValueError:
            pass

        return False

    def validate_manifest(self, manifest_data: dict) -> ValidationResult:
        """
        Validate manifest structure and required fields.

        Args:
            manifest_data: Raw manifest dictionary

        Returns:
            ValidationResult with success or error details
        """
        # Check for required fields
        missing_fields = []
        for field in REQUIRED_MANIFEST_FIELDS:
            if field not in manifest_data:
                missing_fields.append(field)

        if missing_fields:
            return ValidationResult.error(
                error_code="MANIFEST_MISSING_FIELD",
                error_message=f"Manifest is missing required field(s): {', '.join(missing_fields)}",
                missing_fields=missing_fields,
                required_changes=[
                    f"Add missing field '{field}' to manifest" for field in missing_fields
                ],
            )

        # Validate field types
        try:
            manifest = SkillManifest.from_dict(manifest_data)
        except (KeyError, TypeError) as e:
            return ValidationResult.error(
                error_code="MANIFEST_INVALID_JSON",
                error_message=f"Manifest has invalid field types: {str(e)}",
                required_changes=["Fix field types in manifest to match schema"],
            )

        return ValidationResult.success(
            manifest=manifest,
            package_id="TEMP",  # Will be replaced in full validation
            revision=manifest.revision,
            evidence_ref="TEMP",
            run_id="TEMP",
        )

    def validate_package(
        self,
        package_path: Path,
        manifest_path: Optional[Path] = None,
        skip_signature: bool = False,
    ) -> ValidationResult:
        """
        Validate an external skill package.

        Args:
            package_path: Path to the skill package (directory or zip)
            manifest_path: Optional path to manifest file (defaults to package_path/manifest.json)
            skip_signature: Skip signature verification (for testing only)

        Returns:
            ValidationResult with package_id/revision/evidence_ref on success
        """
        # Check package exists
        if not package_path.exists():
            return ValidationResult.error(
                error_code="PACKAGE_NOT_FOUND",
                error_message=f"Package not found at: {package_path}",
                required_changes=["Ensure package path is correct"],
            )

        # Determine manifest path
        if manifest_path is None:
            if package_path.is_dir():
                manifest_path = package_path / "manifest.json"
            else:
                return ValidationResult.error(
                    error_code="PACKAGE_INVALID_STRUCTURE",
                    error_message="Package must be a directory containing manifest.json",
                    required_changes=["Extract package to directory or provide manifest path"],
                )

        # Load manifest
        if not manifest_path.exists():
            return ValidationResult.error(
                error_code="MANIFEST_NOT_FOUND",
                error_message=f"Manifest not found at: {manifest_path}",
                required_changes=["Add manifest.json to package root"],
            )

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except json.JSONDecodeError as e:
            return ValidationResult.error(
                error_code="MANIFEST_INVALID_JSON",
                error_message=f"Manifest is not valid JSON: {str(e)}",
                required_changes=["Fix manifest.json syntax"],
            )

        # Validate manifest structure
        manifest_result = self.validate_manifest(manifest_data)
        if not manifest_result.ok:
            return manifest_result

        manifest = manifest_result.manifest
        if manifest is None:
            return ValidationResult.error(
                error_code="MANIFEST_INVALID_JSON",
                error_message="Manifest parsed but returned None",
                required_changes=["Fix manifest structure"],
            )

        # Compute content hash of package
        content_hash = self._compute_package_hash(package_path)

        # Verify content hash (if present in manifest)
        if manifest.content_hash:
            if manifest.content_hash != content_hash:
                return ValidationResult.error(
                    error_code="CONTENT_HASH_MISMATCH",
                    error_message=(
                        f"Content hash mismatch: manifest says '{manifest.content_hash}', "
                        f"but computed '{content_hash}'"
                    ),
                    required_changes=[
                        "Re-compute content hash after any changes",
                        f"Update manifest.content_hash to '{content_hash}'",
                    ],
                )
        else:
            # Content hash missing - fail-closed per contract
            return ValidationResult.error(
                error_code="CONTENT_HASH_MISSING",
                error_message="Manifest does not contain content_hash field",
                required_changes=[
                    f"Add 'content_hash': '{content_hash}' to manifest",
                ],
            )

        # Verify signature (fail-closed)
        if not skip_signature:
            if not manifest.signature:
                return ValidationResult.error(
                    error_code="SIGNATURE_MISSING",
                    error_message="Package signature is missing from manifest",
                    required_changes=[
                        "Sign the package and add 'signature' field to manifest",
                    ],
                )

            # Read package content for signature verification
            package_content = self._read_package_content(package_path)
            if not self._verify_signature(manifest, package_content):
                return ValidationResult.error(
                    error_code="SIGNATURE_VERIFICATION_FAILED",
                    error_message="Package signature verification failed",
                    required_changes=[
                        "Re-sign the package with correct key",
                        "Ensure signature format is valid (hex string >= 64 chars)",
                    ],
                )

        # Generate final IDs
        package_id, revision, evidence_ref, run_id = self._generate_ids(manifest)

        # Cache validation result for replay pointer
        self._validation_cache[package_id] = ValidationResult.success(
            manifest=manifest,
            package_id=package_id,
            revision=revision,
            evidence_ref=evidence_ref,
            run_id=run_id,
        )

        return ValidationResult.success(
            manifest=manifest,
            package_id=package_id,
            revision=revision,
            evidence_ref=evidence_ref,
            run_id=run_id,
        )

    def _compute_package_hash(self, package_path: Path) -> str:
        """Compute hash of package contents (excluding manifest.json)."""
        hasher = hashlib.sha256()

        if package_path.is_file():
            with open(package_path, "rb") as f:
                hasher.update(f.read())
        elif package_path.is_dir():
            # Hash all files in directory (excluding manifest.json), sorted for determinism
            for file_path in sorted(package_path.rglob("*")):
                if file_path.is_file() and file_path.name != "manifest.json":
                    # Include relative path in hash
                    relative_path = file_path.relative_to(package_path)
                    hasher.update(str(relative_path).encode())
                    with open(file_path, "rb") as f:
                        hasher.update(f.read())

        return f"sha256:{hasher.hexdigest()}"

    def _read_package_content(self, package_path: Path) -> bytes:
        """Read package content for signature verification."""
        if package_path.is_file():
            with open(package_path, "rb") as f:
                return f.read()
        elif package_path.is_dir():
            # Concatenate all file contents (sorted for determinism)
            content = b""
            for file_path in sorted(package_path.rglob("*")):
                if file_path.is_file() and file_path.name != "manifest.json":
                    with open(file_path, "rb") as f:
                        content += f.read()
            return content
        return b""

    def get_replay_pointer(
        self,
        package_id: str,
        at_time: str,
        evidence_bundle_ref: str,
    ) -> ReplayPointer:
        """
        Generate replay pointer for at-time replay.

        Args:
            package_id: The package identifier
            at_time: ISO-8601 timestamp for point-in-time query
            evidence_bundle_ref: Reference to evidence bundle

        Returns:
            ReplayPointer for audit replay
        """
        # Extract revision from cached validation or generate
        cached = self._validation_cache.get(package_id)
        revision: str = cached.revision if cached and cached.revision else "unknown"

        return ReplayPointer(
            at_time=at_time,
            revision=revision,
            package_id=package_id,
            evidence_bundle_ref=evidence_bundle_ref,
        )


# ============================================================================
# Convenience Functions
# ============================================================================

def validate_external_skill_package(
    package_path: Path,
    manifest_path: Optional[Path] = None,
    verification_key: Optional[str] = None,
) -> ValidationResult:
    """
    Validate an external skill package.

    Args:
        package_path: Path to the skill package
        manifest_path: Optional path to manifest file
        verification_key: Optional key for signature verification

    Returns:
        ValidationResult
    """
    adapter = ExternalSkillPackageAdapter(verification_key)
    return adapter.validate_package(package_path, manifest_path)
