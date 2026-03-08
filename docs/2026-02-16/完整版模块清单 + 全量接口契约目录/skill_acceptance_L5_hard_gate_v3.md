# skill_acceptance_L5_hard_gate_v3

- Level: `L5 Hard Gate`
- Policy: `Fail-Closed`
- Rule: 任一项不达标 => `REJECTED`（不算过关）
- Scope: `00_common` 到 `70_read_models` 契约体系

## 1. Skill 定义

```yaml
skill_id: l5-hard-acceptance-gate
version: "1.1.0"
description: "对 00-70 体系执行 L5 硬性验收。任一失败立即阻断。"
mode: "read_only_audit"
pass_condition: "all_checks_pass"
fail_condition: "any_check_fail"
output_contract: "L5AcceptanceResult"
```

## 2. 输入契约

```json
{
  "project_root": "<workspace_root>",
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

## 2.1 输入 Schema（强校验）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "L5AcceptanceInput",
  "type": "object",
  "required": ["project_root", "contracts_root", "reports", "trace_context"],
  "additionalProperties": false,
  "properties": {
    "project_root": { "type": "string", "minLength": 1 },
    "contracts_root": { "type": "string", "minLength": 1 },
    "reports": {
      "type": "object",
      "required": ["consistency", "boundary"],
      "additionalProperties": false,
      "properties": {
        "consistency": { "type": "string", "minLength": 1 },
        "boundary": { "type": "string", "minLength": 1 }
      }
    },
    "trace_context": {
      "type": "object",
      "required": ["run_id", "trace_id"],
      "additionalProperties": false,
      "properties": {
        "run_id": { "type": "string", "minLength": 1 },
        "trace_id": { "type": "string", "minLength": 1 }
      }
    }
  }
}
```

## 2.2 前置工件检查

- `reports.consistency` 指向文件必须存在且可读。
- `reports.boundary` 指向文件必须存在且可读。
- 任一缺失直接 `REJECTED`，错误码 `L5.INPUT.REPORT_MISSING`。

## 3. 五条硬性验收（必须全部通过）

### G1 能力可运行
- 验收对象: 4 个 Core Skills
- 机审命令:
  - `python -m skillforge.skills.contract_common_builder --help`
  - `python -m skillforge.skills.contract_module_builder --help`
  - `python -m skillforge.skills.contract_consistency_auditor --help`
  - `python -m skillforge.skills.governance_boundary_auditor --help`
- 通过标准: 4 个命令均返回 `exit code 0`
- 失败即阻断: `L5.G1.RUNTIME_NOT_READY`
- `evidence_ref`: `runtime_check_report.json`

### G2 治理可阻断
- 验收对象: 边界审计结果 + CI 配置
- 通过标准:
  - `audit_report_boundary.json.summary.total_violations == 0`
  - CI 存在“违规即失败（exit code 1）”规则
- 失败即阻断: `L5.G2.GOVERNANCE_NOT_ENFORCED`
- `evidence_ref`: `audit_report_boundary.json`

### G3 证据可追溯
- 验收对象: 运行与报告元数据
- 通过标准:
  - 报告和产物均包含 `run_id`
  - 报告和产物均包含 `trace_id`
  - `run_id` 与 `trace_id` 映射可复核
- 失败即阻断: `L5.G3.TRACEABILITY_BROKEN`
- `evidence_ref`: `traceability_report.json`

### G4 回放可复核
- 验收对象: 重复运行结果
- 机审方法:
  - 同一输入运行两次，输出 `result_a.json`、`result_b.json`
  - 仅比较字段: `status`, `gates[].id`, `gates[].passed`, `gates[].error_code`
  - 忽略字段: `timestamp`, `run_id`, `trace_id`
- 通过标准: 比较字段完全一致
- 失败即阻断: `L5.G4.REPLAY_NOT_REPRODUCIBLE`
- `evidence_ref`: `replay_diff_report.json`

### G5 变更可控
- 验收对象: 契约一致性
- 通过标准:
  - `naming_conflicts == 0`
  - `broken_references == 0`
  - `missing_sections == 0`
  - `version_mismatches == 0`
- 失败即阻断: `L5.G5.CHANGE_NOT_CONTROLLED`
- `evidence_ref`: `audit_report_consistency.json`

## 4. 输出契约

```json
{
  "status": "PASSED|REJECTED",
  "level": "L5",
  "gates": [
    {
      "id": "G1",
      "passed": true,
      "error_code": null,
      "evidence_ref": "runtime_check_report.json",
      "check_id": "G1-RUN-001"
    },
    {
      "id": "G2",
      "passed": true,
      "error_code": null,
      "evidence_ref": "audit_report_boundary.json",
      "check_id": "G2-GOV-001"
    },
    {
      "id": "G3",
      "passed": true,
      "error_code": null,
      "evidence_ref": "traceability_report.json",
      "check_id": "G3-TRC-001"
    },
    {
      "id": "G4",
      "passed": true,
      "error_code": null,
      "evidence_ref": "replay_diff_report.json",
      "check_id": "G4-RPL-001"
    },
    {
      "id": "G5",
      "passed": true,
      "error_code": null,
      "evidence_ref": "audit_report_consistency.json",
      "check_id": "G5-CHG-001"
    }
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

## 4.1 输出 Schema（强校验）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "L5AcceptanceResult",
  "type": "object",
  "required": ["status", "level", "gates", "summary", "trace"],
  "additionalProperties": false,
  "properties": {
    "status": { "type": "string", "enum": ["PASSED", "REJECTED"] },
    "level": { "type": "string", "enum": ["L5"] },
    "gates": {
      "type": "array",
      "minItems": 5,
      "maxItems": 5,
      "items": {
        "type": "object",
        "required": ["id", "passed", "error_code", "evidence_ref", "check_id"],
        "additionalProperties": false,
        "properties": {
          "id": { "type": "string", "enum": ["G1", "G2", "G3", "G4", "G5"] },
          "passed": { "type": "boolean" },
          "error_code": { "type": ["string", "null"] },
          "evidence_ref": { "type": "string", "minLength": 1 },
          "check_id": { "type": "string", "minLength": 1 }
        }
      }
    },
    "summary": {
      "type": "object",
      "required": ["passed_count", "failed_count"],
      "additionalProperties": false,
      "properties": {
        "passed_count": { "type": "integer", "minimum": 0, "maximum": 5 },
        "failed_count": { "type": "integer", "minimum": 0, "maximum": 5 }
      }
    },
    "trace": {
      "type": "object",
      "required": ["run_id", "trace_id", "timestamp"],
      "additionalProperties": false,
      "properties": {
        "run_id": { "type": "string", "minLength": 1 },
        "trace_id": { "type": "string", "minLength": 1 },
        "timestamp": { "type": "string", "format": "date-time" }
      }
    }
  }
}
```

## 5. 判定规则

```text
IF any(gate.passed == false) THEN status = REJECTED
ELSE status = PASSED
```

## 6. 执行命令与退出码

### 6.1 执行命令

```bash
python -m skillforge.skills.l5_hard_acceptance_gate --input-file config/l5_acceptance_input.json --output l5_acceptance_result.json
```

### 6.2 退出码约定

- `0`: `PASSED`
- `1`: `REJECTED`
- `2`: 输入 schema 校验失败
- `3`: 报告文件缺失或不可读

## 7. CI 集成要求（硬门）

- 在 pipeline 末段执行 `l5-hard-acceptance-gate`。
- 返回 `REJECTED` 必须 `exit 1`。
- 禁止 `warning only` 模式。

## 8. 错误码表

- `L5.G1.RUNTIME_NOT_READY`
- `L5.G2.GOVERNANCE_NOT_ENFORCED`
- `L5.G3.TRACEABILITY_BROKEN`
- `L5.G4.REPLAY_NOT_REPRODUCIBLE`
- `L5.G5.CHANGE_NOT_CONTROLLED`
- `L5.INPUT.REPORT_MISSING`
- `L5.INPUT.SCHEMA_INVALID`

## 9. 最小样例

### 9.1 PASSED 样例

```json
{
  "status": "PASSED",
  "level": "L5",
  "gates": [
    {"id":"G1","passed":true,"error_code":null,"evidence_ref":"runtime_check_report.json","check_id":"G1-RUN-001"},
    {"id":"G2","passed":true,"error_code":null,"evidence_ref":"audit_report_boundary.json","check_id":"G2-GOV-001"},
    {"id":"G3","passed":true,"error_code":null,"evidence_ref":"traceability_report.json","check_id":"G3-TRC-001"},
    {"id":"G4","passed":true,"error_code":null,"evidence_ref":"replay_diff_report.json","check_id":"G4-RPL-001"},
    {"id":"G5","passed":true,"error_code":null,"evidence_ref":"audit_report_consistency.json","check_id":"G5-CHG-001"}
  ],
  "summary": {"passed_count":5,"failed_count":0},
  "trace": {"run_id":"run-001","trace_id":"trace-001","timestamp":"2026-02-17T09:00:00Z"}
}
```

### 9.2 REJECTED 样例（G2 失败）

```json
{
  "status": "REJECTED",
  "level": "L5",
  "gates": [
    {"id":"G1","passed":true,"error_code":null,"evidence_ref":"runtime_check_report.json","check_id":"G1-RUN-001"},
    {"id":"G2","passed":false,"error_code":"L5.G2.GOVERNANCE_NOT_ENFORCED","evidence_ref":"audit_report_boundary.json","check_id":"G2-GOV-001"},
    {"id":"G3","passed":true,"error_code":null,"evidence_ref":"traceability_report.json","check_id":"G3-TRC-001"},
    {"id":"G4","passed":true,"error_code":null,"evidence_ref":"replay_diff_report.json","check_id":"G4-RPL-001"},
    {"id":"G5","passed":true,"error_code":null,"evidence_ref":"audit_report_consistency.json","check_id":"G5-CHG-001"}
  ],
  "summary": {"passed_count":4,"failed_count":1},
  "trace": {"run_id":"run-002","trace_id":"trace-002","timestamp":"2026-02-17T09:15:00Z"}
}
```

## 10. 验收口径

- 口径: `不达标不算过关`
- 无人工豁免，必须以审计输出为准。
