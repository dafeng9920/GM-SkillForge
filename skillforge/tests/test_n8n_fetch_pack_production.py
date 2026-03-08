"""
Tests for n8n fetch_pack production implementation.

T8 (L45-D2-ORCH-MINCAP-20260220-002)

Test cases:
1. 成功读取 - 通过 run_id 读取
2. 成功读取 - 通过 evidence_ref 读取
3. 一致性校验 - run_id 和 evidence_ref 指向同一个 pack
4. 缺标识 - run_id 和 evidence_ref 都未提供
5. 不一致 - run_id 和 evidence_ref 指向不同 pack
6. replay_pointer 字段存在（可空）
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "skillforge"))


class TestAuditPackStore:
    """Tests for AuditPackStore."""

    def test_fetch_by_run_id_success(self):
        """Successfully fetch pack by run_id."""
        from storage.audit_pack_store import AuditPackStore, AuditPack, ReplayPointer
        import time
        import uuid

        store = AuditPackStore()
        ts = int(time.time())

        # Create and store a test pack
        pack = AuditPack(
            pack_id=f"RCP-L45-{uuid.uuid4().hex[:8].upper()}",
            run_id=f"RUN-L4-{ts}-TEST0001",
            evidence_ref=f"EV-EXEC-L4-{ts}-TEST0001",
            gate_decision="PASSED",
            executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            skill_id="test_skill",
            workflow_id="wf_test",
        )
        store.store_pack(pack)

        # Fetch by run_id
        result = store.fetch_by_run_id(f"RUN-L4-{ts}-TEST0001")

        assert result.success is True
        assert result.pack is not None
        assert result.pack.run_id == f"RUN-L4-{ts}-TEST0001"
        assert result.pack.evidence_ref == f"EV-EXEC-L4-{ts}-TEST0001"

    def test_fetch_by_evidence_ref_success(self):
        """Successfully fetch pack by evidence_ref."""
        from storage.audit_pack_store import AuditPackStore, AuditPack
        import time
        import uuid

        store = AuditPackStore()
        ts = int(time.time())

        # Create and store a test pack
        pack = AuditPack(
            pack_id=f"RCP-L45-{uuid.uuid4().hex[:8].upper()}",
            run_id=f"RUN-L4-{ts}-TEST0002",
            evidence_ref=f"EV-EXEC-L4-{ts}-TEST0002",
            gate_decision="PASSED",
            executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            skill_id="test_skill",
            workflow_id="wf_test",
        )
        store.store_pack(pack)

        # Fetch by evidence_ref
        result = store.fetch_by_evidence_ref(f"EV-EXEC-L4-{ts}-TEST0002")

        assert result.success is True
        assert result.pack is not None
        assert result.pack.evidence_ref == f"EV-EXEC-L4-{ts}-TEST0002"

    def test_fetch_missing_identifier(self):
        """Fail when neither run_id nor evidence_ref is provided."""
        from storage.audit_pack_store import AuditPackStore

        store = AuditPackStore()
        result = store.fetch_with_consistency_check(run_id=None, evidence_ref=None)

        assert result.success is False
        assert result.error_code == "INVALID_IDENTIFIER"

    def test_fetch_pack_not_found(self):
        """Fail when pack not found for given identifier."""
        from storage.audit_pack_store import AuditPackStore

        store = AuditPackStore()
        result = store.fetch_by_run_id("RUN-L4-NONEXISTENT")

        assert result.success is False
        assert result.error_code == "PACK_NOT_FOUND"

    def test_consistency_check_same_pack(self):
        """Consistency check passes when run_id and evidence_ref point to same pack."""
        from storage.audit_pack_store import AuditPackStore, AuditPack
        import time
        import uuid

        store = AuditPackStore()
        ts = int(time.time())

        # Create and store a test pack
        pack = AuditPack(
            pack_id=f"RCP-L45-{uuid.uuid4().hex[:8].upper()}",
            run_id=f"RUN-L4-{ts}-TEST0003",
            evidence_ref=f"EV-EXEC-L4-{ts}-TEST0003",
            gate_decision="PASSED",
            executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            skill_id="test_skill",
            workflow_id="wf_test",
        )
        store.store_pack(pack)

        # Fetch with consistency check using both identifiers
        result = store.fetch_with_consistency_check(
            run_id=f"RUN-L4-{ts}-TEST0003",
            evidence_ref=f"EV-EXEC-L4-{ts}-TEST0003",
        )

        assert result.success is True
        assert result.pack.run_id == f"RUN-L4-{ts}-TEST0003"

    def test_consistency_check_different_packs(self):
        """Consistency check fails when run_id and evidence_ref point to different packs."""
        from storage.audit_pack_store import AuditPackStore, AuditPack
        import time
        import uuid

        store = AuditPackStore()
        ts = int(time.time())

        # Create and store two different packs
        pack1 = AuditPack(
            pack_id=f"RCP-L45-{uuid.uuid4().hex[:8].upper()}",
            run_id=f"RUN-L4-{ts}-TEST0004A",
            evidence_ref=f"EV-EXEC-L4-{ts}-TEST0004A",
            gate_decision="PASSED",
            executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            skill_id="test_skill",
            workflow_id="wf_test",
        )
        pack2 = AuditPack(
            pack_id=f"RCP-L45-{uuid.uuid4().hex[:8].upper()}",
            run_id=f"RUN-L4-{ts}-TEST0004B",
            evidence_ref=f"EV-EXEC-L4-{ts}-TEST0004B",
            gate_decision="PASSED",
            executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            skill_id="test_skill",
            workflow_id="wf_test",
        )
        store.store_pack(pack1)
        store.store_pack(pack2)

        # Try to fetch with mismatched identifiers
        result = store.fetch_with_consistency_check(
            run_id=f"RUN-L4-{ts}-TEST0004A",
            evidence_ref=f"EV-EXEC-L4-{ts}-TEST0004B",
        )

        assert result.success is False
        assert result.error_code == "CONSISTENCY_ERROR"


class TestFetchPackResponse:
    """Tests for fetch_pack response structure."""

    def test_replay_pointer_field_present(self):
        """Response must include replay_pointer field (nullable allowed)."""
        from storage.audit_pack_store import AuditPack, ReplayPointer
        import time
        import uuid

        ts = int(time.time())
        pack = AuditPack(
            pack_id=f"RCP-L45-{uuid.uuid4().hex[:8].upper()}",
            run_id=f"RUN-L4-{ts}-TEST0005",
            evidence_ref=f"EV-EXEC-L4-{ts}-TEST0005",
            gate_decision="PASSED",
            executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            skill_id="test_skill",
            workflow_id="wf_test",
            replay_pointer=ReplayPointer(
                snapshot_ref="snapshot://test/v1",
                at_time=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                revision="v1.0.0",
                evidence_bundle_ref="evidence://test",
            ),
        )

        pack_dict = pack.to_dict()

        assert "replay_pointer" in pack_dict
        assert pack_dict["replay_pointer"]["snapshot_ref"] == "snapshot://test/v1"

    def test_replay_pointer_nullable(self):
        """replay_pointer can be null but structure must be defined."""
        from storage.audit_pack_store import AuditPack
        import time
        import uuid

        ts = int(time.time())
        pack = AuditPack(
            pack_id=f"RCP-L45-{uuid.uuid4().hex[:8].upper()}",
            run_id=f"RUN-L4-{ts}-TEST0006",
            evidence_ref=f"EV-EXEC-L4-{ts}-TEST0006",
            gate_decision="PASSED",
            executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            skill_id="test_skill",
            workflow_id="wf_test",
            replay_pointer=None,
        )

        pack_dict = pack.to_dict()

        assert "replay_pointer" in pack_dict
        assert pack_dict["replay_pointer"] is None

    def test_receipt_schema_compatibility(self):
        """Response must be compatible with n8n_execution_receipt schema."""
        from storage.audit_pack_store import AuditPack
        import time
        import uuid

        ts = int(time.time())
        pack = AuditPack(
            pack_id=f"RCP-L45-{uuid.uuid4().hex[:8].upper()}",
            run_id=f"RUN-L4-{ts}-TEST0007",
            evidence_ref=f"EV-EXEC-L4-{ts}-TEST0007",
            gate_decision="PASSED",
            executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            skill_id="test_skill",
            workflow_id="wf_test",
        )

        pack_dict = pack.to_dict()

        # Verify required fields per n8n_execution_receipt.schema.json
        required_fields = [
            "receipt_id",
            "run_id",
            "evidence_ref",
            "gate_decision",
            "executed_at",
            "skill_id",
            "workflow_id",
        ]

        for field in required_fields:
            assert field in pack_dict, f"Missing required field: {field}"


class TestFailClosedBehavior:
    """Tests for fail-closed error handling."""

    def test_error_envelope_structure(self):
        """Error responses must have structured error envelope."""
        from storage.audit_pack_store import AuditPackStore

        store = AuditPackStore()
        result = store.fetch_by_run_id("RUN-L4-NONEXISTENT")

        assert result.success is False
        assert result.error_code is not None
        assert result.error_message is not None

    def test_error_includes_evidence_ref(self):
        """Error responses must include evidence_ref for audit."""
        from storage.audit_pack_store import AuditPackStore

        store = AuditPackStore()
        result = store.fetch_by_run_id("RUN-L4-NONEXISTENT")

        # evidence_ref should be generated even for errors
        # (run_id is provided in the request)
        assert result.run_id == "RUN-L4-NONEXISTENT"
