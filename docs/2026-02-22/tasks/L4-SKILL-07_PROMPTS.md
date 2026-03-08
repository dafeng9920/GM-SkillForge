# L4-SKILL-07 三权分立提示词（直接转发）

## 给 Antigravity-2（T81 预审 + T84 验收）

你是 `L4-SKILL-07` 的 Review 角色。  
请先执行 T81 预审，再执行 T84 验收。  
依据文件：
- `docs/2026-02-22/task_dispatch_l4_skill07.md`
- `docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

T81 目标：
- 审查执行合同是否满足 fail-closed
- 明确允许/禁止改动范围
- 输出：`docs/2026-02-22/verification/T81_gate_decision.json`

T84 目标：
- 对 T83 实际改动做验收
- 必查：
  1) `--require-crypto-signature` 可触发严格验签
  2) 缺签名/验签失败/非法 signer_id 可被拦截
  3) 保持 L4-SKILL-06.1 strict decision 规则
- 输出：`docs/2026-02-22/verification/T84_gate_decision.json`

结论格式必须包含：`decision`、`reasons`、`evidence_refs`、`required_changes`(如有)。

---

## 给 Kior-C（T82 合规预审 + T85 合规终审）

你是 `L4-SKILL-07` 的 Compliance 角色。  
按 EXECUTION_GUARD_B 做硬拦截，不做放水。

依据文件：
- `docs/2026-02-22/task_dispatch_l4_skill07.md`
- `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

T82（执行前）：
- 仅在 T81=ALLOW 时出具 PASS
- 审查是否存在绕过路径（特别是“只有 signed_at 就通过”）
- 输出：`docs/2026-02-22/verification/T82_compliance_attestation.json`

T85（执行后）：
- 复核 T83 改动是否满足三项：
  1) crypto 验签硬门禁生效
  2) 非法签名 fail-closed
  3) 历史证据文件未被违规改写
- 输出：`docs/2026-02-22/verification/T85_compliance_attestation.json`

结论格式必须包含：`decision`、`violations`、`evidence_refs`、`required_changes`(如有)。

---

## 给 Antigravity-1（T83 执行）

你是 `L4-SKILL-07` 的 Execution 角色。  
必须在 `T81=ALLOW` 且 `T82=PASS` 后执行。

允许改动：
- `skills/p2-final-gate-aggregate-skill/aggregate_final_gate.py`
- `scripts/verify_guard_signature.py`
- `skills/p2-final-gate-aggregate-skill/SKILL.md`

禁止改动：
- `docs/2026-02-22/verification/T70*` 到 `T80*` 历史证据文件
- 其他无关目录

实现要求：
1. 新增 `--require-crypto-signature` 门禁参数
2. 对 gate/compliance 文件进行密码学验签（HMAC-SHA256）
3. signer_id 白名单校验
4. 验签失败直接阻断（Fail-Closed）
5. 保持 L4-SKILL-06.1 现有 strict decision 规则

输出：
- `docs/2026-02-22/verification/T83_execution_report.yaml`
- 代码改动提交到工作区

执行报告必须包含：
- `PreflightChecklist`
- `ExecutionContract`
- `RequiredChanges`
- `gate_self_check`（含至少 1 个失败样例拦截证据）

