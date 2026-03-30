# GM LITE Flow Observability And Output Reporting v1

## 核心结论
- 当插件自动流转开始可用后，必须补一层 `监控件 + 产出报告`
- 目标不是花哨统计，而是让系统能回答：
  - 从启动到结束做了什么
  - 产出了多少
  - 完成了多少任务
  - 花了多少时间
  - 达到了什么结果

## 监控层的意义
- 让自动流转不再是黑箱
- 让主控官能快速判断：
  - 效率
  - 成本
  - 稳定性
  - 产出质量
- 为后续优化提供依据

## 最低监控维度

### 1. 运行区间
- `run_started_at`
- `run_finished_at`
- `duration_seconds`
- 默认解释为：
  - `系统内生过程时间`
  - 即从本次运行启动到本次任务完成/中止的耗时
- 不以现实世界钟表时间作为核心评估口径
- 更推荐补充：
  - `run_t0`
  - `task_elapsed_ms`
  - `step_duration_seconds`
  - `time_to_gate_ready`
  - `time_to_writeback`
  - `time_to_completion`

### 2. 任务产出
- `tasks_total`
- `tasks_completed`
- `tasks_blocked`
- `tasks_failed`
- `gate_ready_count`

### 3. 代码产出
- `files_created`
- `files_updated`
- `lines_added`
- `lines_deleted`
- `net_lines_changed`

### 4. 自动流转效率
- `send_actions_triggered`
- `writebacks_received`
- `state_transitions_completed`
- `manual_interventions_count`

### 5. 成本与资源
- `token_burn_total`
- `retry_total`
- `suspend_total`
- `critical_error_total`

### 6. 结果摘要
- `main_outcomes`
- `key_artifacts`
- `final_status`

## 推荐产物

### A. 运行时指标文件
- 例如：
  - `D:\gm-lite\_runtime\reports\run_metrics.json`

### B. 人眼摘要报告
- 例如：
  - `D:\gm-lite\_runtime\reports\run_summary.md`

### C. 插件内最小展示
- 例如：
  - 最近一次运行时长
  - 完成任务数
  - 代码产出量
  - 当前最终状态

## 当前不前置实现
- 不在当前 `manual_transfer_elimination_minimal_implementation` 里插队实现
- 先记为下一层增强件

## 建议归属的未来主线
- `gm_lite_flow_observability_preparation_v1`
- 后续再进：
  - `gm_lite_flow_observability_minimal_implementation_v1`

## 主控官结论
- 自动流转一旦开始，监控件就必须跟上
- 否则系统只是“会跑”，但不会“自我说明”
- 这层最终会成为插件内的产出报告与效率仪表盘基础
- 时间口径默认应以 `系统过程时间` 为准，而不是现实世界时间
