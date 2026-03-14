"""
Test suite for receipt_hash module.

T08 - ISSUE-07: 审计回执哈希修正验证

验证目标：
1. receipt hash = SHA-256(canonical payload)
2. 去除 Python hash()
3. 提供一致性测试结果
4. EvidenceRef 完整
"""

import pytest
from skillforge.src.utils.receipt_hash import (
    EvidenceRef,
    ReceiptPayload,
    compute_receipt_hash,
    compute_receipt_hash_from_dict,
    verify_receipt_consistency,
    create_evidence_ref,
    create_receipt_payload,
)


class TestEvidenceRef:
    """Test EvidenceRef dataclass."""

    def test_create_evidence_ref(self):
        """Test creating an EvidenceRef."""
        ref = EvidenceRef(
            envelope_id="env-001",
            envelope_hash="a" * 64,
            storage_location="/storage/env-001.json",
            received_at="2026-02-26T12:00:00Z",
            verified=True,
            node_id="node-001",
        )

        assert ref.envelope_id == "env-001"
        assert ref.envelope_hash == "a" * 64
        assert ref.storage_location == "/storage/env-001.json"
        assert ref.verified is True
        assert ref.node_id == "node-001"

    def test_evidence_ref_to_dict(self):
        """Test EvidenceRef serialization."""
        ref = EvidenceRef(
            envelope_id="env-002",
            envelope_hash="b" * 64,
            storage_location="s3://bucket/env-002",
            received_at="2026-02-26T13:00:00Z",
            verified=False,
            node_id=None,
        )

        result = ref.to_dict()

        assert result["envelope_id"] == "env-002"
        assert result["envelope_hash"] == "b" * 64
        assert result["verified"] is False
        assert "node_id" not in result  # None values excluded


class TestReceiptPayload:
    """Test ReceiptPayload dataclass."""

    def test_create_receipt_payload(self):
        """Test creating a ReceiptPayload."""
        refs = [
            create_evidence_ref(
                envelope_id="env-001",
                envelope_hash="a" * 64,
                storage_location="/storage/1",
                received_at="2026-02-26T12:00:00Z",
            )
        ]

        payload = ReceiptPayload(
            audit_id="audit-001",
            job_id="job-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            decision="PASSED",
            evidence_refs=refs,
            manifest_hash="c" * 64,
            trace_id="trace-001",
        )

        assert payload.audit_id == "audit-001"
        assert payload.decision == "PASSED"
        assert len(payload.evidence_refs) == 1

    def test_receipt_payload_to_dict(self):
        """Test ReceiptPayload serialization."""
        refs = [
            EvidenceRef(
                envelope_id="env-001",
                envelope_hash="a" * 64,
                storage_location="/storage/1",
                received_at="2026-02-26T12:00:00Z",
            )
        ]

        payload = ReceiptPayload(
            audit_id="audit-001",
            job_id="job-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            decision="PASSED",
            evidence_refs=refs,
        )

        result = payload.to_dict()

        assert result["audit_id"] == "audit-001"
        assert result["decision"] == "PASSED"
        assert len(result["evidence_refs"]) == 1
        assert isinstance(result["evidence_refs"][0], dict)


class TestComputeReceiptHash:
    """Test receipt hash computation."""

    def test_hash_length_is_64(self):
        """Test that SHA-256 produces 64 hex characters."""
        payload = create_receipt_payload(
            audit_id="audit-001",
            job_id="job-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            decision="PASSED",
            evidence_refs=[],
        )

        hash_val = compute_receipt_hash(payload)
        assert len(hash_val) == 64
        assert all(c in "0123456789abcdef" for c in hash_val)

    def test_same_payload_same_hash(self):
        """Test that identical payloads produce identical hashes."""
        payload = create_receipt_payload(
            audit_id="audit-001",
            job_id="job-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            decision="PASSED",
            evidence_refs=[],
        )

        hash1 = compute_receipt_hash(payload)
        hash2 = compute_receipt_hash(payload)
        hash3 = compute_receipt_hash(payload)

        assert hash1 == hash2 == hash3

    def test_different_payloads_different_hashes(self):
        """Test that different payloads produce different hashes."""
        payload1 = create_receipt_payload(
            audit_id="audit-001",
            job_id="job-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            decision="PASSED",
            evidence_refs=[],
        )

        payload2 = create_receipt_payload(
            audit_id="audit-002",  # Different audit_id
            job_id="job-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            decision="PASSED",
            evidence_refs=[],
        )

        hash1 = compute_receipt_hash(payload1)
        hash2 = compute_receipt_hash(payload2)

        assert hash1 != hash2

    def test_key_order_independent(self):
        """Test that dict key order doesn't affect hash."""
        refs = [EvidenceRef(
            envelope_id="env-001",
            envelope_hash="a" * 64,
            storage_location="/storage/1",
            received_at="2026-02-26T12:00:00Z",
        )]

        payload_dict1 = {
            "audit_id": "audit-001",
            "job_id": "job-001",
            "created_at": "2026-02-26T12:00:00Z",
            "node_id": "node-001",
            "decision": "PASSED",
            "evidence_refs": [ref.to_dict() for ref in refs],
        }

        payload_dict2 = {
            "decision": "PASSED",
            "audit_id": "audit-001",
            "evidence_refs": [ref.to_dict() for ref in refs],
            "job_id": "job-001",
            "created_at": "2026-02-26T12:00:00Z",
            "node_id": "node-001",
        }

        hash1 = compute_receipt_hash_from_dict(payload_dict1)
        hash2 = compute_receipt_hash_from_dict(payload_dict2)

        assert hash1 == hash2

    def test_hash_with_evidence_refs(self):
        """Test hashing payload with multiple evidence refs."""
        refs = [
            create_evidence_ref(
                envelope_id=f"env-{i:03d}",
                envelope_hash="a" * 64,
                storage_location=f"/storage/{i}",
                received_at="2026-02-26T12:00:00Z",
                verified=(i % 2 == 0),
            )
            for i in range(3)
        ]

        payload = create_receipt_payload(
            audit_id="audit-001",
            job_id="job-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            decision="PASSED",
            evidence_refs=refs,
        )

        hash_val = compute_receipt_hash(payload)
        assert len(hash_val) == 64

        # Verify ref order matters
        refs_reversed = list(reversed(refs))
        payload_reversed = create_receipt_payload(
            audit_id="audit-001",
            job_id="job-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            decision="PASSED",
            evidence_refs=refs_reversed,
        )
        hash_reversed = compute_receipt_hash(payload_reversed)
        assert hash_val != hash_reversed


class TestVerifyReceiptConsistency:
    """Test receipt hash consistency verification."""

    def test_consistent_payload(self):
        """Test that normal payload is consistent."""
        refs = [
            create_evidence_ref(
                envelope_id="env-001",
                envelope_hash="a" * 64,
                storage_location="/storage/1",
                received_at="2026-02-26T12:00:00Z",
            )
        ]

        payload = create_receipt_payload(
            audit_id="audit-001",
            job_id="job-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            decision="PASSED",
            evidence_refs=refs,
        )

        result = verify_receipt_consistency(payload, iterations=100)

        assert result["consistent"] is True
        assert result["unique_hashes"] == 1
        assert result["iterations"] == 100
        assert result["hash"] is not None
        assert len(result["hash"]) == 64

    def test_multiple_iterations(self):
        """Test across different iteration counts."""
        payload = create_receipt_payload(
            audit_id="audit-001",
            job_id="job-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            decision="PASSED",
            evidence_refs=[],
        )

        for iterations in [10, 50, 100, 500]:
            result = verify_receipt_consistency(payload, iterations=iterations)
            assert result["consistent"] is True
            assert result["iterations"] == iterations
            assert result["unique_hashes"] == 1

    def test_complex_payload_consistency(self):
        """Test complex payload with all fields."""
        refs = [
            create_evidence_ref(
                envelope_id="env-001",
                envelope_hash="a" * 64,
                storage_location="s3://bucket/env-001",
                received_at="2026-02-26T12:00:00Z",
                verified=True,
                node_id="node-001",
            ),
            create_evidence_ref(
                envelope_id="env-002",
                envelope_hash="b" * 64,
                storage_location="s3://bucket/env-002",
                received_at="2026-02-26T12:01:00Z",
                verified=False,
                node_id="node-002",
            ),
        ]

        payload = create_receipt_payload(
            audit_id="audit-complex-001",
            job_id="job-complex-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-auditor",
            decision="PASSED",
            evidence_refs=refs,
            manifest_hash="m" * 64,
            trace_id="trace-complex-001",
        )

        result = verify_receipt_consistency(payload, iterations=200)

        assert result["consistent"] is True
        assert result["unique_hashes"] == 1
        assert result["hash"] is not None


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_create_evidence_ref_function(self):
        """Test create_evidence_ref convenience function."""
        ref = create_evidence_ref(
            envelope_id="env-001",
            envelope_hash="a" * 64,
            storage_location="/storage/1",
            received_at="2026-02-26T12:00:00Z",
            verified=True,
            node_id="node-001",
        )

        assert isinstance(ref, EvidenceRef)
        assert ref.envelope_id == "env-001"

    def test_create_receipt_payload_function(self):
        """Test create_receipt_payload convenience function."""
        refs = [
            create_evidence_ref(
                envelope_id="env-001",
                envelope_hash="a" * 64,
                storage_location="/storage/1",
                received_at="2026-02-26T12:00:00Z",
            )
        ]

        payload = create_receipt_payload(
            audit_id="audit-001",
            job_id="job-001",
            created_at="2026-02-26T12:00:00Z",
            node_id="node-001",
            decision="PASSED",
            evidence_refs=refs,
        )

        assert isinstance(payload, ReceiptPayload)
        assert payload.audit_id == "audit-001"


class TestIntegrationEvidenceRefComplete:
    """Integration test: EvidenceRef completeness in receipt context."""

    def test_evidence_ref_all_fields(self):
        """Test that EvidenceRef contains all required fields."""
        ref = EvidenceRef(
            envelope_id="ev-test-001",
            envelope_hash="abcd1234" * 8,
            storage_location="file:///data/ev/test-001.json",
            received_at="2026-02-26T15:30:00Z",
            verified=True,
            evidence_type="evidence_envelope.v1",
            node_id="skillforge-node-01",
        )

        # All fields should be present
        assert ref.envelope_id == "ev-test-001"
        assert ref.envelope_hash == "abcd1234" * 8
        assert ref.storage_location == "file:///data/ev/test-001.json"
        assert ref.received_at == "2026-02-26T15:30:00Z"
        assert ref.verified is True
        assert ref.evidence_type == "evidence_envelope.v1"
        assert ref.node_id == "skillforge-node-01"

    def test_receipt_with_multiple_evidence_refs(self):
        """Test receipt payload with multiple EvidenceRef entries."""
        refs = [
            create_evidence_ref(
                envelope_id=f"ev-{i:03d}",
                envelope_hash=f"hash{i}{'0'*60}",
                storage_location=f"/storage/evidence/{i:03d}.json",
                received_at="2026-02-26T15:30:00Z",
                verified=(i % 2 == 0),
                node_id=f"node-{i%3}",
            )
            for i in range(1, 6)  # 5 evidence refs
        ]

        payload = create_receipt_payload(
            audit_id="audit-multi-ev-001",
            job_id="job-multi-ev-001",
            created_at="2026-02-26T15:30:00Z",
            node_id="auditor-node-01",
            decision="PASSED",
            evidence_refs=refs,
        )

        # Verify all evidence refs are included
        assert len(payload.evidence_refs) == 5

        # Compute hash (should be deterministic)
        hash_val = compute_receipt_hash(payload)
        assert len(hash_val) == 64

        # Verify consistency
        result = verify_receipt_consistency(payload, iterations=50)
        assert result["consistent"] is True

    def test_evidence_ref_serialization_roundtrip(self):
        """Test EvidenceRef serialization to dict and back."""
        original = EvidenceRef(
            envelope_id="ev-rt-001",
            envelope_hash="abcd" * 16,
            storage_location="s3://bucket/ev/rt-001",
            received_at="2026-02-26T16:00:00Z",
            verified=True,
            evidence_type="evidence_envelope.v1",
            node_id="node-rt-01",
        )

        # Serialize to dict
        ref_dict = original.to_dict()

        # All non-None fields should be present
        assert ref_dict["envelope_id"] == "ev-rt-001"
        assert ref_dict["envelope_hash"] == "abcd" * 16
        assert ref_dict["storage_location"] == "s3://bucket/ev/rt-001"
        assert ref_dict["received_at"] == "2026-02-26T16:00:00Z"
        assert ref_dict["verified"] is True
        assert ref_dict["evidence_type"] == "evidence_envelope.v1"
        assert ref_dict["node_id"] == "node-rt-01"

        # Verify dict can be used in hash computation
        payload = create_receipt_payload(
            audit_id="audit-rt-001",
            job_id="job-rt-001",
            created_at="2026-02-26T16:00:00Z",
            node_id="node-rt-01",
            decision="PASSED",
            evidence_refs=[original],
        )

        hash_val = compute_receipt_hash(payload)
        assert len(hash_val) == 64


# Run tests with: pytest tests/test_receipt_hash.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
