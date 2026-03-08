"""
Tech SEO Audit - Contract Tests
tech_seo_audit Skill 的合同测试

关键硬测试：
- issue_key 一致性：examples 中出现的 issue_key 必须存在于 issue_catalog.yml
  （就算有人绕过 validate.py 也会被 pytest 卡死）
- input/output schema 结构校验
"""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
import yaml


ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def schemas():
    input_schema = _load_json(ROOT / "schemas" / "tech_seo_audit.input.schema.json")
    output_schema = _load_json(ROOT / "schemas" / "tech_seo_audit.output.schema.json")
    return {"input": input_schema, "output": output_schema}


# ================================================================
# Schema 存在性与结构测试
# ================================================================

class TestTechSeoAuditSchemas:
    """Input/Output Schema 合规性"""

    def test_input_schema_exists(self):
        path = ROOT / "schemas" / "tech_seo_audit.input.schema.json"
        assert path.exists(), f"Missing input schema: {path}"

    def test_output_schema_exists(self):
        path = ROOT / "schemas" / "tech_seo_audit.output.schema.json"
        assert path.exists(), f"Missing output schema: {path}"

    def test_input_schema_has_url_required(self, schemas):
        assert "url" in schemas["input"].get("required", []), "Input schema must require 'url'"

    def test_output_schema_has_results_required(self, schemas):
        assert "results" in schemas["output"].get("required", []), "Output schema must require 'results'"

    def test_output_issue_key_pattern(self, schemas):
        """Verify issue_key enforces UPPER_SNAKE_CASE pattern"""
        results_items = schemas["output"]["properties"]["results"]["items"]
        issues_items = results_items["properties"]["issues"]["items"]
        issue_key_def = issues_items["properties"]["issue_key"]
        assert "pattern" in issue_key_def, "issue_key must have a pattern constraint"

    def test_input_schema_minimal_valid(self, schemas):
        """最小有效 input 校验"""
        v = Draft202012Validator(schemas["input"])
        payload = {"url": "https://example.com"}
        errors = list(v.iter_errors(payload))
        assert not errors, "; ".join([e.message for e in errors])

    def test_output_schema_minimal_valid(self, schemas):
        """最小有效 output 校验"""
        v = Draft202012Validator(schemas["output"])
        payload = {
            "url": "https://example.com",
            "score": 80,
            "results": []
        }
        errors = list(v.iter_errors(payload))
        assert not errors, "; ".join([e.message for e in errors])


# ================================================================
# Issue Catalog 结构测试
# ================================================================

class TestIssueCatalog:
    """issue_catalog.yml 结构校验"""

    def test_catalog_exists(self):
        path = ROOT / "orchestration" / "issue_catalog.yml"
        assert path.exists(), f"Missing catalog: {path}"

    def test_catalog_structure(self):
        catalog = _load_yaml(ROOT / "orchestration" / "issue_catalog.yml")
        assert isinstance(catalog, dict), "Catalog must be a dict"
        assert "issues" in catalog, "Catalog must have 'issues' key"
        assert isinstance(catalog["issues"], list), "'issues' must be a list"
        assert len(catalog["issues"]) > 0, "Catalog must have at least one issue"

    def test_catalog_keys_unique(self):
        """所有 issue_key 必须唯一"""
        catalog = _load_yaml(ROOT / "orchestration" / "issue_catalog.yml")
        keys = set()
        for item in catalog["issues"]:
            assert isinstance(item, dict) and "issue_key" in item, \
                "Invalid issue entry (missing issue_key)"
            k = item["issue_key"]
            assert isinstance(k, str) and k.strip(), f"Invalid issue_key: {k!r}"
            assert k not in keys, f"Duplicate issue_key in catalog: {k}"
            keys.add(k)

    def test_catalog_entries_have_required_fields(self):
        """每个 entry 必须有 severity, category, description"""
        catalog = _load_yaml(ROOT / "orchestration" / "issue_catalog.yml")
        for item in catalog["issues"]:
            key = item.get("issue_key", "<unknown>")
            assert "severity" in item, f"{key}: missing 'severity'"
            assert item["severity"] in ("error", "warning", "info"), \
                f"{key}: severity must be error/warning/info, got {item['severity']}"
            assert "category" in item, f"{key}: missing 'category'"
            assert "description" in item, f"{key}: missing 'description'"

    def test_catalog_keys_are_upper_snake_case(self):
        """issue_key 必须是 UPPER_SNAKE_CASE"""
        import re
        pattern = re.compile(r"^[A-Z][A-Z0-9_]+$")
        catalog = _load_yaml(ROOT / "orchestration" / "issue_catalog.yml")
        for item in catalog["issues"]:
            k = item["issue_key"]
            assert pattern.match(k), f"issue_key '{k}' is not UPPER_SNAKE_CASE"


# ================================================================
# 🔒 硬门禁：issue_key 一致性
# ================================================================

class TestIssueKeyConsistency:
    """
    Hard gate: any issue_key used in examples must be declared
    in orchestration/issue_catalog.yml.
    This prevents drift even if someone bypasses tools/validate.py.
    """

    def test_examples_issue_keys_must_exist_in_catalog(self):
        """Examples 中使用的 issue_key 必须在 catalog 中注册"""
        catalog_path = ROOT / "orchestration" / "issue_catalog.yml"
        assert catalog_path.exists(), f"Missing catalog: {catalog_path}"

        catalog = _load_yaml(catalog_path)
        assert isinstance(catalog, dict) and isinstance(catalog.get("issues"), list), \
            "Invalid issue_catalog.yml structure"

        catalog_keys = set()
        for it in catalog["issues"]:
            assert isinstance(it, dict) and "issue_key" in it, \
                "Invalid issue entry in catalog (missing issue_key)"
            k = it["issue_key"]
            assert isinstance(k, str) and k.strip(), "Invalid issue_key in catalog"
            assert k not in catalog_keys, f"Duplicate issue_key in catalog: {k}"
            catalog_keys.add(k)

        examples_dir = ROOT / "orchestration" / "examples" / "tech_seo_audit"
        assert examples_dir.exists(), f"Missing examples dir: {examples_dir}"

        used = set()
        for f in sorted(examples_dir.glob("*.json")):
            data = _load_json(f)

            # 扫描 results[].issues[].issue_key
            results = data.get("results", [])
            if not isinstance(results, list):
                # 也检查 skill_output_example 内部
                output = data.get("skill_output_example", {})
                results = output.get("results", [])
                if not isinstance(results, list):
                    continue

            for r in results:
                if not isinstance(r, dict):
                    continue
                issues = r.get("issues", [])
                if not isinstance(issues, list):
                    continue
                for iss in issues:
                    if isinstance(iss, dict) and isinstance(iss.get("issue_key"), str):
                        used.add(iss["issue_key"])

            # 也扫描 summary.top_issues[].issue_key
            summary = data.get("summary", data.get("skill_output_example", {}).get("summary", {}))
            if isinstance(summary, dict):
                top_issues = summary.get("top_issues", [])
                if isinstance(top_issues, list):
                    for ti in top_issues:
                        if isinstance(ti, dict) and isinstance(ti.get("issue_key"), str):
                            used.add(ti["issue_key"])

        missing = sorted(list(used - catalog_keys))
        assert not missing, \
            "Examples reference undefined issue_key(s): " + ", ".join(missing)

    def test_catalog_issue_keys_coverage(self):
        """信息性测试：看哪些 catalog keys 还没被使用过"""
        catalog = _load_yaml(ROOT / "orchestration" / "issue_catalog.yml")
        catalog_keys = {it["issue_key"] for it in catalog["issues"]}

        examples_dir = ROOT / "orchestration" / "examples" / "tech_seo_audit"
        if not examples_dir.exists():
            pytest.skip("Examples dir not found")

        used = set()
        for f in sorted(examples_dir.glob("*.json")):
            data = _load_json(f)
            output = data.get("skill_output_example", data)
            results = output.get("results", [])
            if isinstance(results, list):
                for r in results:
                    if isinstance(r, dict):
                        for iss in r.get("issues", []):
                            if isinstance(iss, dict) and isinstance(iss.get("issue_key"), str):
                                used.add(iss["issue_key"])

        unused = catalog_keys - used
        # This is informational, not a failure
        if unused:
            print(f"\n  [INFO] {len(unused)} catalog keys not yet used in examples: "
                  f"{', '.join(sorted(unused))}")


# ================================================================
# Error Envelope 测试（来自执行者原始提案）
# ================================================================

class TestErrorEnvelope:
    """验证 error_policy 中 suggested_fixes 使用合法的 kind"""

    def test_error_envelope_has_standard_fix_kinds(self):
        policy = _load_yaml(ROOT / "orchestration" / "error_policy.yml")
        valid_kinds = set(policy.get("suggested_fix_kinds", []))

        for p in policy.get("policies", []):
            for err in p.get("on_error", []):
                na = err.get("next_action", {})
                for fx in na.get("suggested_fixes", []):
                    assert fx["kind"] in valid_kinds, \
                        f"Invalid fix kind '{fx['kind']}' in {p['node_id']}/{err['error_code']}"


# ================================================================
# Issue Catalog Versioning 测试
# ================================================================

class TestIssueCatalogVersioning:
    """issue_catalog.yml 版本化字段校验"""

    def test_catalog_has_version(self):
        """catalog 必须有 schema_version 和 catalog_version"""
        catalog = _load_yaml(ROOT / "orchestration" / "issue_catalog.yml")
        assert "schema_version" in catalog, "Missing schema_version in issue_catalog.yml"
        assert "catalog_version" in catalog, "Missing catalog_version in issue_catalog.yml"

        # schema_version should be 1
        sv = catalog.get("schema_version")
        assert sv == 1 or sv == "1", f"schema_version should be 1, got {sv}"

        # catalog_version should be a non-empty string
        cv = catalog.get("catalog_version")
        assert isinstance(cv, str) and cv.strip(), \
            f"catalog_version should be a non-empty string, got {cv!r}"

    def test_all_issues_have_added_in(self):
        """所有 issue 必须有 added_in 字段"""
        catalog = _load_yaml(ROOT / "orchestration" / "issue_catalog.yml")
        issues = catalog.get("issues", [])
        assert isinstance(issues, list), "issues should be a list"

        missing = []
        for issue in issues:
            if isinstance(issue, dict):
                key = issue.get("issue_key", "<unknown>")
                if "added_in" not in issue or issue["added_in"] is None:
                    missing.append(key)

        assert not missing, \
            f"Issues missing 'added_in' field: {', '.join(missing)}"

    def test_no_orphan_deprecated_issues(self):
        """废弃的 issue 必须有明确的 deprecated_in 版本"""
        catalog = _load_yaml(ROOT / "orchestration" / "issue_catalog.yml")
        issues = catalog.get("issues", [])

        # This is informational - we check that deprecated_in is either null or a valid version
        deprecated_issues = []
        for issue in issues:
            if isinstance(issue, dict):
                deprecated_in = issue.get("deprecated_in")
                if deprecated_in is not None:
                    key = issue.get("issue_key", "<unknown>")
                    deprecated_issues.append((key, deprecated_in))

        # If there are deprecated issues, they should have a valid version string
        for key, version in deprecated_issues:
            assert isinstance(version, str) and version.strip(), \
                f"Deprecated issue '{key}' has invalid deprecated_in: {version!r}"

    def test_effective_from_valid_iso(self):
        """effective_from 必须是有效的 ISO-8601 时间戳"""
        import re
        catalog = _load_yaml(ROOT / "orchestration" / "issue_catalog.yml")

        effective_from = catalog.get("effective_from")
        assert effective_from is not None, "Missing effective_from in issue_catalog.yml"

        # ISO-8601 format: YYYY-MM-DDTHH:MM:SSZ or with timezone
        iso_pattern = re.compile(
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
        )

        assert iso_pattern.match(str(effective_from)), \
            f"effective_from '{effective_from}' is not a valid ISO-8601 timestamp"

