# A股量化交易系统 📈

完整的A股量化交易系统，支持实时数据获取、多因子策略、模拟交易、风险管理和Web监控。

## ✨ 功能特性

### 核心功能
- ✅ **实时A股数据** - 使用AKShare获取真实实时行情
- ✅ **多因子策略** - 动量、波动率、成交量、RSI多因子分析
- ✅ **模拟交易** - 完整的模拟券商系统，支持市价单和限价单
- ✅ **风险管理** - 仓位控制、止损止盈、最大回撤控制
- ✅ **交易日志** - 完整的交易记录持久化，支持绩效分析
- ✅ **实时监控** - 命令行仪表板 + Web界面
- ✅ **回测引擎** - 历史数据回测验证策略

### 交易功能
- 📊 **订单管理** - 市价单、限价单、订单撤销
- 💼 **持仓管理** - 实时持仓跟踪、浮动盈亏计算
- 💰 **资金管理** - 资金使用、冻结资金、手续费计算
- 📈 **绩效分析** - 资金曲线、收益率、最大回撤、夏普比率
- 🎯 **风险控制** - 仓位限制、止损止盈、单日亏损限制

## 🚀 快速开始

### 1. 安装依赖

```bash
# 核心依赖
pip install akshare pandas numpy

# Web界面（可选）
pip install streamlit plotly
```

### 2. 启动方式

#### 方式一：命令行模式

```bash
# 进入项目目录
cd d:\GM-SkillForge

# 运行一次（测试）
python adapters/quant/trading/start_trading.py --once

# 自动交易模式（每60秒刷新）
python adapters/quant/trading/start_trading.py

# 自定义参数
python adapters/quant/trading/start_trading.py \
    --capital 500000 \
    --symbols 600519.SH 000001.SZ 000002.SZ \
    --interval 30
```

#### 方式二：Web监控模式

```bash
# 启动Web界面
python adapters/quant/trading/start_trading.py --web

# 或直接使用streamlit
streamlit run adapters/quant/trading/web_monitor.py
```

浏览器会自动打开 http://localhost:8501

## 📁 系统架构

```
adapters/quant/trading/
├── quant_trading_system.py    # 主交易系统
├── simulated_broker.py         # 模拟券商
├── trade_journal.py            # 交易日志
├── trading_dashboard.py        # 命令行仪表板
├── web_monitor.py              # Web监控界面
└── start_trading.py            # 快速启动脚本

adapters/quant/strategies/
├── multi_factor_momentum.py    # 多因子动量策略
└── live_a_share_trader.py      # A股实时交易器

adapters/quant/data/
└── china_stock_fetcher.py      # A股数据获取
```

## 🎯 使用指南

### 基本流程

1. **初始化系统**
   ```python
   from adapters.quant.trading.quant_trading_system import QuantTradingSystem

   system = QuantTradingSystem(
       initial_capital=1000000,  # 初始资金100万
       symbols=["600519.SH", "000001.SZ"],  # 监控股票
       data_dir="trading_data"  # 数据目录
   )

   # 加载历史数据
   system.load_historical_data(days=120)
   ```

2. **运行一次**
   ```python
   system.run_once()
   ```

3. **自动运行**
   ```python
   system.run_auto(interval_seconds=60)
   ```

### 命令行参数

```bash
python adapters/quant/trading/start_trading.py --help

选项:
  --web               启动Web监控界面
  --once              只运行一次后退出
  --capital FLOAT     初始资金（默认: 1000000）
  --symbols SYMBOLS   监控股票代码列表
  --interval INT      刷新间隔/秒（默认: 60）
  --data-dir STR      数据保存目录（默认: trading_data）
```

### 热门股票代码

```python
# 默认监控的热门股票
popular_stocks = [
    "600519.SH",  # 贵州茅台
    "000001.SZ",  # 平安银行
    "000002.SZ",  # 万科A
    "600030.SH",  # 中信证券
    "600036.SH",  # 招商银行
    "601318.SH",  # 中国平安
    "600276.SH",  # 恒瑞医药
    "300750.SZ",  # 宁德时代
    "002594.SZ",  # 比亚迪
    "600900.SH",  # 长江电力
]
```

## 📊 绩效指标

系统自动计算以下绩效指标：

- **总收益率** - 从开始到现在的总回报
- **最大回撤** - 历史最大回撤幅度
- **夏普比率** - 风险调整后的收益
- **胜率** - 盈利交易占总交易的比例
- **盈亏比** - 平均盈利与平均亏损的比值
- **交易次数** - 总交易笔数

## ⚙️ 配置说明

### 策略配置

```python
from adapters.quant.strategies.multi_factor_momentum import StrategyConfig

config = StrategyConfig(
    momentum_weight=0.5,       # 动量因子权重
    volatility_weight=0.2,     # 波动率因子权重
    volume_weight=0.15,        # 成交量因子权重
    rsi_weight=0.15,           # RSI因子权重
    min_composite_score=0.15,  # 买入最小综合得分
    max_composite_score=-0.15, # 卖出最大综合得分
    min_confidence=0.55,       # 最小置信度
    max_position_size=0.25,    # 最大仓位比例
    base_position_size=0.12,   # 基础仓位比例
    stop_loss_pct=0.08,        # 止损比例 8%
    take_profit_pct=0.20       # 止盈比例 20%
)
```

### 风险管理配置

```python
risk_manager = RiskManager(
    max_positions=5,            # 最大持仓数
    max_single_position=0.2,    # 单只股票最大仓位 20%
    max_daily_loss=0.02,        # 单日最大亏损 2%
    max_drawdown=0.10,          # 最大回撤 10%
    stop_loss_pct=0.08,         # 默认止损 8%
    take_profit_pct=0.20        # 默认止盈 20%
)
```

## 📱 Web界面

Web界面提供以下功能：

### 页面导航
- **📊 概览** - 系统概览和关键指标
- **📈 资金曲线** - 资金曲线可视化
- **💼 持仓分析** - 当前持仓详情
- **🔄 交易记录** - 历史交易明细
- **🎯 实时行情** - 实时股票行情

### 交互功能
- 实时数据刷新
- 股票代码查询
- 数据导出（CSV）
- 自定义过滤条件

## 🔧 高级用法

### 自定义策略

```python
from adapters.quant.strategies.multi_factor_momentum import MultiFactorMomentumStrategy

# 创建策略实例
strategy = MultiFactorMomentumStrategy(config=your_config)

# 生成信号
signal = strategy.generate_signal(market_data)

# 信号包含
# - action: "BUY" / "SELL" / "HOLD"
# - confidence: 置信度 (0-1)
# - factors: 各因子得分
# - target_price: 目标价
# - stop_loss: 止损价
```

### 直接使用模拟券商

```python
from adapters.quant.trading.simulated_broker import SimulatedBroker, OrderSide, OrderType

# 创建模拟券商
broker = SimulatedBroker(initial_capital=1000000)
broker.connect_data_source()

# 下单
order = broker.place_order(
    symbol="600519.SH",
    side=OrderSide.BUY,
    order_type=OrderType.MARKET,
    quantity=100
)

# 查询账户
account = broker.get_account_info()
positions = broker.get_positions()
trades = broker.get_trades()
```

## 📝 数据存储

交易数据保存在 `trading_data/` 目录：

```
trading_data/
├── snapshots/          # 每日快照
│   └── snapshots_2026-03.json
├── trades/             # 交易记录
│   └── trades_2026-03.json
└── reports/            # 绩效报告
    └── trade_report_20260309_123456.json
```

## ⚠️ 注意事项

1. **数据源** - 系统使用AKShare获取免费数据，有访问频率限制
2. **交易时间** - 系统会自动判断A股交易时间
3. **风险控制** - 建议在模拟环境充分测试后再考虑实盘
4. **数据备份** - 定期备份 `trading_data/` 目录
5. **性能监控** - 监控系统资源使用，特别是长时间运行

## 🐛 故障排除

### 问题：AKShare数据获取失败
```bash
# 重新安装AKShare
pip uninstall akshare
pip install akshare --upgrade
```

### 问题：模块导入错误
```bash
# 确保项目路径正确
cd d:\GM-SkillForge

# 检查Python路径
python -c "import sys; print(sys.path)"
```

### 问题：Web界面无法启动
```bash
# 检查streamlit版本
pip install --upgrade streamlit

# 清除缓存
streamlit cache clear
```

## 📚 参考资料

- [AKShare文档](https://akshare.akfamily.xyz/)
- [Pandas文档](https://pandas.pydata.org/docs/)
- [Streamlit文档](https://docs.streamlit.io/)

## 📄 许可证

本项目仅供学习和研究使用。

---

**祝您交易顺利！📈**
