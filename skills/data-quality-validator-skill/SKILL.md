---
name: data-quality-validator-skill
description: 数据质量验证（完整性、准确性、一致性检查）
---

# data-quality-validator-skill

## 触发条件

- 数据摄入后验证
- 定期质量检查
- 异常数据检测

## 输入

```yaml
input:
  data_source: "market_data"
  table: "stock_prices"
  validation_rules:
    - check: "price_positive"
    - check: "volume_non_negative"
    - check: "timestamp_continuous"
    - check: "ohlc_consistency"
```

## 输出

```yaml
output:
  status: "PASSED"
  total_rows: 10000
  valid_rows: 9950
  invalid_rows: 50
  issues:
    - type: "ohlc_inconsistency"
      count: 25
      severity: "high"
    - type: "missing_values"
      count: 25
      severity: "medium"
```

## 核心功能

### 验证规则

| 规则 | 说明 |
|------|------|
| price_positive | 价格必须 > 0 |
| volume_non_negative | 成交量 >= 0 |
| ohlc_consistency | low <= close <= high |
| timestamp_continuous | 时间戳连续无跳跃 |
| no_duplicates | 无重复记录 |

### 质量指标

- 完整性: 缺失值比例
- 准确性: 异常值比例
- 一致性: 逻辑一致性
- 及时性: 数据延迟

## DoD

- [ ] 支持自定义验证规则
- [ ] 自动生成质量报告
- [ ] 异常数据隔离
- [ ] 质量趋势监控
