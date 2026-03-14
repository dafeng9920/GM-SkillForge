---
name: failure-explainer-skill
description: 当 OpenClaw 执行失败时，自动生成可读性故障报告（原因、影响、建议修复步骤）。
---

# failure-explainer-skill

## 触发条件

- 容器退出码非 0
- Gateway 无法启动
- Agent 连接失败
- 任何需要故障诊断的场景

## 输入

```yaml
input:
  docker_logs: "docker compose logs openclaw-agent --tail 100"
  container_exit_code: 1
  error_timestamp: "2026-02-28T23:15:00Z"
  context: "startup|runtime|shutdown"
```

## 输出

```yaml
output:
  failure_type: "MISSING_ENV|NETWORK_ERROR|PERMISSION_DENIED|UNKNOWN"
  root_cause: "OPENAI_API_KEY not set in .env"
  impact: "Container cannot authenticate with upstream API"
  suggested_fix:
    - step: 1
      action: "Edit openclaw-box/.env"
      command: "Set GLM_API_KEY=sk-..."
    - step: 2
      action: "Restart container"
      command: "docker compose restart"
  escalation_needed: false
```

## 报告位置

- `data/logs/failure_explanation_{timestamp}.json`
- 同时输出 Markdown 格式便于阅读

## DoD

- [ ] 解析容器日志
- [ ] 识别错误模式
- [ ] 生成可执行修复建议
- [ ] 写入报告文件
