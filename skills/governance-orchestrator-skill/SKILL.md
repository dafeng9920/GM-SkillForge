# governance-orchestrator-skill

> 版本: v1.0.0  
> 目标: 统一三权分立调度、返工收敛、最终门禁裁决为一个主 Skill 资产

---

## 触发词

- `governance orchestrator`
- `统一治理调度`
- `dispatch next/validate/final gate`
- `三权分立收口`
- `L4.5 final gate`

---

## 统一结构（一主多子）

主 Skill：`governance-orchestrator-skill`

子 profile（见 `references/profiles.md`）：
1. `dispatch`: 调度推进与下一棒提示
2. `validate`: 调度包结构与角色映射校验
3. `reconcile`: 依赖冲突最小返工链
4. `final_gate`: 最终 ALLOW/REQUIRES_CHANGES/DENY 裁决

---

## 统一输出协议

固定 decision 语义：
- Gate: `ALLOW | REQUIRES_CHANGES | DENY`
- Compliance: `PASS | FAIL`

固定证据字段：
- `evidence_refs[].id`
- `evidence_refs[].kind`
- `evidence_refs[].locator`
- `evidence_refs[].sha256`

固定修复字段：
- `required_changes[].issue_key`
- `required_changes[].reason`
- `required_changes[].next_action`

---

## 统一路径约定

- 调度单: `docs/{date}/task_dispatch_*.md`
- 提示词: `docs/{date}/tasks/*_PROMPTS.md`
- 验证产物: `docs/{date}/verification/Txx_*`
- 最终裁决: `docs/{date}/verification/*_final_gate_decision.json`

---

## 统一 CLI

```bash
skillforge dispatch next --date <YYYY-MM-DD> --dispatch <path> --prompts <path>
skillforge dispatch validate --date <YYYY-MM-DD> --dispatch <path> --prompts <path> --dispatch-registry <path>
skillforge gate final --date <YYYY-MM-DD> --job-id <JOB_ID>
```

---

## DoD

1. 同一批次可由统一 Skill 完成推进、校验、收口。
2. 最终裁决可复现且依赖链闭合。
3. 不允许 decision 语义漂移与证据字段缺失。

