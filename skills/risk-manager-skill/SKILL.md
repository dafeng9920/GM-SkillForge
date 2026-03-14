---
name: risk-manager-skill
description: 风险管理（VaR、CVaR、风险归因、压力测试）
---

# risk-manager-skill

## 触发条件

- 计算组合风险
- 风险限额检查
- 压力测试

## 输入

```yaml
input:
  portfolio:
    AAPL: 10000
    MSFT: 8000
    GOOGL: 12000
  risk_measures:
    - "VaR"
    - "CVaR"
    - "beta"
  confidence_level: 0.95
  time_horizon: 1  # days
```

## 输出

```yaml
output:
  status: "SUCCESS"
  risk_metrics:
    portfolio_value: 30000
    var_95_1d: 1500
    cvar_95_1d: 2100
    beta: 1.2
    volatility: 0.18
  risk_contributions:
    AAPL: 0.35
    MSFT: 0.28
    GOOGL: 0.37
  alerts:
    - type: "var_exceeded"
      message: "VaR 超过限额"
```

## 核心功能

### 风险指标

| 指标 | 说明 |
|------|------|
| VaR | 在险价值 |
| CVaR | 条件在险价值 |
| Beta | 系统性风险 |
| Volatility | 波动率 |
| Tracking Error | 跟踪误差 |
| Maximum Drawdown | 最大回撤 |

### 风险控制

- 仓位限额
- 行业集中度限制
- 止损设置
- 风险归因

## DoD
- [ ] 计算 VaR/CVaR
- [ ] 风险归因分析
- [ ] 压力测试
- [ ] 风险限额检查
- [ ] 实时风险监控
