# Task Dispatch Fastlane Template

job_id: <JOB_ID>
protocol: multi-ai-collaboration.md v3
owner: Codex (Orchestrator)
mode: batch-fastlane
goal: <GOAL>

## 三权分立（MUST）

- Execution：按任务实名绑定
- Review：集中批审（按波次）
- Compliance：集中批审（按波次）
- 缺 `execution_report + gate_decision + compliance_attestation` 直接 `DENY`

## Fastlane 波次模板

### Wave X - Execution（并行）

| Task | Executor | 输出 |
|---|---|---|
| Txx | <name> | `Txx_execution_report.yaml` |
| Txy | <name> | `Txy_execution_report.yaml` |
| Txz | <name> | `Txz_execution_report.yaml` |

放行到 Review 条件：
- 本波次执行任务的 `execution_report` 全部到齐。

### Wave X - Review（集中）

Reviewer: `<name>`

| Task | 输出 |
|---|---|
| Txx | `Txx_gate_decision.json` |
| Txy | `Txy_gate_decision.json` |
| Txz | `Txz_gate_decision.json` |

放行到 Compliance 条件：
- 本波次 `gate_decision` 全部为 `ALLOW`。

### Wave X - Compliance（集中）

Compliance: `<name>`

| Task | 输出 |
|---|---|
| Txx | `Txx_compliance_attestation.json` |
| Txy | `Txy_compliance_attestation.json` |
| Txz | `Txz_compliance_attestation.json` |

放行到下一波次条件：
- 本波次 `compliance_attestation.decision` 全部为 `PASS`。

## 自动降级规则（强制）

任一任务出现以下高风险关键词，调度自动降级为 `strict`：
- `shell`, `shell_execution`
- `delete`, `file_delete`, `rm`
- `db`, `database`, `drop table`, `truncate`
- `network`, `外网调用`

## 验收产物路径

- `docs/{date}/verification/Txx_execution_report.yaml`
- `docs/{date}/verification/Txx_gate_decision.json`
- `docs/{date}/verification/Txx_compliance_attestation.json`
- `docs/{date}/verification/final_gate_decision.json`

