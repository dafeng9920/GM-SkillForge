"""
Tests for External Skill Package Adapter

Contract: T13 (L45-D3-EXT-SKILL-GOV-20260220-003)
Coverage: manifest/signature/content_hash/revision validation
"""
import json
import tempfile
from pathlib import Path

import pytest

from skillforge.src.adapters.external_skill_package_adapter import (
    ERROR_CODES,
    ExternalSkillPackageAdapter,
    validate_external_skill_package,
)


# ============================================================================
# Helper Functions
# ============================================================================

def setup_package_with_correct_hash(
    package_path: Path,
    include_signature: bool = True,
) -> dict:
    """
    Set up a package with correct content hash.

    Returns the final manifest data.
    """
    adapter = ExternalSkillPackageAdapter()
    manifest_path = package_path / "manifest.json"

    # Read existing manifest
    with open(manifest_path, "r") as f:
        data = json.load(f)

    # Set signature if needed
    if include_signature:
        data["signature"] = "sig_" + "a" * 64
    elif "signature" in data:
        del data["signature"]

    # Write without content_hash first
    if "content_hash" in data:
        del data["content_hash"]

    with open(manifest_path, "w") as f:
        json.dump(data, f)

    # Compute correct hash
    correct_hash = adapter._compute_package_hash(package_path)
    data["content_hash"] = correct_hash

    # Write final manifest
    with open(manifest_path, "w") as f:
        json.dump(data, f)

    return data


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def adapter():
    """Create adapter instance for testing."""
    return ExternalSkillPackageAdapter(verification_key="test_key")


@pytest.fixture
def valid_manifest_data():
    """Create valid manifest data."""
    return {
        "name": "test_skill",
        "version": "1.0.0",
        "revision": "rev-001",
        "capability": "test_capability",
        "input_schema": {"type": "object"},
        "output_schema": {"type": "object"},
        "content_hash": "sha256:abc123",
        "signature": "sig_" + "a" * 64,
    }


@pytest.fixture
def temp_package_dir(valid_manifest_data):
    """Create temporary package directory with valid manifest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        package_path = Path(tmpdir)
        manifest_path = package_path / "manifest.json"

        # Write manifest
        with open(manifest_path, "w") as f:
            json.dump(valid_manifest_data, f)

        # Write a skill file
        skill_file = package_path / "skill.py"
        skill_file.write_text("# Test skill\nprint('hello')\n")

        yield package_path


# ============================================================================
# Manifest Validation Tests
# ============================================================================

class TestManifestValidation:
    """Tests for manifest validation."""

    def test_valid_manifest(self, adapter, valid_manifest_data):
        """Valid manifest should pass validation."""
        result = adapter.validate_manifest(valid_manifest_data)

        assert result.ok is True
        assert result.manifest is not None
        assert result.manifest.name == "test_skill"
        assert result.manifest.version == "1.0.0"
        assert result.manifest.revision == "rev-001"

    @pytest.mark.parametrize("missing_field", [
        "name", "version", "revision", "capability", "input_schema", "output_schema"
    ])
    def test_missing_required_field_fail_closed(self, adapter, valid_manifest_data, missing_field):
        """Missing required fields must fail-closed."""
        data = valid_manifest_data.copy()
        del data[missing_field]

        result = adapter.validate_manifest(data)

        assert result.ok is False
        assert result.error_code == "MANIFEST_MISSING_FIELD"
        assert missing_field in result.missing_fields
        assert len(result.required_changes) > 0

    def test_missing_multiple_fields(self, adapter):
        """Multiple missing fields should all be reported."""
        data = {"name": "test"}  # Missing most required fields

        result = adapter.validate_manifest(data)

        assert result.ok is False
        assert result.error_code == "MANIFEST_MISSING_FIELD"
        assert len(result.missing_fields) >= 5


# ============================================================================
# Content Hash Validation Tests
# ============================================================================

class TestContentHashValidation:
    """Tests for content hash validation."""

    def test_content_hash_missing_fail_closed(self, adapter, temp_package_dir):
        """Missing content_hash must fail-closed."""
        # Remove content_hash from manifest
        manifest_path = temp_package_dir / "manifest.json"
        with open(manifest_path, "r") as f:
            data = json.load(f)
        del data["content_hash"]
        with open(manifest_path, "w") as f:
            json.dump(data, f)

        result = adapter.validate_package(temp_package_dir, skip_signature=True)

        assert result.ok is False
        assert result.error_code == "CONTENT_HASH_MISSING"
        assert "content_hash" in result.error_message
        assert result.required_changes is not None

    def test_content_hash_mismatch_fail_closed(self, adapter, temp_package_dir):
        """Content hash mismatch must block."""
        # Set wrong content hash
        manifest_path = temp_package_dir / "manifest.json"
        with open(manifest_path, "r") as f:
            data = json.load(f)
        data["content_hash"] = "sha256:wrong_hash"
        with open(manifest_path, "w") as f:
            json.dump(data, f)

        result = adapter.validate_package(temp_package_dir, skip_signature=True)

        assert result.ok is False
        assert result.error_code == "CONTENT_HASH_MISMATCH"
        assert "mismatch" in result.error_message.lower()

    def test_content_hash_matches_success(self, adapter, temp_package_dir):
        """Matching content hash should succeed."""
        setup_package_with_correct_hash(temp_package_dir, include_signature=True)

        result = adapter.validate_package(temp_package_dir, skip_signature=False)

        assert result.ok is True
        assert result.package_id is not None
        assert result.revision == "rev-001"


# ============================================================================
# Signature Validation Tests
# ============================================================================

class TestSignatureValidation:
    """Tests for signature validation."""

    def test_signature_missing_fail_closed(self, adapter, temp_package_dir):
        """Missing signature must fail-closed."""
        setup_package_with_correct_hash(temp_package_dir, include_signature=False)

        result = adapter.validate_package(temp_package_dir, skip_signature=False)

        assert result.ok is False
        assert result.error_code == "SIGNATURE_MISSING"
        assert result.required_changes is not None

    def test_signature_invalid_fail_closed(self, adapter, temp_package_dir):
        """Invalid signature must fail-closed with structured error."""
        manifest_path = temp_package_dir / "manifest.json"

        # Setup with correct hash
        setup_package_with_correct_hash(temp_package_dir, include_signature=True)

        # Then corrupt the signature
        with open(manifest_path, "r") as f:
            data = json.load(f)
        data["signature"] = "invalid_short_sig"
        with open(manifest_path, "w") as f:
            json.dump(data, f)

        result = adapter.validate_package(temp_package_dir, skip_signature=False)

        assert result.ok is False
        assert result.error_code == "SIGNATURE_VERIFICATION_FAILED"
        assert "verification failed" in result.error_message.lower()

    def test_skip_signature_verification(self, adapter, temp_package_dir):
        """Skip signature should bypass signature check."""
        setup_package_with_correct_hash(temp_package_dir, include_signature=False)

        result = adapter.validate_package(temp_package_dir, skip_signature=True)

        assert result.ok is True


# ============================================================================
# Package Validation Tests
# ============================================================================

class TestPackageValidation:
    """Tests for full package validation."""

    def test_package_not_found(self, adapter):
        """Non-existent package must fail-closed."""
        result = adapter.validate_package(Path("/nonexistent/path"))

        assert result.ok is False
        assert result.error_code == "PACKAGE_NOT_FOUND"

    def test_manifest_not_found(self, adapter):
        """Missing manifest must fail-closed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_path = Path(tmpdir)
            # No manifest.json

            result = adapter.validate_package(package_path)

            assert result.ok is False
            assert result.error_code == "MANIFEST_NOT_FOUND"

    def test_invalid_json_manifest(self, adapter):
        """Invalid JSON manifest must fail-closed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_path = Path(tmpdir)
            manifest_path = package_path / "manifest.json"
            manifest_path.write_text("not valid json {")

            result = adapter.validate_package(package_path)

            assert result.ok is False
            assert result.error_code == "MANIFEST_INVALID_JSON"

    def test_successful_validation_outputs_required_fields(self, adapter, temp_package_dir):
        """Successful validation must output package_id/revision/evidence_ref."""
        setup_package_with_correct_hash(temp_package_dir, include_signature=True)

        result = adapter.validate_package(temp_package_dir, skip_signature=False)

        assert result.ok is True
        assert result.package_id is not None
        assert result.package_id.startswith("PKG-EXT-")
        assert result.revision == "rev-001"
        assert result.evidence_ref is not None
        assert result.evidence_ref.startswith("EV-PKG-VAL-")
        assert result.run_id is not None
        assert result.run_id.startswith("RUN-PKG-")


# ============================================================================
# Revision and Replay Tests
# ============================================================================

class TestRevisionAndReplay:
    """Tests for revision binding and at-time replay."""

    def test_revision_available_for_replay(self, adapter, temp_package_dir):
        """Revision must be available for at-time replay."""
        setup_package_with_correct_hash(temp_package_dir, include_signature=True)

        result = adapter.validate_package(temp_package_dir, skip_signature=False)

        assert result.ok is True
        assert result.revision == "rev-001"

        # Verify revision is in output
        result_dict = result.to_dict()
        assert "revision" in result_dict
        assert result_dict["revision"] == "rev-001"

    def test_replay_pointer_generation(self, adapter):
        """Replay pointer should be generatable from validation result."""
        pointer = adapter.get_replay_pointer(
            package_id="PKG-EXT-TEST-001",
            at_time="2026-02-20T14:30:00Z",
            evidence_bundle_ref="EV-BUNDLE-001",
        )

        assert pointer.at_time == "2026-02-20T14:30:00Z"
        assert pointer.package_id == "PKG-EXT-TEST-001"
        assert pointer.evidence_bundle_ref == "EV-BUNDLE-001"

        pointer_dict = pointer.to_dict()
        assert "at_time" in pointer_dict
        assert "revision" in pointer_dict


# ============================================================================
# Fail-Closed Constraint Tests
# ============================================================================

class TestFailClosedConstraints:
    """Tests for fail-closed constraints."""

    def test_no_silent_failures(self, adapter):
        """All failures must return structured error, not exception."""
        # Package that doesn't exist
        result = adapter.validate_package(Path("/nonexistent"))

        assert result.ok is False
        assert result.error_code is not None
        assert result.error_message is not None

    def test_error_codes_are_structured(self, adapter):
        """Error codes must be from defined set."""
        result = adapter.validate_package(Path("/nonexistent"))

        assert result.error_code in ERROR_CODES

    def test_required_changes_are_executable(self, adapter, valid_manifest_data):
        """Failed validations must include executable required_changes."""
        data = valid_manifest_data.copy()
        del data["name"]

        result = adapter.validate_manifest(data)

        assert result.ok is False
        assert result.required_changes is not None
        assert len(result.required_changes) > 0
        # Each required_change should be an actionable statement
        for change in result.required_changes:
            assert isinstance(change, str)
            assert len(change) > 0


# ============================================================================
# Convenience Function Tests
# ============================================================================

class TestConvenienceFunction:
    """Tests for convenience function."""

    def test_validate_external_skill_package(self, temp_package_dir):
        """Convenience function should work the same as adapter method."""
        setup_package_with_correct_hash(temp_package_dir, include_signature=True)

        result = validate_external_skill_package(temp_package_dir)

        assert result.ok is True


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete validation flow."""

    def test_complete_validation_flow(self, adapter, temp_package_dir):
        """Complete validation flow should work end-to-end."""
        setup_package_with_correct_hash(temp_package_dir, include_signature=True)

        # Validate
        result = adapter.validate_package(temp_package_dir)

        assert result.ok is True

        # Generate replay pointer
        pointer = adapter.get_replay_pointer(
            package_id=result.package_id,
            at_time="2026-02-20T14:30:00Z",
            evidence_bundle_ref=result.evidence_ref,
        )

        assert pointer.revision == result.revision

    def test_validation_result_serialization(self, adapter, valid_manifest_data):
        """Validation result should serialize to dict correctly."""
        result = adapter.validate_manifest(valid_manifest_data)

        result_dict = result.to_dict()

        assert "ok" in result_dict
        assert "validated_at" in result_dict
        assert result_dict["ok"] is True
