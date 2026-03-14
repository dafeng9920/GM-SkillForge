---
name: INTELLIGENCE_FACTORY
description: "自动化情报工厂。按照 monitor_config.json 的配置，定时执行全网增量抓取、意图识别与对手探测逻辑。"
---

# INTELLIGENCE_FACTORY

本技能是 OpenClaw 智能体执行“固定复用模式”的情报采集核心。它通过整合 `monitor_config.json` 和 `TREND_SNIFFER` 协议，实现从“全网监控”到“利基报告”的自动化生产闭环。

## 1. 执行流程 (Execution Flow)

1. [ ] **Load Config**: 读取 `/root/.openclaw/monitor_config.json`，识别当前的 Tier 1-5 监控目标。
2. [ ] **Incremental Scrape**: 
   - 调用浏览器工具，对 X 赛道、Reddit 赛道及行业社区进行**增量抓取**。
   - 过滤掉已抓取的旧语料。
3. [ ] **Applying TREND_SNIFFER**:
   - 对抓取到的“抱怨”和“需求”进行意图识别。
   - 筛选出“Zero Volume”高潜力词。
4. [ ] **Competitor Detection**:
   - 自动执行 SERP Top 5 预检（论坛占领/老旧站识别）。
5. [ ] **Reporting**:
   - 生成 `latest_briefing.json`。
   - 在 Discord/WebChat 中输出精炼的“利基词获利建议”。

## 2. 调度逻辑 (Scheduling Strategy)

- **Cron**: 每日上午 9:00 (UTC+8) 触发一次全量嗅探。
- **Real-time Trigger**: 当 Tier 1 目标（如 Karpathy）发布动态时，由 Discord 插件配合触发瞬时解析。

## 3. 结果存储 (Persistence)

- 所有发现将持久化存储在 D:\GM-SkillForge\docs\ 下的日期目录中，确保数据不丢失。

---
> "From Noise to Signal. From Intelligence to Revenue."
