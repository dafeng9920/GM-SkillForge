# A股量化策略开发指南

> 适用于中国A股市场的多因子动量策略完整开发指南
>
> 创建日期: 2026-03-09

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    A股数据源层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ AKShare     │  │ Tushare     │  │ Baostock    │        │
│  │ (免费推荐)  │  │ (高质量)    │  │ (免费)      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 数据管理层 (Data Fetcher)                   │
│  • 自动数据源切换                                           │
│  • 数据缓存管理                                             │
│  • 错误处理和重试                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  策略引擎层 (Strategy)                       │
│  • 多因子动量策略                                           │
│  • 技术指标计算                                             │
│  • 信号生成                                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  执行层 (Execution)                          │
│  • 实时监控                                                 │
│  • 风险控制                                                 │
│  • 订单管理                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 快速开始

### 1. 安装依赖

```bash
# 基础依赖
pip install pandas numpy

# A股数据源（推荐）
pip install akshare

# 可选：Tushare（需要token）
pip install tushare
```

### 2. 运行演示

```bash
# A股策略演示（模拟数据）
python adapters/quant/strategies/demo_a_share_strategy.py

# 多因子动量策略演示
python adapters/quant/strategies/multi_factor_momentum.py

# 回测测试
python adapters/quant/strategies/tests/test_multi_factor_momentum.py
```

### 3. 使用真实数据

```bash
# 运行实时策略（需要先安装akshare）
python adapters/quant/strategies/live_a_share_trader.py
```

---

## 监控的A股股票

| 代码 | 名称 | 板块 | 特点 |
|------|------|------|------|
| 600519.SH | 贵州茅台 | 主板 | 白酒龙头，高增长 |
| 000001.SZ | 平安银行 | 银行 | 金融板块，稳定分红 |
| 000002.SZ | 万科A | 地产 | 地产龙头，周期性 |
| 600030.SH | 中信证券 | 券商 | 券商龙头，行情风向标 |
| 300750.SZ | 宁德时代 | 创业板 | 新能源龙头，高波动 |
| 002594.SZ | 比亚迪 | 中小板 | 新能源车，成长性 |

---

## 策略配置

### 激进配置（适合牛市）

```python
config = StrategyConfig(
    momentum_weight=0.6,      # 高动量权重
    volatility_weight=0.1,
    volume_weight=0.2,
    rsi_weight=0.1,
    min_composite_score=0.12, # 低买入阈值
    max_position_size=0.35,   # 高仓位
    stop_loss_pct=0.10,       # 宽松止损
    take_profit_pct=0.30      # 高止盈目标
)
```

### 保守配置（适合震荡市）

```python
config = StrategyConfig(
    momentum_weight=0.3,
    volatility_weight=0.35,    # 高稳定性权重
    volume_weight=0.2,
    rsi_weight=0.15,
    min_composite_score=0.25,  # 高买入阈值
    max_position_size=0.20,   # 低仓位
    stop_loss_pct=0.05,       # 严格止损
    take_profit_pct=0.12
)
```

---

## A股市场特点

### 1. 交易制度

| 特点 | 说明 | 影响 |
|------|------|------|
| **涨跌停限制** | ±10%（创业板/科创板±20%） | 限制单日波动，需注意流动性 |
| **T+1 交易** | 当日买入次日才能卖出 | 降低策略灵活性 |
| **融资融券** | 部分股票支持 | 可用于对冲和加杠杆 |
| **股指期货** | 沪深300、中证500等 | 可用于套保 |

### 2. 市场时间

```
交易日: 周一至周五（节假日除外）
交易时间: 9:30-11:30, 13:00-15:00
集合竞价: 9:15-9:25
```

### 3. 数据获取

#### AKShare（推荐）

```python
from adapters.quant.data.china_stock_fetcher import ChinaStockDataFetcher

# 初始化
fetcher = ChinaStockDataFetcher(preferred_source="akshare")

# 获取历史数据
df = fetcher.get_daily_bars(
    symbol="600519.SH",
    start_date="2024-01-01",
    end_date="2024-12-31",
    adjust="qfq"  # 前复权
)

# 获取实时行情
quotes = fetcher.get_realtime_quotes(["600519.SH", "000001.SZ"])
```

---

## 策略优化

### 参数优化流程

1. **数据准备**: 收集2年以上历史数据
2. **网格搜索**: 遍历参数组合
3. **交叉验证**: 时间序列交叉验证
4. **绩效评估**: 夏普比率、最大回撤、胜率
5. **实盘验证**: 模拟盘测试

### 关键参数

| 参数 | 范围 | 推荐值 | 说明 |
|------|------|--------|------|
| momentum_weight | 0.3-0.6 | 0.5 | 动量因子权重 |
| min_composite_score | 0.1-0.3 | 0.15 | 买入阈值 |
| max_position_size | 0.2-0.4 | 0.25 | 最大仓位 |
| stop_loss_pct | 0.05-0.10 | 0.08 | 止损幅度 |

---

## 风险管理

### A股特有风险

1. **政策风险**: 政策变化对市场影响大
2. **流动性风险**: 小盘股可能存在流动性问题
3. **黑天鹅风险**: 突发事件难以预测
4. **技术风险**: 系统故障、网络中断

### 风险控制措施

```python
# 仓位限制
MAX_POSITION_SIZE = 0.25      # 单股最大仓位
MAX_TOTAL_POSITION = 0.8      # 总仓位上限

# 止损止盈
STOP_LOSS_PCT = 0.08         # 8% 止损
TAKE_PROFIT_PCT = 0.20       # 20% 止盈

# 持仓数量限制
MAX_POSITIONS = 5             # 最多持有5只股票

# 换手率控制
MAX_TURNOVER = 0.5           # 月换手率不超过50%
```

---

## 实盘部署

### 1. 模拟盘测试

```python
# 使用模拟券商API
from simulator import SimulatedBroker

broker = SimulatedBroker(
    initial_capital=1000000,
    commission_rate=0.0003,  # 万三佣金
    slippage_rate=0.001      # 0.1% 滑点
)

# 运行策略
strategy = MultiFactorMomentumStrategy(config)
strategy.run_backtest(broker, days=252)
```

### 2. 实盘连接

```python
# 支持的券商API
# - 华泰证券
# - 国金证券
# - 银河证券
# 东方财富API（模拟）

# 示例：连接实盘
from broker import RealBroker

broker = RealBroker(
    broker_id="htsc",
    account="your_account",
    password="your_password"
)

# 风险检查
broker.set_risk_controls({
    "max_position": 0.25,
    "stop_loss": 0.08,
    "daily_loss_limit": 0.03
})
```

### 3. 监控告警

```python
# 设置监控指标
alerts = [
    {"type": "drawdown", "threshold": -0.10, "action": "email"},
    {"type": "position", "threshold": 0.30, "action": "sms"},
    {"type": "signal", "symbols": ["BUY"], "action": "webhook"}
]
```

---

## 性能监控

### 关键指标

```python
# 每日监控
daily_metrics = {
    "总权益": portfolio.total_value,
    "今日盈亏": daily_pnl,
    "持仓数量": len(positions),
    "现金比例": cash / total_value,
}

# 每周分析
weekly_metrics = {
    "收益率": weekly_return,
    "夏普比率": sharpe_ratio,
    "最大回撤": max_drawdown,
    "胜率": win_rate,
}

# 每月报告
monthly_metrics = {
    "月收益": monthly_return,
    "换手率": turnover_rate,
    "交易次数": trade_count,
}
```

---

## 故障排除

### 常见问题

**Q: AKShare无法安装？**
```bash
# 使用国内镜像
pip install akshare -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Q: 数据获取失败？**
```python
# 检查网络连接
import requests
response = requests.get("http://www.baidu.com")
print(response.status_code)  # 应该返回200

# 使用备用数据源
fetcher = ChinaStockDataFetcher(preferred_source="tushare")
```

**Q: 策略无信号？**
- 检查数据完整性（需要至少20天历史数据）
- 调整策略阈值（降低min_composite_score）
- 检查市场环境（震荡市信号较少）

---

## 相关资源

### 数据源

- [AKShare文档](https://akshare.akfamily.xyz/)
- [Tushare文档](https://tushare.pro/document/2)
- [Baostock文档](http://baostock.com/baostock-web/)

### 策略文档

- [多因子动量策略指南](QUANT_STRATEGY_GUIDE.md)
- [Phase 4 系统文档](./2026-02-22/量化/PHASE4_DETAILED_PLAN.md)
- [回测引擎文档](./2026-02-22/量化/QUANT_SYSTEM_FULL_ARCHITECTURE.md)

### 社区

- GM-SkillForge GitHub
- 量化交易技术交流群
- A股量化投资论坛

---

**版本**: 1.0.0
**最后更新**: 2026-03-09
**维护者**: GM-SkillForge Team
