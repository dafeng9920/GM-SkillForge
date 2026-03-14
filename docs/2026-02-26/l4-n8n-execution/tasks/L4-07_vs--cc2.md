# L4-07 任务卡（vs--cc2）

## 目标
把 L4 最小链路接入 CI smoke gate（失败即阻断）。

## 依赖
- L4-06 = ALLOW + PASS

## 交付
- `docs/2026-02-26/l4-n8n-execution/verification/L4-07_execution_report.yaml`
- `docs/2026-02-26/l4-n8n-execution/verification/L4-07_gate_decision.json`
- `docs/2026-02-26/l4-n8n-execution/verification/L4-07_compliance_attestation.json`

## DoD
1. CI 中可触发 L4 smoke。
2. smoke 失败时 fail-closed。

