---
name: capability-evolver-skill
description: OpenClaw 2026 “养成系”自进化核心。通过对操作历史轨迹的自反思和协议约束下的自修改，实现智能体的越用越聪明。
---

# capability-evolver-skill

## 触发条件

- 任务完成后的“复盘时刻 (Reflection Time)”
- 连续出现同类操作失败或低效时
- 收到 Commander 的“能力升级”专项指令

## 演化维度 (Evolution Paths)

1. **Protocol Refinement**: 自主修正 `openclaw.json` 中的紧缩 (compaction) 策略或上下文管理参数。
2. **Logic Distillation**: 将复杂的重复操作序列抽象为新的“原子 Skill”并提交给 Commander 审计。
3. **Reasoning Calibration**: 根据实战反馈调整“意志识别”或“打分倾向”权重。

## 演化流程 (Evolution Loop)

1. **Trajectory Audit**: 回溯历史 Session，提取“逻辑死点”或“冗余跳过点”。
2. **Proposal Generation**: 生成针对性的优化提案（如：更改 Prompts、精简流程）。
3. **Simulation Test**: 在本地沙盒预演提案，确保不违反 `Permit Guard`。
4. **Injection**: 审计通过后，正式注入新的逻辑因子。

## DoD

- [ ] 具备“自反思”产生的日志审计记录
- [ ] 所有的自修改建议必须经过 Aegis Audit 扫描
- [ ] 性能随使用时长提升的趋势可量化跟踪
