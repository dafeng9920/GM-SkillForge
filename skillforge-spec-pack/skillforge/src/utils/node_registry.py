"""
Node Registry Module for SkillForge.

This module provides a centralized node registry that maps node_id to
public keys, certificates, and status. It enforces fail-closed behavior
by rejecting unknown or disabled nodes with NODE_UNTRUSTED error.

Dependencies:
    - cryptography >= 41.0.0 (for Ed25519 key handling)
    - skillforge.src.utils.canonical_json (for hash computation)

Usage:
    >>> from skillforge.src.utils.node_registry import (
    ...     NodeRegistry,
    ...     NodeStatus,
    ...     NODE_UNTRUSTED_ERROR
    ... )
    >>> registry = NodeRegistry()
    >>> registry.register_node("node-001", public_key_hex)
    >>> node_info = registry.get_node("node-001")
    >>> is_trusted = registry.is_node_trusted("node-001")
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path

try:
    from cryptography.hazmat.primitives.serialization import (
        load_pem_public_key,
        Encoding,
        PublicFormat
    )
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


# Error codes for node registry operations
class NodeRegistryError(str, Enum):
    """Error codes for node registry operations."""
    NODE_UNTRUSTED = "NODE_UNTRUSTED"
    NODE_NOT_FOUND = "NODE_NOT_FOUND"
    NODE_DISABLED = "NODE_DISABLED"
    NODE_EXPIRED = "NODE_EXPIRED"
    INVALID_PUBLIC_KEY = "INVALID_PUBLIC_KEY"
    INVALID_NODE_ID = "INVALID_NODE_ID"
    REGISTRY_LOAD_ERROR = "REGISTRY_LOAD_ERROR"
    REGISTRY_SAVE_ERROR = "REGISTRY_SAVE_ERROR"


# Constants
NODE_UNTRUSTED_ERROR = NodeRegistryError.NODE_UNTRUSTED
DEFAULT_REGISTRY_PATH = "db/node_registry.json"
NODE_ID_PREFIX = "node-"


class NodeStatus(str, Enum):
    """Node status in the registry."""
    ACTIVE = "active"
    DISABLED = "disabled"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass
class NodeInfo:
    """Information about a registered node."""
    node_id: str
    public_key_hex: str
    status: NodeStatus = NodeStatus.ACTIVE
    registered_at: str = ""
    last_seen_at: str = ""
    cert_fingerprint: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Set timestamps if not provided."""
        if not self.registered_at:
            self.registered_at = datetime.utcnow().isoformat() + "Z"
        if not self.last_seen_at:
            self.last_seen_at = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            "node_id": self.node_id,
            "public_key_hex": self.public_key_hex,
            "status": self.status.value,
            "registered_at": self.registered_at,
            "last_seen_at": self.last_seen_at,
            "cert_fingerprint": self.cert_fingerprint,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "NodeInfo":
        """Create from dictionary format."""
        return cls(
            node_id=data["node_id"],
            public_key_hex=data["public_key_hex"],
            status=NodeStatus(data.get("status", NodeStatus.ACTIVE)),
            registered_at=data.get("registered_at", ""),
            last_seen_at=data.get("last_seen_at", ""),
            cert_fingerprint=data.get("cert_fingerprint"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class TrustDecision:
    """Result of a node trust verification."""
    is_trusted: bool
    node_id: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    node_info: Optional[NodeInfo] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            "is_trusted": self.is_trusted,
            "node_id": self.node_id,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "node_info": self.node_info.to_dict() if self.node_info else None,
        }


class NodeRegistry:
    """
    Centralized node registry for SkillForge.

    This registry maintains a mapping of node_id to node information including
    public keys, certificates, and status. It enforces fail-closed behavior:
    unknown nodes are automatically rejected with NODE_UNTRUSTED error.

    The registry can be persisted to disk and supports in-memory operations.
    """

    def __init__(
        self,
        registry_path: Optional[str] = None,
        fail_closed: bool = True
    ):
        """
        Initialize the node registry.

        Args:
            registry_path: Path to the registry file on disk.
            fail_closed: If True, unknown nodes are rejected (default: True).
        """
        self.registry_path = registry_path or DEFAULT_REGISTRY_PATH
        self.fail_closed = fail_closed
        self._nodes: Dict[str, NodeInfo] = {}
        self._load()

    # ========== Registration ==========

    def register_node(
        self,
        node_id: str,
        public_key_hex: str,
        status: NodeStatus = NodeStatus.ACTIVE,
        cert_fingerprint: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> NodeInfo:
        """
        Register a node in the registry.

        Args:
            node_id: Unique node identifier.
            public_key_hex: Hex-encoded Ed25519 public key (64 hex chars).
            status: Initial status of the node.
            cert_fingerprint: Optional certificate fingerprint.
            metadata: Optional metadata dictionary.

        Returns:
            NodeInfo: The registered node information.

        Raises:
            ValueError: If node_id or public_key_hex is invalid.
        """
        self._validate_node_id(node_id)
        self._validate_public_key_hex(public_key_hex)

        node_info = NodeInfo(
            node_id=node_id,
            public_key_hex=public_key_hex,
            status=status,
            cert_fingerprint=cert_fingerprint,
            metadata=metadata or {},
        )

        self._nodes[node_id] = node_info
        return node_info

    def unregister_node(self, node_id: str) -> bool:
        """
        Remove a node from the registry.

        Args:
            node_id: Node identifier to remove.

        Returns:
            bool: True if node was removed, False if not found.
        """
        if node_id in self._nodes:
            del self._nodes[node_id]
            return True
        return False

    # ========== Query ==========

    def get_node(self, node_id: str) -> Optional[NodeInfo]:
        """
        Get node information by ID.

        Args:
            node_id: Node identifier.

        Returns:
            NodeInfo if found, None otherwise.
        """
        return self._nodes.get(node_id)

    def list_nodes(
        self,
        status: Optional[NodeStatus] = None
    ) -> List[NodeInfo]:
        """
        List all nodes, optionally filtered by status.

        Args:
            status: Optional status filter.

        Returns:
            List of NodeInfo objects.
        """
        nodes = list(self._nodes.values())
        if status:
            nodes = [n for n in nodes if n.status == status]
        return nodes

    def get_public_key(self, node_id: str) -> Optional[str]:
        """
        Get the public key hex for a node.

        Args:
            node_id: Node identifier.

        Returns:
            Public key hex if found, None otherwise.
        """
        node_info = self.get_node(node_id)
        return node_info.public_key_hex if node_info else None

    # ========== Trust Verification ==========

    def is_node_trusted(
        self,
        node_id: str,
        allow_pending: bool = False
    ) -> bool:
        """
        Check if a node is trusted (active and registered).

        Args:
            node_id: Node identifier.
            allow_pending: If True, pending nodes are also trusted.

        Returns:
            bool: True if node is trusted, False otherwise.
        """
        decision = self.verify_node_trust(node_id, allow_pending)
        return decision.is_trusted

    def verify_node_trust(
        self,
        node_id: str,
        allow_pending: bool = False
    ) -> TrustDecision:
        """
        Verify if a node is trusted with detailed error information.

        This is the main method for enforcing NODE_UNTRUSTED policy.
        It returns a TrustDecision with error codes for fail-closed handling.

        Args:
            node_id: Node identifier to verify.
            allow_pending: If True, pending nodes are also trusted.

        Returns:
            TrustDecision: Decision with detailed status and error codes.

        Examples:
            >>> registry = NodeRegistry()
            >>> registry.register_node("node-001", public_key_hex)
            >>> decision = registry.verify_node_trust("node-001")
            >>> assert decision.is_trusted == True

            >>> decision = registry.verify_node_trust("unknown-node")
            >>> assert decision.is_trusted == False
            >>> assert decision.error_code == "NODE_UNTRUSTED"
        """
        # Check if node exists
        node_info = self.get_node(node_id)

        if node_info is None:
            # Fail-closed: Unknown nodes are rejected
            if self.fail_closed:
                return TrustDecision(
                    is_trusted=False,
                    node_id=node_id,
                    error_code=NodeRegistryError.NODE_UNTRUSTED,
                    error_message=f"Node '{node_id}' is not registered in the registry",
                )
            else:
                # Fail-open: Unknown nodes are allowed (not recommended)
                return TrustDecision(
                    is_trusted=True,
                    node_id=node_id,
                    error_message=f"Node '{node_id}' not found but fail_closed=False",
                )

        # Check node status
        if node_info.status == NodeStatus.DISABLED:
            return TrustDecision(
                is_trusted=False,
                node_id=node_id,
                node_info=node_info,
                error_code=NodeRegistryError.NODE_DISABLED,
                error_message=f"Node '{node_id}' is disabled",
            )

        if node_info.status == NodeStatus.REVOKED:
            return TrustDecision(
                is_trusted=False,
                node_id=node_id,
                node_info=node_info,
                error_code=NodeRegistryError.NODE_UNTRUSTED,
                error_message=f"Node '{node_id}' has been revoked",
            )

        if node_info.status == NodeStatus.PENDING and not allow_pending:
            return TrustDecision(
                is_trusted=False,
                node_id=node_id,
                node_info=node_info,
                error_code=NodeRegistryError.NODE_UNTRUSTED,
                error_message=f"Node '{node_id}' is pending approval",
            )

        # Node is trusted
        return TrustDecision(
            is_trusted=True,
            node_id=node_id,
            node_info=node_info,
        )

    # ========== Status Management ==========

    def set_node_status(self, node_id: str, status: NodeStatus) -> bool:
        """
        Update the status of a node.

        Args:
            node_id: Node identifier.
            status: New status to set.

        Returns:
            bool: True if status was updated, False if node not found.
        """
        node_info = self.get_node(node_id)
        if node_info:
            node_info.status = status
            node_info.last_seen_at = datetime.utcnow().isoformat() + "Z"
            return True
        return False

    def enable_node(self, node_id: str) -> bool:
        """Enable a node (set status to ACTIVE)."""
        return self.set_node_status(node_id, NodeStatus.ACTIVE)

    def disable_node(self, node_id: str) -> bool:
        """Disable a node (set status to DISABLED)."""
        return self.set_node_status(node_id, NodeStatus.DISABLED)

    def revoke_node(self, node_id: str) -> bool:
        """Revoke a node (set status to REVOKED)."""
        return self.set_node_status(node_id, NodeStatus.REVOKED)

    def update_last_seen(self, node_id: str) -> bool:
        """
        Update the last_seen timestamp for a node.

        Args:
            node_id: Node identifier.

        Returns:
            bool: True if updated, False if node not found.
        """
        node_info = self.get_node(node_id)
        if node_info:
            node_info.last_seen_at = datetime.utcnow().isoformat() + "Z"
            return True
        return False

    # ========== Persistence ==========

    def save(self) -> None:
        """
        Save the registry to disk.

        Raises:
            IOError: If save fails.
        """
        try:
            path = Path(self.registry_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "version": "1.0",
                "saved_at": datetime.utcnow().isoformat() + "Z",
                "fail_closed": self.fail_closed,
                "nodes": [node.to_dict() for node in self._nodes.values()],
            }

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise IOError(
                f"{NodeRegistryError.REGISTRY_SAVE_ERROR}: {str(e)}"
            )

    def _load(self) -> None:
        """
        Load the registry from disk.

        If the file doesn't exist, starts with an empty registry.
        """
        try:
            path = Path(self.registry_path)
            if not path.exists():
                return

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.fail_closed = data.get("fail_closed", True)

            for node_data in data.get("nodes", []):
                node_info = NodeInfo.from_dict(node_data)
                self._nodes[node_info.node_id] = node_info

        except Exception as e:
            # On load error, start with empty registry but log warning
            # In production, this should be logged properly
            self._nodes = {}

    def reload(self) -> None:
        """Reload the registry from disk."""
        self._nodes = {}
        self._load()

    # ========== Validation ==========

    def _validate_node_id(self, node_id: str) -> None:
        """
        Validate node ID format.

        Args:
            node_id: Node identifier to validate.

        Raises:
            ValueError: If node_id is invalid.
        """
        if not node_id:
            raise ValueError("node_id cannot be empty")

        if not isinstance(node_id, str):
            raise ValueError("node_id must be a string")

        # Optional: Enforce prefix
        # if not node_id.startswith(NODE_ID_PREFIX):
        #     raise ValueError(f"node_id must start with '{NODE_ID_PREFIX}'")

    def _validate_public_key_hex(self, public_key_hex: str) -> None:
        """
        validate Ed25519 public key hex format.

        Ed25519 public keys are 32 bytes = 64 hex characters.

        Args:
            public_key_hex: Hex-encoded public key to validate.

        Raises:
            ValueError: If public_key_hex is invalid.
        """
        if not public_key_hex:
            raise ValueError("public_key_hex cannot be empty")

        if not isinstance(public_key_hex, str):
            raise ValueError("public_key_hex must be a string")

        # Remove any whitespace or '0x' prefix
        public_key_hex = public_key_hex.strip().lower()
        if public_key_hex.startswith("0x"):
            public_key_hex = public_key_hex[2:]

        # Ed25519 public key is 32 bytes = 64 hex chars
        if len(public_key_hex) != 64:
            raise ValueError(
                f"public_key_hex must be 64 characters (32 bytes), got {len(public_key_hex)}"
            )

        # Verify it's valid hex
        try:
            int(public_key_hex, 16)
        except ValueError:
            raise ValueError("public_key_hex must contain valid hexadecimal characters")

    # ========== Utility ==========

    def count(self) -> int:
        """Return the number of registered nodes."""
        return len(self._nodes)

    def is_empty(self) -> bool:
        """Check if the registry is empty."""
        return len(self._nodes) == 0

    def clear(self) -> None:
        """Clear all nodes from the registry."""
        self._nodes.clear()

    def to_dict(self) -> Dict:
        """
        Export the entire registry as a dictionary.

        Returns:
            Dictionary representation of the registry.
        """
        return {
            "version": "1.0",
            "fail_closed": self.fail_closed,
            "node_count": self.count(),
            "nodes": [node.to_dict() for node in self._nodes.values()],
        }


# ========== Convenience Functions ==========

def create_sample_registry() -> NodeRegistry:
    """
    Create a sample registry with test nodes for development/testing.

    Returns:
        NodeRegistry with 3 sample nodes.
    """
    registry = NodeRegistry()

    # Sample Ed25519 public keys (64 hex chars each)
    # These are test keys only - do not use in production
    sample_keys = {
        "node-001": "a" * 64,  # Placeholder key
        "node-002": "b" * 64,
        "node-003": "c" * 64,
    }

    for node_id, public_key in sample_keys.items():
        registry.register_node(
            node_id=node_id,
            public_key_hex=public_key,
            status=NodeStatus.ACTIVE,
            metadata={"environment": "test"},
        )

    return registry


def verify_node_with_registry(
    node_id: str,
    registry: Optional[NodeRegistry] = None
) -> TrustDecision:
    """
    Convenience function to verify a node using the default registry.

    Args:
        node_id: Node identifier to verify.
        registry: Optional custom registry. If None, creates a default one.

    Returns:
        TrustDecision with verification result.
    """
    if registry is None:
        registry = NodeRegistry()

    return registry.verify_node_trust(node_id)
