---
name: strategy-builder-skill
description: 策略构建器（组合多种信号、构建完整策略）
---

# strategy-builder-skill

## 触发条件

- 构建新策略
- 组合多个信号
- 策略回测

## 输入

```yaml
input:
  name: "dual_ma_momentum"
  signals:
    - signal: "ma_crossover"
      weight: 0.6
    - signal: "rsi_filter"
      weight: 0.4
  entry_rules:
    - "both_bullish"
  exit_rules:
    - "stop_loss_5pct"
    - "take_profit_10pct"
  position_sizing: "kelly"
```

## 输出

```yaml
output:
  status: "SUCCESS"
  strategy_id: "dual_ma_momentum_v1"
  code: "..."
  backtest_ready: true
```

## 核心功能

### 信号组合

- 加权组合
- 逻辑组合（AND/OR）
- 投票机制

### 入场/出场规则

- 入场条件
- 出场条件
- 止损/止盈

### 仓位管理

- 等权重
- 风险平价
- Kelly公式
- 波动率目标

## DoD
- [ ] 支持多信号组合
- [ ] 可配置的入场/出场规则
- [ ] 多种仓位管理方式
- [ ] 生成可回测代码
