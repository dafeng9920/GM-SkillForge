# Governance Telemetry Report

- Window Start: `2026-03-07T00:00:00Z`
- Window End: `2026-03-08T19:40:00Z`
- Generated At: `2026-03-08T20:15:00Z`
- Scope: `cloud execution / bridge / absorb / review / compliance`

## 1. Sample Summary

- Total Tasks: `1`
- Total Delivery Events: `1`
- Total Sync Events: `1`
- Total Probe Runs: `1`

## 2. Issue Summary

| Issue Type | Count | Severity Mix | Human Intervention Needed | Notes |
|---|---:|---|---:|---|
| path_drift | 1 | HIGH | 1 | 容器工作区产物与主仓 authoritative 路径脱节，先在 `.openclaw/workspace`，后经主控吸收回仓 |
| false_completion | 1 | HIGH | 1 | 执行播报先于主仓真实落盘，需人工审计后纠偏 |
| artifact_missing | 1 | HIGH | 1 | 核心四件套最初未在主仓出现，后由手工落盘补齐 |
| role_boundary_violation | 0 | - | 0 | 本轮未记录新的正式越权结论文件 |
| sync_failure | 1 | HIGH | 1 | 初始云端到主仓同步失败，后转为受控桥接与手工 absorb |
| absorb_failure | 0 | - | 0 | 尚未记录正式 absorb 脚本运行失败样本 |
| probe_gap | 1 | MEDIUM | 1 | 初始 probe 未覆盖 T3-A 新增产物，后补入 CR-014~CR-017 |
| skill_drift | 1 | MEDIUM | 1 | 新 skill 先只存在本地，需经 Gemini 桥接到云端 |
| resume_failure | 0 | - | 0 | 本轮未记录明确 resume 失败，handoff/checkpoint 最终可用 |
| governance_doc_drift | 1 | MEDIUM | 1 | 治理公告与同步协议曾存在 L5/角色/路径口径漂移，后统一修正 |

## 3. Core Metrics

| Metric | Value | Unit | Sample Size | Evidence Refs | Interpretation |
|---|---:|---|---:|---|---|
| false_completion_rate | 1.00 | ratio | 1 | [LOBSTER_OUTPUT_REMEDIATION_2026-03-08.md](/d:/GM-SkillForge/docs/2026-03-08/LOBSTER_OUTPUT_REMEDIATION_2026-03-08.md), [T3-A_冻结结论_2026-03-08.md](/d:/GM-SkillForge/docs/2026-03-08/T3-A_%E5%86%BB%E7%BB%93%E7%BB%93%E8%AE%BA_2026-03-08.md) | 单样本下曾出现“先报完成、后补证据”，执行体仍需强约束 |
| artifact_recovery_rate | 1.00 | ratio | 1 | [T3-A_冻结结论_2026-03-08.md](/d:/GM-SkillForge/docs/2026-03-08/T3-A_%E5%86%BB%E7%BB%93%E7%BB%93%E8%AE%BA_2026-03-08.md) | 交付包最终回到主仓，但依赖人工吸收，不代表链路已自动稳定 |
| manual_intervention_per_task | 4.00 | count_per_task | 1 | [REPO_TRIAGE_2026-03-08.md](/d:/GM-SkillForge/docs/2026-03-08/REPO_TRIAGE_2026-03-08.md), [LOBSTER_OUTPUT_REMEDIATION_2026-03-08.md](/d:/GM-SkillForge/docs/2026-03-08/LOBSTER_OUTPUT_REMEDIATION_2026-03-08.md), [T3-A_冻结结论_2026-03-08.md](/d:/GM-SkillForge/docs/2026-03-08/T3-A_%E5%86%BB%E7%BB%93%E7%BB%93%E8%AE%BA_2026-03-08.md) | 人工介入仍高，当前不适合直接放量到长任务/高并发 |
| resume_success_rate | 1.00 | ratio | 1 | [resume_handoff.md](/d:/GM-SkillForge/docs/2026-03-08/resume_handoff.md), [state.yaml](/d:/GM-SkillForge/docs/2026-03-08/checkpoint/state.yaml) | 有手工辅助下成功完成恢复与收口，说明 resume 机制可用但不够自动 |
| probe_escape_rate | 1.00 | ratio | 1 | [review_latest.md](/d:/GM-SkillForge/docs/compliance_reviews/review_latest.md), [run_3day_compliance_review.py](/d:/GM-SkillForge/scripts/run_3day_compliance_review.py) | 初始问题依赖人工发现，后续才把 T3-A 专项检查补入探针 |
| sync_success_rate | 1.00 | ratio | 1 | [cloud_skill_sync_report.md](/d:/GM-SkillForge/docs/2026-03-08/cloud_skill_sync_report.md) | 桥接报告当前为成功，但仍主要基于桥接报告与本地可见证据，需再经历至少一轮真实消费验证 |
| governance_violation_rate | 1.00 | ratio | 1 | [LOBSTER_OUTPUT_REMEDIATION_2026-03-08.md](/d:/GM-SkillForge/docs/2026-03-08/LOBSTER_OUTPUT_REMEDIATION_2026-03-08.md), [CODEX_SYNC_GOVERNANCE_v1.md](/d:/GM-SkillForge/docs/2026-03-08/CODEX_SYNC_GOVERNANCE_v1.md) | 单样本下发生过假完成、路径漂移、文档口径漂移，说明治理强约束必须继续维持 |

## 4. Trend Read

- What improved:
  - `dropzone -> host absorb -> local accept` 链路已经从概念变成实物。
  - `T3-A` 产物已主仓落盘，且 probe 已补齐专项检查。
  - 云端 skill/script 桥接已有正式报告和角色分工。
- What stayed flat:
  - 执行体仍然需要强合同、强路径、强状态词约束。
  - 最终业务验收仍必须在本地完成，不能下放。
- What regressed:
  - 无明显系统性回退，但“单次 clean run 并不等于长期稳定”仍需警惕。

## 5. Upgrade Decision

- Decision: `LIMITED_UPGRADE`

### Reasoning

- 当前不适合直接升级到长任务、高并发、受控 git。
- 但已经适合从“单条受控试跑”升级到“多 agent 小任务并行试运行 + 继续保留强人工收口”。
- 关键理由是：底盘已经成型，但人工介入成本和 probe 初期漏检率仍然偏高。

### Blocking Factors

1. 单样本成功不足以证明链路长期稳定。
2. `manual_intervention_per_task` 仍高，说明桥接/吸收还没有真正自动化。
3. `probe_escape_rate` 曾为 1，说明专项问题一开始靠人工而不是探针发现。

### Recommended Next Step

- 下一阶段只允许：
  - 多 agent 小任务并行试运行
  - 保持 `dropzone + absorb + local accept`
  - 持续记录问题分类与指标
- 暂不允许：
  - 长时间自治任务
  - 直接受控 git 提交
  - 无人工复核的批量放量

## 6. Evidence Refs

- [review_latest.md](/d:/GM-SkillForge/docs/compliance_reviews/review_latest.md)
- [T3-A_冻结结论_2026-03-08.md](/d:/GM-SkillForge/docs/2026-03-08/T3-A_%E5%86%BB%E7%BB%93%E7%BB%93%E8%AE%BA_2026-03-08.md)
- [LOBSTER_OUTPUT_REMEDIATION_2026-03-08.md](/d:/GM-SkillForge/docs/2026-03-08/LOBSTER_OUTPUT_REMEDIATION_2026-03-08.md)
- [REPO_TRIAGE_2026-03-08.md](/d:/GM-SkillForge/docs/2026-03-08/REPO_TRIAGE_2026-03-08.md)
- [cloud_skill_sync_report.md](/d:/GM-SkillForge/docs/2026-03-08/cloud_skill_sync_report.md)
- [CODEX_SYNC_GOVERNANCE_v1.md](/d:/GM-SkillForge/docs/2026-03-08/CODEX_SYNC_GOVERNANCE_v1.md)
- [CLOUD_MULTI_AGENT_OVERSIGHT_PROTOCOL_v1.md](/d:/GM-SkillForge/docs/2026-03-08/CLOUD_MULTI_AGENT_OVERSIGHT_PROTOCOL_v1.md)
- [CLOUD_SKILL_SYNC_INSTALL_PROTOCOL_v1.md](/d:/GM-SkillForge/docs/2026-03-08/CLOUD_SKILL_SYNC_INSTALL_PROTOCOL_v1.md)

## 7. Notes

- 本报告只覆盖 2026-03-07 到 2026-03-08 的首个真实样本窗口。
- 单次成功样本不足以直接判定 `READY_FOR_NEXT_STAGE`。
- 本报告已明确把“探针 PASS”和“专项人工审核通过”区分开，避免假成熟判断。
