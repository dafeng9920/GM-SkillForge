---
name: research-loop-skill
description: OpenClaw 自动实验室。实现“假设-实验-评估”的自主闭环，专注于量化策略与技术架构的持续优化。
---

# research-loop-skill

## 触发条件

- 市场行情进入“新常态”，原有裁决评分倾向出现持续偏离。
- 需要调研新的技术选型（如：n8n 节点效率测试）。
- 执行 `CapabilityEvolver` 提出的实验性改良提案。

## 实验循环 (Experimental Loop)

1. **Hypothesis**: 提出具体假设（如：“如果将换手率权重调高 10%，打分准确率会提升”）。
2. **Backtest/Simulation**: 在历史数据或本地沙盒中运行自动化测试任务。
3. **Metric Evaluation**: 基于指定的标量指标（Accuracy, ROI, Latency）评估结果。
4. **Conclusion**: 自动生成实验报告，并建议是否将修改合并至 Production 环境。

## DoD

- [ ] 具备自动化的回测数据加载能力
- [ ] 实验报告包含清晰的“对比（Before vs After）”数据
- [ ] 任何策略变更必须先通过 `Aegis Audit` 和 Commander 终审
