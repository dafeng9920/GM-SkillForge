---
name: memory-os-skill
description: OpenClaw 的“记忆系统”。将记忆视为一等公民和可调度的 OS 资源，实现长期记忆的持续增长与高效检索。
---

# memory-os-skill

## 触发条件

- 任务开始前：检索历史相关上下文。
- 任务执行中：动态调度不同维度的记忆（参数化、激活态、明文态）。
- 任务完成后：对当前 Session 知识进行提取、归约并存入长期库。

## 记忆类型 (Memory Types)

1. **Short-term (Working Memory)**: 当前会话的上下文窗口，动态紧缩。
2. **Long-term (Persistent Memory)**: 存放在 LanceDB Pro 中的向量+全文索引库。
3. **Procedural (Methodology Memory)**: 存储已验证的操作流程（Skills/Workflows）。

## 核心回路 (The MAG Loop)

1. **Context Analysis**: 识别当前查询中的实体和语义关键字。
2. **Hybrid Retrieval**: 调用 `memory-manager` (LanceDB Pro) 进行向量与 BM25 的混合检索。
3. **Reranking**: 根据相关性、重要度和时效性对调取的记忆进行重新排序。
4. **Injection**: 将最相关的记忆片段注入当前模型的 Prompt。

## DoD

- [ ] 记忆检索延迟低于 200ms
- [ ] 成功解决“关键词语义错配”或“短记忆淹没”问题
- [ ] 具备系统级的备份与自动恢复机制（System Resilience）
