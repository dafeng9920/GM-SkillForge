# 2026-02-22 Task Dispatch（L4-SKILL-07 密码学签名门禁）

job_id: L4-SKILL-07-CRYPTO-SIGNATURE-20260222-001
protocol: multi-ai-collaboration.md v3
owner: Codex (Orchestrator)
goal: 将“时间戳签署”升级为“密码学验签”硬门禁（Fail-Closed）

## 三权分立（MUST）
- Execution: Antigravity-1
- Review: Antigravity-2
- Compliance: Kior-C
- 角色不可混同；缺任一角色记录即 `DENY`。

## 波次编排

| Wave | Task | Role | Depends On | 输出 |
|---|---|---|---|---|
| 1 | T81 | Review 预审（Antigravity-2） | - | `T81_gate_decision.json` (ALLOW/REQUIRES_CHANGES) |
| 2 | T82 | Compliance 预审（Kior-C） | T81=ALLOW | `T82_compliance_attestation.json` (PASS/FAIL) |
| 3 | T83 | Execution 实施（Antigravity-1） | T81=ALLOW, T82=PASS | 代码改动 + `T83_execution_report.yaml` |
| 4 | T84 | Review 验收（Antigravity-2） | T83 | `T84_gate_decision.json` |
| 5 | T85 | Compliance 终审（Kior-C） | T84=ALLOW | `T85_compliance_attestation.json` |
| 6 | T86 | Final Gate（Codex） | T83,T84,T85 | `L4-SKILL-07_final_gate_decision.json` |

## 目标改动范围（Execution 合同）
- 允许改动：
  - `skills/p2-final-gate-aggregate-skill/aggregate_final_gate.py`
  - `scripts/verify_guard_signature.py`
  - `skills/p2-final-gate-aggregate-skill/SKILL.md`
- 禁止改动：
  - `docs/2026-02-22/verification/T70-T80*` 历史证据文件（只读）
  - 任何无关技能目录

## 硬门禁定义（L4-SKILL-07）
1. 启用 `--require-crypto-signature` 时：
   - 缺失签名字段 => `REQUIRES_CHANGES`
   - 验签失败 => `DENY`
   - signer_id 不在允许名单 => `DENY`
2. 禁止“仅时间戳即通过”。
3. 禁止从非标准字段推导 PASS（保持 06.1 的 strict decision 规则）。

## 必交付文件
- `docs/2026-02-22/verification/T81_gate_decision.json`
- `docs/2026-02-22/verification/T82_compliance_attestation.json`
- `docs/2026-02-22/verification/T83_execution_report.yaml`
- `docs/2026-02-22/verification/T84_gate_decision.json`
- `docs/2026-02-22/verification/T85_compliance_attestation.json`
- `docs/2026-02-22/verification/L4-SKILL-07_final_gate_decision.json`

