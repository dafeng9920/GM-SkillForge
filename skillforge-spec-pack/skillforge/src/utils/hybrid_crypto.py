"""
Hybrid Encryption Module for GM-SkillForge

This module implements AES-256-GCM + RSA-OAEP-256 hybrid encryption
for evidence envelope protection.

Task: T04 - ISSUE-03: 混合加密替换整包 RSA
Executor: Kior-B

Hybrid Encryption Flow:
1. Generate random DEK (Data Encryption Key) - 256 bits for AES-256
2. Encrypt body with AES-256-GCM using DEK (produces ciphertext + IV + tag)
3. Encrypt DEK with RSA-OAEP-256 using recipient's public key
4. Package: encrypted_dek + iv + ciphertext + tag

Decryption Flow:
1. Decrypt DEK using RSA-OAEP-256 with recipient's private key
2. Decrypt ciphertext with AES-256-GCM using DEK
3. Verify authentication tag
"""

from __future__ import annotations

import base64
import os
import secrets
from dataclasses import dataclass
from typing import Optional, Union

# Try to import cryptography library
try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.asymmetric.rsa import (
        RSAPublicKey,
        RSAPrivateKey,
    )
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    RSAPublicKey = None  # type: ignore
    RSAPrivateKey = None  # type: ignore


# Constants
AES_KEY_SIZE = 32  # 256 bits for AES-256
GCM_IV_SIZE = 12    # 96 bits (recommended for GCM)
GCM_TAG_SIZE = 16   # 128 bits (default tag size for GCM)
RSA_KEY_SIZE = 2048  # RSA key size for OAEP


class HybridCryptoError(Exception):
    """Base exception for hybrid crypto errors."""
    pass


class EncryptionError(HybridCryptoError):
    """Raised when encryption fails."""
    pass


class DecryptionError(HybridCryptoError):
    """Raised when decryption fails."""
    pass


class KeyGenerationError(HybridCryptoError):
    """Raised when key generation fails."""
    pass


class IntegrityError(DecryptionError):
    """Raised when authentication tag verification fails (tampering detected)."""
    pass


class CryptographyNotAvailableError(HybridCryptoError):
    """Raised when cryptography library is not installed."""
    pass


@dataclass
class EncryptionResult:
    """
    Result of hybrid encryption operation.

    Attributes:
        encrypted_dek: Base64-encoded RSA-OAEP-256 encrypted DEK
        iv: Base64-encoded initialization vector (12 bytes)
        ciphertext: Base64-encoded AES-256-GCM ciphertext
        tag: Base64-encoded authentication tag (16 bytes)
        key_id: Identifier of the RSA key used for DEK wrapping
    """
    encrypted_dek: str
    iv: str
    ciphertext: str
    tag: str
    key_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "encrypted_dek": self.encrypted_dek,
            "iv": self.iv,
            "ciphertext": self.ciphertext,
            "tag": self.tag,
            "key_id": self.key_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EncryptionResult":
        """Create from dictionary."""
        return cls(
            encrypted_dek=data["encrypted_dek"],
            iv=data["iv"],
            ciphertext=data["ciphertext"],
            tag=data["tag"],
            key_id=data.get("key_id"),
        )


@dataclass
class RSAKeyPair:
    """
    RSA key pair for hybrid encryption.

    Attributes:
        private_key: RSA private key object
        public_key: RSA public key object
        key_id: Optional identifier for this key pair
    """
    private_key: "RSAPrivateKey"
    public_key: "RSAPublicKey"
    key_id: Optional[str] = None

    def get_public_key_pem(self) -> str:
        """Get public key in PEM format."""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem.decode('utf-8')

    def get_private_key_pem(self, password: Optional[bytes] = None) -> str:
        """Get private key in PEM format (optionally encrypted)."""
        if password:
            encryption = serialization.BestAvailableEncryption(password)
        else:
            encryption = serialization.NoEncryption()

        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption,
        )
        return pem.decode('utf-8')


def _check_cryptography():
    """Check if cryptography library is available."""
    if not CRYPTOGRAPHY_AVAILABLE:
        raise CryptographyNotAvailableError(
            "The 'cryptography' library is required for hybrid encryption. "
            "Install it with: pip install cryptography"
        )


def generate_dek() -> bytes:
    """
    Generate a random Data Encryption Key (DEK) for AES-256.

    Returns:
        32 bytes (256 bits) random key

    Raises:
        KeyGenerationError: If key generation fails
    """
    try:
        return secrets.token_bytes(AES_KEY_SIZE)
    except Exception as e:
        raise KeyGenerationError(f"Failed to generate DEK: {e}")


def generate_rsa_keypair(
    key_size: int = RSA_KEY_SIZE,
    key_id: Optional[str] = None,
) -> RSAKeyPair:
    """
    Generate a new RSA key pair for DEK wrapping.

    Args:
        key_size: RSA key size in bits (default: 2048)
        key_id: Optional identifier for the key pair

    Returns:
        RSAKeyPair with private and public keys

    Raises:
        KeyGenerationError: If key generation fails
        CryptographyNotAvailableError: If cryptography library is not installed
    """
    _check_cryptography()

    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend(),
        )
        public_key = private_key.public_key()
        return RSAKeyPair(
            private_key=private_key,
            public_key=public_key,
            key_id=key_id,
        )
    except Exception as e:
        raise KeyGenerationError(f"Failed to generate RSA key pair: {e}")


def encrypt_dek(
    dek: bytes,
    public_key: "RSAPublicKey",
) -> bytes:
    """
    Encrypt DEK using RSA-OAEP-256.

    Args:
        dek: Data Encryption Key (32 bytes for AES-256)
        public_key: RSA public key for encryption

    Returns:
        Encrypted DEK bytes

    Raises:
        EncryptionError: If encryption fails
        CryptographyNotAvailableError: If cryptography library is not installed
    """
    _check_cryptography()

    if len(dek) != AES_KEY_SIZE:
        raise EncryptionError(f"DEK must be {AES_KEY_SIZE} bytes, got {len(dek)}")

    try:
        encrypted_dek = public_key.encrypt(
            dek,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return encrypted_dek
    except Exception as e:
        raise EncryptionError(f"Failed to encrypt DEK: {e}")


def decrypt_dek(
    encrypted_dek: bytes,
    private_key: "RSAPrivateKey",
) -> bytes:
    """
    Decrypt DEK using RSA-OAEP-256.

    Args:
        encrypted_dek: RSA-encrypted DEK
        private_key: RSA private key for decryption

    Returns:
        Decrypted DEK bytes (32 bytes for AES-256)

    Raises:
        DecryptionError: If decryption fails
        CryptographyNotAvailableError: If cryptography library is not installed
    """
    _check_cryptography()

    try:
        dek = private_key.decrypt(
            encrypted_dek,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        if len(dek) != AES_KEY_SIZE:
            raise DecryptionError(f"Decrypted DEK has invalid size: {len(dek)}")
        return dek
    except DecryptionError:
        raise
    except Exception as e:
        raise DecryptionError(f"Failed to decrypt DEK: {e}")


def encrypt_body(
    plaintext: Union[str, bytes],
    dek: bytes,
) -> tuple[bytes, bytes, bytes]:
    """
    Encrypt body content using AES-256-GCM.

    Args:
        plaintext: Data to encrypt (string or bytes)
        dek: Data Encryption Key (32 bytes)

    Returns:
        Tuple of (iv, ciphertext, tag) all as bytes

    Raises:
        EncryptionError: If encryption fails
        CryptographyNotAvailableError: If cryptography library is not installed
    """
    _check_cryptography()

    if len(dek) != AES_KEY_SIZE:
        raise EncryptionError(f"DEK must be {AES_KEY_SIZE} bytes, got {len(dek)}")

    # Convert string to bytes if needed
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')

    # Generate random IV (12 bytes for GCM)
    iv = secrets.token_bytes(GCM_IV_SIZE)

    try:
        aesgcm = AESGCM(dek)
        # AESGCM.encrypt returns ciphertext with tag appended
        ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, None)

        # Split ciphertext and tag (tag is last 16 bytes)
        ciphertext = ciphertext_with_tag[:-GCM_TAG_SIZE]
        tag = ciphertext_with_tag[-GCM_TAG_SIZE:]

        return iv, ciphertext, tag
    except Exception as e:
        raise EncryptionError(f"Failed to encrypt body: {e}")


def decrypt_body(
    iv: bytes,
    ciphertext: bytes,
    tag: bytes,
    dek: bytes,
) -> bytes:
    """
    Decrypt body content using AES-256-GCM.

    Args:
        iv: Initialization vector (12 bytes)
        ciphertext: Encrypted data
        tag: Authentication tag (16 bytes)
        dek: Data Encryption Key (32 bytes)

    Returns:
        Decrypted plaintext bytes

    Raises:
        DecryptionError: If decryption fails
        IntegrityError: If authentication tag verification fails (tampering detected)
        CryptographyNotAvailableError: If cryptography library is not installed
    """
    _check_cryptography()

    if len(dek) != AES_KEY_SIZE:
        raise DecryptionError(f"DEK must be {AES_KEY_SIZE} bytes, got {len(dek)}")

    if len(iv) != GCM_IV_SIZE:
        raise DecryptionError(f"IV must be {GCM_IV_SIZE} bytes, got {len(iv)}")

    if len(tag) != GCM_TAG_SIZE:
        raise DecryptionError(f"Tag must be {GCM_TAG_SIZE} bytes, got {len(tag)}")

    try:
        aesgcm = AESGCM(dek)
        # AESGCM.decrypt expects ciphertext with tag appended
        ciphertext_with_tag = ciphertext + tag
        plaintext = aesgcm.decrypt(iv, ciphertext_with_tag, None)
        return plaintext
    except Exception as e:
        error_msg = str(e).lower()
        if "tag" in error_msg or "authentication" in error_msg or "invalid" in error_msg:
            raise IntegrityError(
                "Authentication tag verification failed - data may have been tampered with"
            )
        raise DecryptionError(f"Failed to decrypt body: {e}")


def hybrid_encrypt(
    plaintext: Union[str, bytes, dict],
    public_key: "RSAPublicKey",
    key_id: Optional[str] = None,
) -> EncryptionResult:
    """
    Perform hybrid encryption: AES-256-GCM + RSA-OAEP-256.

    This is the main entry point for encrypting evidence data.

    Args:
        plaintext: Data to encrypt (string, bytes, or dict)
        public_key: RSA public key for DEK wrapping
        key_id: Optional identifier for the RSA key

    Returns:
        EncryptionResult with encrypted_dek, iv, ciphertext, and tag

    Raises:
        EncryptionError: If encryption fails
        CryptographyNotAvailableError: If cryptography library is not installed

    Example:
        >>> keypair = generate_rsa_keypair()
        >>> result = hybrid_encrypt({"evidence": "data"}, keypair.public_key)
        >>> result.encrypted_dek  # RSA-encrypted DEK
        >>> result.ciphertext     # AES-encrypted body
    """
    _check_cryptography()

    # Handle dict input by converting to JSON string
    if isinstance(plaintext, dict):
        import json
        plaintext = json.dumps(plaintext, sort_keys=True)

    # Generate DEK
    dek = generate_dek()

    # Encrypt DEK with RSA-OAEP-256
    encrypted_dek = encrypt_dek(dek, public_key)

    # Encrypt body with AES-256-GCM
    iv, ciphertext, tag = encrypt_body(plaintext, dek)

    # Clear DEK from memory (best effort)
    # Note: Python doesn't guarantee memory clearing, but we try
    del dek

    return EncryptionResult(
        encrypted_dek=base64.b64encode(encrypted_dek).decode('utf-8'),
        iv=base64.b64encode(iv).decode('utf-8'),
        ciphertext=base64.b64encode(ciphertext).decode('utf-8'),
        tag=base64.b64encode(tag).decode('utf-8'),
        key_id=key_id,
    )


def hybrid_decrypt(
    encryption_result: Union[EncryptionResult, dict],
    private_key: "RSAPrivateKey",
) -> bytes:
    """
    Perform hybrid decryption: RSA-OAEP-256 + AES-256-GCM.

    This is the main entry point for decrypting evidence data.

    Args:
        encryption_result: EncryptionResult or dict with encrypted data
        private_key: RSA private key for DEK unwrapping

    Returns:
        Decrypted plaintext bytes

    Raises:
        DecryptionError: If decryption fails
        IntegrityError: If authentication tag verification fails (tampering detected)
        CryptographyNotAvailableError: If cryptography library is not installed

    Example:
        >>> keypair = generate_rsa_keypair()
        >>> result = hybrid_encrypt("secret data", keypair.public_key)
        >>> plaintext = hybrid_decrypt(result, keypair.private_key)
        >>> plaintext.decode('utf-8')
        'secret data'
    """
    _check_cryptography()

    # Handle dict input
    if isinstance(encryption_result, dict):
        encryption_result = EncryptionResult.from_dict(encryption_result)

    # Decode base64 values
    encrypted_dek = base64.b64decode(encryption_result.encrypted_dek)
    iv = base64.b64decode(encryption_result.iv)
    ciphertext = base64.b64decode(encryption_result.ciphertext)
    tag = base64.b64decode(encryption_result.tag)

    # Decrypt DEK with RSA-OAEP-256
    dek = decrypt_dek(encrypted_dek, private_key)

    try:
        # Decrypt body with AES-256-GCM
        plaintext = decrypt_body(iv, ciphertext, tag, dek)
        return plaintext
    finally:
        # Clear DEK from memory (best effort)
        del dek


def hybrid_decrypt_to_string(
    encryption_result: Union[EncryptionResult, dict],
    private_key: "RSAPrivateKey",
) -> str:
    """
    Perform hybrid decryption and return result as UTF-8 string.

    Convenience wrapper around hybrid_decrypt for string data.

    Args:
        encryption_result: EncryptionResult or dict with encrypted data
        private_key: RSA private key for DEK unwrapping

    Returns:
        Decrypted plaintext string

    Raises:
        DecryptionError: If decryption fails or result is not valid UTF-8
        IntegrityError: If authentication tag verification fails
    """
    plaintext_bytes = hybrid_decrypt(encryption_result, private_key)
    try:
        return plaintext_bytes.decode('utf-8')
    except UnicodeDecodeError as e:
        raise DecryptionError(f"Decrypted data is not valid UTF-8: {e}")


def hybrid_decrypt_to_json(
    encryption_result: Union[EncryptionResult, dict],
    private_key: "RSAPrivateKey",
) -> dict:
    """
    Perform hybrid decryption and parse result as JSON.

    Convenience wrapper around hybrid_decrypt for JSON data.

    Args:
        encryption_result: EncryptionResult or dict with encrypted data
        private_key: RSA private key for DEK unwrapping

    Returns:
        Decrypted and parsed JSON dict

    Raises:
        DecryptionError: If decryption fails or result is not valid JSON
        IntegrityError: If authentication tag verification fails
    """
    import json

    plaintext_str = hybrid_decrypt_to_string(encryption_result, private_key)
    try:
        return json.loads(plaintext_str)
    except json.JSONDecodeError as e:
        raise DecryptionError(f"Decrypted data is not valid JSON: {e}")


# Convenience exports
__all__ = [
    # Constants
    "AES_KEY_SIZE",
    "GCM_IV_SIZE",
    "GCM_TAG_SIZE",
    "RSA_KEY_SIZE",
    "CRYPTOGRAPHY_AVAILABLE",

    # Exceptions
    "HybridCryptoError",
    "EncryptionError",
    "DecryptionError",
    "KeyGenerationError",
    "IntegrityError",
    "CryptographyNotAvailableError",

    # Data classes
    "EncryptionResult",
    "RSAKeyPair",

    # Core functions
    "generate_dek",
    "generate_rsa_keypair",
    "encrypt_dek",
    "decrypt_dek",
    "encrypt_body",
    "decrypt_body",

    # High-level API
    "hybrid_encrypt",
    "hybrid_decrypt",
    "hybrid_decrypt_to_string",
    "hybrid_decrypt_to_json",
]
