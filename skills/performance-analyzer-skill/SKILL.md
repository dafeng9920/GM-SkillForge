---
name: performance-analyzer-skill
description: 绩效分析（收益分析、风险调整收益、基准对比）
---

# performance-analyzer-skill

## 触发条件

- 计算策略绩效
- 生成绩效报告
- 对比分析

## 输入

```yaml
input:
  returns: [...]
  benchmark_returns: [...]
  risk_free_rate: 0.02
  analysis_type: "full"  # basic, full, attribution
```

## 输出

```yaml
output:
  status: "SUCCESS"
  return_metrics:
    total_return: 0.25
    annual_return: 0.18
    cagr: 0.175
  risk_metrics:
    volatility: 0.15
    downside_deviation: 0.12
    max_drawdown: -0.08
  risk_adjusted:
    sharpe_ratio: 1.2
    sortino_ratio: 1.5
    calmar_ratio: 2.25
    information_ratio: 0.8
  benchmark_comparison:
    excess_return: 0.05
    tracking_error: 0.08
    beta: 1.1
    alpha: 0.03
```

## 核心功能

### 收益指标

- 总收益
- 年化收益
- CAGR
- 月度/年度收益分布

### 风险指标

- 波动率
- 下行波动率
- 最大回撤
- VaR/CVaR

### 风险调整收益

- 夏普比率
- 索提诺比率
- 卡尔玛比率
- 信息比率
- 特雷纳比率

### 基准对比

- 超额收益
- 跟踪误差
- Alpha/Beta
- 胜率

## DoD
- [ ] 计算所有绩效指标
- [ ] 生成可视化报告
- [ ] 基准对比分析
- [ ] 滚动窗口分析
- [ ] 收益归因
