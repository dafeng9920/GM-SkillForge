---
name: order-router-skill
description: 订单路由（智能拆单、交易通道选择、订单分发）
---

# order-router-skill

## 触发条件

- 收到交易订单
- 需要拆分大单
- 多通道执行

## 输入

```yaml
input:
  order:
    symbol: "AAPL"
    side: "BUY"
    quantity: 10000
    order_type: "MARKET"
    time_in_force: "DAY"
  routing_strategy: "smart"
  venues:
    - name: "NYSE"
      priority: 1
      fee_rate: 0.001
    - name: "NASDAQ"
      priority: 2
      fee_rate: 0.0012
  constraints:
    max_order_size: 1000
    min_order_size: 100
    venue_capacity: 0.3
```

## 输出

```yaml
output:
  status: "SUCCESS"
  routed_orders:
    - venue: "NYSE"
      symbol: "AAPL"
      side: "BUY"
      quantity: 3000
      order_type: "LIMIT"
      price: 150.25
    - venue: "NASDAQ"
      symbol: "AAPL"
      side: "BUY"
      quantity: 3000
      order_type: "LIMIT"
      price: 150.26
    - venue: "ARCA"
      symbol: "AAPL"
      side: "BUY"
      quantity: 4000
      order_type: "LIMIT"
      price: 150.24
  routing_summary:
    total_quantity: 10000
    venues_used: 3
    avg_price: 150.25
    estimated_slippage: 0.02
```

## 核心功能

### 路由策略

| 策略 | 说明 |
|------|------|
| smart | 智能路由（综合考虑价格、流动性、成本） |
| vwap | VWAP 拆单 |
| twap | TWAP 拆单 |
| iceberg | 冰山订单（隐藏大单） |
| best_price | 最优价格路由 |

### 拆单算法

- 按时间拆分（TWAP）
- 按成交量拆分（VWAP）
- 按比例拆分
- 随机拆分

### 通道选择

- 最优价格
- 最低成本
- 最快速度
- 负载均衡

## DoD

- [ ] 支持多种路由策略
- [ ] 智能拆单算法
- [ ] 多通道分发
- [ ] 实时监控执行
- [ ] 异常处理
