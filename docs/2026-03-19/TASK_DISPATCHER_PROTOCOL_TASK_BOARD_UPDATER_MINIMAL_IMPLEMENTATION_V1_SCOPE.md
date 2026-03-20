# Task Dispatcher Protocol Task Board Updater Minimal Implementation v1 Scope

## 当前模块
- task_dispatcher_protocol task-board-updater minimal implementation v1

## 当前唯一目标
- 落一个最小 updater，用于基于标准 writeback 件安全更新任务板状态，并输出异常摘要。

## 本模块允许项
- 读取任务板 markdown
- 读取 verification 目录中的 writeback 文件
- 推导最小状态
- 安全更新任务板状态列
- 输出 anomaly / summary 报告

## 本模块禁止项
- 不自动发送任务
- 不自动做终验
- 不修改任务卡正文
- 不把异常组合强行改成某个状态
- 不改写模块结论

## 固定输出
- `TASK_DISPATCHER_PROTOCOL_TASK_BOARD_UPDATER_MINIMAL_IMPLEMENTATION_V1_SCOPE.md`
- `TASK_DISPATCHER_PROTOCOL_TASK_BOARD_UPDATER_MINIMAL_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
- `TASK_DISPATCHER_PROTOCOL_TASK_BOARD_UPDATER_MINIMAL_IMPLEMENTATION_V1_REPORT.md`
- `TASK_DISPATCHER_PROTOCOL_TASK_BOARD_UPDATER_MINIMAL_IMPLEMENTATION_V1_CHANGE_CONTROL_RULES.md`
- `tools/task_board_updater.py`

