# 2026-02-22 P1 Task Dispatch（L4 能力底座）

job_id: L4-P1-FOUNDATION-20260222-002
protocol: multi-ai-collaboration.md v3
scope: P1（前端可读可用 + 契约校验 + 演示链路闭环）
owner: Codex (Orchestrator)

## 目标
1. 前端审计页面可读可用（真实数据渲染 + 排序）。
2. 前后端契约校验落地（坏数据可读报错）。
3. 演示链路闭环（5 分钟可复现）。

## 三权分立硬规则
- 无 ComplianceAttestation(PASS) 不得放行执行完成态。
- 无 EvidenceRef 不得宣称完成。
- Review 与 Execution 不可同人。

## 波次编排

| Wave | Task | Execution | Review | Compliance | Depends On | 目标 |
|---|---|---|---|---|---|---|
| 1 | T60 | Kior-A | vs--cc3 | Kior-C | - | P1-1 审计结果页 MVP 强化 |
| 1 | T61 | vs--cc1 | Kior-B | Kior-C | T60 | P1-2 契约校验与前端校验提示 |
| 2 | T62 | Antigravity-2 | vs--cc2 | Kior-C | T60,T61 | P1-3 DEMO 闭环文档与回放脚本 |
| 2 | T63 | Codex | 用户复核 | Kior-C | T60,T61,T62 | Final Gate 收口 |

## 放行条件
- T60、T61 均 ALLOW 后，才可启动 T62。
- T60-T62 三任务全部满足：execution_report + gate_decision(ALLOW) + compliance(PASS) 后，T63 才可 ALLOW。

## 验收产物
- docs/2026-02-22/tasks/T60_*.md ~ T62_*.md
- docs/2026-02-22/verification/T60_execution_report.yaml
- docs/2026-02-22/verification/T60_gate_decision.json
- docs/2026-02-22/verification/T60_compliance_attestation.json
- docs/2026-02-22/verification/T61_execution_report.yaml
- docs/2026-02-22/verification/T61_gate_decision.json
- docs/2026-02-22/verification/T61_compliance_attestation.json
- docs/2026-02-22/verification/T62_execution_report.yaml
- docs/2026-02-22/verification/T62_gate_decision.json
- docs/2026-02-22/verification/T62_compliance_attestation.json
- docs/2026-02-22/verification/final_gate_decision_p1.json
