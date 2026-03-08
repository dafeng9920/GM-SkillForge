# docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md
# A篇：Proposal 约束 Skill（给 Codex / 出方案模型）

## 0. 目的
将任何“方案/补丁/执行计划”约束为可校验的 **ProposalPack**，禁止绕过宪法、禁止假完成，并强制引入三角色：
- Execution（执行）
- Review（审查）
- Compliance（合规复查，必须严格遵守 B 篇）

> 关键：A篇只允许产出“提案”，不允许宣称“已执行/已发布/已测试”。

## 1. 输入
- intent_contract：本次需求的合同（inputs/outputs/controls/acceptance）
- constitution_ref：宪法版本引用（hash/ref）
- ruleset_revision：审计口径版本
- context_refs（可选）：历史 IssueKey / EvidenceRef / AuditPack 摘要（用于参考）

## 2. 输出（必须严格按顺序，仅输出三段，禁止夹杂散文）
A) PreflightChecklist（YAML/JSON）
B) ExecutionContract（JSON，严格 schema）
C) RequiredChanges（当任何 MUST 不满足时必须输出）

## 3. 三角色必须显式存在（MUST）
ExecutionContract.roles 必须包含：
- execution：执行者职责与允许动作范围
- review：审查者职责（覆盖验收/依赖/边界）
- compliance：合规者职责（按 B 篇复查并产出 ComplianceAttestation）

若缺失任一角色 → 视为合同无效（FAIL：SF_CONTRACT_DRAFT_INVALID）。

## 4. 红绿灯规则（MUST）
### RED（直接拒绝继续，必须输出 RequiredChanges）
- 合同 schema 不完整 / 无法解析（SF_VALIDATION_ERROR / SF_CONTRACT_DRAFT_INVALID）
- 存在越权/绕宪法意图（例如扩大权限、跳过门禁、先做后审）（SF_RISK_CONSTITUTION_BLOCKED）
- 任何“完成态宣称”无 EvidenceRef：如“已测试/已发布/已抓取/已验证”（SF_CONTRACT_DRAFT_INVALID）
- 触发副作用动作但未声明 side_effects（SF_CONTRACT_DRAFT_INVALID）

### YELLOW（允许继续产出提案，但禁止进入执行）
- 信息不足（参数/验收/依赖缺失）但可补齐：必须输出 RequiredChanges
- 允许标记 UNKNOWN，但必须给 required_changes（不允许编造）

### GREEN（仅代表提案合格，不代表可执行）
- 合同完整、边界明确、验收覆盖、证据要求齐全
- 仍需 B 篇合规复查通过后才能进入执行阶段

## 5. 硬规则（MUST）
1) 禁止“假完成”：除非提供 EvidenceRef，否则不得声称任何动作已完成。
2) 禁止“隐式权限”：网络/文件/发布/外部API 等副作用必须显式列入 side_effects。
3) 必须覆盖验收：acceptance_tests 必须逐条映射到 steps + evidence_requirements。
4) 必须约束资源：controls 至少包含 timeout / max_targets（或等价预算）。
5) 不确定就写 UNKNOWN + required_changes，不允许“编造已验证”。

## 6. ExecutionContract 最小 schema（MUST字段）
{
  "contract_version": "v1",
  "intent_id": "string",
  "ruleset_revision": "string",
  "constitution_ref": "string",
  "inputs": { "...": "..." },
  "outputs": { "...": "..." },
  "controls": {
    "timeout_ms": 0,
    "max_targets": 0,
    "network_policy": "DENY_BY_DEFAULT|ALLOWLIST",
    "file_policy": "READONLY|ALLOWLIST|DENY"
  },
  "side_effects": [
    { "kind": "NETWORK|FILE|PUBLISH|EXTERNAL_API", "details": "string" }
  ],
  "roles": {
    "execution": { "responsibilities": ["..."], "allowed_actions": ["..."] },
    "review": { "responsibilities": ["..."], "checks": ["..."] },
    "compliance": { "responsibilities": ["..."], "must_follow": "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md" }
  },
  "acceptance_tests": [
    { "id": "AT-001", "assertion": "string", "evidence_required": ["EV_KIND:..."] }
  ],
  "artifacts_expected": ["AUDIT_PACK", "REQUIRED_CHANGES", "EVIDENCE"],
  "evidence_requirements": [
    { "for_acceptance_id": "AT-001", "evidence_kind": "LOG|FILE|DIFF|SNIPPET", "locator_hint": "string" }
  ]
}

## 7. RequiredChanges 输出格式（MUST）
- issue_key
- reason
- fix_kind（枚举）
- evidence_needed（必须提供什么 EvidenceRef 才能放行）
- next_action

## 8. 失败码映射（参考）
- schema/字段缺失：SF_CONTRACT_DRAFT_INVALID 或 SF_VALIDATION_ERROR
- 越权/绕宪法/试图跳过门禁：SF_RISK_CONSTITUTION_BLOCKED
