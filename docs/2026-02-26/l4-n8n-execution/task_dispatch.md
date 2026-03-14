# 2026-02-26 Task Dispatch（L4 n8n 最小闭环）

job_id: L4-N8N-MVP-20260226-001  
mode: strict  
owner: Codex (Orchestrator)  
protocol: multi-ai-collaboration.md v3

## 0. 强制规则

1. 顺序固定：`Review -> Compliance -> Execution`
2. 无 `ComplianceAttestation(PASS)` 不得执行
3. 涉及副作用操作时，无 `permit=VALID` 不得执行
4. 无 `EvidenceRef` 不得宣称完成
5. 调度策略：`Wave内并发，Wave间门禁`

## 1. 本轮目标（L4 最小实现）

1. 打通一次 `Diagnosis -> AEV` 端到端链路（含 evidence_ref）。
2. 完成 n8n 接入最小闭环（触发、收敛、报告、CI smoke）。
3. 输出最终裁决：`docs/2026-02-26/l4-n8n-execution/verification/final_gate_decision.json`。

## 2. 波次编排（可直接转发）

| Wave | Task | Execution | Review | Compliance | Depends On | 目标 |
|---|---|---|---|---|---|---|
| 1 | L4-01 | Antigravity-2 | vs--cc2 | Kior-C | - | n8n 接入契约与输入输出结构冻结 |
| 1 | L4-02 | vs--cc1 | Antigravity-2 | Kior-C | L4-01 | n8n 触发入口与桥接脚本 |
| 1 | L4-03 | vs--cc3 | Kior-A | Kior-C | L4-01 | Diagnosis.json 标准输出（含 evidence_ref） |
| 2 | L4-04 | Kior-B | vs--cc3 | Kior-C | L4-02,L4-03 | AEV 计算模块接入（四象限） |
| 2 | L4-05 | Antigravity-1 | vs--cc1 | Kior-C | L4-04 | AEV 报告输出（JSON+MD） |
| 2 | L4-06 | Kior-A | Antigravity-1 | Kior-C | L4-05 | 单条真实 run 复核（Diagnosis->AEV） |
| 3 | L4-07 | vs--cc2 | Kior-B | Antigravity-2 | L4-06 | CI smoke gate 接入 L4 最小链路 |
| 3 | L4-08 | Codex | 用户复核 | Kior-C | L4-01~L4-07 | 最终 Gate 裁决与封板建议 |

## 3. 任务卡索引

- `docs/2026-02-26/l4-n8n-execution/tasks/L4-01_Antigravity-2.md`
- `docs/2026-02-26/l4-n8n-execution/tasks/L4-02_vs--cc1.md`
- `docs/2026-02-26/l4-n8n-execution/tasks/L4-03_vs--cc3.md`
- `docs/2026-02-26/l4-n8n-execution/tasks/L4-04_Kior-B.md`
- `docs/2026-02-26/l4-n8n-execution/tasks/L4-05_Antigravity-1.md`
- `docs/2026-02-26/l4-n8n-execution/tasks/L4-06_Kior-A.md`
- `docs/2026-02-26/l4-n8n-execution/tasks/L4-07_vs--cc2.md`
- `docs/2026-02-26/l4-n8n-execution/tasks/L4-08_Codex.md`

## 4. 一键转发模板

```text
[L4 Dispatch] {TASK_ID} / {ROLE}
job_id: L4-N8N-MVP-20260226-001
mode: strict (Review -> Compliance -> Execution)
task_card: docs/2026-02-26/l4-n8n-execution/tasks/{TASK_FILE}

硬约束：
1) 无 Compliance PASS 不得执行
2) 无 permit=VALID 不得做副作用操作
3) 无 EvidenceRef 不得宣称完成

回传三件套：
- docs/2026-02-26/l4-n8n-execution/verification/{TASK_ID}_execution_report.yaml
- docs/2026-02-26/l4-n8n-execution/verification/{TASK_ID}_gate_decision.json
- docs/2026-02-26/l4-n8n-execution/verification/{TASK_ID}_compliance_attestation.json
```

## 5. 放行规则

1. Wave 1 全部 `ALLOW` 才可进入 Wave 2
2. Wave 2 全部 `ALLOW` 才可进入 Wave 3
3. 任一任务缺三件套：`DENY`
4. 任一任务 `compliance != PASS`：`REQUIRES_CHANGES`
5. 任一任务无 `EvidenceRef`：`REQUIRES_CHANGES`

