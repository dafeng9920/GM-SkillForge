---
name: compliance-check-skill
description: 合规检查（监管规则、风险限额、黑名单过滤）
---

# compliance-check-skill

## 触发条件

- 订单提交前
- 持仓检查
- 风险限额监控

## 输入

```yaml
input:
  order:
    symbol: "AAPL"
    side: "BUY"
    quantity: 1000
    price: 150.25
  portfolio:
    cash: 100000
    positions:
      AAPL: 5000
      MSFT: 2000
  rules:
    - type: "position_limit"
      max_per_symbol: 10000
    - type: "concentration_limit"
      max_concentration: 0.3
    - type: "blacklist"
      symbols: ["XYZ", "ABC"]
    - type: "short_restriction"
      check_hard_to_borrow: true
```

## 输出

```yaml
output:
  status: "APPROVED"
  decision: "PASS"
  checks:
    - name: "position_limit"
      status: "PASS"
      details: "当前持仓5000，新增1000，总计6000 < 10000"
    - name: "concentration_limit"
      status: "PASS"
      details: "AAPL占比18% < 30%"
    - name: "blacklist"
      status: "PASS"
      details: "AAPL不在黑名单"
  warnings: []
```

## 核心功能

### 合规规则

| 规则 | 说明 |
|------|------|
| position_limit | 单一标的持仓限额 |
| concentration_limit | 集中度限制 |
| blacklist | 黑名单过滤 |
| short_restriction | 融券限制 |
| leverage_limit | 杠杆限制 |
| wash_sale | 洗售规则 |
| insider_trading | 内幕交易检测 |
| best_execution | 最佳执行义务 |

### 检查类型

- 预检查（订单提交前）
- 实时检查（执行中）
- 后检查（成交后）

### 风险限额

- 单笔订单限额
- 日交易限额
- 持仓限额
- 损失限额

## DoD

- [ ] 支持多种合规规则
- [ ] 实时合规检查
- [ ] 黑名单管理
- [ ] 风险限额监控
- [ ] 合规报告生成
