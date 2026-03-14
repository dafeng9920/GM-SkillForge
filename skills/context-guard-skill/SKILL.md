# ContextGuardSkill: Self-Healing Memory Manager (Draft V1)
# --------------------------------------------------------
# 🎯 目标：当检测到上下文溢出时，自动压缩历史并保持对话连贯。
# --------------------------------------------------------

## 核心机制 (Reconstruct & Clear)

### 1. 拦截逻辑 (The Interceptor)
当检测到溢出错误时，用户可以手动发送指令，或者由系统捕获后执行：

```bash
# 💡 这是一个内置指令，如果 Skill 加载成功，它可以直接清理当前会话：
!system session-clear-history
```

### 2. 手动清理技能 (Internal Skill)
```python
def on_error(error):
    if "context_window_exceeded" in str(error):
        # 释放紧急信号
        return "⚠️ 记忆溢出！请发送 `!system session-clear-history` 来重启本轮对话。"

def handle_command(cmd):
    if cmd == "clear-session-memory":
        # 调用内核清理
        openclaw.clear_history()
        return "🧹 记忆已清空，我们可以重新开始这段对话了。"
```

## 配置加固 (Strategy)

在 `openclaw.json` 中配置“预防性医疗”方案：

```json
"agents": {
  "defaults": {
    "compaction": {
      "mode": "summary",     // 启用摘要压缩模式
      "window": 20,          // 到达 20 条消息时强制触发一次清理
      "buffer": 0.1          // 预留 10% 的 Token 安全带
    }
  }
}
```

## 使用说明
1. **自动触发**：无需手动干预，Skill 会在报错瞬间拦截。
2. **状态提示**：自愈完成后，机器人会发送一条“整理笔记”的提示。
