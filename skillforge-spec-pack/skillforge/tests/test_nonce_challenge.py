"""
Test Suite for Nonce Challenge Module.

This test suite validates the nonce challenge system for replay attack prevention.

Task: T06 - ISSUE-05: Nonce Challenge 防重放
Executor: Kior-A

Acceptance Criteria (from ISSUE-05):
- 重放旧包返回 `REPLAY_DETECTED`
- 过期返回 `CHALLENGE_EXPIRED`
"""

import time
import threading
import pytest

from skillforge.src.utils.nonce_challenge import (
    # Exceptions
    ChallengeError,
    ReplayDetectedError,
    ChallengeExpiredError,
    ChallengeInvalidError,
    # Enums
    ChallengeStatus,
    # Data classes
    Challenge,
    ChallengeResponse,
    ValidationResult,
    # Core classes
    ChallengeStore,
    NonceChallengeManager,
    # Utility functions
    build_challenge_response_payload,
    create_challenge_response,
    verify_challenge_response_signature,
    # Constants
    DEFAULT_CHALLENGE_LENGTH,
    DEFAULT_TTL_SECONDS,
    MAX_STORED_CHALLENGES,
)


class TestChallenge:
    """Test Challenge data class."""

    def test_challenge_creation(self):
        """Test basic challenge creation."""
        now = time.time()
        challenge = Challenge(
            nonce="abc123",
            created_at=now,
            expires_at=now + 300,
        )

        assert challenge.nonce == "abc123"
        assert challenge.status == ChallengeStatus.PENDING
        assert challenge.node_id is None
        assert challenge.context is None

    def test_challenge_is_expired(self):
        """Test expiration check."""
        now = time.time()

        # Not expired
        challenge = Challenge(
            nonce="abc123",
            created_at=now,
            expires_at=now + 300,
        )
        assert not challenge.is_expired()

        # Expired
        expired_challenge = Challenge(
            nonce="abc123",
            created_at=now - 400,
            expires_at=now - 100,
        )
        assert expired_challenge.is_expired()

    def test_challenge_is_valid(self):
        """Test validity check."""
        now = time.time()

        # Valid challenge
        challenge = Challenge(
            nonce="abc123",
            created_at=now,
            expires_at=now + 300,
        )
        assert challenge.is_valid()

        # Expired challenge
        expired_challenge = Challenge(
            nonce="abc123",
            created_at=now - 400,
            expires_at=now - 100,
        )
        assert not expired_challenge.is_valid()

        # Used challenge
        used_challenge = Challenge(
            nonce="abc123",
            created_at=now,
            expires_at=now + 300,
            status=ChallengeStatus.USED,
        )
        assert not used_challenge.is_valid()

    def test_challenge_serialization(self):
        """Test to_dict and from_dict."""
        now = time.time()
        original = Challenge(
            nonce="abc123",
            created_at=now,
            expires_at=now + 300,
            node_id="node-001",
            context={"key": "value"},
        )

        data = original.to_dict()
        restored = Challenge.from_dict(data)

        assert restored.nonce == original.nonce
        assert restored.created_at == original.created_at
        assert restored.expires_at == original.expires_at
        assert restored.node_id == original.node_id
        assert restored.context == original.context


class TestChallengeResponse:
    """Test ChallengeResponse data class."""

    def test_response_creation(self):
        """Test basic response creation."""
        response = ChallengeResponse(
            nonce="abc123",
            node_id="node-001",
            timestamp=time.time(),
            signature="def456",
        )

        assert response.nonce == "abc123"
        assert response.node_id == "node-001"
        assert response.signature == "def456"

    def test_response_serialization(self):
        """Test to_dict and from_dict."""
        original = ChallengeResponse(
            nonce="abc123",
            node_id="node-001",
            timestamp=12345.6789,
            signature="def456",
        )

        data = original.to_dict()
        restored = ChallengeResponse.from_dict(data)

        assert restored.nonce == original.nonce
        assert restored.node_id == original.node_id
        assert restored.timestamp == original.timestamp
        assert restored.signature == original.signature


class TestValidationResult:
    """Test ValidationResult data class."""

    def test_success_result(self):
        """Test successful validation result."""
        result = ValidationResult(
            valid=True,
            node_id="node-001",
            nonce="abc123",
        )

        assert result.valid
        assert result.error_code is None
        assert result.error_message is None

    def test_failure_result(self):
        """Test failed validation result."""
        result = ValidationResult(
            valid=False,
            error_code="REPLAY_DETECTED",
            error_message="Nonce has been used",
        )

        assert not result.valid
        assert result.error_code == "REPLAY_DETECTED"
        assert result.error_message == "Nonce has been used"

    def test_result_serialization(self):
        """Test to_dict."""
        result = ValidationResult(
            valid=True,
            node_id="node-001",
            nonce="abc123",
        )

        data = result.to_dict()
        assert data["valid"] is True
        assert data["node_id"] == "node-001"
        assert data["nonce"] == "abc123"


class TestChallengeStore:
    """Test ChallengeStore class."""

    def test_store_and_get(self):
        """Test storing and retrieving challenges."""
        store = ChallengeStore()
        now = time.time()

        challenge = Challenge(
            nonce="abc123",
            created_at=now,
            expires_at=now + 300,
        )

        store.store(challenge)
        retrieved = store.get("abc123")

        assert retrieved is not None
        assert retrieved.nonce == "abc123"

    def test_mark_used(self):
        """Test marking challenge as used."""
        store = ChallengeStore()
        now = time.time()

        challenge = Challenge(
            nonce="abc123",
            created_at=now,
            expires_at=now + 300,
        )

        store.store(challenge)
        assert store.mark_used("abc123")
        assert store.is_used("abc123")
        assert store.get("abc123") is None  # Removed from active store

    def test_nonexistent_challenge(self):
        """Test operations on nonexistent challenges."""
        store = ChallengeStore()

        assert store.get("nonexistent") is None
        assert not store.is_used("nonexistent")
        assert not store.mark_used("nonexistent")

    def test_cleanup_expired(self):
        """Test automatic cleanup of expired challenges."""
        store = ChallengeStore()
        now = time.time()

        # Store an expired challenge
        expired = Challenge(
            nonce="expired",
            created_at=now - 400,
            expires_at=now - 100,
        )
        store.store(expired)

        # Store a valid challenge
        valid = Challenge(
            nonce="valid",
            created_at=now,
            expires_at=now + 300,
        )
        store.store(valid)

        # Run cleanup
        store._cleanup_expired()

        assert store.get("expired") is None
        assert store.get("valid") is not None

    def test_thread_safety(self):
        """Test thread-safe operations."""
        store = ChallengeStore()
        errors = []

        def store_challenges(prefix, count):
            try:
                for i in range(count):
                    now = time.time()
                    challenge = Challenge(
                        nonce=f"{prefix}_{i}",
                        created_at=now,
                        expires_at=now + 300,
                    )
                    store.store(challenge)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = [
            threading.Thread(target=store_challenges, args=(f"thread_{t}", 10))
            for t in range(5)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have 50 challenges with no errors
        assert len(errors) == 0
        assert store.size() == 50


class TestNonceChallengeManager:
    """Test NonceChallengeManager class."""

    def test_generate_challenge(self):
        """Test challenge generation."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge()

        assert challenge.nonce is not None
        assert len(challenge.nonce) == DEFAULT_CHALLENGE_LENGTH * 2  # hex encoding
        assert challenge.status == ChallengeStatus.PENDING
        assert not challenge.is_expired()

    def test_generate_challenge_with_node_binding(self):
        """Test challenge generation with node binding."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge(node_id="node-001")

        assert challenge.node_id == "node-001"

    def test_generate_challenge_custom_ttl(self):
        """Test challenge generation with custom TTL."""
        manager = NonceChallengeManager()
        custom_ttl = 60
        challenge = manager.generate_challenge(ttl_seconds=custom_ttl)

        expected_expiry = challenge.created_at + custom_ttl
        assert abs(challenge.expires_at - expected_expiry) < 1

    def test_validate_challenge_success(self):
        """Test successful challenge validation."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge()

        result = manager.validate_challenge(challenge.nonce)

        assert result.valid
        assert result.nonce == challenge.nonce

    def test_validate_challenge_replay_detection(self):
        """Test REPLAY_DETECTED error when reusing nonce."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge()

        # First use - should succeed
        result1 = manager.consume_nonce(challenge.nonce)
        assert result1.valid

        # Replay attack - should return REPLAY_DETECTED
        result2 = manager.validate_challenge(challenge.nonce)
        assert not result2.valid
        assert result2.error_code == ReplayDetectedError.error_code
        assert "replay" in result2.error_message.lower()

    def test_validate_challenge_expired(self):
        """Test CHALLENGE_EXPIRED error for expired challenges."""
        store = ChallengeStore()
        manager = NonceChallengeManager(store=store, ttl_seconds=1)

        challenge = manager.generate_challenge()

        # Manually expire the challenge
        stored_challenge = store.get(challenge.nonce)
        stored_challenge.expires_at = time.time() - 1

        result = manager.validate_challenge(challenge.nonce)
        assert not result.valid
        assert result.error_code == ChallengeExpiredError.error_code
        assert "EXPIRED" in result.error_message.upper()

    def test_validate_challenge_not_found(self):
        """Test validation of unknown challenge."""
        manager = NonceChallengeManager()

        result = manager.validate_challenge("unknown_nonce")
        assert not result.valid
        assert result.error_code == ChallengeInvalidError.error_code

    def test_consume_nonce(self):
        """Test consume_nonce convenience method."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge()

        # First consumption
        result1 = manager.consume_nonce(challenge.nonce)
        assert result1.valid

        # Second consumption (replay)
        result2 = manager.consume_nonce(challenge.nonce)
        assert not result2.valid
        assert result2.error_code == ReplayDetectedError.error_code

    def test_validate_response_success(self):
        """Test successful response validation."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge(node_id="node-001")

        response = ChallengeResponse(
            nonce=challenge.nonce,
            node_id="node-001",
            timestamp=time.time(),
            signature="test_signature",
        )

        result = manager.validate_response(response)
        assert result.valid
        assert result.node_id == "node-001"

        # Challenge should be consumed
        assert manager.is_nonce_used(challenge.nonce)

    def test_validate_response_node_mismatch(self):
        """Test response validation with node ID mismatch."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge(node_id="node-001")

        response = ChallengeResponse(
            nonce=challenge.nonce,
            node_id="node-002",  # Different node
            timestamp=time.time(),
            signature="test_signature",
        )

        result = manager.validate_response(response)
        assert not result.valid
        assert result.error_code == ChallengeInvalidError.error_code
        assert "mismatch" in result.error_message.lower()

    def test_validate_response_with_signature_verifier(self):
        """Test response validation with signature verification."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge(node_id="node-001")

        # Mock signature verifier that always returns True
        def mock_verifier(nonce, node_id, timestamp, signature):
            return signature == "valid_signature"

        # Valid signature
        response1 = ChallengeResponse(
            nonce=challenge.nonce,
            node_id="node-001",
            timestamp=time.time(),
            signature="valid_signature",
        )
        result1 = manager.validate_response(response1, mock_verifier)
        assert result1.valid

        # Generate new challenge for invalid test
        challenge2 = manager.generate_challenge(node_id="node-001")
        response2 = ChallengeResponse(
            nonce=challenge2.nonce,
            node_id="node-001",
            timestamp=time.time(),
            signature="invalid_signature",
        )
        result2 = manager.validate_response(response2, mock_verifier)
        assert not result2.valid
        assert "signature" in result2.error_message.lower()

    def test_validate_response_replay_detection(self):
        """Test replay detection in response validation."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge()

        response = ChallengeResponse(
            nonce=challenge.nonce,
            node_id="node-001",
            timestamp=time.time(),
            signature="test_signature",
        )

        # First response - valid
        result1 = manager.validate_response(response)
        assert result1.valid

        # Second response with same nonce - replay detected
        result2 = manager.validate_response(response)
        assert not result2.valid
        assert result2.error_code == ReplayDetectedError.error_code


class TestSignatureFunctions:
    """Test Ed25519 signature functions for challenge responses."""

    @pytest.fixture
    def keypair(self):
        """Generate a test keypair."""
        try:
            from cryptography.hazmat.primitives.asymmetric import ed25519
            from cryptography.hazmat.primitives import serialization

            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()

            private_raw = private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )

            public_raw = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )

            return {
                "private_key_hex": private_raw.hex(),
                "public_key_hex": public_raw.hex(),
            }
        except ImportError:
            pytest.skip("cryptography library not available")

    def test_build_challenge_response_payload(self):
        """Test payload building for signing."""
        payload = build_challenge_response_payload(
            nonce="abc123",
            node_id="node-001",
            timestamp=12345.6789,
        )

        assert isinstance(payload, bytes)
        assert b"abc123" in payload
        assert b"node-001" in payload

    def test_create_and_verify_challenge_response(self, keypair):
        """Test full challenge response creation and verification."""
        nonce = "test_nonce_123"
        node_id = "node-001"

        # Create signed response
        response = create_challenge_response(
            nonce=nonce,
            node_id=node_id,
            private_key_hex=keypair["private_key_hex"],
        )

        assert response.nonce == nonce
        assert response.node_id == node_id
        assert response.signature is not None

        # Verify signature
        is_valid = verify_challenge_response_signature(
            nonce=response.nonce,
            node_id=response.node_id,
            timestamp=str(response.timestamp),
            signature=response.signature,
            public_key_hex=keypair["public_key_hex"],
        )

        assert is_valid

    def test_verify_challenge_response_tampered_nonce(self, keypair):
        """Test signature verification fails with tampered nonce."""
        nonce = "original_nonce"
        node_id = "node-001"

        response = create_challenge_response(
            nonce=nonce,
            node_id=node_id,
            private_key_hex=keypair["private_key_hex"],
        )

        # Verify with tampered nonce
        is_valid = verify_challenge_response_signature(
            nonce="tampered_nonce",  # Different nonce
            node_id=response.node_id,
            timestamp=str(response.timestamp),
            signature=response.signature,
            public_key_hex=keypair["public_key_hex"],
        )

        assert not is_valid

    def test_verify_challenge_response_wrong_key(self, keypair):
        """Test signature verification fails with wrong public key."""
        # Generate a different keypair
        try:
            from cryptography.hazmat.primitives.asymmetric import ed25519
            from cryptography.hazmat.primitives import serialization

            other_private = ed25519.Ed25519PrivateKey.generate()
            other_public = other_private.public_key()
            other_public_raw = other_public.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            wrong_public_key_hex = other_public_raw.hex()
        except ImportError:
            pytest.skip("cryptography library not available")

        nonce = "test_nonce"
        node_id = "node-001"

        response = create_challenge_response(
            nonce=nonce,
            node_id=node_id,
            private_key_hex=keypair["private_key_hex"],
        )

        # Verify with wrong public key
        is_valid = verify_challenge_response_signature(
            nonce=response.nonce,
            node_id=response.node_id,
            timestamp=str(response.timestamp),
            signature=response.signature,
            public_key_hex=wrong_public_key_hex,
        )

        assert not is_valid


class TestAcceptanceCriteria:
    """
    Acceptance criteria tests from ISSUE-05.

    - 重放旧包返回 `REPLAY_DETECTED`
    - 过期返回 `CHALLENGE_EXPIRED`
    """

    def test_replay_detected_error_code(self):
        """Test that replay returns REPLAY_DETECTED error code."""
        manager = NonceChallengeManager()

        # Generate and consume a challenge
        challenge = manager.generate_challenge()
        result1 = manager.consume_nonce(challenge.nonce)
        assert result1.valid

        # Attempt replay
        result2 = manager.consume_nonce(challenge.nonce)

        # Verify REPLAY_DETECTED error code
        assert not result2.valid
        assert result2.error_code == "REPLAY_DETECTED"

    def test_challenge_expired_error_code(self):
        """Test that expired challenge returns CHALLENGE_EXPIRED error code."""
        store = ChallengeStore()
        manager = NonceChallengeManager(store=store, ttl_seconds=1)

        # Generate challenge
        challenge = manager.generate_challenge()

        # Manually expire
        stored = store.get(challenge.nonce)
        stored.expires_at = time.time() - 1

        # Validate expired challenge
        result = manager.validate_challenge(challenge.nonce)

        # Verify CHALLENGE_EXPIRED error code
        assert not result.valid
        assert result.error_code == "CHALLENGE_EXPIRED"

    def test_full_challenge_response_flow(self):
        """Test complete challenge-response flow with replay prevention."""
        manager = NonceChallengeManager()

        # Step 1: Server generates challenge
        challenge = manager.generate_challenge(node_id="node-001")
        assert challenge.is_valid()

        # Step 2: Client creates signed response (simplified without crypto)
        response = ChallengeResponse(
            nonce=challenge.nonce,
            node_id="node-001",
            timestamp=time.time(),
            signature="mock_signature",
        )

        # Step 3: Server validates response
        result1 = manager.validate_response(response)
        assert result1.valid

        # Step 4: Attacker attempts replay
        result2 = manager.validate_response(response)
        assert not result2.valid
        assert result2.error_code == "REPLAY_DETECTED"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unique_nonce_generation(self):
        """Test that generated nonces are unique."""
        manager = NonceChallengeManager()
        nonces = set()

        for _ in range(1000):
            challenge = manager.generate_challenge()
            assert challenge.nonce not in nonces
            nonces.add(challenge.nonce)

    def test_challenge_store_capacity(self):
        """Test challenge store capacity limits."""
        store = ChallengeStore(max_size=10)

        # Fill the store
        for i in range(10):
            now = time.time()
            challenge = Challenge(
                nonce=f"nonce_{i}",
                created_at=now,
                expires_at=now + 300,
            )
            store.store(challenge)

        # Attempt to exceed capacity should raise
        with pytest.raises(ChallengeError):
            now = time.time()
            challenge = Challenge(
                nonce="nonce_overflow",
                created_at=now,
                expires_at=now + 300,
            )
            store.store(challenge)

    def test_concurrent_challenge_consumption(self):
        """Test that concurrent consumption of same nonce only succeeds once."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge()

        results = []

        def consume():
            result = manager.consume_nonce(challenge.nonce)
            results.append(result)

        threads = [threading.Thread(target=consume) for _ in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Only one should succeed
        valid_count = sum(1 for r in results if r.valid)
        assert valid_count == 1

        # Rest should be replay detected
        replay_count = sum(1 for r in results if r.error_code == "REPLAY_DETECTED")
        assert replay_count == 9


class TestIntegrationWithEd25519:
    """Test integration with Ed25519 signature module (T05)."""

    @pytest.fixture
    def ed25519_keypair(self):
        """Generate Ed25519 keypair using T05 module."""
        try:
            from skillforge.src.utils.ed25519_signature import generate_keypair

            return generate_keypair()
        except ImportError:
            pytest.skip("ed25519_signature module not available")

    def test_challenge_response_with_ed25519_signature(self, ed25519_keypair):
        """Test challenge response with real Ed25519 signature."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge(node_id="node-001")

        # Create signed response using T06 utility function
        response = create_challenge_response(
            nonce=challenge.nonce,
            node_id="node-001",
            private_key_hex=ed25519_keypair.private_key_hex,
        )

        # Create signature verifier using T06 function
        def signature_verifier(nonce, node_id, timestamp, signature):
            return verify_challenge_response_signature(
                nonce=nonce,
                node_id=node_id,
                timestamp=timestamp,
                signature=signature,
                public_key_hex=ed25519_keypair.public_key_hex,
            )

        # Validate with signature verification
        result = manager.validate_response(response, signature_verifier)

        assert result.valid
        assert result.node_id == "node-001"

    def test_tampered_signature_rejected(self, ed25519_keypair):
        """Test that tampered signatures are rejected."""
        manager = NonceChallengeManager()
        challenge = manager.generate_challenge(node_id="node-001")

        response = create_challenge_response(
            nonce=challenge.nonce,
            node_id="node-001",
            private_key_hex=ed25519_keypair.private_key_hex,
        )

        # Tamper with signature
        tampered_signature = response.signature[:-4] + "ffff"
        tampered_response = ChallengeResponse(
            nonce=response.nonce,
            node_id=response.node_id,
            timestamp=response.timestamp,
            signature=tampered_signature,
        )

        def signature_verifier(nonce, node_id, timestamp, signature):
            return verify_challenge_response_signature(
                nonce=nonce,
                node_id=node_id,
                timestamp=timestamp,
                signature=signature,
                public_key_hex=ed25519_keypair.public_key_hex,
            )

        result = manager.validate_response(tampered_response, signature_verifier)

        assert not result.valid
        assert "signature" in result.error_message.lower()


# Run tests with: pytest tests/test_nonce_challenge.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
