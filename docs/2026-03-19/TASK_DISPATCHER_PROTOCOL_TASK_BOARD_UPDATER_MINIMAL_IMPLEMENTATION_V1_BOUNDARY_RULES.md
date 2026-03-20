# Task Dispatcher Protocol Task Board Updater Minimal Implementation v1 Boundary Rules

## 功能边界
- updater 只负责“根据标准回收件推导状态并安全写回任务板”
- updater 不负责生成任务卡
- updater 不负责投递下一跳
- updater 不负责最终裁决

## 状态边界
- 仅允许自动写入：
  - `未开始`
  - `待审查`
  - `待合规`
  - `待验收`
- 不自动写入：
  - `通过`
  - `退回`

## 异常边界
- 如果出现 review/compliance 存在但 execution 缺失等异常组合
- updater 只输出 anomaly，不擅自纠偏

## 输入边界
- 只读取指定 task board
- 只读取指定 verification 目录
- 只解析任务表中的 task_id

## 输出边界
- 更新任务板状态列
- 输出 summary.json
- 输出 anomalies.json

