"""
Test suite for Node Registry Module.

Tests cover:
- Node registration and management
- Trust verification with NODE_UNTRUSTED rejection
- Status management (active, disabled, revoked, pending)
- Registry persistence (save/load)
- Fail-closed behavior enforcement
- Integration with Ed25519 public keys
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from skillforge.src.utils.node_registry import (
    NodeRegistry,
    NodeStatus,
    NodeInfo,
    TrustDecision,
    NodeRegistryError,
    NODE_UNTRUSTED_ERROR,
    NODE_ID_PREFIX,
    create_sample_registry,
    verify_node_with_registry,
)


class TestNodeInfo:
    """Tests for NodeInfo dataclass."""

    def test_create_node_info(self):
        """Test creating a NodeInfo object."""
        node_info = NodeInfo(
            node_id="node-001",
            public_key_hex="a" * 64,
            status=NodeStatus.ACTIVE,
        )
        assert node_info.node_id == "node-001"
        assert node_info.public_key_hex == "a" * 64
        assert node_info.status == NodeStatus.ACTIVE
        assert node_info.registered_at != ""
        assert node_info.last_seen_at != ""

    def test_node_info_to_dict(self):
        """Test converting NodeInfo to dictionary."""
        node_info = NodeInfo(
            node_id="node-001",
            public_key_hex="a" * 64,
            cert_fingerprint="abc123",
            metadata={"env": "test"},
        )
        data = node_info.to_dict()
        assert data["node_id"] == "node-001"
        assert data["public_key_hex"] == "a" * 64
        assert data["status"] == NodeStatus.ACTIVE.value
        assert data["cert_fingerprint"] == "abc123"
        assert data["metadata"] == {"env": "test"}

    def test_node_info_from_dict(self):
        """Test creating NodeInfo from dictionary."""
        data = {
            "node_id": "node-001",
            "public_key_hex": "a" * 64,
            "status": "active",
            "registered_at": "2026-02-26T10:00:00Z",
            "last_seen_at": "2026-02-26T10:05:00Z",
            "cert_fingerprint": "abc123",
            "metadata": {"env": "test"},
        }
        node_info = NodeInfo.from_dict(data)
        assert node_info.node_id == "node-001"
        assert node_info.status == NodeStatus.ACTIVE
        assert node_info.cert_fingerprint == "abc123"


class TestNodeRegistryCreation:
    """Tests for NodeRegistry initialization and creation."""

    def test_create_registry_default(self):
        """Test creating a registry with default settings."""
        registry = NodeRegistry()
        assert registry.fail_closed == True
        assert registry.is_empty() == True
        assert registry.count() == 0

    def test_create_registry_with_path(self):
        """Test creating a registry with a custom path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "test_registry.json"
            registry = NodeRegistry(registry_path=str(registry_path))
            assert registry.registry_path == str(registry_path)

    def test_create_registry_fail_open(self):
        """Test creating a registry with fail-open mode (not recommended)."""
        registry = NodeRegistry(fail_closed=False)
        assert registry.fail_closed == False

    def test_create_sample_registry(self):
        """Test creating a sample registry with test nodes."""
        registry = create_sample_registry()
        assert registry.count() == 3
        assert registry.is_empty() == False
        assert registry.get_node("node-001") is not None
        assert registry.get_node("node-002") is not None
        assert registry.get_node("node-003") is not None


class TestNodeRegistration:
    """Tests for node registration operations."""

    def test_register_node(self):
        """Test registering a new node."""
        registry = NodeRegistry()
        public_key = "a" * 64
        node_info = registry.register_node("node-001", public_key)

        assert node_info.node_id == "node-001"
        assert node_info.public_key_hex == public_key
        assert node_info.status == NodeStatus.ACTIVE
        assert registry.count() == 1

    def test_register_node_with_metadata(self):
        """Test registering a node with metadata."""
        registry = NodeRegistry()
        node_info = registry.register_node(
            "node-001",
            "a" * 64,
            status=NodeStatus.PENDING,
            cert_fingerprint="abc123",
            metadata={"env": "production", "region": "us-east-1"},
        )

        assert node_info.status == NodeStatus.PENDING
        assert node_info.cert_fingerprint == "abc123"
        assert node_info.metadata["env"] == "production"

    def test_register_node_invalid_node_id(self):
        """Test that registering with empty node_id raises error."""
        registry = NodeRegistry()
        with pytest.raises(ValueError, match="node_id cannot be empty"):
            registry.register_node("", "a" * 64)

    def test_register_node_invalid_public_key_too_short(self):
        """Test that registering with too short public key raises error."""
        registry = NodeRegistry()
        with pytest.raises(ValueError, match="must be 64 characters"):
            registry.register_node("node-001", "a" * 32)

    def test_register_node_invalid_public_key_not_hex(self):
        """Test that registering with non-hex public key raises error."""
        registry = NodeRegistry()
        with pytest.raises(ValueError, match="valid hexadecimal"):
            registry.register_node("node-001", "g" * 64)

    def test_register_node_with_0x_prefix(self):
        """Test that registering with 0x prefix works."""
        registry = NodeRegistry()
        # Should strip 0x prefix
        node_info = registry.register_node("node-001", "0x" + "a" * 64)
        assert node_info.public_key_hex == "a" * 64

    def test_unregister_node(self):
        """Test unregistering a node."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64)
        assert registry.count() == 1

        result = registry.unregister_node("node-001")
        assert result == True
        assert registry.count() == 0

    def test_unregister_nonexistent_node(self):
        """Test unregistering a non-existent node returns False."""
        registry = NodeRegistry()
        result = registry.unregister_node("node-999")
        assert result == False


class TestNodeQuery:
    """Tests for node query operations."""

    def test_get_node(self):
        """Test getting a node by ID."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64)

        node_info = registry.get_node("node-001")
        assert node_info is not None
        assert node_info.node_id == "node-001"

    def test_get_nonexistent_node(self):
        """Test getting a non-existent node returns None."""
        registry = NodeRegistry()
        node_info = registry.get_node("node-999")
        assert node_info is None

    def test_list_all_nodes(self):
        """Test listing all nodes."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64)
        registry.register_node("node-002", "b" * 64)
        registry.register_node("node-003", "c" * 64)

        nodes = registry.list_nodes()
        assert len(nodes) == 3

    def test_list_nodes_filtered_by_status(self):
        """Test listing nodes filtered by status."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64, NodeStatus.ACTIVE)
        registry.register_node("node-002", "b" * 64, NodeStatus.DISABLED)
        registry.register_node("node-003", "c" * 64, NodeStatus.ACTIVE)

        active_nodes = registry.list_nodes(NodeStatus.ACTIVE)
        assert len(active_nodes) == 2

        disabled_nodes = registry.list_nodes(NodeStatus.DISABLED)
        assert len(disabled_nodes) == 1

    def test_get_public_key(self):
        """Test getting public key for a node."""
        registry = NodeRegistry()
        public_key = "a" * 64
        registry.register_node("node-001", public_key)

        retrieved_key = registry.get_public_key("node-001")
        assert retrieved_key == public_key

    def test_get_public_key_nonexistent(self):
        """Test getting public key for non-existent node returns None."""
        registry = NodeRegistry()
        key = registry.get_public_key("node-999")
        assert key is None


class TestTrustVerification:
    """Tests for node trust verification - core of NODE_UNTRUSTED policy."""

    def test_trusted_active_node(self):
        """Test that active node is trusted."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64, NodeStatus.ACTIVE)

        decision = registry.verify_node_trust("node-001")
        assert decision.is_trusted == True
        assert decision.error_code is None
        assert decision.node_info is not None

    def test_is_node_trusted_active(self):
        """Test is_node_trusted for active node."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64)

        assert registry.is_node_trusted("node-001") == True

    def test_unknown_node_rejected_fail_closed(self):
        """Test that unknown node is rejected with NODE_UNTRUSTED (fail-closed)."""
        registry = NodeRegistry(fail_closed=True)

        decision = registry.verify_node_trust("unknown-node")
        assert decision.is_trusted == False
        assert decision.error_code == NodeRegistryError.NODE_UNTRUSTED
        assert "not registered" in decision.error_message

    def test_unknown_node_rejected_is_node_trusted(self):
        """Test is_node_trusted returns False for unknown node."""
        registry = NodeRegistry()
        assert registry.is_node_trusted("unknown-node") == False

    def test_disabled_node_rejected(self):
        """Test that disabled node is rejected."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64, NodeStatus.DISABLED)

        decision = registry.verify_node_trust("node-001")
        assert decision.is_trusted == False
        assert decision.error_code == NodeRegistryError.NODE_DISABLED
        assert "disabled" in decision.error_message

    def test_revoked_node_rejected(self):
        """Test that revoked node is rejected with NODE_UNTRUSTED."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64, NodeStatus.REVOKED)

        decision = registry.verify_node_trust("node-001")
        assert decision.is_trusted == False
        assert decision.error_code == NodeRegistryError.NODE_UNTRUSTED
        assert "revoked" in decision.error_message

    def test_pending_node_rejected_by_default(self):
        """Test that pending node is rejected unless allow_pending=True."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64, NodeStatus.PENDING)

        decision = registry.verify_node_trust("node-001")
        assert decision.is_trusted == False
        assert decision.error_code == NodeRegistryError.NODE_UNTRUSTED

    def test_pending_node_allowed_with_flag(self):
        """Test that pending node is allowed when allow_pending=True."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64, NodeStatus.PENDING)

        decision = registry.verify_node_trust("node-001", allow_pending=True)
        assert decision.is_trusted == True

    def test_trust_decision_to_dict(self):
        """Test converting TrustDecision to dictionary."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64)

        decision = registry.verify_node_trust("node-001")
        data = decision.to_dict()
        assert data["is_trusted"] == True
        assert data["node_id"] == "node-001"
        assert data["error_code"] is None

    def test_trust_decision_to_dict_failure(self):
        """Test converting failed TrustDecision to dictionary."""
        registry = NodeRegistry()

        decision = registry.verify_node_trust("unknown-node")
        data = decision.to_dict()
        assert data["is_trusted"] == False
        assert data["error_code"] == NodeRegistryError.NODE_UNTRUSTED
        assert data["node_info"] is None

    def test_fail_open_mode_unknown_node(self):
        """Test that fail-open mode allows unknown nodes (not recommended)."""
        registry = NodeRegistry(fail_closed=False)

        decision = registry.verify_node_trust("unknown-node")
        # In fail-open mode, unknown nodes are "trusted"
        assert decision.is_trusted == True
        assert "fail_closed=False" in decision.error_message


class TestStatusManagement:
    """Tests for node status management."""

    def test_set_node_status(self):
        """Test setting node status."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64)

        result = registry.set_node_status("node-001", NodeStatus.DISABLED)
        assert result == True

        node_info = registry.get_node("node-001")
        assert node_info.status == NodeStatus.DISABLED

    def test_set_status_nonexistent_node(self):
        """Test setting status for non-existent node returns False."""
        registry = NodeRegistry()
        result = registry.set_node_status("node-999", NodeStatus.DISABLED)
        assert result == False

    def test_enable_node(self):
        """Test enabling a node."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64, NodeStatus.DISABLED)

        result = registry.enable_node("node-001")
        assert result == True

        node_info = registry.get_node("node-001")
        assert node_info.status == NodeStatus.ACTIVE

    def test_disable_node(self):
        """Test disabling a node."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64, NodeStatus.ACTIVE)

        result = registry.disable_node("node-001")
        assert result == True

        node_info = registry.get_node("node-001")
        assert node_info.status == NodeStatus.DISABLED

    def test_revoke_node(self):
        """Test revoking a node."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64, NodeStatus.ACTIVE)

        result = registry.revoke_node("node-001")
        assert result == True

        node_info = registry.get_node("node-001")
        assert node_info.status == NodeStatus.REVOKED

    def test_update_last_seen(self):
        """Test updating last_seen timestamp."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64)

        # Get original timestamp
        original_last_seen = registry.get_node("node-001").last_seen_at

        # Update
        result = registry.update_last_seen("node-001")
        assert result == True

        # Verify it changed
        new_last_seen = registry.get_node("node-001").last_seen_at
        assert new_last_seen != original_last_seen

    def test_update_last_seen_nonexistent(self):
        """Test updating last_seen for non-existent node returns False."""
        registry = NodeRegistry()
        result = registry.update_last_seen("node-999")
        assert result == False


class TestRegistryPersistence:
    """Tests for registry save/load operations."""

    def test_save_and_load_registry(self):
        """Test saving and loading registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "test_registry.json"

            # Create and populate registry
            registry = NodeRegistry(registry_path=str(registry_path))
            registry.register_node("node-001", "a" * 64)
            registry.register_node("node-002", "b" * 64, NodeStatus.DISABLED)
            registry.register_node("node-003", "c" * 64, metadata={"env": "prod"})

            # Save
            registry.save()

            # Load into new registry
            registry2 = NodeRegistry(registry_path=str(registry_path))
            assert registry2.count() == 3
            assert registry2.get_node("node-001") is not None
            assert registry2.get_node("node-002").status == NodeStatus.DISABLED
            assert registry2.get_node("node-003").metadata["env"] == "prod"

    def test_save_creates_directory(self):
        """Test that save creates parent directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "subdir" / "registry.json"

            registry = NodeRegistry(registry_path=str(registry_path))
            registry.register_node("node-001", "a" * 64)
            registry.save()

            assert registry_path.exists()

    def test_load_nonexistent_registry(self):
        """Test loading non-existent registry starts empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "nonexistent.json"

            registry = NodeRegistry(registry_path=str(registry_path))
            assert registry.is_empty() == True

    def test_registry_to_dict(self):
        """Test exporting registry to dictionary."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64)
        registry.register_node("node-002", "b" * 64)

        data = registry.to_dict()
        assert data["node_count"] == 2
        assert len(data["nodes"]) == 2
        assert data["fail_closed"] == True
        assert data["version"] == "1.0"


class TestUtilityMethods:
    """Tests for utility methods."""

    def test_count(self):
        """Test counting nodes."""
        registry = NodeRegistry()
        assert registry.count() == 0

        registry.register_node("node-001", "a" * 64)
        assert registry.count() == 1

        registry.register_node("node-002", "b" * 64)
        assert registry.count() == 2

    def test_is_empty(self):
        """Test checking if registry is empty."""
        registry = NodeRegistry()
        assert registry.is_empty() == True

        registry.register_node("node-001", "a" * 64)
        assert registry.is_empty() == False

    def test_clear(self):
        """Test clearing all nodes."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64)
        registry.register_node("node-002", "b" * 64)
        assert registry.count() == 2

        registry.clear()
        assert registry.count() == 0
        assert registry.is_empty() == True

    def test_reload(self):
        """Test reloading registry from disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "test_registry.json"

            # Create and save
            registry = NodeRegistry(registry_path=str(registry_path))
            registry.register_node("node-001", "a" * 64)
            registry.save()

            # Modify in-memory
            registry.register_node("node-002", "b" * 64)
            assert registry.count() == 2

            # Reload (should have 1 node)
            registry.reload()
            assert registry.count() == 1


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_verify_node_with_registry_default(self):
        """Test verify_node_with_registry with default registry."""
        decision = verify_node_with_registry("unknown-node")
        assert decision.is_trusted == False
        assert decision.error_code == NodeRegistryError.NODE_UNTRUSTED

    def test_verify_node_with_custom_registry(self):
        """Test verify_node_with_registry with custom registry."""
        registry = NodeRegistry()
        registry.register_node("node-001", "a" * 64)

        decision = verify_node_with_registry("node-001", registry)
        assert decision.is_trusted == True


class TestIntegrationWithEd25519:
    """Tests for integration with Ed25519 signature module."""

    def test_store_ed25519_public_key(self):
        """Test storing Ed25519 public key from keypair generation."""
        registry = NodeRegistry()

        # Generate a valid Ed25519 keypair (if cryptography available)
        try:
            from skillforge.src.utils.ed25519_signature import generate_keypair
            keypair = generate_keypair()
            public_key_hex = keypair.public_key_hex

            # Register node
            registry.register_node("node-001", public_key_hex)

            # Retrieve and verify
            node_info = registry.get_node("node-001")
            assert node_info.public_key_hex == public_key_hex
            assert len(public_key_hex) == 64

        except ImportError:
            pytest.skip("cryptography library not available")

    def test_verify_node_before_signature_check(self):
        """Test node registry verification as prerequisite for signature verification."""
        registry = NodeRegistry()

        # Step 1: Verify node is trusted
        decision = registry.verify_node_trust("node-001")
        assert decision.is_trusted == False
        assert decision.error_code == NodeRegistryError.NODE_UNTRUSTED

        # Step 2: Register node
        registry.register_node("node-001", "a" * 64)

        # Step 3: Now node is trusted, can proceed to signature verification
        decision = registry.verify_node_trust("node-001")
        assert decision.is_trusted == True

        # In real flow, would now call verify_node_signature()
        # using public_key from registry


class TestConstants:
    """Tests for module constants."""

    def test_NODE_UNTRUSTED_ERROR(self):
        """Test NODE_UNTRUSTED_ERROR constant."""
        assert NODE_UNTRUSTED_ERROR == NodeRegistryError.NODE_UNTRUSTED

    def test_NODE_ID_PREFIX(self):
        """Test NODE_ID_PREFIX constant."""
        assert NODE_ID_PREFIX == "node-"


class TestErrorCodes:
    """Tests for error code enumeration."""

    def test_all_error_codes_defined(self):
        """Test that all expected error codes are defined."""
        codes = [
            "NODE_UNTRUSTED",
            "NODE_NOT_FOUND",
            "NODE_DISABLED",
            "NODE_EXPIRED",
            "INVALID_PUBLIC_KEY",
            "INVALID_NODE_ID",
            "REGISTRY_LOAD_ERROR",
            "REGISTRY_SAVE_ERROR",
        ]
        for code in codes:
            assert hasattr(NodeRegistryError, code)
