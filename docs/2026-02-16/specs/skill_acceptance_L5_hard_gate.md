# skill_acceptance_L5_hard_gate

- Level: `L5 Hard Gate`
- Policy: `Fail-Closed`
- Rule: 任一项不达标 => `REJECTED`（不算过关）

## 1. Skill 定义

```yaml
skill_id: l5-hard-acceptance-gate
version: "1.0.0"
description: "对 00-70 体系执行 L5 硬性验收。任一失败立即阻断。"
mode: "read_only_audit"
pass_condition: "all_checks_pass"
fail_condition: "any_check_fail"
output_contract: "L5AcceptanceResult"
```

## 2. 输入契约

```json
{
  "project_root": "D:\\GM-SkillForge",
  "contracts_root": "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts",
  "reports": {
    "consistency": "audit_report_consistency.json",
    "boundary": "audit_report_boundary.json"
  },
  "trace_context": {
    "run_id": "string",
    "trace_id": "string"
  }
}
```

## 3. 五条硬性验收（必须全部通过）

### G1 能力可运行
- 验收对象: 4 个 Core Skills
- 通过标准:
  - `contract-common-builder` 可执行
  - `contract-module-builder` 可执行
  - `contract-consistency-auditor` 可执行
  - `governance-boundary-auditor` 可执行
- 失败即阻断: `L5.G1.RUNTIME_NOT_READY`

### G2 治理可阻断
- 验收对象: 边界审计结果
- 通过标准:
  - `audit_report_boundary.json.summary.total_violations == 0`
  - CI 配置中存在“违规即失败（exit code 1）”规则
- 失败即阻断: `L5.G2.GOVERNANCE_NOT_ENFORCED`

### G3 证据可追溯
- 验收对象: 运行与报告元数据
- 通过标准:
  - 产物和报告均包含 `run_id`
  - 产物和报告均包含 `trace_id`
  - `run_id` 与 `trace_id` 能一一映射
- 失败即阻断: `L5.G3.TRACEABILITY_BROKEN`

### G4 回放可复核
- 验收对象: 重复运行结果
- 通过标准:
  - 同输入重复运行两次，验收结论一致
  - 失败原因有确定错误码（非自由文本）
- 失败即阻断: `L5.G4.REPLAY_NOT_REPRODUCIBLE`

### G5 变更可控
- 验收对象: 契约一致性
- 通过标准:
  - `naming_conflicts == 0`
  - `broken_references == 0`
  - `missing_sections == 0`
  - `version_mismatches == 0`
- 失败即阻断: `L5.G5.CHANGE_NOT_CONTROLLED`

## 4. 输出契约

```json
{
  "status": "PASSED|REJECTED",
  "level": "L5",
  "gates": [
    {"id": "G1", "passed": true, "error_code": null},
    {"id": "G2", "passed": true, "error_code": null},
    {"id": "G3", "passed": true, "error_code": null},
    {"id": "G4", "passed": true, "error_code": null},
    {"id": "G5", "passed": true, "error_code": null}
  ],
  "summary": {
    "passed_count": 5,
    "failed_count": 0
  },
  "trace": {
    "run_id": "string",
    "trace_id": "string",
    "timestamp": "datetime"
  }
}
```

## 5. 判定规则

```text
IF any(gate.passed == false) THEN status = REJECTED
ELSE status = PASSED
```

## 6. CI 集成要求（硬门）

- 在 pipeline 末段执行 `l5-hard-acceptance-gate`
- 返回 `REJECTED` 时必须 `exit 1`
- 禁止“warning only”模式

## 7. 验收口径

- 口径: `不达标不算过关`
- 解释权: 无人工豁免；必须以审计输出为准
