---
name: world-vision-skill
description: OpenClaw “环球全景天眼”系统。基于 Tavily-style 的 AI 优化搜索逻辑，为智能体提供过滤杂讯后的全对称世界观测。
---

# world-vision-skill

## 触发条件

- 每日/每小时的例行情报同步请求
- 处理复杂决策（如量化裁决、重大改码决策）前
- 系统检测到宏观风险窗口期（如大盘异动、全球技术宕机）

## 核心视角 (World View Dimensions)

1. **Quant (金融视角)**: A股/全球市场实时脉动、多维情绪指标。
2. **Tech (前沿视角)**: GitHub 趋势、AI 论文/工具发布、安全预警 (CVE)。
3. **Governance (规制视角)**: 行业合规动态、监管禁令、最佳实践变迁。

## 执行回路 (Execution Loop)

1. **Deep Search**: 调用 `search_web` (Tavily 增强模式) 获取多源情报。
2. **Intent Filter**: 丢弃 PR 稿和广告，仅抓取“干货决策因子”。
3. **Context Sync**: 自动生成并同步 `global_view.json` 到云端工作区。

## 输出 (Output)

- `global_view.json`: 供云端 Master Brain 调用。
- `intelligence_briefing.md`: 供 Commander 审阅的战略简报。

## DoD

- [ ] 全球主要宏观因子（USDX, S&P, Gold）已配对
- [ ] 定时同步脚本 `sync_world_vision.ps1` 已运行
- [ ] 裁决逻辑中已关联 `global_view` 变量
