"""
Test suite for canonical_json module.

T02 - ISSUE-01: Canonical JSON 一致性验证
"""

import pytest
from skillforge.src.utils.canonical_json import (
    canonical_json,
    canonical_json_hash,
    verify_canonical_consistency
)


class TestCanonicalJson:
    """Test canonical_json function."""

    def test_key_order_consistency(self):
        """Test that key order doesn't affect output."""
        obj1 = {"b": 2, "a": 1, "c": 3}
        obj2 = {"c": 3, "a": 1, "b": 2}
        obj3 = {"a": 1, "b": 2, "c": 3}

        result1 = canonical_json(obj1)
        result2 = canonical_json(obj2)
        result3 = canonical_json(obj3)

        assert result1 == result2 == result3
        assert result1 == '{"a":1,"b":2,"c":3}'

    def test_nested_dict_consistency(self):
        """Test nested dictionaries."""
        obj1 = {"outer": {"inner_b": 2, "inner_a": 1}}
        obj2 = {"outer": {"inner_a": 1, "inner_b": 2}}

        assert canonical_json(obj1) == canonical_json(obj2)

    def test_list_consistency(self):
        """Test that list order is preserved."""
        obj = {"items": [3, 1, 2]}
        result = canonical_json(obj)
        assert result == '{"items":[3,1,2]}'

    def test_multiple_runs_same_result(self):
        """Test that 100 runs produce identical results."""
        obj = {
            "name": "test",
            "values": [1, 2, 3],
            "nested": {"z": 9, "a": 1}
        }

        results = [canonical_json(obj) for _ in range(100)]
        assert len(set(results)) == 1  # All identical

    def test_special_characters(self):
        """Test Unicode handling."""
        obj = {"message": "你好世界"}
        result = canonical_json(obj)
        assert "你好世界" in result

    def test_null_value(self):
        """Test null value handling."""
        obj = {"value": None}
        result = canonical_json(obj)
        assert result == '{"value":null}'

    def test_boolean_values(self):
        """Test boolean handling."""
        obj = {"flag_true": True, "flag_false": False}
        result = canonical_json(obj)
        assert result == '{"flag_false":false,"flag_true":true}'

    def test_numeric_values(self):
        """Test numeric value handling."""
        obj = {"int": 42, "float": 3.14, "negative": -10}
        result = canonical_json(obj)
        # Keys should be sorted
        assert '"float":3.14' in result
        assert '"int":42' in result
        assert '"negative":-10' in result

    def test_complex_nested_structure(self):
        """Test complex nested structure."""
        obj = {
            "level1": {
                "level2": {
                    "level3": [{"z": 1}, {"a": 2}]
                }
            }
        }
        result = canonical_json(obj)
        # Should be deterministic
        assert canonical_json(obj) == result


class TestCanonicalJsonHash:
    """Test canonical_json_hash function."""

    def test_same_object_same_hash(self):
        """Test that same object always produces same hash."""
        obj = {"data": "test", "number": 123}

        hash1 = canonical_json_hash(obj)
        hash2 = canonical_json_hash(obj)
        hash3 = canonical_json_hash(obj)

        assert hash1 == hash2 == hash3

    def test_key_order_independent_hash(self):
        """Test that key order doesn't affect hash."""
        obj1 = {"b": 2, "a": 1}
        obj2 = {"a": 1, "b": 2}

        assert canonical_json_hash(obj1) == canonical_json_hash(obj2)

    def test_hash_length_sha256(self):
        """Test SHA-256 hash length."""
        obj = {"test": "value"}
        hash_val = canonical_json_hash(obj, algorithm="sha256")
        assert len(hash_val) == 64  # SHA-256 produces 64 hex chars

    def test_different_objects_different_hash(self):
        """Test that different objects produce different hashes."""
        obj1 = {"value": 1}
        obj2 = {"value": 2}

        assert canonical_json_hash(obj1) != canonical_json_hash(obj2)

    def test_multiple_iterations_consistency(self):
        """Test hash consistency across 100 iterations."""
        obj = {"key": "value", "nested": {"a": 1}}

        hashes = [canonical_json_hash(obj) for _ in range(100)]
        assert len(set(hashes)) == 1  # All identical


class TestVerifyCanonicalConsistency:
    """Test verify_canonical_consistency function."""

    def test_consistent_object(self):
        """Test that a normal object is consistent."""
        obj = {"test": [1, 2, 3], "name": "example"}
        result = verify_canonical_consistency(obj, iterations=100)

        assert result["consistent"] is True
        assert result["unique_hashes"] == 1
        assert result["unique_json_strings"] == 1

    def test_complex_object_consistency(self):
        """Test complex nested object."""
        obj = {
            "header": {
                "version": "1.0",
                "timestamp": "2026-02-26T12:00:00Z"
            },
            "data": [
                {"id": 1, "value": "a"},
                {"id": 2, "value": "b"}
            ],
            "metadata": {
                "source": "test",
                "count": 100
            }
        }

        result = verify_canonical_consistency(obj, iterations=50)
        assert result["consistent"] is True

    def test_returns_hash_and_json(self):
        """Test that function returns hash and json."""
        obj = {"simple": "test"}
        result = verify_canonical_consistency(obj)

        assert result["hash"] is not None
        assert result["json"] is not None
        assert result["hash"] == canonical_json_hash(obj)
        assert result["json"] == canonical_json(obj)


class TestEvidenceEnvelopeUseCase:
    """Test use case: Evidence Envelope canonicalization."""

    def test_evidence_envelope_consistency(self):
        """Test that evidence envelope produces consistent hash."""
        envelope = {
            "schema": "gm.evidence.envelope.v1",
            "header": {
                "packet_id": "EVP_01J2TEST",
                "node_id": "GM-NODE-0001",
                "skill_id": "skill-test",
                "issued_at": "2026-02-26T12:00:00Z",
                "nonce": "N_TEST_001"
            },
            "ciphertext": {
                "ct": "base64encoded",
                "tag": "base64tag"
            },
            "signature": {
                "sig": "base64signature",
                "signed_fields": ["header", "ciphertext"]
            }
        }

        # Verify consistency
        result = verify_canonical_consistency(envelope, iterations=100)
        assert result["consistent"] is True

        # Hash should be stable
        hash1 = canonical_json_hash(envelope)
        hash2 = canonical_json_hash(envelope)
        assert hash1 == hash2

    def test_signing_fields_hash(self):
        """Test hashing specific fields for signature."""
        header = {
            "packet_id": "EVP_001",
            "node_id": "NODE_001",
            "issued_at": "2026-02-26T12:00:00Z"
        }

        ciphertext = {
            "ct": "encrypted_data",
            "tag": "auth_tag"
        }

        # Hash individual components
        header_hash = canonical_json_hash(header)
        ciphertext_hash = canonical_json_hash(ciphertext)

        # Combined hash
        combined = {
            "header_hash": header_hash,
            "ciphertext_hash": ciphertext_hash
        }
        combined_hash = canonical_json_hash(combined)

        assert len(header_hash) == 64
        assert len(ciphertext_hash) == 64
        assert len(combined_hash) == 64


# Run tests with: pytest tests/test_canonical_json.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
