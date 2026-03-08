# {TITLE}

job_id: {JOB_ID}
protocol: multi-ai-collaboration.md v3
owner: Codex (Orchestrator)
goal: <replace-with-goal>

## 三权分立（MUST）

- Review 总负责: <name>
- Compliance 总负责: <name>
- Execution 按任务实名绑定（见下表）
- 任一任务缺 `execution_report + gate_decision + compliance_attestation` 即 `DENY`。

## 波次编排（任务编号化 Txx）

| Wave | Task | 模块 | 主责（实名） | 审查人 | 合规人 | Depends On | 输出 |
|---|---|---|---|---|---|---|---|
| 1 | T90 | <module> | <executor> (Execution) | <reviewer> | <compliance> | - | `T90_execution_report.yaml` |

## 每任务统一验收口径

1. `execution_report`：包含 `PreflightChecklist / ExecutionContract / RequiredChanges`。
2. `gate_decision`：包含 `decision / reasons / evidence_refs / required_changes`。
3. `compliance_attestation`：包含 `decision / violations / evidence_refs / required_changes`。
4. 所有任务必须可追溯到 `run_id` 与 `policy_version`。

## 验收产物（统一路径）

- `docs/{DATE}/verification/T90_execution_report.yaml`
- `docs/{DATE}/verification/T90_gate_decision.json`
- `docs/{DATE}/verification/T90_compliance_attestation.json`
- `docs/{DATE}/verification/<batch>_final_gate_decision.json`

