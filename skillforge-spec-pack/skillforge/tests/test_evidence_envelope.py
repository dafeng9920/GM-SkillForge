"""
Tests for Evidence Envelope Implementation (T03 - ISSUE-02)

Run: python -m pytest skillforge/tests/test_evidence_envelope.py -v
"""
from __future__ import annotations

import json
import hashlib
import pytest

from skillforge.src.utils.evidence_envelope import (
    ENVELOPE_SCHEMA_VERSION,
    EnvelopeHeader,
    KeyWrap,
    Ciphertext,
    Signature,
    Certificate,
    EvidenceEnvelope,
    EvidenceEnvelopeBuilder,
    validate_envelope_schema,
    create_signed_envelope,
    create_encrypted_envelope,
)
from skillforge.src.utils.canonical_json import canonical_json_hash


# =============================================================================
# TestEnvelopeHeader — Tests for EnvelopeHeader dataclass
# =============================================================================
class TestEnvelopeHeader:
    """Tests for EnvelopeHeader class."""

    def test_header_required_fields(self) -> None:
        """EnvelopeHeader should have all required fields."""
        header = EnvelopeHeader(
            envelope_id="ev-12345678",
            schema_version="1.0.0",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            body_hash="abc123",
        )

        assert header.envelope_id == "ev-12345678"
        assert header.schema_version == "1.0.0"
        assert header.node_id == "node-001"
        assert header.body_hash == "abc123"
        assert header.body_encoding == "json"
        assert header.compression == "none"

    def test_header_to_dict(self) -> None:
        """EnvelopeHeader.to_dict() should serialize correctly."""
        header = EnvelopeHeader(
            envelope_id="ev-12345678",
            schema_version="1.0.0",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            body_hash="abc123",
            trace_id="trace-xyz",
        )

        d = header.to_dict()
        assert d["envelope_id"] == "ev-12345678"
        assert d["trace_id"] == "trace-xyz"
        assert "expires_at" not in d  # Optional, not set

    def test_header_with_expiration(self) -> None:
        """EnvelopeHeader should handle expiration."""
        header = EnvelopeHeader(
            envelope_id="ev-12345678",
            schema_version="1.0.0",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            body_hash="abc123",
            expires_at="2026-02-27T12:00:00Z",
        )

        d = header.to_dict()
        assert d["expires_at"] == "2026-02-27T12:00:00Z"


# =============================================================================
# TestKeyWrap — Tests for KeyWrap dataclass
# =============================================================================
class TestKeyWrap:
    """Tests for KeyWrap class."""

    def test_keywrap_defaults(self) -> None:
        """KeyWrap should have correct defaults."""
        kw = KeyWrap()

        assert kw.algorithm == "RSA-OAEP-256"
        assert kw.encrypted_dek is None
        assert kw.key_id is None

    def test_keywrap_to_dict(self) -> None:
        """KeyWrap.to_dict() should serialize correctly."""
        kw = KeyWrap(
            encrypted_dek="base64encodedkey",
            key_id="key-001",
        )

        d = kw.to_dict()
        assert d["algorithm"] == "RSA-OAEP-256"
        assert d["encrypted_dek"] == "base64encodedkey"
        assert d["key_id"] == "key-001"


# =============================================================================
# TestCiphertext — Tests for Ciphertext dataclass
# =============================================================================
class TestCiphertext:
    """Tests for Ciphertext class."""

    def test_ciphertext_defaults(self) -> None:
        """Ciphertext should have correct defaults."""
        ct = Ciphertext()

        assert ct.algorithm == "AES-256-GCM"
        assert ct.iv is None
        assert ct.data is None
        assert ct.tag is None

    def test_ciphertext_to_dict(self) -> None:
        """Ciphertext.to_dict() should serialize correctly."""
        ct = Ciphertext(
            iv="base64iv",
            data="base64data",
            tag="base64tag",
        )

        d = ct.to_dict()
        assert d["algorithm"] == "AES-256-GCM"
        assert d["iv"] == "base64iv"
        assert d["data"] == "base64data"
        assert d["tag"] == "base64tag"


# =============================================================================
# TestSignature — Tests for Signature dataclass
# =============================================================================
class TestSignature:
    """Tests for Signature class."""

    def test_signature_defaults(self) -> None:
        """Signature should have correct defaults."""
        sig = Signature()

        assert sig.algorithm == "Ed25519"
        assert sig.value is None
        assert sig.signed_fields == ["header", "body_hash"]

    def test_signature_to_dict(self) -> None:
        """Signature.to_dict() should serialize correctly."""
        sig = Signature(
            value="base64signature",
            signed_at="2026-02-26T12:00:00Z",
        )

        d = sig.to_dict()
        assert d["algorithm"] == "Ed25519"
        assert d["value"] == "base64signature"
        assert d["signed_at"] == "2026-02-26T12:00:00Z"


# =============================================================================
# TestCertificate — Tests for Certificate dataclass
# =============================================================================
class TestCertificate:
    """Tests for Certificate class."""

    def test_certificate_defaults(self) -> None:
        """Certificate should have correct defaults."""
        cert = Certificate()

        assert cert.algorithm == "Ed25519"
        assert cert.issuer == "self-signed"
        assert cert.node_id is None

    def test_certificate_to_dict(self) -> None:
        """Certificate.to_dict() should serialize correctly."""
        cert = Certificate(
            node_id="node-001",
            public_key="base64pubkey",
            issued_at="2026-02-26T12:00:00Z",
        )

        d = cert.to_dict()
        assert d["algorithm"] == "Ed25519"
        assert d["node_id"] == "node-001"
        assert d["public_key"] == "base64pubkey"


# =============================================================================
# TestEvidenceEnvelope — Tests for EvidenceEnvelope dataclass
# =============================================================================
class TestEvidenceEnvelope:
    """Tests for EvidenceEnvelope class."""

    def test_envelope_signed_only(self) -> None:
        """EvidenceEnvelope should work for signed-only (unencrypted) mode."""
        header = EnvelopeHeader(
            envelope_id="ev-12345678",
            schema_version="1.0.0",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            body_hash="abc123",
        )
        sig = Signature(value="sig123")
        cert = Certificate(node_id="node-001", public_key="pk123")

        envelope = EvidenceEnvelope(
            header=header,
            signature=sig,
            cert=cert,
            body={"evidence": "test"},
        )

        d = envelope.to_dict()
        assert "header" in d
        assert "signature" in d
        assert "cert" in d
        assert "body" in d  # Signed-only includes body
        assert "ciphertext" not in d

    def test_envelope_encrypted(self) -> None:
        """EvidenceEnvelope should work for encrypted mode."""
        header = EnvelopeHeader(
            envelope_id="ev-12345678",
            schema_version="1.0.0",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            body_hash="abc123",
        )
        sig = Signature(value="sig123")
        cert = Certificate(node_id="node-001", public_key="pk123")
        kw = KeyWrap(encrypted_dek="dek123", key_id="key-001")
        ct = Ciphertext(iv="iv123", data="data123", tag="tag123")

        envelope = EvidenceEnvelope(
            header=header,
            signature=sig,
            cert=cert,
            keywrap=kw,
            ciphertext=ct,
            body={"evidence": "test"},  # Will be excluded in to_dict
        )

        d = envelope.to_dict()
        assert "keywrap" in d
        assert "ciphertext" in d
        assert "body" not in d  # Encrypted mode excludes body

    def test_envelope_to_json(self) -> None:
        """EvidenceEnvelope.to_json() should produce valid JSON."""
        header = EnvelopeHeader(
            envelope_id="ev-12345678",
            schema_version="1.0.0",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            body_hash="abc123",
        )
        sig = Signature(value="sig123")
        cert = Certificate(node_id="node-001", public_key="pk123")

        envelope = EvidenceEnvelope(
            header=header,
            signature=sig,
            cert=cert,
            body={"evidence": "test"},
        )

        json_str = envelope.to_json()
        parsed = json.loads(json_str)

        assert parsed["header"]["envelope_id"] == "ev-12345678"

    def test_envelope_compute_hash(self) -> None:
        """EvidenceEnvelope.compute_envelope_hash() should be deterministic."""
        header = EnvelopeHeader(
            envelope_id="ev-12345678",
            schema_version="1.0.0",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            body_hash="abc123",
        )
        sig = Signature(value="sig123")
        cert = Certificate(node_id="node-001", public_key="pk123")

        envelope = EvidenceEnvelope(
            header=header,
            signature=sig,
            cert=cert,
            body={"evidence": "test"},
        )

        hash1 = envelope.compute_envelope_hash()
        hash2 = envelope.compute_envelope_hash()

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex digest


# =============================================================================
# TestEvidenceEnvelopeBuilder — Tests for the builder pattern
# =============================================================================
class TestEvidenceEnvelopeBuilder:
    """Tests for EvidenceEnvelopeBuilder class."""

    def test_builder_minimal(self) -> None:
        """Builder should create envelope with minimal required fields."""
        envelope = (EvidenceEnvelopeBuilder()
            .with_node_id("node-001")
            .with_body({"evidence": "test"})
            .build())

        assert envelope.header.node_id == "node-001"
        assert envelope.body == {"evidence": "test"}
        assert envelope.header.envelope_id.startswith("ev-")

    def test_builder_missing_node_id(self) -> None:
        """Builder should raise error if node_id is missing."""
        with pytest.raises(ValueError, match="node_id is required"):
            (EvidenceEnvelopeBuilder()
                .with_body({"evidence": "test"})
                .build())

    def test_builder_missing_body(self) -> None:
        """Builder should raise error if body is missing for unencrypted."""
        with pytest.raises(ValueError, match="body is required"):
            (EvidenceEnvelopeBuilder()
                .with_node_id("node-001")
                .build())

    def test_builder_with_all_fields(self) -> None:
        """Builder should accept all optional fields."""
        envelope = (EvidenceEnvelopeBuilder()
            .with_node_id("node-001")
            .with_body({"evidence": "test"})
            .with_trace_id("trace-123")
            .with_envelope_id("ev-custom")
            .with_expires_at("2026-02-27T12:00:00Z")
            .with_public_key("pk123")
            .with_signature("sig123")
            .build())

        assert envelope.header.envelope_id == "ev-custom"
        assert envelope.header.trace_id == "trace-123"
        assert envelope.header.expires_at == "2026-02-27T12:00:00Z"
        assert envelope.signature.value == "sig123"
        assert envelope.cert.public_key == "pk123"

    def test_builder_encrypted(self) -> None:
        """Builder should create encrypted envelope."""
        envelope = (EvidenceEnvelopeBuilder()
            .with_node_id("node-001")
            .with_body({"evidence": "test"})
            .with_encryption(
                encrypted_dek="dek123",
                key_id="key-001",
                ciphertext_data="ct123",
                ciphertext_iv="iv123",
                ciphertext_tag="tag123",
            )
            .build())

        assert envelope.keywrap is not None
        assert envelope.ciphertext is not None
        assert envelope.keywrap.encrypted_dek == "dek123"
        assert envelope.ciphertext.data == "ct123"

    def test_builder_body_hash_consistency(self) -> None:
        """Builder should compute consistent body hash."""
        body = {"evidence": "test", "data": [1, 2, 3]}

        envelope1 = (EvidenceEnvelopeBuilder()
            .with_node_id("node-001")
            .with_body(body)
            .build())

        envelope2 = (EvidenceEnvelopeBuilder()
            .with_node_id("node-001")
            .with_body(body)
            .build())

        expected_hash = canonical_json_hash(body)
        assert envelope1.header.body_hash == expected_hash
        assert envelope2.header.body_hash == expected_hash


# =============================================================================
# TestValidateEnvelopeSchema — Tests for schema validation
# =============================================================================
class TestValidateEnvelopeSchema:
    """Tests for validate_envelope_schema function."""

    def test_validate_valid_envelope(self) -> None:
        """Valid envelope should pass validation."""
        envelope_dict = {
            "header": {
                "envelope_id": "ev-12345678",
                "schema_version": "1.0.0",
                "created_at": "2026-02-26T12:00:00Z",
                "node_id": "node-001",
                "body_hash": "abc123",
            },
            "signature": {
                "algorithm": "Ed25519",
                "value": "sig123",
                "signed_fields": ["header", "body_hash"],
            },
            "cert": {
                "algorithm": "Ed25519",
                "node_id": "node-001",
            },
        }

        errors = validate_envelope_schema(envelope_dict)
        assert len(errors) == 0

    def test_validate_missing_header(self) -> None:
        """Missing header should fail validation."""
        envelope_dict = {
            "signature": {"algorithm": "Ed25519"},
            "cert": {"algorithm": "Ed25519"},
        }

        errors = validate_envelope_schema(envelope_dict)
        assert any("header" in e for e in errors)

    def test_validate_missing_header_fields(self) -> None:
        """Missing header fields should fail validation."""
        envelope_dict = {
            "header": {
                "envelope_id": "ev-12345678",
                # Missing other required fields
            },
            "signature": {"algorithm": "Ed25519"},
            "cert": {"algorithm": "Ed25519"},
        }

        errors = validate_envelope_schema(envelope_dict)
        assert any("schema_version" in e for e in errors)
        assert any("node_id" in e for e in errors)

    def test_validate_encrypted_envelope(self) -> None:
        """Encrypted envelope should require keywrap and ciphertext fields."""
        envelope_dict = {
            "header": {
                "envelope_id": "ev-12345678",
                "schema_version": "1.0.0",
                "created_at": "2026-02-26T12:00:00Z",
                "node_id": "node-001",
                "body_hash": "abc123",
            },
            "signature": {
                "algorithm": "Ed25519",
                "signed_fields": ["header"],
            },
            "cert": {
                "algorithm": "Ed25519",
            },
            "ciphertext": {
                "algorithm": "AES-256-GCM",
                "iv": "iv123",
                "data": "data123",
                "tag": "tag123",
            },
            # Missing keywrap
        }

        errors = validate_envelope_schema(envelope_dict)
        assert any("keywrap" in e for e in errors)


# =============================================================================
# TestConvenienceFunctions — Tests for convenience functions
# =============================================================================
class TestConvenienceFunctions:
    """Tests for create_signed_envelope and create_encrypted_envelope."""

    def test_create_signed_envelope(self) -> None:
        """create_signed_envelope should create valid envelope."""
        body = {"evidence": "test", "value": 42}
        envelope = create_signed_envelope(
            node_id="node-001",
            body=body,
            signature_value="sig123",
            public_key="pk123",
            trace_id="trace-xyz",
        )

        assert envelope.header.node_id == "node-001"
        assert envelope.header.trace_id == "trace-xyz"
        assert envelope.signature.value == "sig123"
        assert envelope.cert.public_key == "pk123"
        assert envelope.body == body
        assert envelope.keywrap is None
        assert envelope.ciphertext is None

    def test_create_encrypted_envelope(self) -> None:
        """create_encrypted_envelope should create valid encrypted envelope."""
        envelope = create_encrypted_envelope(
            node_id="node-001",
            body_hash="abc123",
            encrypted_dek="dek123",
            key_id="key-001",
            ciphertext_data="ct123",
            ciphertext_iv="iv123",
            ciphertext_tag="tag123",
            signature_value="sig123",
            public_key="pk123",
        )

        assert envelope.header.node_id == "node-001"
        assert envelope.header.body_hash == "abc123"
        assert envelope.keywrap is not None
        assert envelope.keywrap.encrypted_dek == "dek123"
        assert envelope.ciphertext is not None
        assert envelope.ciphertext.data == "ct123"
        assert envelope.body is None  # No plaintext body


# =============================================================================
# TestSchemaVersion — Tests for schema versioning
# =============================================================================
class TestSchemaVersion:
    """Tests for schema version compatibility."""

    def test_schema_version_constant(self) -> None:
        """Schema version should be defined."""
        assert ENVELOPE_SCHEMA_VERSION == "1.0.0"

    def test_envelope_includes_schema_version(self) -> None:
        """Envelope should include schema version."""
        envelope = (EvidenceEnvelopeBuilder()
            .with_node_id("node-001")
            .with_body({"test": 1})
            .build())

        assert envelope.header.schema_version == ENVELOPE_SCHEMA_VERSION


# =============================================================================
# TestIntegration — Integration tests
# =============================================================================
class TestIntegration:
    """Integration tests for envelope functionality."""

    def test_full_roundtrip(self) -> None:
        """Full roundtrip: build -> serialize -> validate -> parse."""
        # Build
        body = {
            "evidence_id": "ev-001",
            "type": "static_analysis",
            "findings": [
                {"rule": "SEC001", "severity": "high"}
            ]
        }

        envelope = create_signed_envelope(
            node_id="node-001",
            body=body,
            signature_value="test-signature",
            public_key="test-public-key",
            trace_id="trace-123",
        )

        # Serialize
        json_str = envelope.to_json()
        envelope_dict = json.loads(json_str)

        # Validate
        errors = validate_envelope_schema(envelope_dict)
        assert len(errors) == 0, f"Validation errors: {errors}"

        # Verify body hash matches
        expected_hash = canonical_json_hash(body)
        assert envelope_dict["header"]["body_hash"] == expected_hash

    def test_encrypted_roundtrip(self) -> None:
        """Encrypted envelope roundtrip validation."""
        envelope = create_encrypted_envelope(
            node_id="node-001",
            body_hash="abc123def456",
            encrypted_dek="encrypted-key-data",
            key_id="rsa-key-001",
            ciphertext_data="encrypted-body-data",
            ciphertext_iv="initialization-vector",
            ciphertext_tag="auth-tag",
            signature_value="signature-value",
            public_key="node-public-key",
        )

        # Serialize
        json_str = envelope.to_json()
        envelope_dict = json.loads(json_str)

        # Validate
        errors = validate_envelope_schema(envelope_dict)
        assert len(errors) == 0, f"Validation errors: {errors}"

        # Verify structure
        assert "keywrap" in envelope_dict
        assert "ciphertext" in envelope_dict
        assert "body" not in envelope_dict
