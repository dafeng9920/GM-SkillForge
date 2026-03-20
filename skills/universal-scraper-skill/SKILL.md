---
name: universal-scraper-skill
description: OpenClaw 全网观测“透视镜”。突破 API 限制，多平台（X, Reddit, GitHub, Bilibili）实时情报获取能力。
---

# universal-scraper-skill

## 触发条件

- `World Vision` 需要特定社交平台的情绪数据时。
- 需要跟踪特定 GitHub 仓库或开发者的动态时。
- 针对前沿 AI 应用进行跨平台“趋势嗅探”时。

## 平台覆盖 (Platform Reach)

- **Social**: X (Twitter), Reddit, Bilibili, XiaoHongShu.
- **Dev**: GitHub, Stack Overflow.
- **Video**: YouTube, YouTube Transcripts.

## 抓取逻辑 (Agent-Reach Logic)

- **Bypass Mode**: 自动模拟浏览器行为或使用公共代理，绕过登录墙和频率限制。
- **Structuring**: 将非结构化的网页/推文转换为结构化的 JSON 情报。
- **Privacy First**: 抓取过程中自动过滤个人敏感信息，仅保留公共舆论因子。

## DoD

- [ ] 与 `agent-browser-skill` 深度配对
- [ ] 抓取结果自动同步至 `World Vision` 存储库
- [ ] 具备自动重试与反探测（Anti-fingerprinting）能力
