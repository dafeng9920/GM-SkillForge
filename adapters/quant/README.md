# Quant Adapter Layer

## 定位

**只做翻译，不执行**

```
策略代码 → Adapter → Core Skills → 执行
         (翻译)     (风控+执行)
```

## 目录结构

```
adapters/quant/
├── data/                    # 数据源适配器
│   └── openbb_fetch.py      # OpenBB 数据获取
├── strategies/              # 策略适配器
│   ├── stock_selector.py    # 股票选股
│   └── signal_generator.py  # 信号生成
└── README.md
```

## 职责边界

| Adapter 做 | Core 做 |
|------------|---------|
| 数据获取 | 风控检查 |
| 策略计算 | 回撤控制 |
| 信号格式化 | 订单路由 |
| 输出标准格式 | 交易执行 |

## 使用示例

```python
# Adapter: 获取数据 + 生成信号
from adapters.quant import OpenBBAdapter, SignalAdapter

data = OpenBBAdapter().fetch("AAPL")
signal = SignalAdapter().generate(data)

# Core: 风控 + 执行
from skillforge.src.skills.quant import execute

result = execute(
    action=signal["action"],
    symbol=signal["symbol"],
    quantity=signal["quantity"],
    context={"total_capital": 1000000}
)
```
