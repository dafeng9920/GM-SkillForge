# GM Shared Task Bus Minimal Validation v1 Acceptance

## 通过标准
1. `.gm_bus` 目录结构与实现文档一致
2. 六个协议对象最小定义齐全
3. `manifest / task_board / projector / validator` 边界清晰
4. 样板链路验证无阻断性问题
5. 未混入 runtime / SQLite / adapter / 插件直连
6. 四个子任务三件套齐全
7. 模块报告可给出明确：通过 / 局部退回 / 整体退回

## 退回标准
1. 结构与文档明显不一致
2. 协议对象缺失关键项
3. `task_board` 被写成权威写源
4. 样板链无法支撑最小共享任务现实
5. 混入 runtime / SQLite / adapter
6. 回收件不完整

## 局部修正后再审
- 命名问题
- README / example 小缺口
- 非阻断性字段建议
- 轻微文档不一致
