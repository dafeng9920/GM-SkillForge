两份可直接落盘的 v1 最小版 YAML（术语与 AUDIT_ENGINE_PROTOCOL_v1.md 对齐），并且做到：

L1–L5：MUST/SHOULD + 阈值 + required_changes 模板

8 节点 gate：统一 action_id、统一 suggested_fixes.kind 枚举、每个 fail 都有 error_code + next_action

说明：error_code 这里按“你们会在 error_codes.yml 里定义”的方式引用；今晚你们把 error_codes.yml 补齐即可。先把 policy 联动骨架钉死。

# orchestration/quality_gate_levels.yml
version: "0.1.0"
title: "GM-SkillForge Quality Gate Levels"
description: >
  Defines pass/fail criteria for L1-L5. The Orchestrator MUST evaluate gates and
  produce required_changes when a level fails. L3 is the commercial baseline.
commercial_baseline_level: "L3"

levels:
  L1:
    title: "Entry"
    intent: "Structure complete, loadable, zero syntax errors."
    must:
      - id: "QG_L1_SCHEMA_VALID"
        description: "All JSON/YAML schema files are syntactically valid and parseable."
        check: "schemas_valid"
      - id: "QG_L1_MIN_DOC"
        description: "Skill has minimal identity fields."
        check: "has_min_identity_fields"
        fields_required: ["skill_id", "name", "description"]
      - id: "QG_L1_EXAMPLES_PRESENT"
        description: "At least 1 example input exists for primary capability."
        check: "examples_count"
        thresholds: { min_examples: 1 }
      - id: "QG_L1_ISSUE_KEYS_VALID"
        description: "Any issue_key appearing in examples/findings must exist in issue_catalog."
        check: "issue_keys_in_catalog"
    should:
      - id: "QG_L1_README_PRESENT"
        description: "README exists for human context."
        check: "file_exists"
        params: { path: "README.md" }
    thresholds: {}
    required_changes_templates:
      - id: "RC_L1_ADD_MIN_FIELDS"
        when_failed_check: "has_min_identity_fields"
        message: "Add missing identity fields: {missing_fields}."
        patch_targets: ["manifest", "skill_spec"]
      - id: "RC_L1_FIX_SCHEMA"
        when_failed_check: "schemas_valid"
        message: "Fix schema parse errors in: {invalid_files}."
        patch_targets: ["schemas/*"]
      - id: "RC_L1_ADD_EXAMPLE"
        when_failed_check: "examples_count"
        message: "Add at least {min_examples} valid example(s) under examples/."
        patch_targets: ["examples/*"]

  L2:
    title: "Standard"
    intent: "Cross-artifact consistency + basic UX for integrators."
    must:
      - id: "QG_L2_CONTRACT_CONSISTENT"
        description: "input_schema/output_schema/examples are consistent (fields/types)."
        check: "contract_consistency"
      - id: "QG_L2_CONTROLS_DECLARED"
        description: "Control fields adhere to controls_catalog whitelist and defaults."
        check: "controls_whitelist_and_defaults"
      - id: "QG_L2_ERROR_POLICY_LINKED"
        description: "Error policy entries exist for all pipeline nodes used."
        check: "error_policy_complete_for_nodes"
        params: { nodes_required: ["intake_repo","license_gate","repo_scan_fit_score","draft_skill_spec","constitution_risk_gate","scaffold_skill_impl","sandbox_test_and_trace","pack_audit_and_publish"] }
    should:
      - id: "QG_L2_DEPENDENCIES_DECLARED"
        description: "Dependencies are declared (requirements/lockfile) when code exists."
        check: "dependencies_declared_if_code"
    thresholds:
      max_controls_per_tool: 12
    required_changes_templates:
      - id: "RC_L2_FIX_CONTRACT_MISMATCH"
        when_failed_check: "contract_consistency"
        message: "Align schemas/examples: {mismatch_summary}."
        patch_targets: ["schemas/*", "examples/*"]
      - id: "RC_L2_FIX_CONTROLS"
        when_failed_check: "controls_whitelist_and_defaults"
        message: "Replace/Remove non-whitelisted controls: {bad_controls}; apply defaults from controls_catalog."
        patch_targets: ["orchestration/controls_catalog.yml", "schemas/*"]
      - id: "RC_L2_ADD_ERROR_POLICY"
        when_failed_check: "error_policy_complete_for_nodes"
        message: "Add missing error_policy entries for nodes: {missing_nodes}."
        patch_targets: ["orchestration/error_policy.yml"]

  L3:
    title: "Trusted"
    intent: "Commercial baseline: static risk gates + evidence chain + provenance."
    must:
      - id: "QG_L3_PROVENANCE_PRESENT"
        description: "original_repo_snapshot.json includes source/id/version/fetched_at/snapshot_hash."
        check: "provenance_present"
      - id: "QG_L3_STATIC_SCAN_PASS"
        description: "Static scan completed; no BLOCKER findings remain unresolved."
        check: "static_scan_no_blockers"
      - id: "QG_L3_POLICY_MATRIX_PRESENT"
        description: "policy_matrix.json exists and all findings bind issue_key + evidence_ref."
        check: "policy_matrix_complete"
      - id: "QG_L3_EVIDENCE_CLOSED_LOOP"
        description: "Every evidence_ref resolves to evidence.jsonl (or evidence/)."
        check: "evidence_refs_resolve"
      - id: "QG_L3_AUDIT_PACK_MIN"
        description: "L3 audit pack MUST files present."
        check: "audit_pack_files_present"
        params:
          required_files:
            - "manifest.json"
            - "policy_matrix.json"
            - "static_analysis.log"
            - "original_repo_snapshot.json"
            - "repro_env.yml"
            - "evidence.jsonl"
    should:
      - id: "QG_L3_DIFF_PRESENT_IF_PATCHED"
        description: "If any modifications were made, source_lineage.diff must exist."
        check: "diff_present_if_patched"
    thresholds:
      max_blockers: 0
      max_high: 5
    required_changes_templates:
      - id: "RC_L3_ADD_PROVENANCE"
        when_failed_check: "provenance_present"
        message: "Add provenance fields to original_repo_snapshot.json: {missing_fields}."
        patch_targets: ["original_repo_snapshot.json"]
      - id: "RC_L3_FIX_BLOCKERS"
        when_failed_check: "static_scan_no_blockers"
        message: "Resolve BLOCKER findings: {blocker_list}. Provide evidence for fixes."
        patch_targets: ["code", "policies", "wrappers"]
      - id: "RC_L3_CLOSE_EVIDENCE_LOOP"
        when_failed_check: "evidence_refs_resolve"
        message: "Add missing evidence records for refs: {missing_evidence_refs}."
        patch_targets: ["evidence.jsonl", "policy_matrix.json"]
      - id: "RC_L3_ADD_AUDIT_PACK_FILES"
        when_failed_check: "audit_pack_files_present"
        message: "Create missing L3 audit pack files: {missing_files}."
        patch_targets: ["audit_pack/*"]

  L4:
    title: "Pro"
    intent: "Performance transparency + repeatable benchmarks (mid-cost)."
    must:
      - id: "QG_L4_SMOKE_EXECUTION"
        description: "Sandbox smoke test executed with isolation; produces run_trace summary."
        check: "smoke_run_trace_present"
      - id: "QG_L4_BENCHMARK_PRESENT"
        description: "harness_benchmark.json exists with p95/success_rate/resource peaks."
        check: "benchmark_present_and_valid"
      - id: "QG_L4_VECTOR_META"
        description: "vectors_meta.json (or equivalent) describes dataset_type/seed/run_count."
        check: "vectors_meta_present"
    should:
      - id: "QG_L4_CONCURRENCY_CALIBRATION"
        description: "Calibration report for max_safe_concurrency exists."
        check: "concurrency_calibration_present"
    thresholds:
      min_success_rate: 0.99
      max_p95_ms: 2000
      max_error_rate: 0.01
      min_runs: 20
      max_runs: 100
    required_changes_templates:
      - id: "RC_L4_ADD_SMOKE_TRACE"
        when_failed_check: "smoke_run_trace_present"
        message: "Add sandbox smoke test + run_trace summary with isolation config."
        patch_targets: ["sandbox/*", "run_trace.jsonl"]
      - id: "RC_L4_FIX_BENCHMARK"
        when_failed_check: "benchmark_present_and_valid"
        message: "Generate harness_benchmark.json and meet thresholds (success_rate/p95)."
        patch_targets: ["benchmarks/*"]
      - id: "RC_L4_ADD_VECTOR_META"
        when_failed_check: "vectors_meta_present"
        message: "Add vectors_meta.json describing dataset_type/seed/run_count."
        patch_targets: ["vectors_meta.json"]

  L5:
    title: "Industrial"
    intent: "High determinism + large sample regression; only for curated targets."
    must:
      - id: "QG_L5_STRESS_VECTORS"
        description: "stress_test_vectors.csv exists with >= min_vectors rows (mock/safe)."
        check: "stress_vectors_count"
        thresholds: { min_vectors: 1000 }
      - id: "QG_L5_LONGRUN_BENCHMARK"
        description: "Long-run benchmark present (duration, stability, resource fragmentation notes)."
        check: "longrun_benchmark_present"
      - id: "QG_L5_DETERMINISM"
        description: "Determinism check: same input seed yields bounded variance."
        check: "determinism_within_bounds"
      - id: "QG_L5_SIGNED_PACK"
        description: "Audit pack is signed (signature.asc) and manifest contains file hashes."
        check: "signature_and_manifest_integrity"
    should:
      - id: "QG_L5_EDGE_CASES"
        description: "Edge-case suite >= target count."
        check: "edge_case_count"
        thresholds: { min_edge_cases: 200 }
    thresholds:
      min_success_rate: 0.9999
      max_p95_ms: 1500
      max_trace_variance: 0.01
      max_crash_rate: 0.0001
      min_vectors: 1000
    required_changes_templates:
      - id: "RC_L5_ADD_STRESS_VECTORS"
        when_failed_check: "stress_vectors_count"
        message: "Add stress_test_vectors.csv with >= {min_vectors} safe mock vectors."
        patch_targets: ["stress_test_vectors.csv"]
      - id: "RC_L5_ADD_SIGNING"
        when_failed_check: "signature_and_manifest_integrity"
        message: "Add signature.asc and ensure manifest.json hashes match files."
        patch_targets: ["signature.asc", "manifest.json"]
      - id: "RC_L5_TIGHTEN_DETERMINISM"
        when_failed_check: "determinism_within_bounds"
        message: "Reduce variance: pin deps, seed randomness, isolate time/network, add replay harness."
        patch_targets: ["repro_env.yml", "harness/*"]
----------------------
orchestration/error_codes.yml：
# orchestration/error_codes.yml
schema_version: 1

# Optional shared enums (UI / validate.py can use these as canonical sets)
enums:
  category: [INTAKE, LICENSE, SCAN, CONTRACT, RISK, SCAFFOLD, SANDBOX, PACK]
  severity: [INFO, WARN, ERROR, BLOCKER]

error_codes:
  # ===== Gate: intake_repo =====
  SF_INTAKE_REPO_FAILED:
    code: SF_INTAKE_REPO_FAILED
    http_status: 400
    severity: BLOCKER
    category: INTAKE
    title: "Repository intake failed"
    default_user_message: "无法接入仓库：请检查仓库地址与访问权限。"
    developer_hint: "Validate repo URL/SSH string; check auth token/SSH key; verify network/DNS; ensure repo exists and is reachable."
    doc: "docs/errors/SF_INTAKE_REPO_FAILED.md"
    i18n:
      title_key: "error.SF_INTAKE_REPO_FAILED.title"
      message_key: "error.SF_INTAKE_REPO_FAILED.message"

  # ===== Gate: license_gate =====
  SF_LICENSE_DENIED:
    code: SF_LICENSE_DENIED
    http_status: 403
    severity: BLOCKER
    category: LICENSE
    title: "License gate denied"
    default_user_message: "许可证门禁未通过：该仓库许可不满足发布或使用要求。"
    developer_hint: "Detect license (SPDX); ensure allowed list; if missing/ambiguous, add LICENSE file or explicit SPDX identifier."
    doc: "docs/errors/SF_LICENSE_DENIED.md"
    i18n:
      title_key: "error.SF_LICENSE_DENIED.title"
      message_key: "error.SF_LICENSE_DENIED.message"

  # ===== Gate: repo_scan_fit_score =====
  SF_SCAN_FIT_SCORE_LOW:
    code: SF_SCAN_FIT_SCORE_LOW
    http_status: 422
    severity: ERROR
    category: SCAN
    title: "Repository scan fit score too low"
    default_user_message: "仓库扫描适配度不足：请按建议修复后重试。"
    developer_hint: "Surface scan signals: missing structure, unsupported language, missing required files; include computed fit_score and thresholds in EvidenceRef."
    doc: "docs/errors/SF_SCAN_FIT_SCORE_LOW.md"
    i18n:
      title_key: "error.SF_SCAN_FIT_SCORE_LOW.title"
      message_key: "error.SF_SCAN_FIT_SCORE_LOW.message"

  # ===== Gate: draft_skill_spec =====
  SF_CONTRACT_DRAFT_INVALID:
    code: SF_CONTRACT_DRAFT_INVALID
    http_status: 422
    severity: ERROR
    category: CONTRACT
    title: "Skill contract draft invalid"
    default_user_message: "Skill 合约草案不满足 contracts-first 约束：请补齐必填字段并修正格式。"
    developer_hint: "Validate required contract fields, IssueKey format, EvidenceRef placeholders, and required_changes_templates alignment with quality_gate_levels.yml."
    doc: "docs/errors/SF_CONTRACT_DRAFT_INVALID.md"
    i18n:
      title_key: "error.SF_CONTRACT_DRAFT_INVALID.title"
      message_key: "error.SF_CONTRACT_DRAFT_INVALID.message"

  # ===== Gate: constitution_risk_gate =====
  SF_RISK_CONSTITUTION_BLOCKED:
    code: SF_RISK_CONSTITUTION_BLOCKED
    http_status: 409
    severity: BLOCKER
    category: RISK
    title: "Constitution risk gate blocked"
    default_user_message: "风险门禁拦截：请求触发宪法级限制，需要调整实现范围或添加必要的安全约束。"
    developer_hint: "Attach decision rationale and minimal EvidenceRef pack; map to Level (L3/L4/L5) constraints; ensure denial includes next_action."
    doc: "docs/errors/SF_RISK_CONSTITUTION_BLOCKED.md"
    i18n:
      title_key: "error.SF_RISK_CONSTITUTION_BLOCKED.title"
      message_key: "error.SF_RISK_CONSTITUTION_BLOCKED.message"

  # ===== Gate: scaffold_skill_impl =====
  SF_SCAFFOLD_GENERATION_FAILED:
    code: SF_SCAFFOLD_GENERATION_FAILED
    http_status: 500
    severity: ERROR
    category: SCAFFOLD
    title: "Skill scaffold generation failed"
    default_user_message: "Skill 脚手架生成失败：请查看构建日志并按建议修复。"
    developer_hint: "Include generator trace, template revision, and file diff summary in EvidenceRef; ensure deterministic outputs under Revision."
    doc: "docs/errors/SF_SCAFFOLD_GENERATION_FAILED.md"
    i18n:
      title_key: "error.SF_SCAFFOLD_GENERATION_FAILED.title"
      message_key: "error.SF_SCAFFOLD_GENERATION_FAILED.message"

  # ===== Gate: sandbox_test_and_trace =====
  SF_SANDBOX_TEST_FAILED:
    code: SF_SANDBOX_TEST_FAILED
    http_status: 422
    severity: ERROR
    category: SANDBOX
    title: "Sandbox test and trace failed"
    default_user_message: "沙盒测试未通过：需要补齐可复现的测试与审计轨迹。"
    developer_hint: "Require minimal test + trace; attach failing test output and trace EvidenceRef; ensure trace includes IssueKey linkage."
    doc: "docs/errors/SF_SANDBOX_TEST_FAILED.md"
    i18n:
      title_key: "error.SF_SANDBOX_TEST_FAILED.title"
      message_key: "error.SF_SANDBOX_TEST_FAILED.message"

  # ===== Gate: pack_audit_and_publish =====
  SF_PACK_AUDIT_FAILED:
    code: SF_PACK_AUDIT_FAILED
    http_status: 422
    severity: ERROR
    category: PACK
    title: "Audit pack assemble/publish failed"
    default_user_message: "审计包组装或发布失败：缺少最小 AuditPack 文件集合或证据链不闭环。"
    developer_hint: "Verify required AuditPack files for Level; ensure EvidenceRef resolves; verify snapshot/index revision and tombstone metadata."
    doc: "docs/errors/SF_PACK_AUDIT_FAILED.md"
    i18n:
      title_key: "error.SF_PACK_AUDIT_FAILED.title"
      message_key: "error.SF_PACK_AUDIT_FAILED.message"

  # ===== Generic codes (allowed extras): =====
  # Use when YAML/schema validation fails before any Gate-specific evaluation.
  SF_VALIDATION_ERROR:
    code: SF_VALIDATION_ERROR
    http_status: 400
    severity: ERROR
    category: CONTRACT
    title: "Configuration validation error"
    default_user_message: "配置校验失败：请修正配置文件格式或缺失字段。"
    developer_hint: "Raised by validate.py on schema mismatch; include file path and JSON-pointer style location."
    i18n:
      title_key: "error.SF_VALIDATION_ERROR.title"
      message_key: "error.SF_VALIDATION_ERROR.message"
    generic: true

  # Use only for unexpected exceptions; should never replace a specific Gate code if determinable.
  SF_INTERNAL_ERROR:
    code: SF_INTERNAL_ERROR
    http_status: 500
    severity: BLOCKER
    category: PACK
    title: "Internal error"
    default_user_message: "系统内部错误：请稍后重试或联系维护者。"
    developer_hint: "Catch-all for unhandled exceptions; must attach stack trace, Revision, and at_time context in EvidenceRef when available."
    i18n:
      title_key: "error.SF_INTERNAL_ERROR.title"
      message_key: "error.SF_INTERNAL_ERROR.message"
    generic: true
-----------------
validate.py 校验要点（<=10条）

载入 orchestration/error_policy.yml 与 orchestration/error_codes.yml，校验 error_codes.yml.schema_version == 1 且存在 error_codes 映射。

收集 error_policy.yml 中所有 error_code（遍历 8 个 Gate 节点的 fail/deny 分支），断言 每一个都在 error_codes.yml.error_codes 中存在同名 reminder（精确匹配）。

反向检查：error_codes.yml 中除 generic: true 的通用码外，不允许出现未被 error_policy.yml 引用的 code（实现“不多不少”，通用码例外）。

校验 error_policy.yml.nodes 只能取这 8 个值之一：intake_repo, license_gate, repo_scan_fit_score, draft_skill_spec, constitution_risk_gate, scaffold_skill_impl, sandbox_test_and_trace, pack_audit_and_publish。

对每个节点：若存在 fail/deny 定义，必须包含 error_code, title, reason, next_action, suggested_fixes, required_changes（字段缺失即 SF_VALIDATION_ERROR）。

校验 suggested_fixes 为数组；其中每项的 kind 必须属于稳定枚举（从配置常量导入），否则报 SF_VALIDATION_ERROR。

校验 required_changes 为数组；每项至少具备可定位字段（如 path/target + instruction），且与 quality_gate_levels.yml.required_changes_templates 的占位符/模板语法兼容（最小：能做字符串渲染）。

校验 error_codes.yml 每个条目至少包含：code, category, severity，并满足 category ∈ enums.category、severity ∈ enums.severity；http_status 若存在必须为整数且在 100–599。

校验 error_codes.yml 中 code 字段必须与其 key 完全一致（避免 UI/索引分裂）。