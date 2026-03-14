---
name: governance-telemetry-skill
description: 用于持续统计云端执行、多 agent 协作、桥接同步、主仓吸收、审查合规过程中出现的问题类型、频次、修复代价和趋势，并据此判断系统是否具备升级条件。适用于需要决定是否从短任务升级到长任务、从单执行升级到多执行、从手工吸收升级到半自动吸收、或从桥接副本升级到受控 git 的场景。
---

# governance-telemetry-skill

## 目标

把“感觉现在差不多可以升级了”变成 **有数据支撑的升级判定**。

本 skill 不负责修问题。  
本 skill 负责：

- 统计问题
- 归类问题
- 看趋势
- 给出升级/不升级建议

## 统计对象

至少覆盖以下环节：

- 云端 executor 执行
- Reviewer 审查
- Compliance 审计
- Bridge Operator 同步
- Dropzone 交付
- Host absorb
- 本地主控验收
- compliance probe / 专项探针

## 问题分类

统一按以下类型归类，不要临时发明新类：

- `path_drift`
  - 路径错位、容器路径与主仓路径不一致
- `false_completion`
  - 提前报完成、播报大于真实落盘
- `artifact_missing`
  - 缺件、四件套不齐、manifest 不完整
- `role_boundary_violation`
  - executor 越权、review/compliance 混写
- `sync_failure`
  - 本地到云端或云端到主仓同步失败
- `absorb_failure`
  - pre_absorb_check / absorb 失败
- `probe_gap`
  - 探针未覆盖、问题靠人工才发现
- `skill_drift`
  - 本地 skill 与云端副本不一致
- `resume_failure`
  - checkpoint / handoff / 恢复失败
- `governance_doc_drift`
  - 文档口径与现行制度不一致

## 核心指标

至少统计以下指标：

### 1. `false_completion_rate`

定义：

- 假完成次数 / 总任务数

意义：

- 判断执行体是否还在大量“先报完成后补证据”

### 2. `artifact_recovery_rate`

定义：

- 成功回到主仓的交付包数 / 总交付包数

意义：

- 判断桥接链是否稳定

### 3. `manual_intervention_per_task`

定义：

- 每任务平均人工介入次数

意义：

- 判断当前执行链是否值得继续自动化升级

### 4. `resume_success_rate`

定义：

- 中断后成功恢复的任务数 / 发生中断的任务数

意义：

- 判断是否具备长任务运行条件

### 5. `probe_escape_rate`

定义：

- 需要人工补抓的问题数 / 总问题数

意义：

- 判断 probe 是否足够成熟

### 6. `sync_success_rate`

定义：

- 成功同步到目标环境的对象数 / 总同步对象数

意义：

- 判断 Gemini/桥接链是否稳定

### 7. `governance_violation_rate`

定义：

- 角色越权、假闭环、路径越权等治理违规数 / 总任务数

意义：

- 判断是否还适合继续加量

## 最低输入

至少应从以下材料提取数据：

- `execution_receipt.json`
- `completion_record.md`
- `resume_handoff.md`
- `checkpoint/state.yaml`
- `review_decision`
- `compliance_attestation`
- `cloud_skill_sync_report.md`
- `review_latest.md`
- 其它专项探针输出

## 输出

输出必须至少包含 4 部分：

1. `问题统计总表`
2. `指标趋势摘要`
3. `当前升级建议`
4. `阻断升级的前三个原因`

## 升级判定

统一输出以下 4 种建议之一：

- `HOLD`
  - 当前不应升级
- `LIMITED_UPGRADE`
  - 允许小幅升级
- `READY_FOR_NEXT_STAGE`
  - 满足下一阶段升级条件
- `ROLLBACK_NEEDED`
  - 当前应先回退或收紧

## 推荐闸门

以下条件全部满足时，才建议从“短任务/低并发”升级：

- `false_completion_rate` 持续下降
- `artifact_recovery_rate >= 0.9`
- `manual_intervention_per_task` 明显下降
- `resume_success_rate >= 0.8`
- `probe_escape_rate` 低于预设阈值
- `governance_violation_rate` 不再上升

只要任一关键指标恶化，就不要升级。

## DoD

- [ ] 问题类型使用统一分类
- [ ] 指标定义清楚且可重复计算
- [ ] 升级建议基于数据，不基于感觉
- [ ] 明确指出阻断升级的原因
- [ ] 不把局部成功包装成整体 ready

## 红线

- 不能只用单次成功样本宣布“可升级”
- 不能忽略人工介入成本
- 不能因为 probe PASS 就忽略未覆盖环节
- 不能把“桥接成功一次”写成“链路长期稳定”

## 参考

- `docs/compliance_reviews/review_latest.md`
- `docs/2026-03-08/cloud_skill_sync_report.md`
- `docs/2026-03-08/CODEX_SYNC_GOVERNANCE_v1.md`
- `docs/2026-03-08/CLOUD_MULTI_AGENT_OVERSIGHT_PROTOCOL_v1.md`
- `docs/2026-03-08/DOCKER_VOLUME_受控物理桥接方案_v1.md`
- `references/metrics_schema.md`
- `docs/2026-03-08/GOVERNANCE_TELEMETRY_REPORT_TEMPLATE_v1.md`
