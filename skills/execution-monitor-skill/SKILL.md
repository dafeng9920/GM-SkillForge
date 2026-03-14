---
name: execution-monitor-skill
description: 执行监控（订单状态跟踪、成交确认、异常检测）
---

# execution-monitor-skill

## 触发条件

- 订单提交后
- 定时检查订单状态
- 检测执行异常

## 输入

```yaml
input:
  order_id: "ORD_20240309_001"
  venue: "NYSE"
  symbol: "AAPL"
  side: "BUY"
  quantity: 1000
  expected_price: 150.25
  monitoring_rules:
    - type: "fill_timeout"
      threshold_seconds: 300
    - type: "price_deviation"
      threshold_pct: 0.5
    - type: "partial_fill"
      min_fill_pct: 0.1
```

## 输出

```yaml
output:
  status: "MONITORING"
  order_id: "ORD_20240309_001"
  current_state:
    status: "PARTIALLY_FILLED"
    filled_quantity: 300
    remaining_quantity: 700
    avg_fill_price: 150.26
    fill_time: "2024-03-09T10:35:00Z"
  alerts:
    - type: "slow_fill"
      message: "成交速度较慢"
      severity: "warning"
  metrics:
    fill_rate: 0.3
    price_deviation: 0.001
    time_elapsed: 180
```

## 核心功能

### 监控规则

| 规则 | 说明 | 阈值 |
|------|------|------|
| fill_timeout | 成交超时 | 默认5分钟 |
| price_deviation | 价格偏离 | 默认0.5% |
| partial_fill | 部分成交 | 最小10% |
| rejection | 订单拒绝 | - |
| cancellation | 订单取消 | - |

### 状态跟踪

- PENDING - 待成交
- ACKNOWLEDGED - 已确认
- PARTIALLY_FILLED - 部分成交
- FILLED - 完全成交
- CANCELLED - 已取消
- REJECTED - 已拒绝
- EXPIRED - 已过期

### 异常检测

- 成交延迟
- 价格异常
- 部分成交异常
- 订单拒绝
- 系统故障

## DoD

- [ ] 实时订单状态跟踪
- [ ] 多种监控规则
- [ ] 异常自动检测
- [ ] 警报通知机制
- [ ] 执行质量分析
