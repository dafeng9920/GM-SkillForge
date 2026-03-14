"""
Ed25519 Signature Module for SkillForge Evidence Envelope.

This module provides Ed25519 signing and verification functionality
for evidence envelopes, ensuring node authenticity and integrity.

Dependencies:
    - cryptography >= 41.0.0 (for Ed25519 operations)

Usage:
    >>> from skillforge.src.utils.ed25519_signature import (
    ...     generate_keypair,
    ...     sign_envelope,
    ...     verify_envelope_signature,
    ...     verify_signed_fields
    ... )
    >>> private_key, public_key = generate_keypair()
    >>> signature = sign_envelope(envelope_dict, private_key)
    >>> is_valid = verify_envelope_signature(envelope_dict, public_key, signature)
"""

import json
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    # Fallback types for when cryptography is not available
    ed25519 = None
    serialization = None
    default_backend = None


from .canonical_json import canonical_json, canonical_json_hash


# Default signed fields for envelope integrity
DEFAULT_SIGNED_FIELDS = [
    "header.envelope_id",
    "header.schema_version",
    "header.created_at",
    "header.node_id",
    "header.body_hash",
    "header.body_encoding",
    "header.nonce",
    "header.expires_at",
    "ciphertext.iv",
    "ciphertext.data",
    "ciphertext.tag",
]


@dataclass
class SignatureResult:
    """Result of a signing operation."""
    signature_value: bytes
    signed_fields: List[str]
    algorithm: str = "Ed25519"

    def to_dict(self) -> Dict:
        """Convert to dictionary format for envelope."""
        return {
            "algorithm": self.algorithm,
            "value": self.signature_value.hex(),
            "signed_fields": self.signed_fields,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SignatureResult":
        """Create from dictionary format."""
        return cls(
            signature_value=bytes.fromhex(data["value"]),
            signed_fields=data.get("signed_fields", []),
            algorithm=data.get("algorithm", "Ed25519"),
        )


@dataclass
class KeypairResult:
    """Result of keypair generation."""
    private_key_hex: str
    public_key_hex: str
    private_key_pem: str
    public_key_pem: str

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "private_key_hex": self.private_key_hex,
            "public_key_hex": self.public_key_hex,
            "private_key_pem": self.private_key_pem,
            "public_key_pem": self.public_key_pem,
        }


class Ed25519Error(Exception):
    """Base exception for Ed25519 operations."""
    pass


class CryptographyNotAvailableError(Ed25519Error):
    """Raised when cryptography library is not available."""
    pass


class InvalidSignatureError(Ed25519Error):
    """Raised when signature verification fails."""
    pass


class MissingFieldError(Ed25519Error):
    """Raised when a required field is missing from signed data."""
    pass


def _check_cryptography_available() -> None:
    """Check if cryptography library is available."""
    if not CRYPTOGRAPHY_AVAILABLE:
        raise CryptographyNotAvailableError(
            "cryptography library is required for Ed25519 operations. "
            "Install it with: pip install cryptography"
        )


def generate_keypair() -> KeypairResult:
    """
    Generate a new Ed25519 keypair.

    Returns:
        KeypairResult containing both PEM and hex formats of the keys.

    Raises:
        CryptographyNotAvailableError: If cryptography library is not available.
    """
    _check_cryptography_available()

    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Serialize to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Serialize to raw bytes (32 bytes for Ed25519)
    private_raw = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    return KeypairResult(
        private_key_hex=private_raw.hex(),
        public_key_hex=public_raw.hex(),
        private_key_pem=private_pem.decode('utf-8'),
        public_key_pem=public_pem.decode('utf-8'),
    )


def _get_nested_value(data: Dict, field_path: str) -> any:
    """
    Get a value from nested dictionary using dot notation.

    Args:
        data: The dictionary to search.
        field_path: Dot-separated path to the field (e.g., "header.envelope_id").

    Returns:
        The value at the specified path.

    Raises:
        MissingFieldError: If the field is not found.
    """
    keys = field_path.split('.')
    value = data

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            raise MissingFieldError(f"Required field '{field_path}' not found in envelope")

    return value


def _build_signed_payload(
    envelope: Dict,
    signed_fields: List[str]
) -> bytes:
    """
    Build the canonical payload for signing from specified fields.

    Args:
        envelope: The envelope dictionary.
        signed_fields: List of dot-separated field paths to include.

    Returns:
        Canonical JSON bytes ready for signing.

    Raises:
        MissingFieldError: If any required field is missing.
    """
    signed_data = {}

    for field_path in signed_fields:
        try:
            value = _get_nested_value(envelope, field_path)
            # Use the last component of the path as the key
            key = field_path.split('.')[-1]

            # Handle duplicate short keys by using full path as key
            if key in signed_data:
                key = field_path.replace('.', '_')

            signed_data[key] = value
        except MissingFieldError:
            raise MissingFieldError(f"Required field '{field_path}' not found in envelope")

    # Return canonical JSON bytes
    return canonical_json(signed_data).encode('utf-8')


def sign_envelope(
    envelope: Dict,
    private_key_hex: str,
    signed_fields: Optional[List[str]] = None
) -> SignatureResult:
    """
    Sign an evidence envelope using Ed25519.

    Args:
        envelope: The envelope dictionary to sign.
        private_key_hex: Hex-encoded private key (64 hex chars).
        signed_fields: List of field paths to sign. Defaults to DEFAULT_SIGNED_FIELDS.

    Returns:
        SignatureResult containing the signature and metadata.

    Raises:
        CryptographyNotAvailableError: If cryptography library is not available.
        MissingFieldError: If any required field is missing.
        Ed25519Error: If signing fails.
    """
    _check_cryptography_available()

    if signed_fields is None:
        signed_fields = DEFAULT_SIGNED_FIELDS

    try:
        # Load private key from hex
        private_key_bytes = bytes.fromhex(private_key_hex)
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)

        # Build payload to sign
        payload = _build_signed_payload(envelope, signed_fields)

        # Sign
        signature = private_key.sign(payload)

        return SignatureResult(
            signature_value=signature,
            signed_fields=signed_fields,
            algorithm="Ed25519",
        )

    except ValueError as e:
        raise Ed25519Error(f"Invalid private key format: {e}")
    except Exception as e:
        raise Ed25519Error(f"Signing failed: {e}")


def verify_envelope_signature(
    envelope: Dict,
    public_key_hex: str,
    signature_result: Union[SignatureResult, Dict]
) -> bool:
    """
    Verify an Ed25519 signature on an evidence envelope.

    Args:
        envelope: The envelope dictionary that was signed.
        public_key_hex: Hex-encoded public key (64 hex chars).
        signature_result: SignatureResult or dict containing signature data.

    Returns:
        True if signature is valid, False otherwise.

    Raises:
        CryptographyNotAvailableError: If cryptography library is not available.
        MissingFieldError: If signed fields are missing.
    """
    _check_cryptography_available()

    # Convert dict to SignatureResult if needed
    if isinstance(signature_result, dict):
        signature_result = SignatureResult.from_dict(signature_result)

    try:
        # Load public key from hex
        public_key_bytes = bytes.fromhex(public_key_hex)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)

        # Build payload (must use same fields as signing)
        payload = _build_signed_payload(envelope, signature_result.signed_fields)

        # Verify
        try:
            public_key.verify(signature_result.signature_value, payload)
            return True
        except Exception:
            return False

    except (ValueError, MissingFieldError):
        return False


def verify_signed_fields(
    signature_result: Union[SignatureResult, Dict],
    required_fields: Optional[List[str]] = None
) -> bool:
    """
    Verify that all required fields are included in signed_fields.

    Args:
        signature_result: SignatureResult or dict containing signed_fields.
        required_fields: List of field paths that must be signed.
                         If None, checks against DEFAULT_SIGNED_FIELDS.

    Returns:
        True if all required fields are present, False otherwise.
    """
    if isinstance(signature_result, dict):
        signature_result = SignatureResult.from_dict(signature_result)

    if required_fields is None:
        required_fields = DEFAULT_SIGNED_FIELDS

    signed_set = set(signature_result.signed_fields)
    required_set = set(required_fields)

    return required_set.issubset(signed_set)


def create_node_signature(
    node_id: str,
    envelope: Dict,
    private_key_hex: str
) -> Dict:
    """
    Create a complete node signature for an envelope.

    This is a convenience function that creates both the signature
    and the certificate for a node.

    Args:
        node_id: The node identifier.
        envelope: The envelope to sign.
        private_key_hex: Hex-encoded private key.

    Returns:
        Dictionary with 'signature' and 'cert' keys ready for envelope.
    """
    keypair = generate_keypair()

    # For this function, we use the provided key for signing
    # but we need the public key for the certificate
    # Extract public key from private key
    _check_cryptography_available()

    private_key_bytes = bytes.fromhex(private_key_hex)
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    public_key = private_key.public_key()

    public_key_raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    # Create signature
    sig_result = sign_envelope(envelope, private_key_hex)

    # Create certificate
    cert = {
        "node_id": node_id,
        "public_key": public_key_raw.hex(),
        "algorithm": "Ed25519",
    }

    return {
        "signature": sig_result.to_dict(),
        "cert": cert,
    }


def verify_node_signature(
    envelope: Dict,
    signature_data: Dict,
    cert_data: Dict
) -> Dict:
    """
    Verify a node signature on an envelope.

    Args:
        envelope: The envelope dictionary.
        signature_data: Signature dict from envelope.
        cert_data: Certificate dict from envelope.

    Returns:
        Dict with 'valid' key and optional 'reason' key.
    """
    try:
        # Extract public key from certificate
        public_key_hex = cert_data.get("public_key")
        node_id = cert_data.get("node_id")

        if not public_key_hex:
            return {"valid": False, "reason": "Certificate missing public_key"}

        if not node_id:
            return {"valid": False, "reason": "Certificate missing node_id"}

        # Verify signature
        is_valid = verify_envelope_signature(envelope, public_key_hex, signature_data)

        if not is_valid:
            return {"valid": False, "reason": "Signature verification failed"}

        # Verify node_id matches envelope header
        envelope_node_id = envelope.get("header", {}).get("node_id")
        if envelope_node_id != node_id:
            return {"valid": False, "reason": f"Node ID mismatch: cert={node_id}, envelope={envelope_node_id}"}

        return {"valid": True, "node_id": node_id}

    except Exception as e:
        return {"valid": False, "reason": f"Verification error: {str(e)}"}


# Exported functions
__all__ = [
    "generate_keypair",
    "sign_envelope",
    "verify_envelope_signature",
    "verify_signed_fields",
    "create_node_signature",
    "verify_node_signature",
    "SignatureResult",
    "KeypairResult",
    "Ed25519Error",
    "InvalidSignatureError",
    "MissingFieldError",
    "CryptographyNotAvailableError",
    "DEFAULT_SIGNED_FIELDS",
    "CRYPTOGRAPHY_AVAILABLE",
]
