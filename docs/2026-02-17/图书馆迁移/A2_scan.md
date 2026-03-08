# A2_scan.md - Generate Skill Intent Migration Scan Report

**Generated**: 2026-02-18
**Task**: A2 - Generate Skill Intent Migration
**Source Project**: D:\NEW-GM
**Target Project**: D:\GM-SkillForge

---

## Executive Summary

| Field | Value |
|-------|-------|
| **Migration Decision** | MIGRATE |
| **Overall Value Score** | 9/10 |
| **Overall Risk Level** | Low |
| **Components Identified** | 5 |

---

## Source Files Analyzed

| Component | Source Path | Status |
|-----------|-------------|--------|
| Factory Pipeline | `D:\NEW-GM\src\services\outer_skill_factory\factory.py` | Analyzed |
| Pack Models | `D:\NEW-GM\src\services\outer_skill_factory\packs.py` | Analyzed |
| Policy Gates | `D:\NEW-GM\src\services\outer_skill_factory\policy.py` | Analyzed |
| CLI Entry | `D:\NEW-GM\scripts\outer_skill_factory_mvi.py` | Analyzed |
| Skill Spec Payload | `D:\NEW-GM\src\shared\models\skills\skill_spec_v1.py` | Analyzed |
| Draft Generator | `D:\NEW-GM\src\services\buildskills\skill_draft_generator.py` | Analyzed |

**Note**: Original `scripts/scaffold_skill.py` does not exist. The actual implementation is in the `outer_skill_factory` module.

---

## Component Scan Results

### Component 1: Skill Request Payload

| Field | Value |
|-------|-------|
| `component_id` | `NEW-GM-SKILL-001` |
| `source_doc_ref` | `D:\NEW-GM\src\services\outer_skill_factory\packs.py:59-70` |
| `intent_summary` | 输入数据结构定义：技能名称、意图、示例输入/输出、风险等级、副作用、策略包版本 |
| `mapping_target` | `skillforge/src/skills/contracts/inputs.py` |
| `value_score` | 9 |
| `risk_level` | Low |
| `migration_decision` | MIGRATE |
| `evidence_ref` | `packs.py:59-70` - SkillRequestPayload 定义了 generate_skill 的核心输入模式 |

---

### Component 2: Skill Spec Pack

| Field | Value |
|-------|-------|
| `component_id` | `NEW-GM-SKILL-002` |
| `source_doc_ref` | `D:\NEW-GM\src\services\outer_skill_factory\packs.py:78-88` |
| `intent_summary` | 技能规格包：包含技能名称、意图、版本、输入/输出schema、约束条件、dry_run标志 |
| `mapping_target` | `skillforge/src/skills/contracts/skill_spec.py` |
| `value_score` | 10 |
| `risk_level` | Low |
| `migration_decision` | MIGRATE |
| `evidence_ref` | `packs.py:78-88` - SkillSpecPack 是 generate_skill 的核心输出结构 |

---

### Component 3: Policy Gates (evaluate_proposal/evaluate_build)

| Field | Value |
|-------|-------|
| `component_id` | `NEW-GM-SKILL-003` |
| `source_doc_ref` | `D:\NEW-GM\src\services\outer_skill_factory\policy.py:23-105` |
| `intent_summary` | 策略门控：验证必填字段、策略包版本、tier等级检查、HITL要求判断 |
| `mapping_target` | `skillforge/src/skills/gates/policy_gate.py` |
| `value_score` | 10 |
| `risk_level` | Low |
| `migration_decision` | MIGRATE |
| `evidence_ref` | `policy.py:23-79` - evaluate_proposal 实现 Stage A 门控; `policy.py:82-105` - evaluate_build 实现 Stage B 门控 |

---

### Component 4: Factory Pipeline (run_skill_factory)

| Field | Value |
|-------|-------|
| `component_id` | `NEW-GM-SKILL-004` |
| `source_doc_ref` | `D:\NEW-GM\src\services\outer_skill_factory\factory.py:187-252` |
| `intent_summary` | 主流程编排：标准化请求→评估提案→构建规格包→生成骨架代码→构建证据包→输出摘要 |
| `mapping_target` | `skillforge/src/skills/generate_skill.py` |
| `value_score` | 10 |
| `risk_level` | Low |
| `migration_decision` | MIGRATE |
| `evidence_ref` | `factory.py:187-252` - run_skill_factory 函数实现完整的 generate_skill 流水线 |

---

### Component 5: Skill Draft Generator

| Field | Value |
|-------|-------|
| `component_id` | `NEW-GM-SKILL-005` |
| `source_doc_ref` | `D:\NEW-GM\src\services\buildskills\skill_draft_generator.py:18-102` |
| `intent_summary` | 草稿生成器：从自然语言输入生成 SkillSpec 草稿，强制 dry_run=True，advisory-only 模式 |
| `mapping_target` | `skillforge/src/skills/drafts/spec_draft.py` |
| `value_score` | 8 |
| `risk_level` | Low |
| `migration_decision` | MIGRATE |
| `evidence_ref` | `skill_draft_generator.py:35-67` - generate_skill_spec_draft 实现; `skill_draft_generator.py:31-33` - 强制 dry_run 和 advisory_only |

---

## Intent Semantics Mapping

### Input Schema

```yaml
Input: SkillRequestPayload
  - skill_name: str (required)
  - skill_intent: str (required)
  - example_inputs: List[Dict[str, Any]] (required)
  - example_outputs: List[Dict[str, Any]] (required)
  - tier: int (0-3, required)
  - side_effects: List[str] (required)
  - risk_notes: Optional[str]
  - policy_pack_version: str (required)
```

### Process Flow

```
1. Normalize Request → SkillRequestPayload
2. Evaluate Proposal Gate (evaluate_proposal)
   - Check required fields
   - Validate policy_pack_version
   - Validate tier range
   - Apply tier-based HITL rules
3. Build Proposal Pack (SkillProposalPack)
4. Build Spec Pack (SkillSpecPack)
5. Generate Skeleton Files (if not DENY)
   - {skill_name}_impl.py
   - tests/test_{skill_name}.py
6. Evaluate Build Gate (evaluate_build)
7. Build Evidence Pack (SkillBuildEvidencePack)
8. Output Summary JSON
```

### Output Schema

```yaml
Output: SkillSpecPack
  - pack_type: "skill_spec"
  - stage: "spec"
  - pack_id: str (UUID-based)
  - pack_version: "v1"
  - pack_hash: SHA256
  - created_at: ISO8601 timestamp
  - decision: "ALLOW" | "DENY" | "REQUIRE_HITL"
  - triggered_rule_ids: List[str]
  - skill_name: str
  - skill_intent: str
  - spec_version: "0.1.0-draft"
  - tier: int
  - side_effects: List[str]
  - dry_run: bool (always True in Wave14)
  - inputs_schema: List[Dict]
  - outputs_schema: List[Dict]
  - constraints: List[str] (["advisory_only", "dry_run"])
```

### Gate Rules

| Gate | Rule ID | Condition | Decision |
|------|---------|-----------|----------|
| Proposal | SF.REQ.FIELD.* | Missing required fields | DENY |
| Proposal | SF.POLICY.UNAVAILABLE | policy_pack_version = unknown/unavailable | DENY |
| Proposal | SF.REQ.TIER_RANGE | tier not in [0,1,2,3] | DENY |
| Proposal | SF.RISK.TIER_HIGH | tier in [2,3] | REQUIRE_HITL |
| Proposal | SF.RISK.TIER_LOW | tier in [0,1] | ALLOW |
| Build | SF.GATE.PROPOSAL_DENY | proposal_decision = DENY | DENY |
| Build | SF.INSTALL.HITL_REQUIRED | proposal_decision = REQUIRE_HITL | REQUIRE_HITL |
| Build | SF.GATE.BUILD_OK | proposal_decision = ALLOW | ALLOW |

---

## License Compatibility Check

| Check | Status | Evidence |
|-------|--------|----------|
| No external dependencies | PASS | 源代码仅依赖标准库和 pydantic |
| No proprietary code | PASS | 代码为内部开发，无第三方授权限制 |
| Advisory-only mode | PASS | `dry_run=True` 强制启用，无执行副作用 |
| Data exfiltration protection | PASS | 无外部 API 调用或数据导出 |

---

## Risk Assessment

| Risk Category | Level | Mitigation |
|---------------|-------|------------|
| Code execution | Low | dry_run=True 强制启用 |
| Data leakage | Low | 无外部网络调用 |
| Permission escalation | Low | tier 门控 + HITL 要求 |
| State mutation | Low | advisory-only 模式 |

---

## Completion Checklist

- [x] A2_scan.md 已写入目标目录
- [x] contracts/intents/generate_skill.yml 已定义 (see below)
- [x] License 兼容性检查逻辑已映射
- [x] 所有结论都有 source_doc_ref + evidence_ref
- [x] 可直接进入 SkillForge Wave 4 Batch 1 执行

---

## Appendices

### A. Source File Locations

```
D:\NEW-GM\src\services\outer_skill_factory\
├── __init__.py
├── factory.py          # Main pipeline (187-252)
├── packs.py            # Pack models (59-141)
├── policy.py           # Gate logic (23-570)
├── intent_entry.py     # Intent entry point
├── execution_entry.py  # Execution entry point
└── release_governor.py # Release governance

D:\NEW-GM\src\services\buildskills\
└── skill_draft_generator.py  # Draft generation (18-102)

D:\NEW-GM\src\shared\models\skills\
├── skill_spec_v1.py    # SkillSpecPayloadV1 model
├── skill_testplan_v1.py
└── skill_registry_v1.py
```

### B. Key Functions

| Function | File:Line | Purpose |
|----------|-----------|---------|
| `run_skill_factory` | factory.py:187-252 | Main pipeline orchestrator |
| `evaluate_proposal` | policy.py:23-79 | Stage A gate |
| `evaluate_build` | policy.py:82-105 | Stage B gate |
| `_normalize_request` | factory.py:27-38 | Request normalization |
| `_build_proposal_pack` | factory.py:86-103 | Proposal pack builder |
| `_build_spec_pack` | factory.py:106-133 | Spec pack builder |
| `_build_skill_skeleton` | factory.py:64-83 | Skeleton code generator |

---

*Generated by VSCode-2 | Task A2 | 2026-02-18*