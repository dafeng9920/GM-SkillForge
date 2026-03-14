# 多因子动量策略 - 部署和使用指南

> 策略类型: 中长期趋势跟踪
> 风险等级: 中等
> 创建日期: 2026-03-09

---

## 策略概述

### 核心逻辑

多因子动量策略通过综合考虑4个技术因子来生成交易信号：

1. **价格动量因子** (40%权重) - 12个月收益率
2. **波动率因子** (20%权重) - 20日波动率（低波动率得分高）
3. **成交量因子** (20%权重) - 成交量变化率
4. **RSI因子** (20%权重) - 相对强弱指标

### 交易规则

| 信号类型 | 触发条件 | 操作 |
|---------|---------|------|
| **买入** | 综合得分 ≥ 0.25 且置信度 ≥ 55% | 按仓位建议买入 |
| **卖出** | 综合得分 ≤ -0.25 | 全部卖出 |
| **止损** | 亏损达到 8% | 立即平仓 |
| **止盈** | 盈利达到 20% | 立即平仓 |

### 仓位管理

- **基础仓位**: 10% 的可用资金
- **最大仓位**: 25% 的可用资金
- **动态调整**: 根据综合得分增减仓位

---

## 文件结构

```
adapters/quant/strategies/
├── multi_factor_momentum.py          # 策略核心实现
└── tests/
    └── test_multi_factor_momentum.py # 回测脚本
```

---

## 快速开始

### 1. 运行策略演示

```bash
python adapters/quant/strategies/multi_factor_momentum.py
```

输出示例：
```
============================================================
多因子动量策略演示
============================================================

因子得分:
  动量因子: 0.038
  波动率因子: 0.158
  成交量因子: 0.000
  RSI因子: -1.000
  综合得分: -0.153

交易信号:
  动作: HOLD
  置信度: 60.6%
  建议仓位: 5.0%
```

### 2. 运行回测

```bash
python adapters/quant/strategies/tests/test_multi_factor_momentum.py
```

### 3. 在代码中使用

```python
from adapters.quant.strategies.multi_factor_momentum import (
    MultiFactorMomentumStrategy,
    MarketData,
    StrategyConfig
)
from datetime import datetime

# 创建策略配置
config = StrategyConfig(
    momentum_weight=0.4,
    volatility_weight=0.2,
    volume_weight=0.2,
    rsi_weight=0.2,
    min_composite_score=0.25,
    min_confidence=0.55,
    stop_loss_pct=0.08,
    take_profit_pct=0.20
)

# 创建策略实例
strategy = MultiFactorMomentumStrategy(config=config)

# 准备市场数据
market_data = MarketData(
    symbol="AAPL",
    timestamp=datetime.now(),
    open=150.0,
    high=152.0,
    low=149.0,
    close=151.0,
    volume=50000000,
    historical_closes=[148.5, 149.2, 150.1, ...],  # 历史收盘价
    historical_volumes=[45000000, 48000000, ...]    # 历史成交量
)

# 生成交易信号
signal = strategy.generate_signal(market_data)

print(f"信号: {signal.action}")
print(f"置信度: {signal.confidence:.1%}")
print(f"建议仓位: {signal.position_size:.1%}")
print(f"理由: {signal.reasoning}")
```

---

## 集成到 Phase 4 系统

### 1. 创建 Phase 4 包装器

```python
# adapters/quant/strategies/integrations/phase4_multi_factor.py

from adapters.quant.strategies.multi_factor_momentum import (
    MultiFactorMomentumStrategy,
    MarketData as MFMarketData,
    StrategyConfig
)
from adapters.quant.phase4.engine import Phase4Engine

class Phase4MultiFactorWrapper:
    """Phase 4 系统包装器"""

    def __init__(self, config: StrategyConfig = None):
        self.strategy = MultiFactorMomentumStrategy(config)
        self.phase4 = Phase4Engine(config={
            'min_breakout_amp': 0.015,
            'min_volume_ratio': 1.3,
            'min_resonance': 2,
        })

    def on_tick(self, tick_data: dict, portfolio_state: dict) -> list:
        """处理tick数据"""

        # 1. 转换为策略数据格式
        market_data = MFMarketData(
            symbol=tick_data['symbol'],
            timestamp=tick_data['timestamp'],
            open=tick_data['price'] * 0.995,
            high=tick_data['price'] * 1.005,
            low=tick_data['price'] * 0.995,
            close=tick_data['price'],
            volume=tick_data['volume']
        )

        # 2. 更新历史数据
        self.strategy.update_market_data(market_data)

        # 3. 获取 enriched 数据
        enriched = self.strategy.get_enriched_data(
            tick_data['symbol'],
            market_data
        )

        # 4. 生成信号
        signal = self.strategy.generate_signal(enriched)

        # 5. Phase 4 确认层验证
        phase4_signals = self.phase4.on_tick(tick_data, portfolio_state)

        # 6. 合并信号（只在两者都同意时交易）
        if signal.action == "BUY" and any(
            s.get('signal_type') == 'BUY' for s in phase4_signals
        ):
            return [{
                "symbol": signal.symbol,
                "timestamp": signal.timestamp,
                "signal_type": "BUY",
                "confidence": min(signal.confidence, 0.8),
                "price": signal.stop_loss,
                "reason": f"多因子+Phase4确认: {signal.reasoning}"
            }]

        return []
```

### 2. 在回测中使用

```python
from adapters.quant.backtest.engine import BacktestEngine
from adapters.quant.strategies.integrations.phase4_multi_factor import Phase4MultiFactorWrapper

# 创建包装器
wrapper = Phase4MultiFactorWrapper()

# 创建回测引擎
engine = BacktestEngine(
    initial_capital=100000,
    commission=0.001,
    signal_handler=wrapper.on_tick
)

# 运行回测
results = engine.run(tick_data_list)
results.print_report()
```

---

## 参数优化

### 激进配置（高收益高风险）

```python
config = StrategyConfig(
    momentum_weight=0.5,      # 提高动量权重
    volatility_weight=0.1,
    volume_weight=0.2,
    rsi_weight=0.2,
    min_composite_score=0.2,  # 降低买入阈值
    max_composite_score=-0.2,
    min_confidence=0.5,       # 降低置信度阈值
    max_position_size=0.4,    # 提高最大仓位
    base_position_size=0.15,
    stop_loss_pct=0.10,       # 宽松止损
    take_profit_pct=0.25      # 更高止盈目标
)
```

### 保守配置（稳健收益）

```python
config = StrategyConfig(
    momentum_weight=0.3,
    volatility_weight=0.3,    # 提高波动率权重（追求稳定）
    volume_weight=0.2,
    rsi_weight=0.2,
    min_composite_score=0.3,  # 提高买入阈值
    max_composite_score=-0.3,
    min_confidence=0.65,      # 提高置信度阈值
    max_position_size=0.2,    # 降低最大仓位
    base_position_size=0.08,
    stop_loss_pct=0.05,       # 严格止损
    take_profit_pct=0.12
)
```

---

## 性能监控

### 关键指标

| 指标 | 目标值 | 监控方法 |
|------|--------|---------|
| 胜率 | > 55% | `win_trades / total_trades` |
| 夏普比率 | > 1.0 | 年化收益 / 年化波动率 |
| 最大回撤 | < -15% | 滚动最大值回撤 |
| 平均盈亏比 | > 1.5 | 平均盈利 / 平均亏损 |

### 警告阈值

```python
ALERT_THRESHOLDS = {
    "min_win_rate": 0.50,        # 胜率低于50%警告
    "min_sharpe": 0.8,           # 夏普比率低于0.8警告
    "max_drawdown": -0.20,       # 回撤超过-20%警告
    "min_avg_win_loss": 1.2,     # 盈亏比低于1.2警告
}
```

---

## 风险提示

⚠️ **重要提示**:

1. **历史表现不代表未来**: 回测结果不能保证未来收益
2. **市场适应性**: 策略在不同市场环境下表现可能差异很大
3. **参数敏感性**: 策略表现对参数设置敏感，需定期优化
4. **滑点影响**: 实际交易中的滑点可能显著影响收益
5. **流动性风险**: 大额交易可能面临流动性不足问题

---

## 下一步

1. **数据接入**: 集成真实市场数据源
2. **实盘测试**: 在模拟环境中测试
3. **参数优化**: 基于最新数据优化参数
4. **风险管理**: 添加更多风险控制机制
5. **性能监控**: 建立实时监控系统

---

## 参考资源

- [Phase 4 系统文档](../docs/2026-02-22/量化/PHASE4_DETAILED_PLAN.md)
- [回测引擎文档](../docs/2026-02-22/量化/QUANT_SYSTEM_FULL_ARCHITECTURE.md)
- [交易执行系统](../core/trading/)

---

**版本**: 1.0.0
**最后更新**: 2026-03-09
**维护者**: GM-SkillForge Team
