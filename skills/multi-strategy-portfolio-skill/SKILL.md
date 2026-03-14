---
name: multi-strategy-portfolio-skill
description: 多策略组合（策略组合、相关性管理、资金分配）
---

# multi-strategy-portfolio-skill

## 触发条件

- 多策略运行
- 组合优化
- 相关性调整

## 输入

```yaml
input:
  strategies:
    - id: "MA_CROSS"
      weight: 0.4
      returns: [...]
    - id: "MEAN_REVERSION"
      weight: 0.3
      returns: [...]
    - id: "MOMENTUM"
      weight: 0.3
      returns: [...]
  optimization:
    method: "sharpe_ratio"
    rebalance_frequency: "weekly"
    max_correlation: 0.7
```

## 输出

```yaml
output:
  status: "SUCCESS"
  optimal_weights:
    MA_CROSS: 0.35
    MEAN_REVERSION: 0.25
    MOMENTUM: 0.40
  portfolio_metrics:
    expected_return: 0.15
    expected_volatility: 0.12
    sharpe_ratio: 1.25
    correlation_matrix: {...}
```

## 核心功能

### 组合方法

| 方法 | 说明 |
|------|------|
| equal_weight | 等权重 |
| return_based | 基于收益率分配 |
| risk_based | 基于风险分配 |
| sharpe_optimization | 夏普比率优化 |
| diversification | 最大化分散度 |

### 相关性管理

- 计算策略相关性
- 限制高相关策略
- 动态调整权重

## DoD

- [ ] 支持多种组合方法
- [ ] 相关性计算和管理
- [ ] 动态权重调整
- [ ] 组合绩效归因
