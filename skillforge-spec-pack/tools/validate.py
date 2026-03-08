#!/usr/bin/env python3
"""
GM OS Schema Validator
校验 JSON/YAML 文件是否符合 schema 定义

用法:
    python validate.py --schema schemas/gate_decision.schema.json --json examples/gate_decision.json
    python validate.py --all  # 校验所有 examples
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import jsonschema
    from jsonschema import validate, ValidationError, RefResolver
    from referencing import Registry, Resource
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("警告: jsonschema 未安装，请运行: pip install jsonschema")


def load_json(path: Path) -> Dict[str, Any]:
    """加载 JSON 文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_yaml(path: Path) -> Dict[str, Any]:
    """加载 YAML 文件"""
    try:
        import yaml
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except ImportError:
        print("警告: PyYAML 未安装，无法加载 YAML 文件")
        return {}


def get_schema_registry(base_path: Path) -> Dict[str, Any]:
    """创建 schema 注册表，支持 $ref 引用"""
    schemas_dir = base_path / "schemas"
    registry = {}

    if schemas_dir.exists():
        for schema_file in schemas_dir.glob("*.schema.json"):
            schema = load_json(schema_file)
            schema_id = schema.get("$id", "")
            if schema_id:
                registry[schema_id] = schema

    return registry


def validate_against_schema(data: Dict[str, Any], schema: Dict[str, Any],
                            registry: Dict[str, Any] = None) -> Tuple[bool, List[str]]:
    """根据 schema 校验数据"""
    if not HAS_JSONSCHEMA:
        return False, ["jsonschema 库未安装"]

    errors = []

    try:
        if registry:
            # 创建 resolver 处理 $ref
            schema_store = {}
            for k, v in registry.items():
                schema_store[k] = v

            resolver = RefResolver.from_schema(schema, store=schema_store)
            validate(instance=data, schema=schema, resolver=resolver)
        else:
            validate(instance=data, schema=schema)

        return True, []
    except ValidationError as e:
        error_path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        errors.append(f"{error_path}: {e.message}")
        return False, errors
    except Exception as e:
        return False, [str(e)]


def validate_file(data_path: Path, schema_path: Path, base_path: Path) -> Tuple[bool, List[str]]:
    """校验单个文件"""
    try:
        # 加载数据
        if data_path.suffix == '.json':
            data = load_json(data_path)
        elif data_path.suffix in ['.yml', '.yaml']:
            data = load_yaml(data_path)
        else:
            return False, [f"不支持的文件格式: {data_path.suffix}"]

        # 加载 schema
        schema = load_json(schema_path)

        # 获取 schema 注册表
        registry = get_schema_registry(base_path)

        # 校验
        return validate_against_schema(data, schema, registry)
    except Exception as e:
        return False, [str(e)]


def _find_schema_for_example(filename_stem: str, schemas_dir: Path) -> Path | None:
    """根据 example 文件名前缀找到对应的 schema 文件。

    文件命名约定: {schema_name}_{valid|invalid}_{N}.json
    例如: gate_decision_valid_1.json -> gate_decision.schema.json
          audit_pack_invalid_2.json  -> audit_pack.schema.json
    """
    # 收集所有可用 schema 名称（不含 .schema.json 后缀）
    available_schemas = sorted(
        [f.stem.replace(".schema", "") for f in schemas_dir.glob("*.schema.json")],
        key=lambda s: len(s),
        reverse=True  # 最长前缀优先匹配
    )

    for schema_name in available_schemas:
        prefix = schema_name + "_"
        if filename_stem.startswith(prefix):
            return schemas_dir / f"{schema_name}.schema.json"

    return None


def validate_all_examples(base_path: Path) -> Dict[str, Tuple[bool, List[str]]]:
    """校验所有 examples"""
    results = {}
    valid_dir = base_path / "contract_tests" / "valid_examples"
    invalid_dir = base_path / "contract_tests" / "invalid_examples"
    schemas_dir = base_path / "schemas"

    # 获取 schema 注册表
    registry = get_schema_registry(base_path)

    # 校验 valid examples
    for example_file in sorted(valid_dir.glob("*.json")):
        # 根据 filename 前缀找对应 schema
        schema_path = _find_schema_for_example(example_file.stem, schemas_dir)

        if schema_path and schema_path.exists():
            is_valid, errors = validate_file(example_file, schema_path, base_path)
            results[f"valid/{example_file.name}"] = (is_valid, errors)
        else:
            results[f"valid/{example_file.name}"] = (False, [f"无法匹配 Schema: {example_file.name}"])

    # 校验 invalid examples (应该校验失败)
    for example_file in sorted(invalid_dir.glob("*.json")):
        schema_path = _find_schema_for_example(example_file.stem, schemas_dir)

        if schema_path and schema_path.exists():
            is_valid, errors = validate_file(example_file, schema_path, base_path)
            # invalid examples 应该校验失败
            expected_invalid = not is_valid
            results[f"invalid/{example_file.name}"] = (
                expected_invalid,
                [] if expected_invalid else ["预期校验失败，但实际通过了"]
            )
        else:
            results[f"invalid/{example_file.name}"] = (False, [f"无法匹配 Schema: {example_file.name}"])

    return results


# ── Audit Config Validation (10-point Protocol check) ──────────────────────

VALID_NODES = {
    "intake_repo",
    "license_gate",
    "repo_scan_fit_score",
    "draft_skill_spec",
    "constitution_risk_gate",
    "scaffold_skill_impl",
    "sandbox_test_and_trace",
    "pack_audit_and_publish",
}


def validate_audit_config(base_path: Path) -> List[Tuple[str, bool, str]]:
    """
    15-point Audit Engine Protocol validation.

    Checks cross-references between:
    - orchestration/error_codes.yml
    - orchestration/error_policy.yml
    - orchestration/quality_gate_levels.yml
    - orchestration/skill_thresholds.yml
    - orchestration/issue_catalog.yml

    Returns list of (check_id, passed, detail).
    """
    results: List[Tuple[str, bool, str]] = []
    orch = base_path / "orchestration"

    # ── Load files ──────────────────────────────────────────
    ec_path = orch / "error_codes.yml"
    ep_path = orch / "error_policy.yml"

    if not ec_path.exists():
        results.append(("LOAD", False, f"Missing {ec_path}"))
        return results
    if not ep_path.exists():
        results.append(("LOAD", False, f"Missing {ep_path}"))
        return results

    ec = load_yaml(ec_path)
    ep = load_yaml(ep_path)

    error_codes_map: Dict[str, Any] = ec.get("error_codes", {})
    policies: List[Dict[str, Any]] = ep.get("policies", [])

    # ── CHECK 1: error_codes.yml schema_version == 1 ──────
    sv = ec.get("schema_version")
    ok = sv == 1 or sv == "1"
    results.append((
        "EC_SCHEMA_VERSION",
        ok,
        f"schema_version={sv}" if ok else f"Expected 1, got {sv}"
    ))

    # ── CHECK 2: All error_policy error_codes exist in error_codes.yml ──
    ep_codes: set = set()
    for policy in policies:
        for entry in policy.get("on_error", []):
            code = entry.get("error_code")
            if code:
                ep_codes.add(code)

    missing_in_ec = ep_codes - set(error_codes_map.keys())
    ok = len(missing_in_ec) == 0
    results.append((
        "EP_CODES_IN_EC",
        ok,
        "All error_policy codes found in error_codes.yml" if ok
        else f"Missing in error_codes.yml: {sorted(missing_in_ec)}"
    ))

    # ── CHECK 3: Reverse check — no orphan codes (except generic) ──
    generic_codes = {k for k, v in error_codes_map.items()
                     if isinstance(v, dict) and v.get("generic")}
    ec_non_generic = set(error_codes_map.keys()) - generic_codes
    orphan_codes = ec_non_generic - ep_codes
    ok = len(orphan_codes) == 0
    results.append((
        "EC_NO_ORPHAN_CODES",
        ok,
        "No orphan non-generic codes" if ok
        else f"Unreferenced codes (not generic): {sorted(orphan_codes)}"
    ))

    # ── CHECK 4: error_policy nodes in whitelist ──────────
    ep_nodes = {p.get("node_id") for p in policies}
    invalid_nodes = ep_nodes - VALID_NODES
    ok = len(invalid_nodes) == 0
    results.append((
        "EP_VALID_NODES",
        ok,
        f"All {len(ep_nodes)} nodes valid" if ok
        else f"Invalid nodes: {sorted(invalid_nodes)}"
    ))

    # ── CHECK 5: Each node fail/deny has required fields ──
    required_fields = {"error_code", "next_action"}
    next_action_fields = {"action_id", "title", "suggested_fixes"}
    field_errors: List[str] = []
    for policy in policies:
        node_id = policy.get("node_id", "?")
        for entry in policy.get("on_error", []):
            for f in required_fields:
                if f not in entry:
                    field_errors.append(f"{node_id}: missing '{f}'")
            na = entry.get("next_action", {})
            if isinstance(na, dict):
                for f in next_action_fields:
                    if f not in na:
                        field_errors.append(f"{node_id}: next_action missing '{f}'")
    ok = len(field_errors) == 0
    results.append((
        "EP_FAIL_FIELDS_COMPLETE",
        ok,
        "All fail entries have required fields" if ok
        else f"Missing fields: {field_errors[:5]}{'...' if len(field_errors) > 5 else ''}"
    ))

    # ── CHECK 6: suggested_fixes.kind in enum ─────────────
    fix_kinds_whitelist = set(ep.get("suggested_fix_kinds", []))
    bad_kinds: List[str] = []
    for policy in policies:
        node_id = policy.get("node_id", "?")
        for entry in policy.get("on_error", []):
            na = entry.get("next_action", {})
            if isinstance(na, dict):
                for fix in na.get("suggested_fixes", []):
                    kind = fix.get("kind")
                    if kind and fix_kinds_whitelist and kind not in fix_kinds_whitelist:
                        bad_kinds.append(f"{node_id}: '{kind}'")
    ok = len(bad_kinds) == 0
    results.append((
        "EP_FIX_KINDS_VALID",
        ok,
        "All suggested_fixes.kind in whitelist" if ok
        else f"Invalid kinds: {bad_kinds[:5]}"
    ))

    # ── CHECK 7: required_changes in quality_gate_levels ──
    qg_path = orch / "quality_gate_levels.yml"
    if qg_path.exists():
        qg = load_yaml(qg_path)
        levels = qg.get("levels", {})
        rc_issues: List[str] = []
        for level_key, level_data in levels.items():
            if not isinstance(level_data, dict):
                continue
            for rc in level_data.get("required_changes_templates", []):
                if not isinstance(rc, dict):
                    rc_issues.append(f"{level_key}: non-dict template")
                    continue
                if "id" not in rc or "message" not in rc:
                    rc_issues.append(f"{level_key}: template missing id/message")
        ok = len(rc_issues) == 0
        results.append((
            "QG_RC_TEMPLATES_VALID",
            ok,
            "All required_changes_templates have id+message" if ok
            else f"Issues: {rc_issues[:5]}"
        ))
    else:
        results.append(("QG_RC_TEMPLATES_VALID", False, "quality_gate_levels.yml missing"))

    # ── CHECK 8: error_codes entries have code/category/severity ──
    ec_entry_errors: List[str] = []
    valid_categories = set(ec.get("enums", {}).get("category", []))
    valid_severities = set(ec.get("enums", {}).get("severity", []))
    for key, entry in error_codes_map.items():
        if not isinstance(entry, dict):
            ec_entry_errors.append(f"{key}: not a dict")
            continue
        for f in ("code", "category", "severity"):
            if f not in entry:
                ec_entry_errors.append(f"{key}: missing '{f}'")
        cat = entry.get("category")
        if valid_categories and cat not in valid_categories:
            ec_entry_errors.append(f"{key}: category '{cat}' not in enum")
        sev = entry.get("severity")
        if valid_severities and sev not in valid_severities:
            ec_entry_errors.append(f"{key}: severity '{sev}' not in enum")
        hs = entry.get("http_status")
        if hs is not None:
            if not isinstance(hs, int) or not (100 <= hs <= 599):
                ec_entry_errors.append(f"{key}: http_status={hs} invalid")
    ok = len(ec_entry_errors) == 0
    results.append((
        "EC_ENTRIES_VALID",
        ok,
        "All error_code entries valid" if ok
        else f"Issues: {ec_entry_errors[:5]}"
    ))

    # ── CHECK 9: code field == key ────────────────────────
    key_mismatch: List[str] = []
    for key, entry in error_codes_map.items():
        if isinstance(entry, dict) and entry.get("code") != key:
            key_mismatch.append(f"{key}: code='{entry.get('code')}'")
    ok = len(key_mismatch) == 0
    results.append((
        "EC_CODE_KEY_MATCH",
        ok,
        "All code fields match their keys" if ok
        else f"Mismatches: {key_mismatch[:5]}"
    ))

    # ── CHECK 10: error_codes has error_codes mapping ─────
    ok = isinstance(error_codes_map, dict) and len(error_codes_map) > 0
    results.append((
        "EC_HAS_CODES",
        ok,
        f"{len(error_codes_map)} error codes defined" if ok
        else "No error_codes mapping found"
    ))

    # ── CHECK 11: skill_thresholds.yml exists and schema_version == 1 ──
    st_path = orch / "skill_thresholds.yml"
    if st_path.exists():
        st = load_yaml(st_path)
        st_sv = st.get("schema_version")
        ok = st_sv == 1 or st_sv == "1"
        results.append((
            "ST_SCHEMA_VERSION",
            ok,
            f"skill_thresholds.yml schema_version={st_sv}" if ok
            else f"Expected schema_version 1, got {st_sv}"
        ))
    else:
        results.append(("ST_SCHEMA_VERSION", False, "skill_thresholds.yml missing"))

    # ── CHECK 12: thresholds.minimum_fit_score <= thresholds.review_fit_score ──
    if st_path.exists():
        st = load_yaml(st_path)
        thresholds = st.get("thresholds", {})
        min_score = thresholds.get("minimum_fit_score")
        review_score = thresholds.get("review_fit_score")

        if min_score is not None and review_score is not None:
            ok = min_score <= review_score
            results.append((
                "ST_THRESHOLD_ORDER",
                ok,
                f"minimum_fit_score({min_score}) <= review_fit_score({review_score})" if ok
                else f"Invalid: minimum_fit_score({min_score}) > review_fit_score({review_score})"
            ))
        else:
            results.append(("ST_THRESHOLD_ORDER", False, "thresholds missing minimum_fit_score or review_fit_score"))
    else:
        results.append(("ST_THRESHOLD_ORDER", False, "skill_thresholds.yml missing - cannot validate thresholds"))

    # ── Issue Catalog Versioning Checks ─────────────────────
    ic_path = orch / "issue_catalog.yml"

    # ── CHECK: issue_catalog.yml exists ──
    if not ic_path.exists():
        results.append(("IC_EXISTS", False, "issue_catalog.yml missing"))
        return results

    ic = load_yaml(ic_path)

    # ── CHECK 13: issue_catalog.yml has schema_version == 1 and catalog_version ──
    ic_sv = ic.get("schema_version")
    ic_cv = ic.get("catalog_version")
    ok = (ic_sv == 1 or ic_sv == "1") and ic_cv is not None
    results.append((
        "IC_VERSION_FIELDS",
        ok,
        f"schema_version={ic_sv}, catalog_version={ic_cv}" if ok
        else f"Missing or invalid: schema_version={ic_sv}, catalog_version={ic_cv}"
    ))

    # ── CHECK 14: all issues have added_in field ──
    issues = ic.get("issues", [])
    missing_added_in: List[str] = []
    for issue in issues:
        if isinstance(issue, dict):
            key = issue.get("issue_key", "<unknown>")
            if "added_in" not in issue or issue["added_in"] is None:
                missing_added_in.append(key)
    ok = len(missing_added_in) == 0
    results.append((
        "IC_ISSUES_ADDED_IN",
        ok,
        "All issues have added_in field" if ok
        else f"Issues missing added_in: {missing_added_in[:5]}{'...' if len(missing_added_in) > 5 else ''}"
    ))

    # ── CHECK 15: effective_from is valid ISO-8601 timestamp ──
    ic_ef = ic.get("effective_from")
    iso_valid = False
    if ic_ef:
        try:
            import re
            # Basic ISO-8601 format check (YYYY-MM-DDTHH:MM:SSZ or with timezone)
            iso_pattern = re.compile(
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
            )
            iso_valid = bool(iso_pattern.match(str(ic_ef)))
        except Exception:
            iso_valid = False
    ok = iso_valid
    results.append((
        "IC_EFFECTIVE_FROM_ISO",
        ok,
        f"effective_from={ic_ef} is valid ISO-8601" if ok
        else f"Invalid or missing effective_from: {ic_ef}"
    ))

    # ── CHECK 16: constitution_v1.md exists ──
    # Path is relative to project root (parent of skillforge-spec-pack)
    constitution_path = base_path.parent / "docs" / "2026-02-16" / "constitution_v1.md"
    ok = constitution_path.exists()
    results.append((
        "CONSTITUTION_EXISTS",
        ok,
        f"constitution_v1.md exists at {constitution_path}" if ok
        else f"Missing: {constitution_path}"
    ))

    # ── CHECK 17: 不可回退架构约束_v1.md exists ──
    constraints_path = base_path.parent / "docs" / "2026-02-16" / "不可回退架构约束_v1.md"
    ok = constraints_path.exists()
    results.append((
        "CONSTRAINTS_EXISTS",
        ok,
        f"不可回退架构约束_v1.md exists at {constraints_path}" if ok
        else f"Missing: {constraints_path}"
    ))

    return results


def main():
    parser = argparse.ArgumentParser(description="GM OS Schema Validator")
    parser.add_argument("--schema", type=str, help="Schema 文件路径")
    parser.add_argument("--json", type=str, help="待校验的 JSON 文件路径")
    parser.add_argument("--all", action="store_true", help="校验所有 examples")
    parser.add_argument("--audit-config", action="store_true",
                        help="Run 17-point Audit Engine Protocol config validation")
    parser.add_argument("--base", type=str, default=".", help="项目根目录")

    args = parser.parse_args()
    base_path = Path(args.base).resolve()

    if not HAS_JSONSCHEMA and not args.audit_config:
        print("错误: 请先安装 jsonschema: pip install jsonschema")
        sys.exit(1)

    if args.audit_config:
        print("=" * 60)
        print("Audit Engine Protocol — 17-Point Config Validation")
        print("=" * 60)

        results = validate_audit_config(base_path)
        passed = 0
        failed = 0

        for check_id, ok, detail in results:
            if ok:
                print(f"  ✅ [{check_id}] {detail}")
                passed += 1
            else:
                print(f"  ❌ [{check_id}] {detail}")
                failed += 1

        print("=" * 60)
        print(f"结果: {passed} passed, {failed} failed")
        print("=" * 60)

        sys.exit(0 if failed == 0 else 1)

    elif args.all:
        print("=" * 60)
        print("校验所有 examples")
        print("=" * 60)

        results = validate_all_examples(base_path)
        passed = 0
        failed = 0

        for name, (is_valid, errors) in results.items():
            if is_valid:
                print(f"✅ {name}")
                passed += 1
            else:
                print(f"❌ {name}")
                for error in errors:
                    print(f"   - {error}")
                failed += 1

        print("=" * 60)
        print(f"结果: {passed} 通过, {failed} 失败")
        print("=" * 60)

        sys.exit(0 if failed == 0 else 1)

    elif args.schema and args.json:
        schema_path = Path(args.schema)
        data_path = Path(args.json)

        is_valid, errors = validate_file(data_path, schema_path, base_path)

        if is_valid:
            print(f"✅ 校验通过: {data_path}")
        else:
            print(f"❌ 校验失败: {data_path}")
            for error in errors:
                print(f"   - {error}")

        sys.exit(0 if is_valid else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

