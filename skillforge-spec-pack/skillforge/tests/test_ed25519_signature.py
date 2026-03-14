"""
Test suite for Ed25519 Signature Module.

Tests cover:
- Keypair generation
- Signing and verification
- Signed fields validation
- Envelope tampering detection
- Node signature verification
"""

import pytest
import json
from skillforge.src.utils.ed25519_signature import (
    generate_keypair,
    sign_envelope,
    verify_envelope_signature,
    verify_signed_fields,
    create_node_signature,
    verify_node_signature,
    SignatureResult,
    KeypairResult,
    Ed25519Error,
    InvalidSignatureError,
    MissingFieldError,
    CryptographyNotAvailableError,
    CRYPTOGRAPHY_AVAILABLE,
    DEFAULT_SIGNED_FIELDS,
)


# Skip all tests if cryptography is not available
pytestmark = pytest.mark.skipif(
    not CRYPTOGRAPHY_AVAILABLE,
    reason="cryptography library not available"
)


class TestKeypairGeneration:
    """Tests for Ed25519 keypair generation."""

    def test_generate_keypair_returns_valid_types(self):
        """Test that keypair generation returns valid KeypairResult."""
        result = generate_keypair()
        assert isinstance(result, KeypairResult)
        assert isinstance(result.private_key_hex, str)
        assert isinstance(result.public_key_hex, str)
        assert isinstance(result.private_key_pem, str)
        assert isinstance(result.public_key_pem, str)

    def test_private_key_hex_length(self):
        """Test that private key hex is 64 chars (32 bytes)."""
        result = generate_keypair()
        assert len(result.private_key_hex) == 64
        assert len(result.public_key_hex) == 64

    def test_private_key_hex_valid_hex(self):
        """Test that private key hex is valid hexadecimal."""
        result = generate_keypair()
        try:
            bytes.fromhex(result.private_key_hex)
            bytes.fromhex(result.public_key_hex)
        except ValueError:
            pytest.fail("Invalid hex string")

    def test_private_key_pem_contains_markers(self):
        """Test that PEM format contains correct markers."""
        result = generate_keypair()
        assert "-----BEGIN PRIVATE KEY-----" in result.private_key_pem
        assert "-----END PRIVATE KEY-----" in result.private_key_pem
        assert "-----BEGIN PUBLIC KEY-----" in result.public_key_pem
        assert "-----END PUBLIC KEY-----" in result.public_key_pem

    def test_keypair_uniqueness(self):
        """Test that each generated keypair is unique."""
        keypair1 = generate_keypair()
        keypair2 = generate_keypair()
        assert keypair1.private_key_hex != keypair2.private_key_hex
        assert keypair1.public_key_hex != keypair2.public_key_hex

    def test_keypair_to_dict(self):
        """Test KeypairResult.to_dict() method."""
        result = generate_keypair()
        data = result.to_dict()
        assert "private_key_hex" in data
        assert "public_key_hex" in data
        assert "private_key_pem" in data
        assert "public_key_pem" in data


class TestSignatureResult:
    """Tests for SignatureResult class."""

    def test_signature_result_initialization(self):
        """Test SignatureResult initialization."""
        sig_bytes = b'\x00' * 64
        result = SignatureResult(
            signature_value=sig_bytes,
            signed_fields=["field1", "field2"],
            algorithm="Ed25519"
        )
        assert result.signature_value == sig_bytes
        assert result.signed_fields == ["field1", "field2"]
        assert result.algorithm == "Ed25519"

    def test_signature_result_to_dict(self):
        """Test SignatureResult.to_dict() method."""
        sig_bytes = bytes.fromhex('a' * 64)
        result = SignatureResult(
            signature_value=sig_bytes,
            signed_fields=["header.envelope_id"],
        )
        data = result.to_dict()
        assert data["algorithm"] == "Ed25519"
        assert data["value"] == 'a' * 64
        assert data["signed_fields"] == ["header.envelope_id"]

    def test_signature_result_from_dict(self):
        """Test SignatureResult.from_dict() class method."""
        data = {
            "algorithm": "Ed25519",
            "value": 'b' * 64,
            "signed_fields": ["header.node_id"]
        }
        result = SignatureResult.from_dict(data)
        assert result.algorithm == "Ed25519"
        assert result.signature_value == bytes.fromhex('b' * 64)
        assert result.signed_fields == ["header.node_id"]


class TestEnvelopeSigning:
    """Tests for envelope signing operations."""

    @pytest.fixture
    def sample_envelope(self):
        """Create a sample envelope for testing."""
        return {
            "header": {
                "envelope_id": "env-test-001",
                "schema_version": "1.0.0",
                "created_at": "2026-02-26T10:00:00Z",
                "node_id": "node-alpha",
                "body_hash": "abc123",
                "body_encoding": "utf-8",
                "nonce": "random-nonce-123",
            },
            "ciphertext": {
                "iv": "iv-bytes-123",
                "data": "encrypted-data",
                "tag": "auth-tag-123",
            }
        }

    @pytest.fixture
    def keypair(self):
        """Generate a keypair for testing."""
        return generate_keypair()

    def test_sign_envelope_returns_signature_result(self, sample_envelope, keypair):
        """Test that sign_envelope returns SignatureResult."""
        result = sign_envelope(sample_envelope, keypair.private_key_hex)
        assert isinstance(result, SignatureResult)
        assert len(result.signature_value) == 64  # Ed25519 signature is 64 bytes
        assert result.algorithm == "Ed25519"
        assert len(result.signed_fields) > 0

    def test_sign_envelope_with_default_fields(self, sample_envelope, keypair):
        """Test signing with default signed fields."""
        result = sign_envelope(sample_envelope, keypair.private_key_hex)
        assert result.signed_fields == DEFAULT_SIGNED_FIELDS

    def test_sign_envelope_with_custom_fields(self, sample_envelope, keypair):
        """Test signing with custom signed fields."""
        custom_fields = ["header.envelope_id", "header.node_id"]
        result = sign_envelope(sample_envelope, keypair.private_key_hex, custom_fields)
        assert result.signed_fields == custom_fields

    def test_sign_missing_field_raises_error(self, keypair):
        """Test that signing with missing required field raises error."""
        incomplete_envelope = {
            "header": {
                "envelope_id": "env-test-001",
            }
        }
        with pytest.raises(MissingFieldError):
            sign_envelope(incomplete_envelope, keypair.private_key_hex)

    def test_sign_invalid_private_key_hex(self, sample_envelope):
        """Test that invalid private key hex raises error."""
        with pytest.raises(Ed25519Error):
            sign_envelope(sample_envelope, "invalid-hex-string")

    def test_sign_wrong_length_private_key(self, sample_envelope):
        """Test that wrong length private key raises error."""
        # Ed25519 private key should be 32 bytes (64 hex chars)
        with pytest.raises(Ed25519Error):
            sign_envelope(sample_envelope, "a" * 32)  # Too short


class TestEnvelopeVerification:
    """Tests for envelope verification operations."""

    @pytest.fixture
    def sample_envelope(self):
        """Create a sample envelope for testing."""
        return {
            "header": {
                "envelope_id": "env-test-002",
                "schema_version": "1.0.0",
                "created_at": "2026-02-26T10:00:00Z",
                "node_id": "node-beta",
                "body_hash": "def456",
                "body_encoding": "utf-8",
                "nonce": "nonce-456",
            },
            "ciphertext": {
                "iv": "iv-789",
                "data": "data-789",
                "tag": "tag-789",
            }
        }

    @pytest.fixture
    def signed_envelope(self, sample_envelope):
        """Create a signed envelope for testing."""
        keypair = generate_keypair()
        signature = sign_envelope(sample_envelope, keypair.private_key_hex)
        return sample_envelope, keypair, signature

    def test_verify_valid_signature(self, signed_envelope):
        """Test that valid signature verifies correctly."""
        envelope, keypair, signature = signed_envelope
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is True

    def test_verify_invalid_signature(self, signed_envelope):
        """Test that invalid signature fails verification."""
        envelope, keypair, signature = signed_envelope
        # Corrupt the signature
        signature.signature_value = b'\xFF' * 64
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is False

    def test_verify_with_dict_signature(self, signed_envelope):
        """Test verification with signature as dict."""
        envelope, keypair, signature = signed_envelope
        sig_dict = signature.to_dict()
        assert verify_envelope_signature(envelope, keypair.public_key_hex, sig_dict) is True

    def test_verify_wrong_public_key(self, signed_envelope):
        """Test that wrong public key fails verification."""
        envelope, keypair, signature = signed_envelope
        # Generate a different keypair
        wrong_keypair = generate_keypair()
        assert verify_envelope_signature(envelope, wrong_keypair.public_key_hex, signature) is False

    def test_verify_tampered_envelope(self, signed_envelope):
        """Test that tampered envelope fails verification."""
        envelope, keypair, signature = signed_envelope
        # Tamper with envelope content
        original_envelope_id = envelope["header"]["envelope_id"]
        envelope["header"]["envelope_id"] = "tampered-id"
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is False
        # Restore for cleanup
        envelope["header"]["envelope_id"] = original_envelope_id


class TestSignedFieldsValidation:
    """Tests for signed fields validation."""

    def test_verify_signed_fields_all_default(self):
        """Test that default signed fields are all covered."""
        signature = SignatureResult(
            signature_value=b'\x00' * 64,
            signed_fields=DEFAULT_SIGNED_FIELDS.copy()
        )
        assert verify_signed_fields(signature) is True

    def test_verify_signed_fields_missing_required(self):
        """Test that missing required field fails validation."""
        signature = SignatureResult(
            signature_value=b'\x00' * 64,
            signed_fields=["header.envelope_id"]  # Missing other required fields
        )
        assert verify_signed_fields(signature) is False

    def test_verify_signed_fields_with_dict(self):
        """Test verify_signed_fields with dict input."""
        sig_dict = {
            "value": "a" * 64,
            "signed_fields": DEFAULT_SIGNED_FIELDS.copy()
        }
        assert verify_signed_fields(sig_dict) is True

    def test_verify_signed_fields_custom_required(self):
        """Test verify_signed_fields with custom required fields."""
        signature = SignatureResult(
            signature_value=b'\x00' * 64,
            signed_fields=["field1", "field2", "field3"]
        )
        # Only require field1 and field2
        assert verify_signed_fields(signature, ["field1", "field2"]) is True
        # Require field4 which is not signed
        assert verify_signed_fields(signature, ["field1", "field4"]) is False


class TestNodeSignature:
    """Tests for node signature convenience functions."""

    def test_create_node_signature(self):
        """Test create_node_signature function."""
        envelope = {
            "header": {
                "envelope_id": "env-node-001",
                "node_id": "test-node",
                "body_hash": "hash123"
            }
        }
        keypair = generate_keypair()
        result = create_node_signature("test-node", envelope, keypair.private_key_hex)
        assert "signature" in result
        assert "cert" in result
        assert result["cert"]["node_id"] == "test-node"
        assert "public_key" in result["cert"]
        assert result["cert"]["algorithm"] == "Ed25519"

    def test_verify_node_signature_valid(self):
        """Test verify_node_signature with valid signature."""
        envelope = {
            "header": {
                "envelope_id": "env-node-002",
                "node_id": "test-node-2",
                "body_hash": "hash456"
            }
        }
        keypair = generate_keypair()
        sig_data = create_node_signature("test-node-2", envelope, keypair.private_key_hex)

        result = verify_node_signature(
            envelope,
            sig_data["signature"],
            sig_data["cert"]
        )
        assert result["valid"] is True
        assert result["node_id"] == "test-node-2"

    def test_verify_node_signature_missing_public_key(self):
        """Test verify_node_signature with missing public_key."""
        envelope = {"header": {"envelope_id": "x"}}
        sig_data = {
            "signature": {"value": "a" * 64, "signed_fields": []},
            "cert": {"node_id": "node1"}  # Missing public_key
        }
        result = verify_node_signature(envelope, sig_data["signature"], sig_data["cert"])
        assert result["valid"] is False
        assert "public_key" in result["reason"]

    def test_verify_node_signature_node_id_mismatch(self):
        """Test verify_node_signature with node_id mismatch."""
        envelope = {
            "header": {
                "envelope_id": "env-node-003",
                "node_id": "node-in-envelope"
            }
        }
        keypair = generate_keypair()
        sig_data = create_node_signature("node-in-cert", envelope, keypair.private_key_hex)

        result = verify_node_signature(
            envelope,
            sig_data["signature"],
            sig_data["cert"]
        )
        assert result["valid"] is False
        assert "mismatch" in result["reason"]


class TestTamperDetection:
    """Tests for tamper detection in signed envelopes."""

    @pytest.fixture
    def signed_envelope(self):
        """Create a fully signed envelope for tamper testing."""
        envelope = {
            "header": {
                "envelope_id": "env-tamper-001",
                "schema_version": "1.0.0",
                "created_at": "2026-02-26T10:00:00Z",
                "node_id": "node-tamper",
                "body_hash": "hash-tamper",
                "body_encoding": "utf-8",
                "nonce": "nonce-tamper",
            },
            "ciphertext": {
                "iv": "iv-tamper",
                "data": "data-tamper",
                "tag": "tag-tamper",
            }
        }
        keypair = generate_keypair()
        signature = sign_envelope(envelope, keypair.private_key_hex)
        return envelope, keypair, signature

    def test_tamper_envelope_id(self, signed_envelope):
        """Test that tampering envelope_id is detected."""
        envelope, keypair, signature = signed_envelope
        envelope["header"]["envelope_id"] = "tampered"
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is False

    def test_tamper_schema_version(self, signed_envelope):
        """Test that tampering schema_version is detected."""
        envelope, keypair, signature = signed_envelope
        envelope["header"]["schema_version"] = "2.0.0"
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is False

    def test_tamper_node_id(self, signed_envelope):
        """Test that tampering node_id is detected."""
        envelope, keypair, signature = signed_envelope
        envelope["header"]["node_id"] = "malicious-node"
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is False

    def test_tamper_body_hash(self, signed_envelope):
        """Test that tampering body_hash is detected."""
        envelope, keypair, signature = signed_envelope
        envelope["header"]["body_hash"] = "malicious-hash"
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is False

    def test_tamper_nonce(self, signed_envelope):
        """Test that tampering nonce is detected."""
        envelope, keypair, signature = signed_envelope
        envelope["header"]["nonce"] = "replay-nonce"
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is False

    def test_tamper_ciphertext_iv(self, signed_envelope):
        """Test that tampering ciphertext.iv is detected."""
        envelope, keypair, signature = signed_envelope
        envelope["ciphertext"]["iv"] = "tampered-iv"
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is False

    def test_tamper_ciphertext_data(self, signed_envelope):
        """Test that tampering ciphertext.data is detected."""
        envelope, keypair, signature = signed_envelope
        envelope["ciphertext"]["data"] = "tampered-data"
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is False

    def test_tamper_ciphertext_tag(self, signed_envelope):
        """Test that tampering ciphertext.tag is detected."""
        envelope, keypair, signature = signed_envelope
        envelope["ciphertext"]["tag"] = "tampered-tag"
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is False

    def test_no_tamper_original_valid(self, signed_envelope):
        """Test that original envelope without tampering verifies correctly."""
        envelope, keypair, signature = signed_envelope
        assert verify_envelope_signature(envelope, keypair.public_key_hex, signature) is True


class TestCryptographyNotAvailable:
    """Tests for behavior when cryptography library is not available."""

    def test_generate_keypair_without_cryptography(self, monkeypatch):
        """Test that generate_keypair raises error without cryptography."""
        # Temporarily set CRYPTOGRAPHY_AVAILABLE to False
        import skillforge.src.utils.ed25519_signature as sig_module
        monkeypatch.setattr(sig_module, "CRYPTOGRAPHY_AVAILABLE", False)
        monkeypatch.setattr(sig_module, "ed25519", None)

        with pytest.raises(CryptographyNotAvailableError):
            generate_keypair()

    def test_sign_without_cryptography(self, monkeypatch):
        """Test that sign_envelope raises error without cryptography."""
        import skillforge.src.utils.ed25519_signature as sig_module
        monkeypatch.setattr(sig_module, "CRYPTOGRAPHY_AVAILABLE", False)
        monkeypatch.setattr(sig_module, "ed25519", None)

        with pytest.raises(CryptographyNotAvailableError):
            sign_envelope({}, "dummy_key")


# Integration Tests
class TestIntegration:
    """Integration tests for complete signing/verification workflows."""

    def test_full_signing_workflow(self):
        """Test complete workflow: generate keys, sign, verify."""
        # 1. Generate keypair
        keypair = generate_keypair()
        assert len(keypair.private_key_hex) == 64

        # 2. Create envelope
        envelope = {
            "header": {
                "envelope_id": "env-integration-001",
                "schema_version": "1.0.0",
                "created_at": "2026-02-26T12:00:00Z",
                "node_id": "node-integration",
                "body_hash": "integration-hash",
                "body_encoding": "utf-8",
                "nonce": "integration-nonce",
            },
            "ciphertext": {
                "iv": "integration-iv",
                "data": "integration-data",
                "tag": "integration-tag",
            }
        }

        # 3. Sign envelope
        signature = sign_envelope(envelope, keypair.private_key_hex)
        assert signature.algorithm == "Ed25519"
        assert len(signature.signature_value) == 64

        # 4. Verify signature
        is_valid = verify_envelope_signature(envelope, keypair.public_key_hex, signature)
        assert is_valid is True

        # 5. Verify signed fields
        fields_valid = verify_signed_fields(signature)
        assert fields_valid is True

    def test_cross_keypair_verification_fails(self):
        """Test that signature from one keypair fails with another keypair."""
        keypair1 = generate_keypair()
        keypair2 = generate_keypair()

        envelope = {
            "header": {
                "envelope_id": "env-cross-001",
                "node_id": "node-cross",
                "body_hash": "cross-hash",
                "schema_version": "1.0.0",
                "created_at": "2026-02-26T12:00:00Z",
                "body_encoding": "utf-8",
                "nonce": "cross-nonce",
            },
            "ciphertext": {
                "iv": "cross-iv",
                "data": "cross-data",
                "tag": "cross-tag",
            }
        }

        # Sign with keypair1
        signature = sign_envelope(envelope, keypair1.private_key_hex)

        # Verify with keypair2 should fail
        is_valid = verify_envelope_signature(envelope, keypair2.public_key_hex, signature)
        assert is_valid is False

    def test_node_signature_workflow(self):
        """Test complete node signature workflow."""
        envelope = {
            "header": {
                "envelope_id": "env-node-workflow-001",
                "schema_version": "1.0.0",
                "created_at": "2026-02-26T13:00:00Z",
                "node_id": "node-workflow",
                "body_hash": "workflow-hash",
                "body_encoding": "utf-8",
                "nonce": "workflow-nonce",
            },
            "ciphertext": {
                "iv": "workflow-iv",
                "data": "workflow-data",
                "tag": "workflow-tag",
            }
        }

        # Generate keypair
        keypair = generate_keypair()

        # Create node signature
        sig_result = create_node_signature("node-workflow", envelope, keypair.private_key_hex)

        # Verify node signature
        verify_result = verify_node_signature(
            envelope,
            sig_result["signature"],
            sig_result["cert"]
        )

        assert verify_result["valid"] is True
        assert verify_result["node_id"] == "node-workflow"
