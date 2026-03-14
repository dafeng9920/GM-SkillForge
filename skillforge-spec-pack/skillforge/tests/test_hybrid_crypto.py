"""
Test Suite for Hybrid Crypto Module (T04 - ISSUE-03)

This test suite validates the AES-256-GCM + RSA-OAEP-256 hybrid encryption
implementation against the acceptance criteria:

1. 正常解密通过 (Normal decryption passes)
2. 任意篡改密文触发解密失败 (Any ciphertext tampering triggers decryption failure)

Executor: Kior-B
"""

import base64
import json
import os
import pytest
from unittest.mock import patch

# Import the module under test
from skillforge.src.utils.hybrid_crypto import (
    # Constants
    AES_KEY_SIZE,
    GCM_IV_SIZE,
    GCM_TAG_SIZE,
    CRYPTOGRAPHY_AVAILABLE,

    # Exceptions
    HybridCryptoError,
    EncryptionError,
    DecryptionError,
    KeyGenerationError,
    IntegrityError,
    CryptographyNotAvailableError,

    # Data classes
    EncryptionResult,
    RSAKeyPair,

    # Core functions
    generate_dek,
    generate_rsa_keypair,
    encrypt_dek,
    decrypt_dek,
    encrypt_body,
    decrypt_body,

    # High-level API
    hybrid_encrypt,
    hybrid_decrypt,
    hybrid_decrypt_to_string,
    hybrid_decrypt_to_json,
)


# Skip all tests if cryptography is not available
pytestmark = pytest.mark.skipif(
    not CRYPTOGRAPHY_AVAILABLE,
    reason="cryptography library not installed"
)


class TestDEKGeneration:
    """Tests for Data Encryption Key generation."""

    def test_generate_dek_returns_correct_size(self):
        """DEK should be 32 bytes (256 bits)."""
        dek = generate_dek()
        assert len(dek) == AES_KEY_SIZE
        assert len(dek) == 32

    def test_generate_dek_returns_random_bytes(self):
        """Each DEK should be unique."""
        dek1 = generate_dek()
        dek2 = generate_dek()
        dek3 = generate_dek()

        assert dek1 != dek2
        assert dek2 != dek3
        assert dek1 != dek3

    def test_generate_dek_multiple_iterations(self):
        """Generate 100 DEKs and verify all are unique."""
        deks = [generate_dek() for _ in range(100)]
        unique_deks = set(deks)
        assert len(unique_deks) == 100


class TestRSAKeyPairGeneration:
    """Tests for RSA key pair generation."""

    def test_generate_rsa_keypair_default_size(self):
        """Default RSA key size should be 2048 bits."""
        keypair = generate_rsa_keypair()
        # Key size in bits
        assert keypair.private_key.key_size == 2048
        assert keypair.public_key.key_size == 2048

    def test_generate_rsa_keypair_with_key_id(self):
        """Key ID should be stored correctly."""
        keypair = generate_rsa_keypair(key_id="test-key-001")
        assert keypair.key_id == "test-key-001"

    def test_generate_rsa_keypair_unique_keys(self):
        """Each key pair should be unique."""
        kp1 = generate_rsa_keypair()
        kp2 = generate_rsa_keypair()

        # Public keys should differ
        assert kp1.get_public_key_pem() != kp2.get_public_key_pem()

    def test_get_public_key_pem_format(self):
        """Public key PEM should have correct format."""
        keypair = generate_rsa_keypair()
        pem = keypair.get_public_key_pem()

        assert "-----BEGIN PUBLIC KEY-----" in pem
        assert "-----END PUBLIC KEY-----" in pem

    def test_get_private_key_pem_format(self):
        """Private key PEM should have correct format."""
        keypair = generate_rsa_keypair()
        pem = keypair.get_private_key_pem()

        assert "-----BEGIN PRIVATE KEY-----" in pem
        assert "-----END PRIVATE KEY-----" in pem

    def test_get_private_key_pem_encrypted(self):
        """Private key PEM can be password encrypted."""
        keypair = generate_rsa_keypair()
        pem = keypair.get_private_key_pem(password=b"secret")

        assert "-----BEGIN ENCRYPTED PRIVATE KEY-----" in pem
        assert "-----END ENCRYPTED PRIVATE KEY-----" in pem


class TestDEKEncryption:
    """Tests for DEK encryption/decryption with RSA-OAEP-256."""

    def test_encrypt_decrypt_dek_roundtrip(self):
        """DEK encryption and decryption should be reversible."""
        keypair = generate_rsa_keypair()
        dek = generate_dek()

        encrypted = encrypt_dek(dek, keypair.public_key)
        decrypted = decrypt_dek(encrypted, keypair.private_key)

        assert decrypted == dek

    def test_encrypt_dek_wrong_size_fails(self):
        """DEK with wrong size should raise error."""
        keypair = generate_rsa_keypair()
        wrong_size_dek = b"short"

        with pytest.raises(EncryptionError):
            encrypt_dek(wrong_size_dek, keypair.public_key)

    def test_decrypt_dek_wrong_key_fails(self):
        """Decryption with wrong key should fail."""
        kp1 = generate_rsa_keypair()
        kp2 = generate_rsa_keypair()  # Different key pair
        dek = generate_dek()

        encrypted = encrypt_dek(dek, kp1.public_key)

        with pytest.raises(DecryptionError):
            decrypt_dek(encrypted, kp2.private_key)


class TestBodyEncryption:
    """Tests for body encryption/decryption with AES-256-GCM."""

    def test_encrypt_decrypt_body_bytes_roundtrip(self):
        """Body encryption and decryption should be reversible."""
        dek = generate_dek()
        plaintext = b"Hello, World! This is a secret message."

        iv, ciphertext, tag = encrypt_body(plaintext, dek)
        decrypted = decrypt_body(iv, ciphertext, tag, dek)

        assert decrypted == plaintext

    def test_encrypt_decrypt_body_string_roundtrip(self):
        """String input should be handled correctly."""
        dek = generate_dek()
        plaintext = "Unicode test: 你好世界 🌍"

        iv, ciphertext, tag = encrypt_body(plaintext, dek)
        decrypted = decrypt_body(iv, ciphertext, tag, dek)

        assert decrypted == plaintext.encode('utf-8')

    def test_encrypt_body_produces_different_iv(self):
        """Each encryption should use a different IV."""
        dek = generate_dek()
        plaintext = b"Same message"

        iv1, _, _ = encrypt_body(plaintext, dek)
        iv2, _, _ = encrypt_body(plaintext, dek)

        assert iv1 != iv2

    def test_encrypt_body_produces_different_ciphertext(self):
        """Same plaintext with same key should produce different ciphertext."""
        dek = generate_dek()
        plaintext = b"Same message"

        _, ct1, _ = encrypt_body(plaintext, dek)
        _, ct2, _ = encrypt_body(plaintext, dek)

        assert ct1 != ct2  # Due to different IV

    def test_decrypt_with_wrong_dek_fails(self):
        """Decryption with wrong DEK should fail."""
        dek1 = generate_dek()
        dek2 = generate_dek()  # Different DEK
        plaintext = b"Secret message"

        iv, ciphertext, tag = encrypt_body(plaintext, dek1)

        with pytest.raises((IntegrityError, DecryptionError)):
            decrypt_body(iv, ciphertext, tag, dek2)

    def test_decrypt_with_tampered_ciphertext_fails(self):
        """ISSUE-03 CRITERION: Tampered ciphertext should trigger decryption failure."""
        dek = generate_dek()
        plaintext = b"Original message"

        iv, ciphertext, tag = encrypt_body(plaintext, dek)

        # Tamper with ciphertext
        tampered_ciphertext = bytearray(ciphertext)
        tampered_ciphertext[0] ^= 0xFF  # Flip first byte

        with pytest.raises((IntegrityError, DecryptionError)):
            decrypt_body(iv, bytes(tampered_ciphertext), tag, dek)

    def test_decrypt_with_tampered_tag_fails(self):
        """ISSUE-03 CRITERION: Tampered tag should trigger decryption failure."""
        dek = generate_dek()
        plaintext = b"Original message"

        iv, ciphertext, tag = encrypt_body(plaintext, dek)

        # Tamper with tag
        tampered_tag = bytearray(tag)
        tampered_tag[0] ^= 0xFF

        with pytest.raises((IntegrityError, DecryptionError)):
            decrypt_body(iv, ciphertext, bytes(tampered_tag), dek)

    def test_decrypt_with_tampered_iv_fails(self):
        """Tampered IV should cause decryption to fail or produce wrong output."""
        dek = generate_dek()
        plaintext = b"Original message"

        iv, ciphertext, tag = encrypt_body(plaintext, dek)

        # Tamper with IV
        tampered_iv = bytearray(iv)
        tampered_iv[0] ^= 0xFF

        with pytest.raises((IntegrityError, DecryptionError)):
            decrypt_body(bytes(tampered_iv), ciphertext, tag, dek)

    def test_encrypt_body_empty_data(self):
        """Empty data should be handled correctly."""
        dek = generate_dek()
        plaintext = b""

        iv, ciphertext, tag = encrypt_body(plaintext, dek)
        decrypted = decrypt_body(iv, ciphertext, tag, dek)

        assert decrypted == plaintext

    def test_encrypt_body_large_data(self):
        """Large data should be encrypted correctly."""
        dek = generate_dek()
        plaintext = os.urandom(1024 * 1024)  # 1 MB

        iv, ciphertext, tag = encrypt_body(plaintext, dek)
        decrypted = decrypt_body(iv, ciphertext, tag, dek)

        assert decrypted == plaintext


class TestHybridEncryption:
    """Tests for the high-level hybrid encryption API."""

    def test_hybrid_encrypt_decrypt_string_roundtrip(self):
        """ISSUE-03 CRITERION: Normal encryption/decryption should pass."""
        keypair = generate_rsa_keypair()
        plaintext = "This is a secret evidence message"

        result = hybrid_encrypt(plaintext, keypair.public_key)
        decrypted = hybrid_decrypt(result, keypair.private_key)

        assert decrypted == plaintext.encode('utf-8')

    def test_hybrid_encrypt_decrypt_bytes_roundtrip(self):
        """Bytes input should work correctly."""
        keypair = generate_rsa_keypair()
        plaintext = b"\x00\x01\x02\x03\x04\x05"

        result = hybrid_encrypt(plaintext, keypair.public_key)
        decrypted = hybrid_decrypt(result, keypair.private_key)

        assert decrypted == plaintext

    def test_hybrid_encrypt_decrypt_dict_roundtrip(self):
        """Dict input should be JSON-serialized."""
        keypair = generate_rsa_keypair()
        plaintext = {"evidence": "data", "count": 42, "valid": True}

        result = hybrid_encrypt(plaintext, keypair.public_key)
        decrypted = hybrid_decrypt_to_json(result, keypair.private_key)

        assert decrypted == plaintext

    def test_hybrid_encrypt_with_key_id(self):
        """Key ID should be preserved in result."""
        keypair = generate_rsa_keypair(key_id="key-123")
        plaintext = "test"

        result = hybrid_encrypt(plaintext, keypair.public_key, key_id="key-123")

        assert result.key_id == "key-123"

    def test_hybrid_encrypt_result_is_base64(self):
        """All result fields should be valid base64."""
        keypair = generate_rsa_keypair()
        plaintext = "test"

        result = hybrid_encrypt(plaintext, keypair.public_key)

        # Should not raise
        base64.b64decode(result.encrypted_dek)
        base64.b64decode(result.iv)
        base64.b64decode(result.ciphertext)
        base64.b64decode(result.tag)

    def test_hybrid_decrypt_to_string(self):
        """hybrid_decrypt_to_string should return UTF-8 string."""
        keypair = generate_rsa_keypair()
        plaintext = "Hello, Unicode: 你好"

        result = hybrid_encrypt(plaintext, keypair.public_key)
        decrypted = hybrid_decrypt_to_string(result, keypair.private_key)

        assert decrypted == plaintext

    def test_hybrid_decrypt_from_dict(self):
        """hybrid_decrypt should accept dict input."""
        keypair = generate_rsa_keypair()
        plaintext = "test message"

        result = hybrid_encrypt(plaintext, keypair.public_key)
        result_dict = result.to_dict()

        decrypted = hybrid_decrypt(result_dict, keypair.private_key)
        assert decrypted == plaintext.encode('utf-8')

    def test_hybrid_encrypt_wrong_key_fails(self):
        """ISSUE-03 CRITERION: Decryption with wrong key should fail."""
        kp1 = generate_rsa_keypair()
        kp2 = generate_rsa_keypair()
        plaintext = "secret"

        result = hybrid_encrypt(plaintext, kp1.public_key)

        with pytest.raises(DecryptionError):
            hybrid_decrypt(result, kp2.private_key)

    def test_hybrid_decrypt_tampered_encrypted_dek_fails(self):
        """ISSUE-03 CRITERION: Tampered encrypted DEK should trigger failure."""
        keypair = generate_rsa_keypair()
        plaintext = "secret"

        result = hybrid_encrypt(plaintext, keypair.public_key)
        result_dict = result.to_dict()
        result_dict["encrypted_dek"] = base64.b64encode(
            b"tampered_dek_data"
        ).decode('utf-8')

        with pytest.raises(DecryptionError):
            hybrid_decrypt(result_dict, keypair.private_key)

    def test_hybrid_decrypt_tampered_ciphertext_fails(self):
        """ISSUE-03 CRITERION: Tampered ciphertext should trigger failure."""
        keypair = generate_rsa_keypair()
        plaintext = "secret"

        result = hybrid_encrypt(plaintext, keypair.public_key)
        result_dict = result.to_dict()

        # Tamper with ciphertext
        ct_bytes = bytearray(base64.b64decode(result_dict["ciphertext"]))
        ct_bytes[0] ^= 0xFF
        result_dict["ciphertext"] = base64.b64encode(bytes(ct_bytes)).decode('utf-8')

        with pytest.raises((IntegrityError, DecryptionError)):
            hybrid_decrypt(result_dict, keypair.private_key)

    def test_hybrid_decrypt_tampered_tag_fails(self):
        """ISSUE-03 CRITERION: Tampered tag should trigger failure."""
        keypair = generate_rsa_keypair()
        plaintext = "secret"

        result = hybrid_encrypt(plaintext, keypair.public_key)
        result_dict = result.to_dict()

        # Tamper with tag
        tag_bytes = bytearray(base64.b64decode(result_dict["tag"]))
        tag_bytes[0] ^= 0xFF
        result_dict["tag"] = base64.b64encode(bytes(tag_bytes)).decode('utf-8')

        with pytest.raises((IntegrityError, DecryptionError)):
            hybrid_decrypt(result_dict, keypair.private_key)


class TestEncryptionResultDataClass:
    """Tests for EncryptionResult data class."""

    def test_to_dict_and_from_dict(self):
        """Serialization roundtrip should preserve data."""
        original = EncryptionResult(
            encrypted_dek="abc123",
            iv="def456",
            ciphertext="ghi789",
            tag="jkl012",
            key_id="key-001",
        )

        dict_form = original.to_dict()
        restored = EncryptionResult.from_dict(dict_form)

        assert restored.encrypted_dek == original.encrypted_dek
        assert restored.iv == original.iv
        assert restored.ciphertext == original.ciphertext
        assert restored.tag == original.tag
        assert restored.key_id == original.key_id

    def test_to_dict_includes_all_fields(self):
        """to_dict should include all fields."""
        result = EncryptionResult(
            encrypted_dek="abc",
            iv="def",
            ciphertext="ghi",
            tag="jkl",
            key_id="key-001",
        )

        d = result.to_dict()

        assert "encrypted_dek" in d
        assert "iv" in d
        assert "ciphertext" in d
        assert "tag" in d
        assert "key_id" in d


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_invalid_dek_size_for_encryption(self):
        """Wrong DEK size should raise EncryptionError."""
        keypair = generate_rsa_keypair()
        wrong_dek = b"too_short"

        with pytest.raises(EncryptionError):
            encrypt_body(b"test", wrong_dek)

    def test_invalid_iv_size_for_decryption(self):
        """Wrong IV size should raise DecryptionError."""
        dek = generate_dek()
        iv, ciphertext, tag = encrypt_body(b"test", dek)

        with pytest.raises(DecryptionError):
            decrypt_body(b"short_iv", ciphertext, tag, dek)

    def test_invalid_tag_size_for_decryption(self):
        """Wrong tag size should raise DecryptionError."""
        dek = generate_dek()
        iv, ciphertext, tag = encrypt_body(b"test", dek)

        with pytest.raises(DecryptionError):
            decrypt_body(iv, ciphertext, b"short_tag", dek)

    def test_decrypt_invalid_json_fails(self):
        """Invalid JSON should raise DecryptionError."""
        keypair = generate_rsa_keypair()
        plaintext = "not json"

        result = hybrid_encrypt(plaintext, keypair.public_key)

        with pytest.raises(DecryptionError):
            hybrid_decrypt_to_json(result, keypair.private_key)

    def test_decrypt_non_utf8_fails(self):
        """Non-UTF8 data should raise DecryptionError when decoded as string."""
        keypair = generate_rsa_keypair()
        plaintext = b"\xff\xfe invalid utf8"

        result = hybrid_encrypt(plaintext, keypair.public_key)

        with pytest.raises(DecryptionError):
            hybrid_decrypt_to_string(result, keypair.private_key)


class TestIntegrationWithEnvelope:
    """Integration tests with EvidenceEnvelope (T03)."""

    def test_hybrid_encrypt_produces_envelope_compatible_result(self):
        """EncryptionResult should be compatible with EvidenceEnvelopeBuilder."""
        from skillforge.src.utils.evidence_envelope import (
            EvidenceEnvelopeBuilder,
            validate_envelope_schema,
        )
        from skillforge.src.utils.ed25519_signature import generate_keypair

        # Generate keys
        rsa_keypair = generate_rsa_keypair(key_id="rsa-001")
        ed_keypair = generate_keypair()

        # Encrypt body
        body = {"evidence": "test data", "timestamp": "2026-02-26"}
        enc_result = hybrid_encrypt(body, rsa_keypair.public_key, key_id="rsa-001")

        # Create envelope
        envelope = (
            EvidenceEnvelopeBuilder()
            .with_node_id("node-001")
            .with_encryption(
                encrypted_dek=enc_result.encrypted_dek,
                key_id=enc_result.key_id,
                ciphertext_data=enc_result.ciphertext,
                ciphertext_iv=enc_result.iv,
                ciphertext_tag=enc_result.tag,
            )
            .with_public_key(ed_keypair.public_key_hex)
            .with_signature("placeholder_signature")
            .build()
        )

        # Validate schema
        errors = validate_envelope_schema(envelope.to_dict())
        # Should have no errors about missing encryption fields
        encryption_errors = [e for e in errors if "keywrap" in e or "ciphertext" in e]
        assert len(encryption_errors) == 0


class TestCryptographyNotAvailable:
    """Tests for behavior when cryptography library is not available."""

    @patch("skillforge.src.utils.hybrid_crypto.CRYPTOGRAPHY_AVAILABLE", False)
    def test_functions_raise_when_not_available(self):
        """All crypto functions should raise when library is not available."""
        from skillforge.src.utils.hybrid_crypto import _check_cryptography

        with pytest.raises(CryptographyNotAvailableError):
            _check_cryptography()


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
