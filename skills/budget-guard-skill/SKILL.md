---
name: budget-guard-skill
description: 检测 OpenClaw 的 API token 消耗异常、执行超预算风险，并在接近阈值时熔断。
---

# budget-guard-skill

## 触发条件

- OpenClaw 执行耗时超过 30 分钟
- 单次对话 token 消耗超过 200K
- 需要做成本控制与熔断保护

## 输入

```yaml
input:
  max_duration_minutes: 30
  max_tokens_per_session: 200000
  warning_threshold_pct: 80
  api_base: "https://open.bigmodel.cn/api/paas/v4/"
```

## 输出

```yaml
output:
  budget_status: "OK|WARNING|EXCEEDED"
  current_tokens: 14575
  current_duration_minutes: 2.3
  recommendation: "CONTINUE|PAUSE|ABORT"
  alert_message: "Token usage at 85% of session limit"
```

## 熔断动作

- 超阈值时自动 `openclaw gateway stop`
- 发送 Discord 警报到指定频道
- 记录 `budget_violation.json` 到 `data/logs/`

## DoD

- [ ] 读取当前 session 的 token 统计
- [ ] 计算 `% usage` vs 上限
- [ ] 超限时触发熔断
- [ ] 警报消息已发送
