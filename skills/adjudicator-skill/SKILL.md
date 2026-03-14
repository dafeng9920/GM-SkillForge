# Adjudicator Skill: 市场行情感知与决断器
# --------------------------------------------------------
# 🎯 目标：基于本地同步的 snapshot.json，为云端操作提供大环境感知。
# --------------------------------------------------------

## 核心功能 (Market Awareness)

本 Skill 负责监控 `trading_data/snapshot.json` 目录，并根据最新行情调整 Agent 的决策倾向。

### 1. 指标解读逻辑
当读取到行情数据时，自动执行以下分类：

- **行情概览**：读取上证指数、深证成指的涨跌幅。
- **板块热度**：分析 `top_gainers` 列表，识别当前市场的核心主线。
- **意图评分 (Intent Scoring)**：
  - 如果大盘上涨且主线清晰 -> 允许进行更积极的风险操作。
  - 如果大盘暴跌 -> 自动切换到“防御模式”，限制高风险 API 调用。

### 2. 指令示例
- `!market status`: 报告当前云端已知的最新行情快照。
- `!market adjudicate`: 根据当前行情对某个待执行任务进行风险评分。

## 数据来源 (Data Feed)
本 Skill 本身不具备联网能力，完全依赖 **Architecture A (Local Sourcing)**：本地运行 `fetch_ashare_data.py` 后经由 `cloud_bridge_sync.ps1` 将数据推送到本容器的 `workspace/trading_data/` 目录。

## 历史兼容
本 Skill 已适配 OpenClaw v2026.3.8，并在 Docker 容器环境下运行。
