---
name: audit-logger-skill
description: 日志审计（完整交易日志、操作记录、合规审计）
---

# audit-logger-skill

## 触发条件

- 任何交易操作
- 系统配置变更
- 用户登录/登出
- 异常事件

## 输入

```yaml
input:
  event_type: "ORDER_SUBMIT"
  data:
    order_id: "ORD_20240309_001"
    symbol: "AAPL"
    side: "BUY"
    quantity: 1000
    price: 150.25
    user_id: "user_123"
    strategy_id: "STRAT_001"
  metadata:
    ip_address: "192.168.1.100"
    user_agent: "QuantSystem/1.0"
    timestamp: "2024-03-09T10:30:00Z"
```

## 输出

```yaml
output:
  status: "LOGGED"
  audit_id: "AUDIT_20240309_103000_001"
  log_entry:
    id: "AUDIT_20240309_103000_001"
    event_type: "ORDER_SUBMIT"
    timestamp: "2024-03-09T10:30:00Z"
    data: {...}
    metadata: {...}
    signature: "a1b2c3d4..."
    checksum: "e5f6g7h8..."
```

## 核心功能

### 日志类型

| 类型 | 说明 |
|------|------|
| ORDER_SUBMIT | 订单提交 |
| ORDER_FILL | 订单成交 |
| ORDER_CANCEL | 订单取消 |
| ORDER_REJECT | 订单拒绝 |
| POSITION_CHANGE | 持仓变更 |
| RISK_LIMIT_HIT | 风险限额触发 |
| COMPLIANCE_ALERT | 合规警报 |
| SYSTEM_CONFIG | 系统配置变更 |
| USER_ACTION | 用户操作 |

### 审计功能

- 完整操作记录
- 数据完整性校验
- 数字签名
- 不可篡改存储
- 审计追溯

### 合规要求

- 日志保留期（至少7年）
- 数据不可修改
- 完整性证明
- 监管报告

## DoD

- [ ] 记录所有交易操作
- [ ] 数据完整性校验
- [ ] 数字签名验证
- [ ] 不可篡改存储
- [ ] 审计报告生成
