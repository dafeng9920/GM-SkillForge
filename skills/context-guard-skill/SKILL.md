# ContextGuardSkill: Self-Healing Memory Manager (Draft V1)
# --------------------------------------------------------
# 🎯 目标：当检测到上下文溢出时，自动压缩历史并保持对话连贯。
# --------------------------------------------------------

## 核心机制 (Intercept & Reconstruct)

当系统捕获到 `model_context_window_exceeded` 异常时，触发此 Skill：

### 1. 拦截逻辑 (The Interceptor)
```python
def handle_overflow(session_id, error):
    # 🚨 检查是否为上下文溢出错误
    if "context_window_exceeded" not in str(error):
        return None # 不干预其他错误

    print(f"检测到会话 {session_id} 记忆过载，启动自愈程序...")
    
    # 📋 获取当前会话的完整历史
    full_history = openclaw.get_history(session_id)
    
    # 🔪 切割策略 (Surgical Pruning)
    # 保留最后 3-5 条关键对话作为“短期记忆” (Critical Context)
    critical_context = full_history[-5:]
    
    # 将前面的历史标记为“长期记忆”并进行摘要压缩
    earlier_history = full_history[:-5]
    memory_summary = openclaw.summarize(earlier_history) 
    
    # 💉 重新注入 (Context Injection)
    # 将摘要作为 System Prompt 的一部分或特殊的 Context Message 注入
    new_context = [
        {"role": "system", "content": f"【历史记忆综述】：{memory_summary}"},
        *critical_context
    ]
    
    openclaw.update_session_context(session_id, new_context)
    return "✅ 记忆过载已缓解，已自动整理历史要点。请继续！"
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
