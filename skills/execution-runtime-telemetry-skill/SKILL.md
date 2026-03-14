---
name: execution-runtime-telemetry-skill
description: 用于统计云端执行任务的起止时间、有效工作时长、代码改动量、完成的任务/子任务数量、遇到的问题、人工介入次数、触发和使用的 skill，以及最终交付状态。适用于需要把“小龙虾/云端 Codex 到底做了多少事、花了多久、靠什么 skill 解决问题”变成可审计数据证据的场景。
---

# execution-runtime-telemetry-skill

## 目标

把“这次任务到底干了多少活、花了多久、遇到了什么问题”变成结构化可审计数据。

本 skill 不负责执行任务本身。  
本 skill 负责在任务运行期间与收口时输出：

- 时间统计
- 工作量统计
- 问题与恢复统计
- skill 使用统计
- 最终任务完成统计

## 最低产物

每个任务至少新增两份运行时统计产物：

- `execution_runtime_report.json`
- `execution_runtime_summary.md`

如需要对外播报或发群/朋友圈式同步，再额外输出：

- `execution_runtime_moments.md`

建议再把精简统计写回：

- `manifest.json.runtime_stats`
- `manifest.json.skills_used`
- `manifest.json.issues`

## 统计维度

### 1. 时间

必须统计：

- `start_time`
- `first_output_time`
- `last_output_time`
- `end_time`
- `wall_clock_duration_seconds`
- `effective_execution_duration_seconds`
- `blocked_duration_seconds`

### 2. 工作量

至少统计：

- `files_changed_count`
- `lines_added`
- `lines_deleted`
- `diff_bytes`
- `artifacts_generated_count`
- `tasks_completed_count`
- `subtasks_completed_count`

### 3. 问题与恢复

至少统计：

- `issues_encountered`
- `resume_count`
- `manual_intervention_count`
- `recovery_success`

统一问题类型优先使用：

- `context_window_exceeded`
- `path_drift`
- `write_failed`
- `sync_failure`
- `missing_artifact`
- `absorb_failure`
- `skill_not_loaded`
- `other`

### 4. skill 使用

必须记录：

- `skills_loaded`
- `skills_effectively_used`
- `skill_resolution_events`

每个 `skill_resolution_event` 至少包含：

- `issue_type`
- `skill_name`
- `resolution_summary`

## 时间口径

统一区分两种耗时：

### wall_clock_duration_seconds

从任务正式开始到任务结束的总自然时间。

### effective_execution_duration_seconds

真正用于执行、写文件、跑命令、整理交付包的有效工作时间。  
不包含纯等待、阻塞、主控离线等待、网络桥接等待。

## 任务完成统计

最终必须给出：

- `final_status`
- `deliverable_status`
- `review_status`
- `compliance_status`
- `host_absorb_status`

建议允许值：

- `EXECUTION_COMPLETE`
- `READY_TO_RESUME`
- `BLOCKED`
- `WAITING_REVIEW`
- `WAITING_COMPLIANCE`
- `HOST_ABSORB_MANUAL`

## 接入点

建议在以下节点更新统计：

1. 任务启动时写 `start_time`
2. 首个有效输出后写 `first_output_time`
3. 每次问题/阻塞时追加 `issues_encountered`
4. 每次 resume/handoff 时更新 `resume_count`
5. 收口时写 `end_time` 与最终统计

## 红线

- 不得只报总耗时，不报有效耗时
- 不得只报改了多少文件，不报问题和人工介入
- 不得把“skill 被加载”写成“skill 真解决了问题”
- 不得在没有证据的情况下写“完成了很多工作”

## DoD

- [ ] 有 JSON 结构化统计
- [ ] 有 Markdown 摘要
- [ ] 时间、工作量、问题、skill 使用四类统计齐全
- [ ] 最终状态与交付状态可被主控复核
- [ ] 能回答“做了多久、改了多少、遇到什么问题、靠什么 skill 解决”

## 参考

- `references/runtime_metrics_schema.md`
- `docs/2026-03-08/EXECUTION_RUNTIME_REPORT_TEMPLATE_v1.md`
- `docs/2026-03-08/EXECUTION_RUNTIME_MOMENTS_TEMPLATE_v1.md`
- `skills/governance-telemetry-skill/SKILL.md`
- `docs/2026-03-08/LOBSTER_TASK_PACKAGE_SPEC.md`
