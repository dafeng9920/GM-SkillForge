"""
Nonce Challenge Module for SkillForge Evidence Envelope.

This module provides nonce challenge generation, validation, and replay attack prevention
for evidence envelopes, ensuring each submission is unique and time-bound.

ISSUE-05: Nonce Challenge 防重放
Task: T06
Executor: Kior-A

Key Features:
- One-time challenge generation with configurable TTL
- Challenge-response validation with signature verification
- Replay attack detection and rejection
- Thread-safe challenge store with automatic cleanup

Integration:
- T03: Envelope structure (header.nonce field)
- T05: Ed25519 signature verification for challenge-response

Error Codes:
- REPLAY_DETECTED: Nonce has been used before
- CHALLENGE_EXPIRED: Challenge TTL has elapsed
- CHALLENGE_INVALID: Challenge format or signature is invalid
"""

from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, Set


# Default configuration
DEFAULT_CHALLENGE_LENGTH = 32  # bytes
DEFAULT_TTL_SECONDS = 300  # 5 minutes
MAX_STORED_CHALLENGES = 10000  # Prevent memory exhaustion


class ChallengeError(Exception):
    """Base exception for challenge operations."""
    pass


class ReplayDetectedError(ChallengeError):
    """Raised when a replay attack is detected."""
    error_code = "REPLAY_DETECTED"


class ChallengeExpiredError(ChallengeError):
    """Raised when a challenge has expired."""
    error_code = "CHALLENGE_EXPIRED"


class ChallengeInvalidError(ChallengeError):
    """Raised when a challenge is invalid."""
    error_code = "CHALLENGE_INVALID"


class ChallengeStatus(Enum):
    """Status of a challenge."""
    PENDING = "pending"
    USED = "used"
    EXPIRED = "expired"


@dataclass
class Challenge:
    """
    Represents a nonce challenge.

    Attributes:
        nonce: Unique challenge string (hex-encoded)
        created_at: Unix timestamp when challenge was created
        expires_at: Unix timestamp when challenge expires
        node_id: Optional node ID this challenge is bound to
        context: Optional additional context data
        status: Current status of the challenge
    """
    nonce: str
    created_at: float
    expires_at: float
    node_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    status: ChallengeStatus = ChallengeStatus.PENDING

    def is_expired(self) -> bool:
        """Check if the challenge has expired."""
        return time.time() > self.expires_at

    def is_valid(self) -> bool:
        """Check if the challenge is still valid for use."""
        return self.status == ChallengeStatus.PENDING and not self.is_expired()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize challenge to dictionary."""
        return {
            "nonce": self.nonce,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "node_id": self.node_id,
            "context": self.context,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Challenge":
        """Deserialize challenge from dictionary."""
        return cls(
            nonce=data["nonce"],
            created_at=data["created_at"],
            expires_at=data["expires_at"],
            node_id=data.get("node_id"),
            context=data.get("context"),
            status=ChallengeStatus(data.get("status", "pending")),
        )


@dataclass
class ChallengeResponse:
    """
    Represents a response to a challenge.

    Attributes:
        nonce: The original challenge nonce
        node_id: The node responding to the challenge
        timestamp: Unix timestamp of the response
        signature: Ed25519 signature of nonce + timestamp
    """
    nonce: str
    node_id: str
    timestamp: float
    signature: str  # Hex-encoded signature

    def to_dict(self) -> Dict[str, Any]:
        """Serialize response to dictionary."""
        return {
            "nonce": self.nonce,
            "node_id": self.node_id,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChallengeResponse":
        """Deserialize response from dictionary."""
        return cls(
            nonce=data["nonce"],
            node_id=data["node_id"],
            timestamp=data["timestamp"],
            signature=data["signature"],
        )


@dataclass
class ValidationResult:
    """
    Result of challenge validation.

    Attributes:
        valid: Whether the validation passed
        error_code: Error code if validation failed
        error_message: Human-readable error message
        node_id: The validated node ID (if successful)
        nonce: The validated nonce (if successful)
    """
    valid: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    node_id: Optional[str] = None
    nonce: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary."""
        result: Dict[str, Any] = {"valid": self.valid}
        if self.error_code:
            result["error_code"] = self.error_code
        if self.error_message:
            result["error_message"] = self.error_message
        if self.node_id:
            result["node_id"] = self.node_id
        if self.nonce:
            result["nonce"] = self.nonce
        return result


class ChallengeStore:
    """
    Thread-safe store for nonce challenges.

    This class manages the lifecycle of challenges including:
    - Storage with automatic expiration
    - Lookup and validation
    - Cleanup of expired challenges
    """

    def __init__(
        self,
        max_size: int = MAX_STORED_CHALLENGES,
        cleanup_interval: int = 60
    ):
        """
        Initialize the challenge store.

        Args:
            max_size: Maximum number of challenges to store
            cleanup_interval: Seconds between automatic cleanup runs
        """
        self._challenges: Dict[str, Challenge] = {}
        self._used_nonces: Set[str] = set()
        self._lock = threading.RLock()
        self._max_size = max_size
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()

    def store(self, challenge: Challenge) -> None:
        """
        Store a challenge.

        Args:
            challenge: The challenge to store

        Raises:
            ChallengeError: If store is at capacity
        """
        with self._lock:
            self._maybe_cleanup()

            if len(self._challenges) >= self._max_size:
                # Force cleanup before rejecting
                self._cleanup_expired()

                if len(self._challenges) >= self._max_size:
                    raise ChallengeError("Challenge store at capacity")

            self._challenges[challenge.nonce] = challenge

    def get(self, nonce: str) -> Optional[Challenge]:
        """
        Get a challenge by nonce.

        Args:
            nonce: The nonce to look up

        Returns:
            The challenge if found, None otherwise
        """
        with self._lock:
            return self._challenges.get(nonce)

    def mark_used(self, nonce: str) -> bool:
        """
        Mark a challenge as used (consumed).

        Args:
            nonce: The nonce to mark as used

        Returns:
            True if the challenge was marked, False if not found
        """
        with self._lock:
            challenge = self._challenges.get(nonce)
            if challenge:
                challenge.status = ChallengeStatus.USED
                self._used_nonces.add(nonce)
                # Remove from active challenges but keep in used set
                del self._challenges[nonce]
                return True
            return False

    def is_used(self, nonce: str) -> bool:
        """
        Check if a nonce has been used.

        Args:
            nonce: The nonce to check

        Returns:
            True if the nonce has been used
        """
        with self._lock:
            return nonce in self._used_nonces

    def exists(self, nonce: str) -> bool:
        """
        Check if a challenge exists (active or expired).

        Args:
            nonce: The nonce to check

        Returns:
            True if the challenge exists
        """
        with self._lock:
            return nonce in self._challenges or nonce in self._used_nonces

    def _maybe_cleanup(self) -> None:
        """Run cleanup if interval has elapsed."""
        now = time.time()
        if now - self._last_cleanup > self._cleanup_interval:
            self._cleanup_expired()
            self._last_cleanup = now

    def _cleanup_expired(self) -> int:
        """
        Remove expired challenges from the store.

        Returns:
            Number of challenges removed
        """
        with self._lock:
            now = time.time()
            expired = [
                nonce for nonce, challenge in self._challenges.items()
                if challenge.expires_at < now
            ]

            for nonce in expired:
                challenge = self._challenges[nonce]
                challenge.status = ChallengeStatus.EXPIRED
                del self._challenges[nonce]

            return len(expired)

    def clear(self) -> None:
        """Clear all challenges from the store."""
        with self._lock:
            self._challenges.clear()
            self._used_nonces.clear()

    def size(self) -> int:
        """Get the number of active challenges."""
        with self._lock:
            return len(self._challenges)

    def used_count(self) -> int:
        """Get the number of used nonces."""
        with self._lock:
            return len(self._used_nonces)


class NonceChallengeManager:
    """
    Manager for nonce challenge lifecycle.

    This class provides the main API for:
    - Generating new challenges
    - Validating challenge responses
    - Detecting replay attacks

    Example:
        >>> manager = NonceChallengeManager()
        >>> challenge = manager.generate_challenge(node_id="node-001")
        >>> # Client signs and returns challenge
        >>> response = ChallengeResponse(
        ...     nonce=challenge.nonce,
        ...     node_id="node-001",
        ...     timestamp=time.time(),
        ...     signature="abc123..."
        ... )
        >>> result = manager.validate_response(response, verify_signature_func)
        >>> if result.valid:
        ...     print("Challenge validated!")
    """

    def __init__(
        self,
        store: Optional[ChallengeStore] = None,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        challenge_length: int = DEFAULT_CHALLENGE_LENGTH
    ):
        """
        Initialize the challenge manager.

        Args:
            store: Optional custom challenge store
            ttl_seconds: Time-to-live for challenges in seconds
            challenge_length: Length of generated nonces in bytes
        """
        self._store = store or ChallengeStore()
        self._ttl_seconds = ttl_seconds
        self._challenge_length = challenge_length

    def generate_challenge(
        self,
        node_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None
    ) -> Challenge:
        """
        Generate a new nonce challenge.

        Args:
            node_id: Optional node ID to bind the challenge to
            context: Optional additional context data
            ttl_seconds: Optional custom TTL (overrides default)

        Returns:
            A new Challenge object
        """
        # Generate cryptographically secure random nonce
        nonce_bytes = secrets.token_bytes(self._challenge_length)
        nonce = nonce_bytes.hex()

        now = time.time()
        ttl = ttl_seconds if ttl_seconds is not None else self._ttl_seconds

        challenge = Challenge(
            nonce=nonce,
            created_at=now,
            expires_at=now + ttl,
            node_id=node_id,
            context=context,
            status=ChallengeStatus.PENDING,
        )

        self._store.store(challenge)
        return challenge

    def validate_challenge(self, nonce: str) -> ValidationResult:
        """
        Validate a challenge nonce.

        This checks:
        1. Challenge exists
        2. Challenge has not expired
        3. Challenge has not been used (replay detection)

        Args:
            nonce: The nonce to validate

        Returns:
            ValidationResult with validation outcome
        """
        # Check for replay (used nonce)
        if self._store.is_used(nonce):
            return ValidationResult(
                valid=False,
                error_code=ReplayDetectedError.error_code,
                error_message="Replay detected: nonce has already been used",
            )

        # Get the challenge
        challenge = self._store.get(nonce)

        if challenge is None:
            # Not in active store and not in used set = unknown
            return ValidationResult(
                valid=False,
                error_code=ChallengeInvalidError.error_code,
                error_message="Challenge not found",
            )

        # Check expiration
        if challenge.is_expired():
            return ValidationResult(
                valid=False,
                error_code=ChallengeExpiredError.error_code,
                error_message=f"Challenge expired at {challenge.expires_at}",
            )

        # Challenge is valid
        return ValidationResult(
            valid=True,
            node_id=challenge.node_id,
            nonce=nonce,
        )

    def validate_response(
        self,
        response: ChallengeResponse,
        signature_verifier: Optional[Callable[[str, str, str, str], bool]] = None
    ) -> ValidationResult:
        """
        Validate a challenge response.

        This performs full validation including:
        1. Challenge validation (existence, expiration, replay)
        2. Optional signature verification
        3. Node ID binding check

        Args:
            response: The challenge response to validate
            signature_verifier: Optional function to verify signature.
                Signature: (nonce, node_id, timestamp, signature) -> bool

        Returns:
            ValidationResult with validation outcome
        """
        # First validate the challenge itself
        challenge_result = self.validate_challenge(response.nonce)
        if not challenge_result.valid:
            return challenge_result

        # Get the challenge for node binding check
        challenge = self._store.get(response.nonce)
        if challenge is None:
            # Should not happen after validate_challenge passed, but safety check
            return ValidationResult(
                valid=False,
                error_code=ChallengeInvalidError.error_code,
                error_message="Challenge disappeared during validation",
            )

        # Check node ID binding if challenge was bound to a specific node
        if challenge.node_id is not None and challenge.node_id != response.node_id:
            return ValidationResult(
                valid=False,
                error_code=ChallengeInvalidError.error_code,
                error_message=f"Node ID mismatch: expected {challenge.node_id}, got {response.node_id}",
            )

        # Verify signature if verifier provided
        if signature_verifier is not None:
            try:
                sig_valid = signature_verifier(
                    response.nonce,
                    response.node_id,
                    str(response.timestamp),
                    response.signature
                )
                if not sig_valid:
                    return ValidationResult(
                        valid=False,
                        error_code=ChallengeInvalidError.error_code,
                        error_message="Signature verification failed",
                    )
            except Exception as e:
                return ValidationResult(
                    valid=False,
                    error_code=ChallengeInvalidError.error_code,
                    error_message=f"Signature verification error: {str(e)}",
                )

        # Mark the challenge as used (consume it)
        self._store.mark_used(response.nonce)

        return ValidationResult(
            valid=True,
            node_id=response.node_id,
            nonce=response.nonce,
        )

    def consume_nonce(self, nonce: str) -> ValidationResult:
        """
        Validate and consume a nonce in a single operation.

        This is a convenience method for simple nonce validation
        without signature verification.

        Args:
            nonce: The nonce to validate and consume

        Returns:
            ValidationResult with validation outcome
        """
        result = self.validate_challenge(nonce)
        if result.valid:
            self._store.mark_used(nonce)
        return result

    def is_nonce_used(self, nonce: str) -> bool:
        """
        Check if a nonce has been used (for replay detection).

        Args:
            nonce: The nonce to check

        Returns:
            True if the nonce has been used
        """
        return self._store.is_used(nonce)

    def get_challenge(self, nonce: str) -> Optional[Challenge]:
        """
        Get a challenge by nonce.

        Args:
            nonce: The nonce to look up

        Returns:
            The challenge if found and active, None otherwise
        """
        return self._store.get(nonce)


def build_challenge_response_payload(
    nonce: str,
    node_id: str,
    timestamp: float
) -> bytes:
    """
    Build the canonical payload for signing a challenge response.

    This creates a deterministic byte sequence that should be signed
    by the node's Ed25519 private key.

    Args:
        nonce: The challenge nonce
        node_id: The node's identifier
        timestamp: Response timestamp

    Returns:
        Canonical bytes ready for signing
    """
    # Use canonical format for consistent signing
    payload = f"{nonce}:{node_id}:{timestamp:.6f}"
    return payload.encode('utf-8')


def create_challenge_response(
    nonce: str,
    node_id: str,
    private_key_hex: str
) -> ChallengeResponse:
    """
    Create a signed challenge response.

    This is a convenience function that creates a response with
    an Ed25519 signature.

    Args:
        nonce: The challenge nonce
        node_id: The node's identifier
        private_key_hex: Hex-encoded Ed25519 private key

    Returns:
        ChallengeResponse with signature

    Raises:
        ChallengeError: If signing fails
    """
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
    except ImportError:
        raise ChallengeError("cryptography library required for signing")

    timestamp = time.time()
    payload = build_challenge_response_payload(nonce, node_id, timestamp)

    # Load private key
    private_key_bytes = bytes.fromhex(private_key_hex)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)

    # Sign
    signature = private_key.sign(payload)

    return ChallengeResponse(
        nonce=nonce,
        node_id=node_id,
        timestamp=timestamp,
        signature=signature.hex(),
    )


def verify_challenge_response_signature(
    nonce: str,
    node_id: str,
    timestamp: str,
    signature: str,
    public_key_hex: str
) -> bool:
    """
    Verify a challenge response signature.

    Args:
        nonce: The challenge nonce
        node_id: The node's identifier
        timestamp: Response timestamp (as string)
        signature: Hex-encoded signature
        public_key_hex: Hex-encoded Ed25519 public key

    Returns:
        True if signature is valid
    """
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
    except ImportError:
        raise ChallengeError("cryptography library required for verification")

    try:
        # Rebuild payload
        payload = build_challenge_response_payload(
            nonce, node_id, float(timestamp)
        )

        # Load public key
        public_key_bytes = bytes.fromhex(public_key_hex)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)

        # Verify
        public_key.verify(bytes.fromhex(signature), payload)
        return True

    except Exception:
        return False


# Convenience exports
__all__ = [
    # Exceptions
    "ChallengeError",
    "ReplayDetectedError",
    "ChallengeExpiredError",
    "ChallengeInvalidError",
    # Enums
    "ChallengeStatus",
    # Data classes
    "Challenge",
    "ChallengeResponse",
    "ValidationResult",
    # Core classes
    "ChallengeStore",
    "NonceChallengeManager",
    # Utility functions
    "build_challenge_response_payload",
    "create_challenge_response",
    "verify_challenge_response_signature",
    # Constants
    "DEFAULT_CHALLENGE_LENGTH",
    "DEFAULT_TTL_SECONDS",
    "MAX_STORED_CHALLENGES",
]
