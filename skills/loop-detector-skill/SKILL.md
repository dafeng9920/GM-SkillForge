---
name: loop-detector-skill
description: 检测 OpenClaw Agent 陷入重复执行模式（相同工具调用 3+ 次），自动中断并建议人工介入。
---

# loop-detector-skill

## 触发条件

- Agent 连续 3 次调用相同工具参数
- 执行结果无进展（相同错误重试）
- session 出现"无限重试"特征

## 输入

```yaml
input:
  session_file: "data/agents/main/sessions/{sessionId}.jsonl"
  max_retries: 3
  detection_window_minutes: 10
```

## 输出

```yaml
output:
  loop_detected: true
  loop_type: "RETRY_STUCK|TOOL_LOOP|NO_PROGRESS"
  offending_tool: "exec"
  occurrence_count: 5
  recommendation: "HALT_AND_ESCALATE"
  pattern_summary: "exec('apt-get update') failed 5 times with same error"
```

## 中断动作

- 写入 `loop_detected.json` 标记
- 停止当前 session 执行
- 发送 Discord 介入请求

## DoD

- [ ] 分析 session 历史 10 分钟窗口
- [ ] 识别重复工具调用模式
- [ ] 确认无进展状态
- [ ] 触发中断并记录
