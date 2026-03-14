---
name: ai-search-scanner-skill
description: AI 搜索可见性扫描器。模拟 AI 搜索引擎查询，检测特定域名是否出现在回答及其引文中。
---

# ai-search-scanner-skill

## 触发条件

- 需要评估网站在 AI 搜索引擎（ChatGPT Search, Perplexity, Google AI Overviews）的可见度
- 需要检测域名是否被 AI 搜索引用
- 需要 AIO (AI Overview) 可见性报告

## 输入

```yaml
input:
  domain: "example.com"
  keywords:
    - "SEO tool"
    - "AI optimization"
  search_engines:
    - "perplexity"
    - "chatgpt"
    - "google_ai_overview"
  capture_evidence: true
```

## 输出

```yaml
output:
  visibility_score: 85  # 0-100
  perplexity_cited: true
  chatgpt_mentioned: true
  ai_overview_rank: 3
  evidence_screenshots:
    - "perplexity_result.png"
    - "chatgpt_result.png"
  lead_capture: "domain.com|user@email.com"
  recommendation: "HIGH_PRIORITY|MEDIUM|LOW"
```

## 执行流程

1. **Intent Check**: 识别域名和核心业务关键词
2. **Perplexity Scan**:
   - 调用 `web_fetch` 访问 Perplexity 搜索
   - 解析 "Sources" 部分，搜索域名是否在引用列表
3. **ChatGPT Scan**:
   - 调用 `browser` 模拟访问 ChatGPT Search
   - 检测返回文本或链接中是否包含域名
4. **Evidence Capture**:
   - 截图捕获原始回答页面
   - 作为审计真实性存证
5. **Scoring Logic**:
   - Perplexity 被引用: +40 分
   - ChatGPT 被提及: +60 分

## 线索捕获格式

```
<lead>domain.com|user@email.com</lead>
```

## DoD

- [ ] 完成 Perplexity 扫描
- [ ] 完成 ChatGPT 扫描
- [ ] 截图证据已保存
- [ ] 可见性评分已计算
- [ ] Lead 格式已输出
- [ ] 报告已生成

---

> "Data-driven SEO for the LLM Era."
