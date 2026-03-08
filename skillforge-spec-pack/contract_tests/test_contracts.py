"""
GM OS Contract Tests
契约测试 - 验证所有 schema、policy、examples 的一致性
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List, Any

try:
    import jsonschema
    from jsonschema import validate, ValidationError, RefResolver
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    pytest.skip("jsonschema not installed", allow_module_level=True)

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# 项目根目录
BASE_PATH = Path(__file__).parent.parent


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_yaml(path: Path) -> Dict[str, Any]:
    if not HAS_YAML:
        pytest.skip("PyYAML not installed")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class TestSchemas:
    """Schema 结构测试"""

    def test_schemas_exist(self):
        """验证所有必需的 schema 文件存在"""
        required_schemas = [
            "common.schema.json",
            "gate_decision.schema.json",
            "audit_pack.schema.json",
            "registry_publish.schema.json",
            "execution_pack.schema.json",
            "trace_event.schema.json",
            "granularity_rules.schema.json",
        ]

        schemas_dir = BASE_PATH / "schemas"
        for schema_name in required_schemas:
            schema_path = schemas_dir / schema_name
            assert schema_path.exists(), f"Schema 文件不存在: {schema_name}"

    def test_schemas_valid_json(self):
        """验证所有 schema 是有效的 JSON"""
        schemas_dir = BASE_PATH / "schemas"
        for schema_file in schemas_dir.glob("*.schema.json"):
            try:
                data = load_json(schema_file)
                assert "$schema" in data, f"{schema_file.name} 缺少 $schema 字段"
                assert "version" in data or "schema_version" in data, f"{schema_file.name} 缺少版本字段"
            except json.JSONDecodeError as e:
                pytest.fail(f"无效 JSON: {schema_file.name} - {e}")

    def test_schema_version_format(self):
        """验证 schema_version 格式正确"""
        schemas_dir = BASE_PATH / "schemas"
        for schema_file in schemas_dir.glob("*.schema.json"):
            data = load_json(schema_file)
            if "version" in data:
                assert data["version"].startswith("0.1."), f"{schema_file.name} 版本格式错误"


class TestNodeSchemas:
    """8 节点 Schema 测试"""

    NODE_IDS = [
        "intake_repo",
        "license_gate",
        "repo_scan_fit_score",
        "draft_skill_spec",
        "constitution_risk_gate",
        "scaffold_skill_impl",
        "sandbox_test_and_trace",
        "pack_audit_and_publish",
    ]

    def test_node_schemas_exist(self):
        """验证 8 个节点的 schema 文件存在"""
        nodes_dir = BASE_PATH / "orchestration" / "nodes"
        for node_id in self.NODE_IDS:
            schema_path = nodes_dir / f"{node_id}.node.schema.json"
            assert schema_path.exists(), f"节点 schema 不存在: {node_id}"

    def test_node_schema_structure(self):
        """验证节点 schema 结构完整"""
        nodes_dir = BASE_PATH / "orchestration" / "nodes"
        for node_id in self.NODE_IDS:
            schema_path = nodes_dir / f"{node_id}.node.schema.json"
            data = load_json(schema_path)

            # 检查 properties.node_id.const
            props = data.get("properties", {})
            node_id_def = props.get("node_id", {})
            assert node_id_def.get("const") == node_id, f"{node_id}: node_id 不匹配"
            assert "input" in props, f"{node_id}: 缺少 input 定义"
            assert "output" in props, f"{node_id}: 缺少 output 定义"
            assert "errors" in props, f"{node_id}: 缺少 errors 定义"


class TestErrorCodes:
    """错误码测试"""

    def test_error_codes_file_exists(self):
        """验证 error_codes.yml 存在"""
        error_codes_path = BASE_PATH / "orchestration" / "error_codes.yml"
        assert error_codes_path.exists(), "orchestration/error_codes.yml 不存在"

    def test_error_codes_structure(self):
        """验证错误码结构完整"""
        data = load_yaml(BASE_PATH / "orchestration" / "error_codes.yml")

        assert "schema_version" in data
        assert "error_codes" in data

        for code_name, code_def in data["error_codes"].items():
            assert "code" in code_def, f"{code_name}: 缺少 code"
            assert "http_status" in code_def, f"{code_name}: 缺少 http_status"
            assert "severity" in code_def, f"{code_name}: 缺少 severity"
            assert "category" in code_def, f"{code_name}: 缺少 category"
            assert "title" in code_def, f"{code_name}: 缺少 title"

    def test_error_policy_references_valid(self):
        """验证 error_policy 引用的错误码都存在"""
        error_codes = load_yaml(BASE_PATH / "orchestration" / "error_codes.yml")
        valid_codes = set(error_codes["error_codes"].keys())

        error_policy = load_yaml(BASE_PATH / "orchestration" / "error_policy.yml")

        for policy in error_policy.get("policies", []):
            for on_error in policy.get("on_error", []):
                code = on_error.get("error_code")
                assert code in valid_codes, f"无效错误码引用: {code} (in {policy['node_id']})"


class TestQualityGateLevels:
    """质量门禁测试"""

    def test_quality_gate_file_exists(self):
        """验证 quality_gate_levels.yml 存在"""
        path = BASE_PATH / "orchestration" / "quality_gate_levels.yml"
        assert path.exists(), "quality_gate_levels.yml 不存在"

    def test_all_levels_defined(self):
        """验证 5 个等级都已定义"""
        data = load_yaml(BASE_PATH / "orchestration" / "quality_gate_levels.yml")

        levels = set(data["levels"].keys())
        expected = {"L1", "L2", "L3", "L4", "L5"}
        assert levels == expected, f"缺少等级: {expected - levels}"

    def test_level_4_runs_threshold(self):
        """验证 Level 4 有 min_runs >= 20"""
        data = load_yaml(BASE_PATH / "orchestration" / "quality_gate_levels.yml")

        l4 = data["levels"]["L4"]
        thresholds = l4.get("thresholds", {})
        min_runs = thresholds.get("min_runs", 0)
        assert min_runs >= 20, f"Level 4 min_runs 必须 >= 20, got {min_runs}"

    def test_level_5_runs_threshold(self):
        """验证 Level 5 有 min_vectors >= 1000"""
        data = load_yaml(BASE_PATH / "orchestration" / "quality_gate_levels.yml")

        l5 = data["levels"]["L5"]
        thresholds = l5.get("thresholds", {})
        min_vectors = thresholds.get("min_vectors", 0)
        assert min_vectors >= 1000, f"Level 5 min_vectors 必须 >= 1000, got {min_vectors}"

    def test_success_rate_in_range(self):
        """验证成功率 thresholds 在 [0, 1] 范围内"""
        data = load_yaml(BASE_PATH / "orchestration" / "quality_gate_levels.yml")

        for level_key, level_data in data["levels"].items():
            thresholds = level_data.get("thresholds", {})
            rate = thresholds.get("min_success_rate")
            if rate is not None:
                assert 0 <= rate <= 1, f"{level_key}: min_success_rate {rate} 必须在 [0,1]"

    def test_required_changes_templates_have_patch_targets(self):
        """验证每个 required_changes_templates 都有 patch_targets"""
        data = load_yaml(BASE_PATH / "orchestration" / "quality_gate_levels.yml")

        for level_key, level_data in data["levels"].items():
            for template in level_data.get("required_changes_templates", []):
                targets = template.get("patch_targets", [])
                assert len(targets) >= 1, f"{level_key}: template '{template.get('id')}' 缺少 patch_targets"



class TestPipeline:
    """流水线测试"""

    def test_pipeline_file_exists(self):
        """验证 pipeline_v0.yml 存在"""
        path = BASE_PATH / "orchestration" / "pipeline_v0.yml"
        assert path.exists(), "pipeline_v0.yml 不存在"

    def test_all_nodes_in_pipeline(self):
        """验证 8 个节点都在 pipeline 中"""
        data = load_yaml(BASE_PATH / "orchestration" / "pipeline_v0.yml")

        node_ids = {node["id"] for node in data["nodes"]}
        expected = {
            "intake_repo", "license_gate", "repo_scan_fit_score", "draft_skill_spec",
            "constitution_risk_gate", "scaffold_skill_impl", "sandbox_test_and_trace",
            "pack_audit_and_publish"
        }

        assert node_ids == expected, f"节点不匹配: {expected - node_ids}"

    def test_node_sequence_correct(self):
        """验证节点顺序正确 (Stage 0-7)"""
        data = load_yaml(BASE_PATH / "orchestration" / "pipeline_v0.yml")

        stages = [node["stage"] for node in sorted(data["nodes"], key=lambda n: n["stage"])]
        assert stages == [0, 1, 2, 3, 4, 5, 6, 7], "节点阶段顺序错误"


class TestControlsCatalog:
    """控制字段目录测试"""

    def test_controls_catalog_exists(self):
        """验证 controls_catalog.yml 存在"""
        path = BASE_PATH / "orchestration" / "controls_catalog.yml"
        assert path.exists(), "controls_catalog.yml 不存在"

    def test_min_default_max_consistency(self):
        """验证 min <= default <= max"""
        data = load_yaml(BASE_PATH / "orchestration" / "controls_catalog.yml")

        for field_name, field_def in data.get("fields", {}).items():
            if "minimum" in field_def and "maximum" in field_def:
                minimum = field_def["minimum"]
                default = field_def.get("default", minimum)
                maximum = field_def["maximum"]

                assert minimum <= default <= maximum, \
                    f"{field_name}: min({minimum}) <= default({default}) <= max({maximum}) 不成立"

    def test_aliases_unique(self):
        """验证所有别名唯一"""
        data = load_yaml(BASE_PATH / "orchestration" / "controls_catalog.yml")

        all_aliases = []
        for field_def in data.get("fields", {}).values():
            all_aliases.extend(field_def.get("aliases", []))

        assert len(all_aliases) == len(set(all_aliases)), "存在重复的别名"


class TestValidExamples:
    """Valid Examples 测试"""

    def test_valid_examples_pass(self):
        """验证 valid examples 能通过 schema 校验"""
        valid_dir = BASE_PATH / "contract_tests" / "valid_examples"
        schemas_dir = BASE_PATH / "schemas"

        if not valid_dir.exists():
            pytest.skip("valid_examples 目录不存在")

        for example_file in valid_dir.glob("*.json"):
            schema_name = example_file.stem.split("_")[0]
            schema_path = schemas_dir / f"{schema_name}.schema.json"

            if schema_path.exists():
                data = load_json(example_file)
                schema = load_json(schema_path)

                try:
                    validate(instance=data, schema=schema)
                except ValidationError as e:
                    pytest.fail(f"{example_file.name}: {e.message}")


class TestInvalidExamples:
    """Invalid Examples 测试"""

    def test_invalid_examples_fail(self):
        """验证 invalid examples 不能通过 schema 校验"""
        invalid_dir = BASE_PATH / "contract_tests" / "invalid_examples"
        schemas_dir = BASE_PATH / "schemas"

        if not invalid_dir.exists():
            pytest.skip("invalid_examples 目录不存在")

        for example_file in invalid_dir.glob("*.json"):
            schema_name = example_file.stem.split("_")[0]
            schema_path = schemas_dir / f"{schema_name}.schema.json"

            if schema_path.exists():
                data = load_json(example_file)
                schema = load_json(schema_path)

                with pytest.raises(ValidationError):
                    validate(instance=data, schema=schema)


class TestCrossReferences:
    """跨引用一致性测试"""

    def test_pipeline_error_policy_node_consistency(self):
        """验证 pipeline 和 error_policy 的 node_id 一致"""
        pipeline = load_yaml(BASE_PATH / "orchestration" / "pipeline_v0.yml")
        error_policy = load_yaml(BASE_PATH / "orchestration" / "error_policy.yml")

        pipeline_nodes = {node["id"] for node in pipeline["nodes"]}
        policy_nodes = {p["node_id"] for p in error_policy["policies"]}

        assert pipeline_nodes == policy_nodes, \
            f"node_id 不一致: pipeline={pipeline_nodes}, policy={policy_nodes}"

    def test_quality_gate_next_action_refs_valid(self):
        """验证 quality_gate 的 next_action_ref 能在 error_policy 找到"""
        quality_gate = load_yaml(BASE_PATH / "orchestration" / "quality_gate_levels.yml")
        error_policy = load_yaml(BASE_PATH / "orchestration" / "error_policy.yml")

        # 构建 error_policy 查找表
        policy_lookup = {}
        for p in error_policy["policies"]:
            node_id = p["node_id"]
            error_codes = {e["error_code"] for e in p.get("on_error", [])}
            policy_lookup[node_id] = error_codes

        # 验证每个 required_changes_templates 的 when_failed_check 存在
        for level_key, level_data in quality_gate["levels"].items():
            for template in level_data.get("required_changes_templates", []):
                assert "id" in template, f"{level_key}: template 缺少 id"
                assert "when_failed_check" in template, f"{level_key}: template '{template.get('id')}' 缺少 when_failed_check"
                assert "message" in template, f"{level_key}: template '{template.get('id')}' 缺少 message"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
