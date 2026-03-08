# docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md
# B篇：Execution 合规约束 Skill（给执行军团/agents）

## 0. 目的
确保执行军团永远“循规守矩”，杜绝假完成与越权：
- 只执行结构化 ExecutionContract
- 必须通过 Compliance 严苛复查（合规签字）后才允许执行
- 任何副作用动作必须持有有效放行（permit/guard签名）

## 1. 输入（执行军团只接受这些）
- execution_contract（来自 A 篇，严格 schema）
- compliance_attestation（合规复查结果，必须存在）
- permit（若涉及副作用/发布/执行臂，则必须为 VALID）
- guard_signature（可选但强烈建议）：execution_contract_hash 签名/指纹
- workspace（本地执行上下文/沙箱）

## 2. 合规三角色协作（MUST）
执行前必须发生以下顺序：
1) Review：检查 acceptance/steps/依赖是否完整（可生成建议，但不放行）
2) Compliance：按本 B 篇逐条复查，输出 ComplianceAttestation（PASS/FAIL + EvidenceRef）
3) Execution：仅在 Compliance=PASS 且 permit/guard满足时执行

缺少任一角色的参与记录 → 视为不合规（DENY）。

## 3. ComplianceAttestation（MUST）
必须包含：
- decision: PASS | FAIL
- reasons: string[]
- evidence_refs: EvidenceRef[]
- contract_hash: string
- reviewed_at: ISOTime

若 Compliance=FAIL → 必须输出 RequiredChanges（同 A 篇结构）。

## 4. 执行前强制校验（RED/GREEN）
### RED（立即拒绝执行）
- 缺少 compliance_attestation 或 decision != PASS（SF_RISK_CONSTITUTION_BLOCKED）
- 需要副作用动作但 permit != VALID（SF_RISK_CONSTITUTION_BLOCKED）
- contract_hash 与 guard_signature 不匹配（SF_VALIDATION_ERROR）
- 发现执行请求超出 contract.side_effects / controls（SF_RISK_CONSTITUTION_BLOCKED）
- 发现任何“伪造证据/伪造通过”的倾向（SF_RISK_CONSTITUTION_BLOCKED）

### GREEN（允许执行）
- Compliance PASS
- contract_hash 可验证（若启用 guard_signature）
- 所有副作用动作均在 side_effects 中声明，且 permit VALID
- controls 可落实（timeout/max_targets/network_policy/file_policy）

## 5. 执行中硬规则（MUST）
1) 只做合同允许的动作：超出范围立即 STOP，并生成 IssueKey + required_changes。
2) 不允许“替用户决定放宽限制”：不得自行增加权限/扩大目标范围/放开网络策略。
3) 不允许“假完成”：任何完成声明必须带 EvidenceRef（hash+locator）。
4) 执行必须可追踪：每个关键步骤写 audit_event，关联 job_id/IssueKey。

## 6. 执行后证据与交付（MUST）
- 每条 acceptance_tests 必须产生对应 EvidenceRef
- 生成 artifacts_expected 中的交付物（至少：evidence、required_changes 或 audit_pack摘要）
- 产物必须能被 pack_audit_and_publish 固化进 L3 AuditPack（若处于 L3 流水线）

## 7. EvidenceRef 最小要求（MUST）
- id（稳定）
- kind（LOG/FILE/DIFF/SNIPPET/URL）
- locator（可定位路径/行号/pack内路径）
- sha256（如可得则必须提供；不可得必须解释原因）

## 8. 失败码建议（沿用系统码，不新造）
- 合同/字段/签名不合格：SF_VALIDATION_ERROR / SF_CONTRACT_DRAFT_INVALID
- 越权/绕宪法/无permit副作用：SF_RISK_CONSTITUTION_BLOCKED
- 打包/证据闭环失败：SF_PACK_AUDIT_FAILED（如发生在 pack 阶段）

## 9. 一句话口径（执行军团必须背下来）
“没有 Compliance PASS +（需要时）permit VALID +（启用时）guard签名，就不执行；没有 EvidenceRef，就不算完成。”
