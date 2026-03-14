# Execution Runtime Metrics Schema

## 用途

定义 `execution-runtime-telemetry-skill` 的最小字段结构，确保不同执行体、不同任务、不同日期之间的数据可横向比较。

## 顶层字段

- `task_id`
- `executor`
- `start_time`
- `first_output_time`
- `last_output_time`
- `end_time`
- `wall_clock_duration_seconds`
- `effective_execution_duration_seconds`
- `blocked_duration_seconds`
- `files_changed_count`
- `lines_added`
- `lines_deleted`
- `diff_bytes`
- `artifacts_generated_count`
- `tasks_completed_count`
- `subtasks_completed_count`
- `resume_count`
- `manual_intervention_count`
- `recovery_success`
- `skills_loaded`
- `skills_effectively_used`
- `skill_resolution_events`
- `issues_encountered`
- `final_status`
- `deliverable_status`
- `review_status`
- `compliance_status`
- `host_absorb_status`
- `evidence_refs`

## issues_encountered

每个问题事件至少包含：

- `issue_id`
- `issue_type`
- `detected_at`
- `severity`
- `resolved`
- `resolution_mode`
- `evidence_refs`

## skill_resolution_events

每个 skill 解决事件至少包含：

- `issue_type`
- `skill_name`
- `used_at`
- `resolution_summary`
- `evidence_refs`

## 推荐状态值

### final_status

- `EXECUTION_COMPLETE`
- `READY_TO_RESUME`
- `BLOCKED`

### deliverable_status

- `COMPLETE`
- `PARTIAL`
- `MISSING_CRITICAL_ARTIFACTS`

### review_status

- `PENDING`
- `ALLOW`
- `DENY`

### compliance_status

- `PENDING`
- `PASS`
- `FAIL`

### host_absorb_status

- `NOT_STARTED`
- `HOST_ABSORB_MANUAL`
- `ABSORBED`
- `BLOCKED`
