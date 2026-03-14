---
name: signal-generator-skill
description: 交易信号生成（技术信号、基本面信号、因子信号）
---

# signal-generator-skill

## 触发条件

- 策略需要交易信号
- 实时监控市场
- 信号回测验证

## 输入

```yaml
input:
  symbol: "AAPL"
  signal_type: "technical"  # technical, fundamental, factor
  rules:
    - type: "crossover"
      fast: "EMA_12"
      slow: "EMA_26"
      direction: "bullish"
    - type: "threshold"
      indicator: "RSI_14"
      condition: "below"
      value: 30
```

## 输出

```yaml
output:
  status: "SUCCESS"
  signal: "BUY"
  strength: 0.85
  confidence: 0.78
  reasons:
    - "EMA12 crossed above EMA26"
    - "RSI is oversold (28.5)"
  timestamp: "2024-03-09T10:30:00Z"
```

## 核心功能

### 信号类型

| 类型 | 说明 | 示例 |
|------|------|------|
| crossover | 金叉/死叉 | MA交叉、MACD金叉 |
| threshold | 阈值突破 | RSI超买超卖 |
| pattern | 形态识别 | 双底、头肩顶 |
| breakout | 突破 | 突破阻力位 |
| momentum | 动量 | 价格加速 |

### 信号强度

- 信号强度: 0-1
- 信号置信度: 基于历史胜率
- 多信号融合

## DoD

- [ ] 支持常用技术信号
- [ ] 支持基本面信号
- [ ] 支持因子信号
- [ ] 信号强度评估
- [ ] 多信号融合逻辑
