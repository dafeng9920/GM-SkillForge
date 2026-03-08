# P2 派发指令（人类可读版，可直接分发）

使用说明：
- 你把下面对应段落原样发给对应 Agent。
- 全员必须遵守：
  - `docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
  - `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`
  - `docs/2026-02-22/P2_HARDENING_TODO.md`
- 每个任务必须产出三件套：
  - `Txx_execution_report.yaml`
  - `Txx_gate_decision.json`
  - `Txx_compliance_attestation.json`

---

## 波次规则（先后关系）

- Wave A 并行：`T70 T71 T72 T73`
- Wave B 并行（前提：Wave A 全部 ALLOW）：`T74 T75 T76`
- Wave C 并行（前提：Wave B 全部 ALLOW）：`T77 T78 T79`
- 收口：`T80`（前提：T70~T79 全部完成且合规 PASS）

---

## 1) 发给 Antigravity-1（T70）

你是 `T70` 执行者。  
任务：落实 `guard_signature` 校验。  
审查者：`vs--cc2`；合规官：`Kior-C`。  
必须输出 A Guard 三段：`PreflightChecklist / ExecutionContract / RequiredChanges`。  
必须输出 B Guard 结论：`Decision / Violations / Evidence Ref`。  
交付物：
- `docs/2026-02-22/tasks/T70_Antigravity-1.md`
- `docs/2026-02-22/verification/T70_execution_report.yaml`
- `docs/2026-02-22/verification/T70_gate_decision.json`
- `docs/2026-02-22/verification/T70_compliance_attestation.json`
- `scripts/verify_guard_signature.py`
- `docs/2026-02-22/verification/signature_verification_report.json`

## 2) 发给 Kior-A（T71）

你是 `T71` 执行者。  
任务：落实 `evidence_sha256` 交叉校验链。  
审查者：`vs--cc1`；合规官：`Kior-C`。  
必须输出 A/B Guard 结构。  
交付物：
- `docs/2026-02-22/tasks/T71_Kior-A.md`
- `docs/2026-02-22/verification/T71_execution_report.yaml`
- `docs/2026-02-22/verification/T71_gate_decision.json`
- `docs/2026-02-22/verification/T71_compliance_attestation.json`
- `scripts/verify_evidence_chain.py`
- `docs/2026-02-22/verification/evidence_chain_report.json`

## 3) 发给 Kior-B（T72）

你是 `T72` 执行者。  
任务：执行 rollback 演练并形成证据。  
审查者：`vs--cc3`；合规官：`Kior-C`。  
必须输出 A/B Guard 结构。  
交付物：
- `docs/2026-02-22/tasks/T72_Kior-B.md`
- `docs/2026-02-22/verification/T72_execution_report.yaml`
- `docs/2026-02-22/verification/T72_gate_decision.json`
- `docs/2026-02-22/verification/T72_compliance_attestation.json`
- `docs/2026-02-22/verification/rollback_drill.md`
- `docs/2026-02-22/verification/rollback_tombstone.json`

## 4) 发给 vs--cc1（T73）

你是 `T73` 执行者。  
任务：落实 `policy_sha256` 锁定。  
审查者：`Antigravity-2`；合规官：`Kior-C`。  
必须输出 A/B Guard 结构。  
交付物：
- `docs/2026-02-22/tasks/T73_vs--cc1.md`
- `docs/2026-02-22/verification/T73_execution_report.yaml`
- `docs/2026-02-22/verification/T73_gate_decision.json`
- `docs/2026-02-22/verification/T73_compliance_attestation.json`
- `docs/2026-02-22/verification/policy_lock_report.json`

## 5) 发给 Antigravity-2（T74，等 Wave A 全部 ALLOW）

你是 `T74` 执行者。  
任务：8-Gate 编排器能力探针（输出 VERIFIED/NOT_IMPLEMENTED + 证据）。  
审查者：`vs--cc2`；合规官：`Kior-B`。  
交付物：
- `docs/2026-02-22/tasks/T74_Antigravity-2.md`
- `docs/2026-02-22/verification/T74_execution_report.yaml`
- `docs/2026-02-22/verification/T74_gate_decision.json`
- `docs/2026-02-22/verification/T74_compliance_attestation.json`
- `docs/2026-02-22/verification/orchestrator_probe_report.json`

## 6) 发给 Antigravity-3（T75，等 Wave A 全部 ALLOW）

你是 `T75` 执行者。  
任务：RAG 3D 能力探针（输出状态 + 复现实验步骤）。  
审查者：`Kior-A`；合规官：`Kior-B`。  
交付物：
- `docs/2026-02-22/tasks/T75_Antigravity-3.md`
- `docs/2026-02-22/verification/T75_execution_report.yaml`
- `docs/2026-02-22/verification/T75_gate_decision.json`
- `docs/2026-02-22/verification/T75_compliance_attestation.json`
- `docs/2026-02-22/verification/rag3d_probe_report.json`

## 7) 发给 vs--cc3（T76，等 Wave A 全部 ALLOW）

你是 `T76` 执行者。  
任务：n8n 集成与 fail-closed 探针。  
审查者：`Antigravity-1`；合规官：`Kior-B`。  
交付物：
- `docs/2026-02-22/tasks/T76_vs--cc3.md`
- `docs/2026-02-22/verification/T76_execution_report.yaml`
- `docs/2026-02-22/verification/T76_gate_decision.json`
- `docs/2026-02-22/verification/T76_compliance_attestation.json`
- `docs/2026-02-22/verification/n8n_probe_report.json`

## 8) 发给 Kior-A（T77，等 Wave B 全部 ALLOW）

你是 `T77` 执行者。  
任务：L3 AuditPack 一键生成验证。  
审查者：`vs--cc1`；合规官：`Kior-C`。  
交付物：
- `docs/2026-02-22/tasks/T77_Kior-A.md`
- `docs/2026-02-22/verification/T77_execution_report.yaml`
- `docs/2026-02-22/verification/T77_gate_decision.json`
- `docs/2026-02-22/verification/T77_compliance_attestation.json`
- `docs/2026-02-22/verification/l3_auditpack_report.json`

## 9) 发给 Antigravity-1（T78，等 Wave B 全部 ALLOW）

你是 `T78` 执行者。  
任务：skills 测试覆盖率基线。  
审查者：`vs--cc2`；合规官：`Kior-B`。  
交付物：
- `docs/2026-02-22/tasks/T78_Antigravity-1.md`
- `docs/2026-02-22/verification/T78_execution_report.yaml`
- `docs/2026-02-22/verification/T78_gate_decision.json`
- `docs/2026-02-22/verification/T78_compliance_attestation.json`
- `docs/2026-02-22/verification/skills_test_coverage.json`

## 10) 发给 Kior-C（T79，等 Wave B 全部 ALLOW）

你是 `T79` 执行者。  
任务：Git 治理与追溯基线。  
审查者：`Antigravity-3`；合规官：`vs--cc1`。  
交付物：
- `docs/2026-02-22/tasks/T79_Kior-C.md`
- `docs/2026-02-22/verification/T79_execution_report.yaml`
- `docs/2026-02-22/verification/T79_gate_decision.json`
- `docs/2026-02-22/verification/T79_compliance_attestation.json`
- `docs/2026-02-22/verification/git_governance_baseline.md`

## 11) 发给 vs--cc2（T80 收口，等 T70~T79 全部完成）

你是 `T80` 执行者（总闸汇总）。  
任务：汇总 T70~T79 三件套结果，生成 P2 总裁决。  
审查者：`Codex`；合规官：`Kior-C`。  
交付物：
- `docs/2026-02-22/tasks/T80_vs--cc2.md`
- `docs/2026-02-22/verification/T80_execution_report.yaml`
- `docs/2026-02-22/verification/T80_gate_decision.json`
- `docs/2026-02-22/verification/T80_compliance_attestation.json`
- `docs/2026-02-22/verification/final_gate_decision_p2.json`

---

## 拦截条件（任一命中即 DENY）

- 缺少 `Txx_gate_decision.json`
- 缺少 `Txx_compliance_attestation.json`
- 声称 PASS 但缺少 EvidenceRef
- 涉及副作用但无 `permit=VALID`
