# {BATCH_NAME} 三权分立提示词（直接转发）

适用调度单：`{DISPATCH_PATH}`  
协议基线：`multi-ai-collaboration.md`、`docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`、`docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

---

## 给 <ExecutionOwner>（Execution：Txx）

你是 `{JOB_ID}` 的 Execution 角色，负责 `Txx`。  
执行前置：对应前置任务 `gate_decision=ALLOW` 且 `compliance=PASS`。

依据文件：
- `{DISPATCH_PATH}`
- `docs/{DATE}/L4.5.MD`
- `multi-ai-collaboration.md`

输出：
- `docs/{DATE}/verification/Txx_execution_report.yaml`

报告必须包含：
- `PreflightChecklist`
- `ExecutionContract`
- `RequiredChanges`
- `gate_self_check`
- `evidence_refs`

---

## 给 <ReviewOwner>（Review：Tyy）

你是 Review 角色，负责 `Tyy`。  
输出：
- `docs/{DATE}/verification/Tyy_gate_decision.json`

结论必须包含：
- `decision` (`ALLOW | REQUIRES_CHANGES | DENY`)
- `reasons`
- `evidence_refs`
- `required_changes`（如有）

---

## 给 <ComplianceOwner>（Compliance：Tzz）

你是 Compliance 角色，负责 `Tzz`。  
输出：
- `docs/{DATE}/verification/Tzz_compliance_attestation.json`

结论必须包含：
- `decision` (`PASS | FAIL`)
- `violations`
- `evidence_refs`
- `required_changes`（如有）

