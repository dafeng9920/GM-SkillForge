# Final Gate 总裁决提示词

适用阶段：

* `Final Gate`

对应角色：

* `主控官 / Orchestrator`

唯一事实源：

* `docs/2026-03-12/前端重构_AI军团任务分发单_v2.md`
* `multi-ai-collaboration.md`
* `docs/2026-03-12/verification/` 下全部三权产物

---

## 1. 可直接转发的 Final Gate Prompt

```text
你是本批次前端治理重构的主控官，负责执行 Final Gate 总裁决。

任务范围：
- T-FE-01
- T-FE-02
- T-FE-03
- T-FE-04
- T-FE-05
- T-FE-06
- T-FE-07

你的职责不是重做任务，而是汇总三权结果、检查闭环完整性，并给出最终裁决。

你必须阅读以下文件：

【总控文档】
- docs/2026-03-12/前端重构_AI军团任务分发单_v2.md
- multi-ai-collaboration.md

【T-FE-01】
- docs/2026-03-12/verification/T-FE-01_execution_report.yaml
- docs/2026-03-12/verification/T-FE-01_gate_decision.json
- docs/2026-03-12/verification/T-FE-01_compliance_attestation.json

【T-FE-02】
- docs/2026-03-12/verification/T-FE-02_execution_report.yaml
- docs/2026-03-12/verification/T-FE-02_gate_decision.json
- docs/2026-03-12/verification/T-FE-02_compliance_attestation.json

【T-FE-03】
- docs/2026-03-12/verification/T-FE-03_execution_report.yaml
- docs/2026-03-12/verification/T-FE-03_gate_decision.json
- docs/2026-03-12/verification/T-FE-03_compliance_attestation.json

【T-FE-04】
- docs/2026-03-12/verification/T-FE-04_execution_report.yaml
- docs/2026-03-12/verification/T-FE-04_gate_decision.json
- docs/2026-03-12/verification/T-FE-04_compliance_attestation.json

【T-FE-05】
- docs/2026-03-12/verification/T-FE-05_execution_report.yaml
- docs/2026-03-12/verification/T-FE-05_gate_decision.json
- docs/2026-03-12/verification/T-FE-05_compliance_attestation.json

【T-FE-06】
- docs/2026-03-12/verification/T-FE-06_execution_report.yaml
- docs/2026-03-12/verification/T-FE-06_gate_decision.json
- docs/2026-03-12/verification/T-FE-06_compliance_attestation.json

【T-FE-07】
- docs/2026-03-12/verification/T-FE-07_execution_report.yaml
- docs/2026-03-12/verification/T-FE-07_gate_decision.json
- docs/2026-03-12/verification/T-FE-07_compliance_attestation.json

你必须检查以下事项：

1. 三权记录完整性
- 每个任务必须同时存在：
  - ExecutionReport
  - GateDecision
  - ComplianceAttestation

2. 任务决策状态
- 每个任务必须满足：
  - Review decision == ALLOW
  - Compliance decision == PASS

3. 依赖链闭环
- Wave 1: T-FE-01 ~ T-FE-04 已全部闭环
- Wave 2: T-FE-05 ~ T-FE-07 已全部闭环

4. 总体设计目标是否成立
- 是否完成从 builder 叙事切换到治理叙事
- 是否确立 Dashboard / Audit Detail / Permit 为三页主链
- 是否保留三权分立、EvidenceRef、Hash、Revision、Permit 绑定关系
- 是否完成 Never-in-DOM / Layer 3 绝对禁止区设计
- 是否明确首页讲价值，应用内讲状态与裁决
- 是否明确 Audit pass != Permit granted

5. 风险复核
- 是否仍存在 builder-first 残留
- 是否仍存在 mechanism leakage 风险
- 是否仍存在“前端拿到敏感数据再隐藏”的倾向
- 是否仍存在 Permit 语义弱化或 Audit/Permit 混淆

裁决规则：
- 任一任务缺少三权记录 -> DENY
- 任一任务 review != ALLOW -> REQUIRES_CHANGES
- 任一任务 compliance != PASS -> REQUIRES_CHANGES
- 任一任务仍存在 builder-first / mechanism leakage / permit semantic confusion 风险 -> REQUIRES_CHANGES
- 全部满足 -> ALLOW

你必须输出：
- docs/2026-03-12/verification/final_gate_decision.json

你的最终回复格式必须包含：
- batch_id
- decision: ALLOW / REQUIRES_CHANGES / DENY
- summary
- task_statuses
- evidence_refs
- residual_risks
- next_action

要求：
- 不接受空泛总结
- 必须逐任务确认状态
- 必须引用 evidence_refs
- 必须给出明确最终裁决
```

---

## 2. 建议输出结构

```json
{
  "batch_id": "FE-GOV-REFACTOR-2026-03-12",
  "decision": "ALLOW",
  "summary": [
    "T-FE-01 ~ T-FE-07 已完成三权闭环",
    "builder 叙事已切换为治理叙事",
    "三页主链、权限裁剪、文案边界与 Permit 语义已建立"
  ],
  "task_statuses": [
    {
      "task_id": "T-FE-01",
      "execution": "COMPLETE",
      "review": "ALLOW",
      "compliance": "PASS"
    }
  ],
  "evidence_refs": [
    {
      "id": "EV-FG-001",
      "kind": "FILE",
      "locator": "docs/2026-03-12/verification/T-FE-01_gate_decision.json",
      "description": "T-FE-01 最终审查通过"
    }
  ],
  "residual_risks": [],
  "next_action": "Archive batch and move to implementation or handoff"
}
```

---

## 3. 当前批次的直接判断口径

基于当前分发单，Final Gate 最核心只看三件事：

* 三权记录是否完整
* 所有任务是否已经 `Review=ALLOW` 且 `Compliance=PASS`
* 总体是否仍然坚持治理型前端，而没有滑回 builder / mechanism leakage / permit confusion

---

## 4. 使用说明

现在你可以把上面的 Prompt 直接发给负责 Final Gate 的主控官。

按当前目录状态，`verification` 下已经具备：

* `T-FE-01 ~ T-FE-07` 的 `execution_report`
* `T-FE-01 ~ T-FE-07` 的 `gate_decision`
* `T-FE-01 ~ T-FE-07` 的 `compliance_attestation`

所以下一步就是：

* 运行 Final Gate
* 生成 `docs/2026-03-12/verification/final_gate_decision.json`
