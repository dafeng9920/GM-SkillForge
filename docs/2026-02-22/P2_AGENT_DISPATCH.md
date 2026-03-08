# 2026-02-22 P2 Task Dispatch（Hardening）

job_id: L4-P2-HARDENING-20260222-003
protocol: multi-ai-collaboration.md v3
scope: P2（系统加固与未知项收敛）
todo_source: docs/2026-02-22/P2_HARDENING_TODO.md
owner: Codex (Orchestrator)

## 目标
1. 补齐签名校验、证据链校验、回滚演练、策略锁定四项底座能力。
2. 将状态报告中的 UNKNOWN 项转为 VERIFIED 或 NOT_IMPLEMENTED（有证据）。
3. 形成 P2 最终总闸结论：`final_gate_decision_p2.json`。

## 三权分立硬规则（MUST）
- 无 `ComplianceAttestation(PASS)`，任务不得进入完成态。
- `Execution` / `Review` / `Compliance` 三角色必须不同人。
- 缺失任一 `Txx_execution_report.yaml` / `Txx_gate_decision.json` / `Txx_compliance_attestation.json`，任务 `DENY`。
- 涉及副作用操作，必须有 `permit=VALID` 证据。
- 无 `EvidenceRef` 不得宣称完成。

## 波次编排

| Wave | Task | Execution | Review | Compliance | Depends On | 目标 |
|---|---|---|---|---|---|---|
| A | T70 | Antigravity-1 | vs--cc2 | Kior-C | - | guard_signature 落地 |
| A | T71 | Kior-A | vs--cc1 | Kior-C | - | evidence_sha256 交叉校验链 |
| A | T72 | Kior-B | vs--cc3 | Kior-C | - | rollback 演练与记录 |
| A | T73 | vs--cc1 | Antigravity-2 | Kior-C | - | policy_sha256 锁定 |
| B | T74 | Antigravity-2 | vs--cc2 | Kior-B | T70,T71,T72,T73 | 8-Gate 编排器探针 |
| B | T75 | Antigravity-3 | Kior-A | Kior-B | T70,T71,T72,T73 | RAG 3D 能力探针 |
| B | T76 | vs--cc3 | Antigravity-1 | Kior-B | T70,T71,T72,T73 | n8n 集成与 fail-closed 探针 |
| C | T77 | Kior-A | vs--cc1 | Kior-C | T74,T75,T76 | L3 AuditPack 生成验证 |
| C | T78 | Antigravity-1 | vs--cc2 | Kior-B | T74,T75,T76 | skills 测试覆盖基线 |
| C | T79 | Kior-C | Antigravity-3 | vs--cc1 | T74,T75,T76 | Git 治理与追溯基线 |
| C | T80 | vs--cc2 | Codex | Kior-C | T70~T79 | P2 Final Gate 汇总 |

## 放行规则
- Wave A 全部 `ALLOW` 才可启动 Wave B。
- Wave B 全部 `ALLOW` 才可启动 Wave C。
- Wave C 中 `T77~T79` 全部 `ALLOW` 后，`T80` 才可执行。
- 任一任务 `REQUIRES_CHANGES`：仅回滚该任务，不影响其他已 `ALLOW` 任务。

## 任务书与产物约束（机器执行）

### T70
- task_spec: `docs/2026-02-22/tasks/T70_Antigravity-1.md`
- must_outputs:
  - `docs/2026-02-22/verification/T70_execution_report.yaml`
  - `docs/2026-02-22/verification/T70_gate_decision.json`
  - `docs/2026-02-22/verification/T70_compliance_attestation.json`
  - `scripts/verify_guard_signature.py`
  - `docs/2026-02-22/verification/signature_verification_report.json`

### T71
- task_spec: `docs/2026-02-22/tasks/T71_Kior-A.md`
- must_outputs:
  - `docs/2026-02-22/verification/T71_execution_report.yaml`
  - `docs/2026-02-22/verification/T71_gate_decision.json`
  - `docs/2026-02-22/verification/T71_compliance_attestation.json`
  - `scripts/verify_evidence_chain.py`
  - `docs/2026-02-22/verification/evidence_chain_report.json`

### T72
- task_spec: `docs/2026-02-22/tasks/T72_Kior-B.md`
- must_outputs:
  - `docs/2026-02-22/verification/T72_execution_report.yaml`
  - `docs/2026-02-22/verification/T72_gate_decision.json`
  - `docs/2026-02-22/verification/T72_compliance_attestation.json`
  - `docs/2026-02-22/verification/rollback_drill.md`
  - `docs/2026-02-22/verification/rollback_tombstone.json`

### T73
- task_spec: `docs/2026-02-22/tasks/T73_vs--cc1.md`
- must_outputs:
  - `docs/2026-02-22/verification/T73_execution_report.yaml`
  - `docs/2026-02-22/verification/T73_gate_decision.json`
  - `docs/2026-02-22/verification/T73_compliance_attestation.json`
  - `docs/2026-02-22/verification/policy_lock_report.json`

### T74
- task_spec: `docs/2026-02-22/tasks/T74_Antigravity-2.md`
- must_outputs:
  - `docs/2026-02-22/verification/T74_execution_report.yaml`
  - `docs/2026-02-22/verification/T74_gate_decision.json`
  - `docs/2026-02-22/verification/T74_compliance_attestation.json`
  - `docs/2026-02-22/verification/orchestrator_probe_report.json`

### T75
- task_spec: `docs/2026-02-22/tasks/T75_Antigravity-3.md`
- must_outputs:
  - `docs/2026-02-22/verification/T75_execution_report.yaml`
  - `docs/2026-02-22/verification/T75_gate_decision.json`
  - `docs/2026-02-22/verification/T75_compliance_attestation.json`
  - `docs/2026-02-22/verification/rag3d_probe_report.json`

### T76
- task_spec: `docs/2026-02-22/tasks/T76_vs--cc3.md`
- must_outputs:
  - `docs/2026-02-22/verification/T76_execution_report.yaml`
  - `docs/2026-02-22/verification/T76_gate_decision.json`
  - `docs/2026-02-22/verification/T76_compliance_attestation.json`
  - `docs/2026-02-22/verification/n8n_probe_report.json`

### T77
- task_spec: `docs/2026-02-22/tasks/T77_Kior-A.md`
- must_outputs:
  - `docs/2026-02-22/verification/T77_execution_report.yaml`
  - `docs/2026-02-22/verification/T77_gate_decision.json`
  - `docs/2026-02-22/verification/T77_compliance_attestation.json`
  - `docs/2026-02-22/verification/l3_auditpack_report.json`

### T78
- task_spec: `docs/2026-02-22/tasks/T78_Antigravity-1.md`
- must_outputs:
  - `docs/2026-02-22/verification/T78_execution_report.yaml`
  - `docs/2026-02-22/verification/T78_gate_decision.json`
  - `docs/2026-02-22/verification/T78_compliance_attestation.json`
  - `docs/2026-02-22/verification/skills_test_coverage.json`

### T79
- task_spec: `docs/2026-02-22/tasks/T79_Kior-C.md`
- must_outputs:
  - `docs/2026-02-22/verification/T79_execution_report.yaml`
  - `docs/2026-02-22/verification/T79_gate_decision.json`
  - `docs/2026-02-22/verification/T79_compliance_attestation.json`
  - `docs/2026-02-22/verification/git_governance_baseline.md`

### T80
- task_spec: `docs/2026-02-22/tasks/T80_vs--cc2.md`
- must_outputs:
  - `docs/2026-02-22/verification/T80_execution_report.yaml`
  - `docs/2026-02-22/verification/T80_gate_decision.json`
  - `docs/2026-02-22/verification/T80_compliance_attestation.json`
  - `docs/2026-02-22/verification/final_gate_decision_p2.json`

## 每任务指令协议（统一）
- 输入必须引用：
  - `docs/2026-02-22/P2_HARDENING_TODO.md`
  - `docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
  - `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`
  - 对应 `task_spec` 文件
- 输出必须包含（A Guard）：
  - `PreflightChecklist`
  - `ExecutionContract`
  - `RequiredChanges`
- 合规结论必须包含（B Guard）：
  - `Decision`
  - `Violations`
  - `Evidence Ref`

## 验收产物目录
- `docs/2026-02-22/tasks/T70_*.md` ... `T80_*.md`
- `docs/2026-02-22/verification/T70_execution_report.yaml` ... `T80_execution_report.yaml`
- `docs/2026-02-22/verification/T70_gate_decision.json` ... `T80_gate_decision.json`
- `docs/2026-02-22/verification/T70_compliance_attestation.json` ... `T80_compliance_attestation.json`
- `docs/2026-02-22/verification/final_gate_decision_p2.json`
