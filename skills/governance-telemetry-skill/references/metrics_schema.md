# Governance Telemetry Metrics Schema

## 用途

本文件定义 `governance-telemetry-skill` 的最小指标结构，确保不同轮次、不同 agent、不同任务之间可横向比较。

## 统计窗口

每次统计必须注明：

- `window_start`
- `window_end`
- `sample_tasks`
- `sample_sync_events`
- `sample_probe_runs`

## 统一字段

所有指标项统一包含：

- `metric_name`
- `value`
- `unit`
- `window_start`
- `window_end`
- `sample_size`
- `evidence_refs`
- `notes`

## 核心指标定义

### false_completion_rate

- `metric_name`: `false_completion_rate`
- `unit`: `ratio`
- `value`: `false_completion_count / total_task_count`
- `sample_size`: `total_task_count`

### artifact_recovery_rate

- `metric_name`: `artifact_recovery_rate`
- `unit`: `ratio`
- `value`: `recovered_to_authoritative_repo_count / total_delivery_count`
- `sample_size`: `total_delivery_count`

### manual_intervention_per_task

- `metric_name`: `manual_intervention_per_task`
- `unit`: `count_per_task`
- `value`: `manual_intervention_count / total_task_count`
- `sample_size`: `total_task_count`

### resume_success_rate

- `metric_name`: `resume_success_rate`
- `unit`: `ratio`
- `value`: `successful_resume_count / interrupted_task_count`
- `sample_size`: `interrupted_task_count`

### probe_escape_rate

- `metric_name`: `probe_escape_rate`
- `unit`: `ratio`
- `value`: `human_only_detected_issue_count / total_issue_count`
- `sample_size`: `total_issue_count`

### sync_success_rate

- `metric_name`: `sync_success_rate`
- `unit`: `ratio`
- `value`: `successful_sync_object_count / total_sync_object_count`
- `sample_size`: `total_sync_object_count`

### governance_violation_rate

- `metric_name`: `governance_violation_rate`
- `unit`: `ratio`
- `value`: `governance_violation_count / total_task_count`
- `sample_size`: `total_task_count`

## 问题分类字段

每个问题事件至少记录：

- `issue_id`
- `issue_type`
- `task_id`
- `discovered_at`
- `discovered_by`
- `severity`
- `manual_intervention_required`
- `resolved`
- `evidence_refs`

允许的 `issue_type`：

- `path_drift`
- `false_completion`
- `artifact_missing`
- `role_boundary_violation`
- `sync_failure`
- `absorb_failure`
- `probe_gap`
- `skill_drift`
- `resume_failure`
- `governance_doc_drift`

## 升级判定输出

最终结论字段固定为：

- `upgrade_decision`
- `decision_reasoning`
- `blocking_factors`
- `recommended_next_step`

允许值：

- `HOLD`
- `LIMITED_UPGRADE`
- `READY_FOR_NEXT_STAGE`
- `ROLLBACK_NEEDED`
