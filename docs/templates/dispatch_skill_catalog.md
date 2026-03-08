# 可调用 Skill 清单（统一调度入口）

> 用途: 统一约束 AI 军团在 dispatch 执行时可调用的治理技能，避免执行口径漂移。

| skill | 触发场景 | 标准产出 |
|---|---|---|
| `seed-gate-validator-skill` | 批次收口前 strict gate 校验 | `ALLOW/BLOCK` 结论 + suite 统计 + 复验命令 |
| `master-signoff-skill` | 主控签核阶段（Txx Master-Control） | `READY_FOR_*` 判定 + 签核时间 + 证据路径 |
| `task-pack-writer-skill` | 新批次任务包生成/改版 | `task_dispatch + Txx + 汇总模板` 三件套 |
| `drill-evidence-collector-skill` | 单次可审计演练收口 | `run_id/evidence_ref/error_code/replay_pointer` 证据块 |
| `experience-template-retriever-skill` | 按 IssueKey/FixKind 复用经验模板 | 可复核修复建议（含 EvidenceRef） |
| `governance-orchestrator-skill` | 统一治理主 Skill（一主多子） | `dispatch next/validate + gate final + reconcile` |
| `trinity-dispatch-orchestrator-skill` | 三权分立调度包产品化（生成+校验+重跑） | `task_dispatch + prompts + validate` 一致性闭环 |
| `GOVERNANCE_PROTOCOL` | 高风险动作治理（Shell/File/DB/Network） | `Contract-First + Permit Gate + AuditPack` |

## 调用约束

1. 不得跳过 `seed-gate-validator-skill` 的 strict 结果直接签核。  
2. `master-signoff-skill` 仅可在上游 `gate_decision=ALLOW` 后触发。  
3. 所有 skill 输出必须写回任务汇总文档并附证据路径。  
4. 调度中涉及高风险操作时，必须显式声明 `GOVERNANCE_PROTOCOL` 并执行 Fail-Closed。
5. 新批次优先使用 `governance-orchestrator-skill`；`trinity-dispatch-orchestrator-skill` 仅作兼容。

## 引用方式

在各批次 dispatch 中固定添加以下说明：

`本批次可调用 Skill 清单见 docs/templates/dispatch_skill_catalog.md；本文件仅维护批次特有映射。`

机器可读注册映射（建议同时维护）：

`configs/dispatch_skill_registry.json`
