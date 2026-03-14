---
name: backtest-engine-skill
description: 回测引擎（历史数据回放、订单模拟、绩效计算）
---

# backtest-engine-skill

## 触发条件

- 策略验证
- 参数优化
- 风险评估

## 输入

```yaml
input:
  strategy:
    name: "dual_moving_average"
    params:
      fast_period: 12
      slow_period: 26
  data:
    symbol: "AAPL"
    start: "2023-01-01"
    end: "2024-03-09"
  settings:
    initial_capital: 100000
    commission: 0.001
    slippage: 0.0001
    position_size: 0.95
```

## 输出

```yaml
output:
  status: "SUCCESS"
  equity_curve: [...]
  trades:
    - entry: "2023-01-15"
      exit: "2023-02-20"
      type: "LONG"
      entry_price: 150.2
      exit_price: 155.8
      return_pct: 3.73
      return_amt: 3730
  metrics:
    total_return: 0.25
    annual_return: 0.18
    sharpe_ratio: 1.52
    max_drawdown: -0.12
    win_rate: 0.58
    profit_factor: 2.1
```

## 核心功能

### 回测流程

1. **数据准备**: 加载历史数据
2. **信号生成**: 根据策略逻辑生成交易信号
3. **订单模拟**: 处理订单成交（考虑滑点和手续费）
4. **持仓管理**: 维护当前持仓和现金
5. **绩效计算**: 计算各项绩效指标

### 交易类型

- 市价单 (Market Order)
- 限价单 (Limit Order)
- 止损单 (Stop Loss)
- 止盈单 (Take Profit)

### 成本模型

- 手续费: 按交易金额百分比
- 滑点: 按价格偏移
- 资金成本: 融资利息
- 股息: 持仓股息收入

## DoD

- [ ] 完整的回测流程
- [ ] 支持多策略并行
- [ ] 准确的订单模拟
- [ ] 完整的绩效指标
- [ ] 回测报告生成
