# 2026-02-22 Task Dispatch（L3 收官日）

job_id: L3-CLOSING-20260222-001
protocol: multi-ai-collaboration.md v3
constitution:
  - docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md
  - docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md
owner: Codex (Orchestrator)

## 今日目标
1. 完成 P0 全部项：审计入口、策略版本化、证据链、CI smoke gate。
2. 完成 P1 核心闭环：审计结果页 MVP + 前后端契约 + Demo 步骤。
3. 产出 L3 收官验收文件：`verification/final_gate_decision.json`。

## 三权分立硬规则（全任务适用）
- 无 `ComplianceAttestation(PASS)` 不得执行。
- 涉及副作用动作时，无 `permit=VALID` 不得执行。
- 无 `EvidenceRef` 不得宣称完成。

## 波次编排

| Wave | Task | Execution | Review | Compliance | Depends On | 目标 |
|---|---|---|---|---|---|---|
| 1 | T50 | vs--cc1 | vs--cc2 | Kior-C | - | P0-2 策略配置化 |
| 1 | T51 | vs--cc3 | Kior-A | Kior-C | T50 | P0-1 统一命令入口 |
| 1 | T52 | Kior-B | vs--cc1 | Kior-C | T50 | P0-3 证据链标准输出 |
| 2 | T53 | vs--cc2 | Kior-A | Kior-C | T51,T52 | P0-4 CI smoke gate |
| 2 | T54 | Kior-A | vs--cc3 | Kior-C | T51,T52 | P1-1 审计结果页 MVP |
| 2 | T55 | vs--cc1 | Kior-B | Kior-C | T54 | P1-2 契约与校验 |
| 3 | T56 | Kior-C | vs--cc2 | Kior-B | T53,T54,T55 | P1-3 Demo 脚本 |
| 3 | T57 | Codex | 用户复核 | Kior-C | T50~T56 | 最终 Gate 验收 |

## 放行规则
- Wave 1 全部 `ALLOW` 才可进入 Wave 2。
- Wave 2 全部 `ALLOW` 才可进入 Wave 3。
- 任一任务 `REQUIRES_CHANGES`：仅回滚该任务，不回滚其他已 ALLOW 任务。

## 验收产物目录
- `docs/2026-02-22/tasks/T50_*.md` ... `T56_*.md`
- `docs/2026-02-22/verification/T50_gate_decision.json` ... `T56_gate_decision.json`
- `docs/2026-02-22/verification/T50_compliance_attestation.json` ... `T56_compliance_attestation.json`
- `docs/2026-02-22/verification/final_gate_decision.json`
