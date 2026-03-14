---
name: lobster-intelligence-harvester-skill
description: SEO Matrix 专用情报收割协议。用于大规模探测 AI 搜索引用动态、挖掘高意图 Leads 并填充 pSEO 行业数据库
---

# lobster-intelligence-harvester-skill

## 触发条件

- 需要为 pSEO 引擎提供行业数据
- 需要挖掘高意图 SEO Leads
- 需要监控竞品 AI 搜索引用动态

## 输入

```yaml
input:
  task_type: "PSEO_HARVESTER|SOCIAL_LEAD_SCRAPER|CITATION_MONITOR"
  target_industry: "Cybersecurity|EdTech|ManagedServices"
  monitoring_keywords:
    - "Perplexity citations"
    - "AIO traffic drop"
    - "ChatGPT Search visibility"
  competitor_domains: ["competitor1.com", "competitor2.com"]
  output_formats: ["JSON", "Markdown"]
```

## 输出

```yaml
output:
  task_type: "PSEO_HARVESTER"
  industry_data:
    industry: "Cybersecurity"
    top_brands: 50
    estimated_aev: 125000  # Annual Hidden Value
  leads_captured: 15
  citation_changes:
    domain: "competitor1.com"
    perplexity_position: 3
    chatgpt_mentioned: true
  report_paths:
    json: "data/pSEO_Industries.json"
    leads: "skillforge/captured_leads.json"
    intel: "docs/Pathogen_Intel.md"
```

## 核心目标

1. **大规模工业侦察**: 为 pSEO 引擎提供行业数据
2. **高意图 Leads 挖掘**: 通过社交媒体抓取迫切需要 AIO 优化的潜在客户
3. **竞品引用扫描**: 监控 Perplexity 和 Google AIO 的信源变动

## 任务指令

### 任务 A: 行业数据自动化填充
1. 研究指定的垂直行业
2. 识别该行业的前 50 个核心品牌及主要业务关键词
3. 估算 AEV = `月均搜索量 * 0.8 * $4 * 12`
4. 将结果追加到 `data/pSEO_Industries.json`

### 任务 B: 社交媒体"病理"钓鱼
1. 监控 Reddit (`r/SEO`, `r/SaaS`, `r/Marketing`) 和 X (Twitter)
2. 搜寻关键词并识别抱怨流量下滑的用户
3. 将发现的域名和联系方式追加到 `skillforge/captured_leads.json`

### 任务 C: 实时引用监控
1. 使用 `ai-search-scanner-skill` 扫描指定竞品域名
2. 对比其在 Perplexity 和 ChatGPT 结果中的排位
3. 在 `docs/Pathogen_Intel.md` 中生成对比报告

## 治理约束

- **代码只读原则**: 严禁修改任何 `.py` 或 `.html` 文件
- **合法写入区域**: 仅限于 `data/` 内容追加、`pseo/` 页面生成、`docs/` 情报报告
- **违规处置**: 任何越权修改核心代码的行为将触发即时会话止损

## DoD

- [ ] 行业数据已识别
- [ ] AEV 已计算
- [ ] Leads 已捕获并保存
- [ ] 竞品引用已扫描
- [ ] 报告已生成
- [ ] 治理约束已遵守

---

*Created by Antigravity for Commander.* 🛰️🔥🦞
