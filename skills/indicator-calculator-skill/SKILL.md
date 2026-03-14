---
name: indicator-calculator-skill
description: 计算技术指标（MA、MACD、RSI、布林带等）
---

# indicator-calculator-skill

## 触发条件

- 策略需要技术指标
- 信号生成需要
- 技术分析需求

## 输入

```yaml
input:
  data:
    symbol: "AAPL"
    timeframe: "1d"
    ohlcv: [...]
  indicators:
    - name: "SMA"
      params: {period: 20}
    - name: "EMA"
      params: {period: 12}
    - name: "RSI"
      params: {period: 14}
    - name: "MACD"
      params: {fast: 12, slow: 26, signal: 9}
    - name: "BOLLINGER_BANDS"
      params: {period: 20, std_dev: 2}
```

## 输出

```yaml
output:
  status: "SUCCESS"
  indicators:
    SMA_20: [150.2, 151.3, 152.1, ...]
    EMA_12: [150.5, 151.2, 152.0, ...]
    RSI_14: [58.3, 60.1, 59.7, ...]
    MACD:
      macd: [1.2, 1.5, 1.3, ...]
      signal: [1.0, 1.2, 1.1, ...]
      histogram: [0.2, 0.3, 0.2, ...]
    BOLLINGER_BANDS_20_2:
      upper: [155.0, 155.5, 156.0, ...]
      middle: [150.0, 150.5, 151.0, ...]
      lower: [145.0, 145.5, 146.0, ...]
```

## 核心功能

### 趋势指标

| 指标 | 说明 | 参数 |
|------|------|------|
| SMA | 简单移动平均 | period |
| EMA | 指数移动平均 | period |
| WMA | 加权移动平均 | period |
| MACD | 指数平滑异同移动平均线 | fast, slow, signal |

### 动量指标

| 指标 | 说明 | 参数 |
|------|------|------|
| RSI | 相对强弱指标 | period |
| Stochastic | 随机指标 | k_period, d_period |
| Momentum | 动量 | period |
| ROC | 变动率 | period |

### 波动率指标

| 指标 | 说明 | 参数 |
|------|------|------|
| Bollinger Bands | 布林带 | period, std_dev |
| ATR | 真实波幅 | period |
| Keltner Channels | 肯特纳通道 | period |

### 成交量指标

| 指标 | 说明 | 参数 |
|------|------|------|
| OBV | 能量潮 | - |
| VWAP | 成交量加权平均价 | - |
| Volume MA | 成交量移动平均 | period |

## 实现细节

```python
class IndicatorCalculator:
    async def calculate(self, data: pd.DataFrame, indicators: List[dict])
    async def calculate_sma(self, data: pd.Series, period: int) -> pd.Series
    async def calculate_ema(self, data: pd.Series, period: int) -> pd.Series
    async def calculate_rsi(self, data: pd.Series, period: int) -> pd.Series
    async def calculate_macd(self, data: pd.Series, fast: int, slow: int, signal: int)
    async def calculate_bollinger_bands(self, data: pd.Series, period: int, std_dev: float)
```

## DoD

- [ ] 支持至少 15 个常用技术指标
- [ ] 支持 Pandas DataFrame 输入输出
- [ ] 支持批量计算多个指标
- [ ] 处理边界情况（NaN、短数据）
- [ ] 高性能计算（使用 NumPy 向量化）
