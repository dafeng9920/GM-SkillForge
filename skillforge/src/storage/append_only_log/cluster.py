"""
Log Cluster Module for Append-Only Log.

Implements minimal cluster infrastructure for:
- High availability
- Data replication
- Consensus-based writes

Cluster size: 3 nodes (minimum for quorum)
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class NodeRole(str, Enum):
    """Node roles in the cluster."""
    LEADER = "leader"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"


class NodeStatus(str, Enum):
    """Node health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"


@dataclass
class ClusterConfig:
    """
    Configuration for the log cluster.

    Minimum viable cluster: 3 nodes
    - Supports 1 node failure with full operation
    - Supports 2 node failures in read-only mode
    """
    cluster_id: str
    cluster_name: str

    # Replication settings
    replication_factor: int = 3
    write_quorum: int = 2  # Majority for 3 nodes
    read_quorum: int = 2

    # Timeout settings (milliseconds)
    election_timeout_ms: int = 5000
    heartbeat_interval_ms: int = 1000
    write_timeout_ms: int = 10000

    # Consistency settings
    require_quorum_for_write: bool = True
    allow_stale_reads: bool = False

    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def minimal_cluster(cls, cluster_id: str = "cluster-minimal") -> "ClusterConfig":
        """Create minimal 3-node cluster configuration."""
        return cls(
            cluster_id=cluster_id,
            cluster_name="Minimal Append-Only Log Cluster",
            replication_factor=3,
            write_quorum=2,
            read_quorum=2,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize config to dictionary."""
        return {
            "cluster_id": self.cluster_id,
            "cluster_name": self.cluster_name,
            "replication_factor": self.replication_factor,
            "write_quorum": self.write_quorum,
            "read_quorum": self.read_quorum,
            "election_timeout_ms": self.election_timeout_ms,
            "heartbeat_interval_ms": self.heartbeat_interval_ms,
            "write_timeout_ms": self.write_timeout_ms,
            "require_quorum_for_write": self.require_quorum_for_write,
            "allow_stale_reads": self.allow_stale_reads,
            "metadata": self.metadata,
        }


@dataclass
class NodeInfo:
    """Information about a cluster node."""
    node_id: str
    node_url: str
    role: NodeRole
    status: NodeStatus
    last_heartbeat: str
    sequence_no: int = 0
    term: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize node info to dictionary."""
        return {
            "node_id": self.node_id,
            "node_url": self.node_url,
            "role": self.role.value,
            "status": self.status.value,
            "last_heartbeat": self.last_heartbeat,
            "sequence_no": self.sequence_no,
            "term": self.term,
            "metadata": self.metadata,
        }


class LogCluster:
    """
    Minimal cluster implementation for append-only log.

    Features:
    - Leader election (simplified Raft-style)
    - Write replication
    - Quorum-based consistency
    - Health monitoring

    Note: This is a MINIMAL implementation for the initial deployment.
    Production clusters should use etcd, Consul, or similar proven systems.
    """

    def __init__(self, config: ClusterConfig, node_id: str, db_path: str | Path):
        """
        Initialize cluster node.

        Args:
            config: Cluster configuration
            node_id: This node's ID
            db_path: Path to local log database
        """
        self.config = config
        self.node_id = node_id
        self.db_path = Path(db_path)

        self._nodes: dict[str, NodeInfo] = {}
        self._current_term = 0
        self._current_role = NodeRole.FOLLOWER
        self._leader_id: str | None = None

        # Register self
        self._nodes[node_id] = NodeInfo(
            node_id=node_id,
            node_url=f"local://{db_path}",
            role=NodeRole.FOLLOWER,
            status=NodeStatus.HEALTHY,
            last_heartbeat=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    @property
    def is_leader(self) -> bool:
        """Check if this node is the leader."""
        return self._current_role == NodeRole.LEADER

    @property
    def current_leader(self) -> str | None:
        """Get the current leader node ID."""
        return self._leader_id

    @property
    def nodes(self) -> dict[str, NodeInfo]:
        """Get all registered nodes."""
        return self._nodes.copy()

    def register_node(
        self,
        node_id: str,
        node_url: str,
        metadata: dict[str, Any] | None = None,
    ) -> NodeInfo:
        """Register a new node in the cluster."""
        node = NodeInfo(
            node_id=node_id,
            node_url=node_url,
            role=NodeRole.FOLLOWER,
            status=NodeStatus.UNKNOWN,
            last_heartbeat="",
            metadata=metadata or {},
        )
        self._nodes[node_id] = node
        return node

    def update_node_status(
        self,
        node_id: str,
        status: NodeStatus,
        sequence_no: int | None = None,
    ) -> None:
        """Update a node's status."""
        if node_id in self._nodes:
            self._nodes[node_id].status = status
            self._nodes[node_id].last_heartbeat = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            )
            if sequence_no is not None:
                self._nodes[node_id].sequence_no = sequence_no

    def start_election(self) -> bool:
        """
        Start a leader election.

        Returns True if this node becomes leader.
        """
        self._current_role = NodeRole.CANDIDATE
        self._current_term += 1

        # Count votes (simplified: all healthy nodes vote for self)
        healthy_count = sum(
            1 for n in self._nodes.values()
            if n.status == NodeStatus.HEALTHY
        )

        votes_needed = (len(self._nodes) // 2) + 1

        if healthy_count >= votes_needed:
            self._current_role = NodeRole.LEADER
            self._leader_id = self.node_id
            return True

        # Election failed
        self._current_role = NodeRole.FOLLOWER
        return False

    def check_quorum(self) -> bool:
        """Check if quorum is available for writes."""
        healthy_count = sum(
            1 for n in self._nodes.values()
            if n.status in (NodeStatus.HEALTHY, NodeStatus.DEGRADED)
        )
        return healthy_count >= self.config.write_quorum

    def get_cluster_status(self) -> dict[str, Any]:
        """Get overall cluster status."""
        nodes_status = {
            node_id: {
                "status": node.status.value,
                "role": node.role.value,
                "sequence_no": node.sequence_no,
            }
            for node_id, node in self._nodes.items()
        }

        healthy_count = sum(
            1 for n in self._nodes.values()
            if n.status == NodeStatus.HEALTHY
        )

        return {
            "cluster_id": self.config.cluster_id,
            "cluster_name": self.config.cluster_name,
            "current_term": self._current_term,
            "leader_id": self._leader_id,
            "self_node_id": self.node_id,
            "self_role": self._current_role.value,
            "is_quorum_available": self.check_quorum(),
            "total_nodes": len(self._nodes),
            "healthy_nodes": healthy_count,
            "nodes": nodes_status,
            "config": self.config.to_dict(),
        }

    def can_accept_write(self) -> tuple[bool, str]:
        """
        Check if this node can accept a write.

        Returns:
            Tuple of (can_write, reason)
        """
        if not self.is_leader:
            return False, f"Not leader (leader is {self._leader_id})"

        if not self.check_quorum():
            return False, "Quorum not available"

        return True, "OK"

    def replicate_write(
        self,
        entry_hash: str,
        sequence_no: int,
    ) -> tuple[bool, int]:
        """
        Simulate write replication to quorum nodes.

        Returns:
            Tuple of (success, replication_count)
        """
        if not self.is_leader:
            return False, 0

        successful_replicas = 1  # Leader counts

        for node_id, node in self._nodes.items():
            if node_id == self.node_id:
                continue

            if node.status in (NodeStatus.HEALTHY, NodeStatus.DEGRADED):
                # Simulate replication
                node.sequence_no = sequence_no
                successful_replicas += 1

        if successful_replicas >= self.config.write_quorum:
            return True, successful_replicas

        return False, successful_replicas

    def get_cluster_health(self) -> dict[str, Any]:
        """Get cluster health summary."""
        healthy = sum(1 for n in self._nodes.values() if n.status == NodeStatus.HEALTHY)
        degraded = sum(1 for n in self._nodes.values() if n.status == NodeStatus.DEGRADED)
        unreachable = sum(1 for n in self._nodes.values() if n.status == NodeStatus.UNREACHABLE)

        if unreachable > 1:
            health_status = "critical"
        elif unreachable == 1:
            health_status = "degraded"
        else:
            health_status = "healthy"

        return {
            "status": health_status,
            "total_nodes": len(self._nodes),
            "healthy": healthy,
            "degraded": degraded,
            "unreachable": unreachable,
            "quorum_available": self.check_quorum(),
            "can_accept_writes": self.is_leader and self.check_quorum(),
        }
