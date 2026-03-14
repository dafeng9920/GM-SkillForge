---
name: circuit-breaker-skill
description: 熔断器（市场异常、系统过载、紧急暂停）
---

# circuit-breaker-skill

## 触发条件

- 市场剧烈波动
- 系统异常
- 风险限额触发
- 手动触发

## 输入

```yaml
input:
  trigger_type: "auto"  # auto, manual
  trigger_condition:
    type: "portfolio_loss"
    threshold: 0.1  # 10%
    time_window: 3600  # 1小时
  current_state:
    portfolio_value: 1000000
    daily_pnl: -150000
    market_status: "volatile"
```

## 输出

```yaml
output:
  status: "TRIPPED"
  action: "SUSPEND_ALL_TRADING"
  reason: "组合损失超过阈值: -15% < -10%"
  triggered_at: "2024-03-09T14:30:00Z"
  cooldown_period: 3600  # 秒
  auto_recovery: false
  notifications_sent:
    - type: "email"
      recipients: ["risk@quant.local"]
    - type: "slack"
      channel: "#risk-alerts"
```

## 核心功能

### 熔断类型

| 类型 | 触发条件 | 恢复条件 |
|------|----------|----------|
| portfolio_loss | 组合损失超过阈值 | 人工审核 |
| market_volatility | 市场波动率异常 | 市场平稳 |
| system_overload | 系统负载过高 | 负载正常 |
| data_anomaly | 数据异常 | 数据恢复 |
| manual | 手动触发 | 人工恢复 |

### 熔断级别

- Level 1: 警告（允许交易，限制仓位）
- Level 2: 暂停新开仓（允许平仓）
- Level 3: 完全停止交易
- Level 4: 紧急清算

### 恢复机制

- 自动恢复（定时检查）
- 人工审核恢复
- 条件触发恢复

## DoD

- [ ] 多级熔断机制
- [ ] 自动触发和手动触发
- [ ] 可配置恢复条件
- [ ] 多渠道通知
- [ ] 完整事件记录
