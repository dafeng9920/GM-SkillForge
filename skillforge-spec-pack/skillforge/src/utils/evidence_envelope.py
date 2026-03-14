"""
Evidence Envelope Implementation for GM-SkillForge

This module provides the Envelope + Body structure for evidence packages
following the L6 authenticity protocol.

Task: T03 - ISSUE-02: Envelope + Body 结构实现
Executor: vs--cc3

Envelope Structure (v1):
- header: metadata about the envelope (version, timestamps, node_id, etc.)
- keywrap: encrypted DEK (Data Encryption Key) using RSA-OAEP-256
- ciphertext: encrypted body content using AES-256-GCM
- signature: Ed25519 signature of canonical(header) + canonical(body_hash)
- cert: node certificate for signature verification
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

from skillforge.src.utils.canonical_json import canonical_json, canonical_json_hash


# Envelope Schema Version
ENVELOPE_SCHEMA_VERSION = "1.0.0"
ENVELOPE_TYPE = "evidence_envelope.v1"


@dataclass
class EnvelopeHeader:
    """
    Envelope header containing metadata.

    Required fields:
    - envelope_id: unique identifier for this envelope
    - schema_version: envelope schema version
    - created_at: ISO-8601 timestamp
    - node_id: identifier of the node that created this envelope
    - body_hash: SHA-256 hash of the canonical body
    - body_encoding: encoding of the body (e.g., "json", "cbor")
    - compression: compression algorithm used (e.g., "none", "gzip")
    """
    envelope_id: str
    schema_version: str
    created_at: str
    node_id: str
    body_hash: str
    body_encoding: str = "json"
    compression: str = "none"
    expires_at: Optional[str] = None
    nonce: Optional[str] = None
    content_type: str = "application/json"
    trace_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class KeyWrap:
    """
    Key wrap structure for encrypted DEK.

    Contains the encrypted Data Encryption Key (DEK) that was used
    to encrypt the body content. The DEK is encrypted using RSA-OAEP-256.

    Fields:
    - algorithm: key wrapping algorithm (RSA-OAEP-256)
    - encrypted_dek: base64-encoded encrypted DEK
    - key_id: identifier of the RSA public key used for encryption
    """
    algorithm: str = "RSA-OAEP-256"
    encrypted_dek: Optional[str] = None
    key_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Ciphertext:
    """
    Ciphertext structure for encrypted body.

    Contains the encrypted body content along with the IV/nonce
    and authentication tag required for AES-256-GCM decryption.

    Fields:
    - algorithm: encryption algorithm (AES-256-GCM)
    - iv: base64-encoded initialization vector (12 bytes for GCM)
    - data: base64-encoded ciphertext
    - tag: base64-encoded authentication tag (16 bytes for GCM)
    """
    algorithm: str = "AES-256-GCM"
    iv: Optional[str] = None
    data: Optional[str] = None
    tag: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Signature:
    """
    Signature structure for envelope authentication.

    Contains the Ed25519 signature of the canonical header and body hash.
    This allows verification that the envelope has not been tampered with.

    Fields:
    - algorithm: signature algorithm (Ed25519)
    - value: base64-encoded signature
    - signed_fields: list of fields that were signed
    - signed_at: ISO-8601 timestamp when signature was created
    """
    algorithm: str = "Ed25519"
    value: Optional[str] = None
    signed_fields: list[str] = field(default_factory=lambda: ["header", "body_hash"])
    signed_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Certificate:
    """
    Certificate structure for node identity verification.

    Contains the node's public key certificate that can be used
    to verify the signature on this envelope.

    Fields:
    - node_id: identifier of the node
    - public_key: base64-encoded Ed25519 public key
    - algorithm: public key algorithm (Ed25519)
    - issued_at: ISO-8601 timestamp when certificate was issued
    - expires_at: ISO-8601 timestamp when certificate expires
    - issuer: identifier of the certificate issuer
    """
    node_id: Optional[str] = None
    public_key: Optional[str] = None
    algorithm: str = "Ed25519"
    issued_at: Optional[str] = None
    expires_at: Optional[str] = None
    issuer: str = "self-signed"

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class EvidenceEnvelope:
    """
    Complete Evidence Envelope with all components.

    This is the top-level structure that contains:
    - header: envelope metadata
    - keywrap: encrypted DEK (for encrypted envelopes)
    - ciphertext: encrypted body (for encrypted envelopes)
    - signature: Ed25519 signature
    - cert: node certificate
    - body: plaintext body (for unencrypted envelopes, not serialized)

    The envelope can be in two modes:
    1. Encrypted: body is encrypted, keywrap and ciphertext are populated
    2. Signed-only: body is plaintext but signed
    """
    header: EnvelopeHeader
    signature: Signature
    cert: Certificate
    keywrap: Optional[KeyWrap] = None
    ciphertext: Optional[Ciphertext] = None
    body: Optional[dict[str, Any]] = None  # Plaintext body (not in encrypted envelopes)

    def to_dict(self) -> dict[str, Any]:
        """Serialize envelope to dictionary."""
        result = {
            "header": self.header.to_dict(),
            "signature": self.signature.to_dict(),
            "cert": self.cert.to_dict(),
        }
        if self.keywrap:
            result["keywrap"] = self.keywrap.to_dict()
        if self.ciphertext:
            result["ciphertext"] = self.ciphertext.to_dict()
        # Note: body is NOT included in serialized form for encrypted envelopes
        # For signed-only envelopes, body may be included
        if self.body and not self.ciphertext:
            result["body"] = self.body
        return result

    def to_json(self, *, indent: Optional[int] = None) -> str:
        """Serialize envelope to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def compute_envelope_hash(self) -> str:
        """Compute SHA-256 hash of the canonical envelope."""
        return canonical_json_hash(self.to_dict())


class EvidenceEnvelopeBuilder:
    """
    Builder for creating Evidence Envelopes.

    This class provides a fluent interface for constructing envelopes
    with all required components.

    Example:
        envelope = (EvidenceEnvelopeBuilder()
            .with_node_id("node-001")
            .with_body({"evidence": "data"})
            .with_trace_id("trace-123")
            .build())
    """

    def __init__(self):
        self._node_id: Optional[str] = None
        self._body: Optional[dict[str, Any]] = None
        self._trace_id: Optional[str] = None
        self._envelope_id: Optional[str] = None
        self._expires_at: Optional[str] = None
        self._public_key: Optional[str] = None
        self._encrypted: bool = False
        self._signature_value: Optional[str] = None
        self._encrypted_dek: Optional[str] = None
        self._key_id: Optional[str] = None
        self._ciphertext_data: Optional[str] = None
        self._ciphertext_iv: Optional[str] = None
        self._ciphertext_tag: Optional[str] = None

    def with_node_id(self, node_id: str) -> "EvidenceEnvelopeBuilder":
        """Set the node ID for this envelope."""
        self._node_id = node_id
        return self

    def with_body(self, body: dict[str, Any]) -> "EvidenceEnvelopeBuilder":
        """Set the body content for this envelope."""
        self._body = body
        return self

    def with_trace_id(self, trace_id: str) -> "EvidenceEnvelopeBuilder":
        """Set the trace ID for correlation."""
        self._trace_id = trace_id
        return self

    def with_envelope_id(self, envelope_id: str) -> "EvidenceEnvelopeBuilder":
        """Set a specific envelope ID (auto-generated if not set)."""
        self._envelope_id = envelope_id
        return self

    def with_expires_at(self, expires_at: str) -> "EvidenceEnvelopeBuilder":
        """Set the expiration timestamp."""
        self._expires_at = expires_at
        return self

    def with_public_key(self, public_key: str) -> "EvidenceEnvelopeBuilder":
        """Set the node's public key for the certificate."""
        self._public_key = public_key
        return self

    def with_encryption(
        self,
        encrypted_dek: str,
        key_id: str,
        ciphertext_data: str,
        ciphertext_iv: str,
        ciphertext_tag: str
    ) -> "EvidenceEnvelopeBuilder":
        """Enable encryption with the given encrypted DEK and ciphertext."""
        self._encrypted = True
        self._encrypted_dek = encrypted_dek
        self._key_id = key_id
        self._ciphertext_data = ciphertext_data
        self._ciphertext_iv = ciphertext_iv
        self._ciphertext_tag = ciphertext_tag
        return self

    def with_signature(self, signature_value: str) -> "EvidenceEnvelopeBuilder":
        """Set the signature value (computed externally)."""
        self._signature_value = signature_value
        return self

    def build(self) -> EvidenceEnvelope:
        """
        Build the EvidenceEnvelope.

        Raises:
            ValueError: if required fields are missing
        """
        if not self._node_id:
            raise ValueError("node_id is required")
        if self._body is None and not self._encrypted:
            raise ValueError("body is required for unencrypted envelopes")

        now = _now_iso()
        envelope_id = self._envelope_id or f"ev-{uuid.uuid4().hex[:8]}"

        # Compute body hash
        if self._body:
            body_hash = canonical_json_hash(self._body)
        else:
            # For encrypted envelopes, hash is of the ciphertext
            body_hash = hashlib.sha256(
                (self._ciphertext_data or "").encode()
            ).hexdigest()

        # Build header
        header = EnvelopeHeader(
            envelope_id=envelope_id,
            schema_version=ENVELOPE_SCHEMA_VERSION,
            created_at=now,
            node_id=self._node_id,
            body_hash=body_hash,
            expires_at=self._expires_at,
            trace_id=self._trace_id,
        )

        # Build signature
        signature = Signature(
            value=self._signature_value,
            signed_at=now if self._signature_value else None,
        )

        # Build certificate
        cert = Certificate(
            node_id=self._node_id,
            public_key=self._public_key,
            issued_at=now,
            expires_at=self._expires_at,
        )

        # Build keywrap and ciphertext for encrypted envelopes
        keywrap = None
        ciphertext = None
        body = self._body

        if self._encrypted:
            keywrap = KeyWrap(
                encrypted_dek=self._encrypted_dek,
                key_id=self._key_id,
            )
            ciphertext = Ciphertext(
                iv=self._ciphertext_iv,
                data=self._ciphertext_data,
                tag=self._ciphertext_tag,
            )
            body = None  # Don't include plaintext body in encrypted envelopes

        return EvidenceEnvelope(
            header=header,
            signature=signature,
            cert=cert,
            keywrap=keywrap,
            ciphertext=ciphertext,
            body=body,
        )


def validate_envelope_schema(envelope_dict: dict[str, Any]) -> list[str]:
    """
    Validate an envelope dictionary against the schema.

    Returns a list of validation errors (empty if valid).
    """
    errors: list[str] = []

    # Check required top-level fields
    required_fields = ["header", "signature", "cert"]
    for field in required_fields:
        if field not in envelope_dict:
            errors.append(f"Missing required field: {field}")

    # Validate header
    header = envelope_dict.get("header", {})
    header_required = ["envelope_id", "schema_version", "created_at", "node_id", "body_hash"]
    for field in header_required:
        if field not in header:
            errors.append(f"Missing required header field: {field}")

    # Validate signature
    sig = envelope_dict.get("signature", {})
    if "algorithm" not in sig:
        errors.append("Missing signature algorithm")
    if "signed_fields" not in sig:
        errors.append("Missing signed_fields in signature")

    # Validate cert
    cert = envelope_dict.get("cert", {})
    if "algorithm" not in cert:
        errors.append("Missing cert algorithm")

    # If encrypted, validate keywrap and ciphertext
    if "ciphertext" in envelope_dict:
        ct = envelope_dict.get("ciphertext", {})
        ct_required = ["algorithm", "iv", "data", "tag"]
        for field in ct_required:
            if field not in ct:
                errors.append(f"Missing ciphertext field: {field}")

        kw = envelope_dict.get("keywrap", {})
        kw_required = ["algorithm", "encrypted_dek", "key_id"]
        for field in kw_required:
            if field not in kw:
                errors.append(f"Missing keywrap field: {field}")

    return errors


def create_signed_envelope(
    node_id: str,
    body: dict[str, Any],
    signature_value: str,
    public_key: str,
    trace_id: Optional[str] = None,
    expires_at: Optional[str] = None,
) -> EvidenceEnvelope:
    """
    Convenience function to create a signed (but not encrypted) envelope.

    Args:
        node_id: Identifier of the signing node
        body: The evidence body content
        signature_value: Ed25519 signature value
        public_key: Node's Ed25519 public key
        trace_id: Optional trace ID for correlation
        expires_at: Optional expiration timestamp

    Returns:
        EvidenceEnvelope with signature
    """
    return (EvidenceEnvelopeBuilder()
        .with_node_id(node_id)
        .with_body(body)
        .with_signature(signature_value)
        .with_public_key(public_key)
        .with_trace_id(trace_id)
        .with_expires_at(expires_at)
        .build())


def create_encrypted_envelope(
    node_id: str,
    body_hash: str,
    encrypted_dek: str,
    key_id: str,
    ciphertext_data: str,
    ciphertext_iv: str,
    ciphertext_tag: str,
    signature_value: str,
    public_key: str,
    trace_id: Optional[str] = None,
    expires_at: Optional[str] = None,
) -> EvidenceEnvelope:
    """
    Convenience function to create an encrypted and signed envelope.

    Args:
        node_id: Identifier of the signing node
        body_hash: Hash of the original body content
        encrypted_dek: RSA-OAEP-256 encrypted DEK
        key_id: Identifier of the RSA key used
        ciphertext_data: AES-256-GCM encrypted body
        ciphertext_iv: Initialization vector for AES-GCM
        ciphertext_tag: Authentication tag for AES-GCM
        signature_value: Ed25519 signature value
        public_key: Node's Ed25519 public key
        trace_id: Optional trace ID for correlation
        expires_at: Optional expiration timestamp

    Returns:
        EvidenceEnvelope with encryption and signature
    """
    builder = (EvidenceEnvelopeBuilder()
        .with_node_id(node_id)
        .with_signature(signature_value)
        .with_public_key(public_key)
        .with_encryption(
            encrypted_dek=encrypted_dek,
            key_id=key_id,
            ciphertext_data=ciphertext_data,
            ciphertext_iv=ciphertext_iv,
            ciphertext_tag=ciphertext_tag,
        )
        .with_trace_id(trace_id)
        .with_expires_at(expires_at))

    # Set body hash directly
    envelope = builder.build()
    envelope.header.body_hash = body_hash
    return envelope


def _now_iso() -> str:
    """Return current ISO-8601 UTC timestamp."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# Convenience exports
__all__ = [
    "ENVELOPE_SCHEMA_VERSION",
    "ENVELOPE_TYPE",
    "EnvelopeHeader",
    "KeyWrap",
    "Ciphertext",
    "Signature",
    "Certificate",
    "EvidenceEnvelope",
    "EvidenceEnvelopeBuilder",
    "validate_envelope_schema",
    "create_signed_envelope",
    "create_encrypted_envelope",
]
