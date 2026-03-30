# GM LITE Dispatch Assist Preparation v1 Acceptance

## 通过标准

### A. 职责边界
- 已明确 dispatch assist 只负责半自动派发辅助，不承担自动发送
- 已明确 dispatch assist 与 `.gm_bus`、controller console、verification 的关系

### B. 输入输出
- 已明确 assist 的最小输入对象
- 已明确 assist 的最小输出对象
- 已明确权威路径判断规则

### C. assist 动作
- 已明确 next hop assist
- 已明确 missing piece / backfill assist
- 已明确 dispatch packet build assist

### D. 禁止项
- 已明确自动发送、receipt/ack、timeout/retry、direct-connect 不在本轮
- 已明确 change control

## 不通过条件
- 任何任务越界到自动发送或 direct-connect
- 任何任务把 assist 写成完整 runtime
- 任何任务未给出标准写回与下一跳
