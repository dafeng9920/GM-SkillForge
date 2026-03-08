---
name: AI_SEARCH_SCANNER
description: "AI 搜索可见性扫描器。模拟 AI 搜索引擎查询，检测特定域名是否出现在回答及其引文中。"
---

# AI_SEARCH_SCANNER

本技能用于评估网站在 AI 搜索时代（ChatGPT Search, Perplexity, Google AI Overviews）的可见度指数。

## 1. 扫描准则 (Scanning Ritual)

1. [ ] **Intent Check**: 识别域名 (`domain`) 和核心业务关键词。
2. [ ] **Perplexity Scan (High Priority)**:
   - 调用 `web_fetch` 访问 `https://www.perplexity.ai/search?q=[关键词]`。
   - 解析页面中的 "Sources" 部分，搜索 `domain` 是否在引用列表中。
3. [ ] **ChatGPT Scan**:
   - 调用 `browser` 模拟访问 `https://chatgpt.com/?q=[关键词]`。
   - 检测返回文本或生成的链接中是否包含 `domain`。
4. [ ] **Evidence Capture (Critical)**:
   - **Screenshot**: 调用 `browser.screenshot` 捕获 Perplexity/ChatGPT 的原始回答页面。
   - **Transparency**: 将截图上传至频道，作为审计结果的“真实性存证”。
5. [ ] **Scoring Logic**:
   - 如果在 Perplexity 被引用: +40 分。
   - 如果在 ChatGPT 被提及: +60 分。

## 2. 线索捕获 (Lead Acquisition)

在完成扫描后，必须输出以下格式以便后端自动记录：
`<lead>domain.com|user@email.com</lead>`

## 3. 下一步行动 (Next Step)

生成报告并使用 `Report_Generator.py` 逻辑将摘要回复给用户。

---
> "Data-driven SEO for the LLM Era."
