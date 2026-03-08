"""
Tests for Provenance Loader - SEEDS-P1-9 Repro Env 指纹占位测试

测试覆盖：
1. provenance 模板加载
2. repro_env 字段存在性
3. GateDecision 注入
4. 读取失败 fail-closed

Contract: docs/SEEDS_v0.md P1-9
Job ID: L45-D5-SEEDS-P1-20260220-005
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from contracts.governance.provenance_loader import (
    ProvenanceLoader,
    ProvenanceData,
    ProvenanceSource,
    ReproEnv,
    ProvenanceLoadError,
    load_provenance,
    get_repro_env,
    get_full_provenance,
    inject_provenance_to_gate_decision,
    create_provenance_for_job,
    reset_loader,
    DENY_ERROR_CODE,
)


# ============================================================================
# Test Constants
# ============================================================================

JOB_ID = "L45-D5-SEEDS-P1-20260220-005"
SKILL_ID = "l45_seeds_p1_guardrails"


# ============================================================================
# Test Cases - ReproEnv
# ============================================================================

class TestReproEnv(unittest.TestCase):
    """ReproEnv 数据结构测试。"""

    def test_repro_env_default_values(self):
        """Test 1: ReproEnv 默认值。"""
        print("\n=== Test 1: ReproEnv Default Values ===")

        repro_env = ReproEnv()

        self.assertIsNotNone(repro_env.python_version)
        self.assertEqual(repro_env.deps_lock_hash, "PLACEHOLDER")
        self.assertEqual(repro_env.os, "PLACEHOLDER")
        self.assertIn("gm_skillforge", repro_env.tool_versions)

        print(f"  python_version: {repro_env.python_version}")
        print(f"  deps_lock_hash: {repro_env.deps_lock_hash}")
        print(f"  os: {repro_env.os}")
        print(f"  tool_versions: {repro_env.tool_versions}")

    def test_repro_env_to_dict(self):
        """Test 2: ReproEnv 序列化为字典。"""
        print("\n=== Test 2: ReproEnv To Dict ===")

        repro_env = ReproEnv(
            python_version="3.11",
            deps_lock_hash="abc123",
            os="Windows 11",
            tool_versions={"gm_skillforge": "0.0.1"},
        )

        data = repro_env.to_dict()

        self.assertEqual(data["python_version"], "3.11")
        self.assertEqual(data["deps_lock_hash"], "abc123")
        self.assertEqual(data["os"], "Windows 11")
        self.assertEqual(data["tool_versions"]["gm_skillforge"], "0.0.1")

        print(f"  Serialized: {json.dumps(data, indent=2)}")

    def test_repro_env_from_dict(self):
        """Test 3: ReproEnv 从字典反序列化。"""
        print("\n=== Test 3: ReproEnv From Dict ===")

        data = {
            "python_version": "3.10",
            "deps_lock_hash": "def456",
            "os": "Linux",
            "tool_versions": {"gm_skillforge": "0.0.2"},
        }

        repro_env = ReproEnv.from_dict(data)

        self.assertEqual(repro_env.python_version, "3.10")
        self.assertEqual(repro_env.deps_lock_hash, "def456")
        self.assertEqual(repro_env.os, "Linux")
        self.assertEqual(repro_env.tool_versions["gm_skillforge"], "0.0.2")

        print(f"  Deserialized: python={repro_env.python_version}, os={repro_env.os}")


# ============================================================================
# Test Cases - ProvenanceData
# ============================================================================

class TestProvenanceData(unittest.TestCase):
    """ProvenanceData 完整数据结构测试。"""

    def test_provenance_data_structure(self):
        """Test 4: ProvenanceData 完整结构。"""
        print("\n=== Test 4: ProvenanceData Structure ===")

        provenance = ProvenanceData(
            captured_at="2026-02-20T12:00:00Z",
            source=ProvenanceSource(
                repo_url="https://github.com/test/repo",
                commit_sha="abc123",
            ),
            ruleset_revision="v1",
            repro_env=ReproEnv(
                python_version="3.11",
                deps_lock_hash="hash123",
                os="Windows 11",
                tool_versions={"gm_skillforge": "0.0.1"},
            ),
        )

        # Verify all required fields exist
        self.assertEqual(provenance.captured_at, "2026-02-20T12:00:00Z")
        self.assertEqual(provenance.source.repo_url, "https://github.com/test/repo")
        self.assertEqual(provenance.ruleset_revision, "v1")
        self.assertIsNotNone(provenance.repro_env)

        print(f"  captured_at: {provenance.captured_at}")
        print(f"  source.repo_url: {provenance.source.repo_url}")
        print(f"  ruleset_revision: {provenance.ruleset_revision}")
        print(f"  repro_env.os: {provenance.repro_env.os}")

    def test_provenance_data_to_dict(self):
        """Test 5: ProvenanceData 序列化。"""
        print("\n=== Test 5: ProvenanceData To Dict ===")

        provenance = ProvenanceData(
            captured_at="2026-02-20T12:00:00Z",
            source=ProvenanceSource(repo_url="https://github.com/test/repo", commit_sha="abc123"),
            ruleset_revision="v1",
            repro_env=ReproEnv(),
        )

        data = provenance.to_dict()

        # Verify structure matches SEEDS_v0.md template
        self.assertIn("captured_at", data)
        self.assertIn("source", data)
        self.assertIn("ruleset_revision", data)
        self.assertIn("repro_env", data)

        # Verify repro_env has required fields
        repro_env = data["repro_env"]
        self.assertIn("python_version", repro_env)
        self.assertIn("deps_lock_hash", repro_env)
        self.assertIn("os", repro_env)
        self.assertIn("tool_versions", repro_env)

        print(f"  Full structure: {json.dumps(data, indent=2)}")


# ============================================================================
# Test Cases - ProvenanceLoader
# ============================================================================

class TestProvenanceLoader(unittest.TestCase):
    """ProvenanceLoader 核心功能测试。"""

    def setUp(self):
        """Set up test fixtures."""
        reset_loader()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        reset_loader()
        import shutil
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_loader_with_template(self):
        """Test 6: Loader 从模板加载。"""
        print("\n=== Test 6: Loader With Template ===")

        # Create a test template
        template_path = Path(self.temp_dir) / "provenance.json"
        template_data = {
            "captured_at": "2026-02-20T00:00:00Z",
            "source": {"repo_url": "REPO_URL", "commit_sha": "COMMIT_SHA"},
            "ruleset_revision": "v1",
            "repro_env": {
                "python_version": "3.11",
                "deps_lock_hash": "LOCKHASH-PLACEHOLDER",
                "os": "OS-PLACEHOLDER",
                "tool_versions": {"gm_skillforge": "0.0.1"},
            },
        }

        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(template_data, f)

        loader = ProvenanceLoader(template_path=template_path)
        provenance = loader.load()

        self.assertEqual(provenance.ruleset_revision, "v1")
        self.assertEqual(provenance.repro_env.python_version, "3.11")

        print(f"  Loaded ruleset_revision: {provenance.ruleset_revision}")
        print(f"  Loaded repro_env.os: {provenance.repro_env.os}")

    def test_loader_without_template(self):
        """Test 7: Loader 无模板时从当前环境创建。"""
        print("\n=== Test 7: Loader Without Template ===")

        loader = ProvenanceLoader(template_path=None)
        provenance = loader.load()

        # Should have been created from current environment
        self.assertIsNotNone(provenance.captured_at)
        self.assertIsNotNone(provenance.repro_env.python_version)

        print(f"  Created captured_at: {provenance.captured_at}")
        print(f"  Created repro_env.python_version: {provenance.repro_env.python_version}")

    def test_loader_fail_closed_invalid_json(self):
        """Test 8: Loader 读取失败必须 fail-closed（无效 JSON）。"""
        print("\n=== Test 8: Loader Fail-Closed Invalid JSON ===")

        # Create an invalid JSON file
        template_path = Path(self.temp_dir) / "invalid_provenance.json"
        with open(template_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        loader = ProvenanceLoader(template_path=template_path)

        with self.assertRaises(ProvenanceLoadError) as context:
            loader.load()

        self.assertEqual(context.exception.code, DENY_ERROR_CODE)
        print(f"  Raised ProvenanceLoadError with code: {context.exception.code}")
        print(f"  Message: {context.exception.message}")

    def test_loader_get_repro_env(self):
        """Test 9: Loader.get_repro_env() 返回正确字典。"""
        print("\n=== Test 9: Loader Get Repro Env ===")

        loader = ProvenanceLoader(template_path=None)
        repro_env = loader.get_repro_env()

        # Verify required fields
        self.assertIn("python_version", repro_env)
        self.assertIn("deps_lock_hash", repro_env)
        self.assertIn("os", repro_env)
        self.assertIn("tool_versions", repro_env)

        print(f"  repro_env keys: {list(repro_env.keys())}")


# ============================================================================
# Test Cases - Global Functions
# ============================================================================

class TestGlobalFunctions(unittest.TestCase):
    """全局便捷函数测试。"""

    def setUp(self):
        """Set up test fixtures."""
        reset_loader()

    def tearDown(self):
        """Clean up test fixtures."""
        reset_loader()

    def test_load_provenance(self):
        """Test 10: load_provenance() 全局函数。"""
        print("\n=== Test 10: load_provenance() ===")

        provenance = load_provenance()

        self.assertIsInstance(provenance, ProvenanceData)
        self.assertIsNotNone(provenance.captured_at)
        self.assertIsNotNone(provenance.repro_env)

        print(f"  Loaded provenance type: {type(provenance).__name__}")

    def test_get_repro_env(self):
        """Test 11: get_repro_env() 全局函数。"""
        print("\n=== Test 11: get_repro_env() ===")

        repro_env = get_repro_env()

        self.assertIsInstance(repro_env, dict)
        self.assertIn("python_version", repro_env)
        self.assertIn("os", repro_env)

        print(f"  repro_env.python_version: {repro_env['python_version']}")
        print(f"  repro_env.os: {repro_env['os']}")

    def test_get_full_provenance(self):
        """Test 12: get_full_provenance() 全局函数。"""
        print("\n=== Test 12: get_full_provenance() ===")

        full = get_full_provenance()

        self.assertIn("captured_at", full)
        self.assertIn("source", full)
        self.assertIn("ruleset_revision", full)
        self.assertIn("repro_env", full)

        print(f"  Full provenance keys: {list(full.keys())}")


# ============================================================================
# Test Cases - GateDecision Injection
# ============================================================================

class TestGateDecisionInjection(unittest.TestCase):
    """GateDecision 注入测试 - 关键测试。"""

    def setUp(self):
        """Set up test fixtures."""
        reset_loader()

    def tearDown(self):
        """Clean up test fixtures."""
        reset_loader()

    def test_inject_provenance_to_empty_gate_decision(self):
        """Test 13: 注入到空的 GateDecision。"""
        print("\n=== Test 13: Inject To Empty GateDecision ===")

        gate_decision = {
            "job_id": JOB_ID,
            "gate_decision": "ALLOW",
        }

        result = inject_provenance_to_gate_decision(gate_decision)

        # Verify provenance field exists
        self.assertIn("provenance", result)

        # Verify repro_env field exists (SEEDS_v0.md DoD requirement)
        self.assertIn("repro_env", result["provenance"])

        repro_env = result["provenance"]["repro_env"]
        self.assertIn("python_version", repro_env)
        self.assertIn("os", repro_env)

        print(f"  GateDecision now has provenance: {bool(result.get('provenance'))}")
        print(f"  provenance.repro_env exists: {bool(result['provenance'].get('repro_env'))}")

    def test_inject_provenance_preserves_existing(self):
        """Test 14: 注入时保留现有字段。"""
        print("\n=== Test 14: Inject Preserves Existing ===")

        gate_decision = {
            "job_id": JOB_ID,
            "gate_decision": "ALLOW",
            "ruleset_revision": "v2",  # Existing field
            "existing_field": "should_remain",
        }

        result = inject_provenance_to_gate_decision(gate_decision)

        # Existing fields should remain
        self.assertEqual(result["ruleset_revision"], "v2")
        self.assertEqual(result["existing_field"], "should_remain")

        # New provenance field should be added
        self.assertIn("provenance", result)

        print(f"  existing_field preserved: {result['existing_field']}")
        print(f"  provenance added: {bool(result.get('provenance'))}")

    def test_inject_provenance_with_existing_provenance(self):
        """Test 15: 注入时已有 provenance 字段的情况。"""
        print("\n=== Test 15: Inject With Existing Provenance ===")

        gate_decision = {
            "job_id": JOB_ID,
            "gate_decision": "ALLOW",
            "provenance": {
                "captured_at": "2026-02-20T10:00:00Z",
                "source": {"repo_url": "https://github.com/existing/repo"},
            },
        }

        result = inject_provenance_to_gate_decision(gate_decision)

        # Existing provenance values should be preserved
        self.assertEqual(
            result["provenance"]["captured_at"],
            "2026-02-20T10:00:00Z"
        )
        self.assertEqual(
            result["provenance"]["source"]["repo_url"],
            "https://github.com/existing/repo"
        )

        # repro_env should be added
        self.assertIn("repro_env", result["provenance"])

        print(f"  Existing captured_at preserved: {result['provenance']['captured_at']}")
        print(f"  repro_env added: {bool(result['provenance'].get('repro_env'))}")

    def test_repro_env_field_structure(self):
        """Test 16: repro_env 字段结构必须稳定。"""
        print("\n=== Test 16: repro_env Field Structure ===")

        gate_decision = {"job_id": JOB_ID}
        result = inject_provenance_to_gate_decision(gate_decision)

        repro_env = result["provenance"]["repro_env"]

        # Verify all required fields per SEEDS_v0.md
        required_fields = ["python_version", "deps_lock_hash", "os", "tool_versions"]

        for field in required_fields:
            self.assertIn(field, repro_env, f"Missing required field: {field}")
            print(f"  Field '{field}': present={field in repro_env}")

    def test_create_provenance_for_job(self):
        """Test 17: create_provenance_for_job() 工厂函数。"""
        print("\n=== Test 17: create_provenance_for_job() ===")

        provenance = create_provenance_for_job(
            job_id=JOB_ID,
            repo_url="https://github.com/skillforge/GM-SkillForge",
            commit_sha="abc123def456",
            ruleset_revision="v1",
        )

        self.assertIsInstance(provenance, ProvenanceData)
        self.assertEqual(provenance.source.repo_url, "https://github.com/skillforge/GM-SkillForge")
        self.assertEqual(provenance.source.commit_sha, "abc123def456")
        self.assertEqual(provenance.ruleset_revision, "v1")

        print(f"  repo_url: {provenance.source.repo_url}")
        print(f"  commit_sha: {provenance.source.commit_sha}")
        print(f"  ruleset_revision: {provenance.ruleset_revision}")


# ============================================================================
# Test Cases - Integration with T22_gate_decision.json format
# ============================================================================

class TestGateDecisionIntegration(unittest.TestCase):
    """与 T22_gate_decision.json 格式集成测试。"""

    def setUp(self):
        """Set up test fixtures."""
        reset_loader()

    def tearDown(self):
        """Clean up test fixtures."""
        reset_loader()

    def test_matches_t22_gate_decision_format(self):
        """Test 18: 输出格式与 T22_gate_decision.json 兼容。"""
        print("\n=== Test 18: Matches T22_gate_decision.json Format ===")

        # Create a GateDecision similar to T22_gate_decision.json
        gate_decision = {
            "job_id": JOB_ID,
            "skill_id": SKILL_ID,
            "task_id": "T26",
            "executor": "Kior-B",
            "wave": "Wave 1",
            "timestamp": "2026-02-20T18:30:00Z",
            "gate_decision": "ALLOW",
            "ruleset_revision": "v1",
        }

        result = inject_provenance_to_gate_decision(gate_decision)

        # Verify the structure matches T22 format
        self.assertIn("provenance", result)
        self.assertIn("repro_env", result["provenance"])

        repro_env = result["provenance"]["repro_env"]

        # Verify repro_env fields match T22_gate_decision.json
        self.assertIn("python_version", repro_env)
        self.assertIn("deps_lock_hash", repro_env)
        self.assertIn("os", repro_env)
        self.assertIn("tool_versions", repro_env)
        self.assertIn("gm_skillforge", repro_env["tool_versions"])

        print(f"  GateDecision format matches T22: True")
        print(f"  repro_env.python_version: {repro_env['python_version']}")
        print(f"  repro_env.os: {repro_env['os']}")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
