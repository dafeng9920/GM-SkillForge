---
name: TREND_SNIFFER
description: "意图引擎与竞争对手探测协议。用于识别高价值的‘零搜索量’利基市场，并基于搜索结果质量决定是否触发自动化建站流程。"
---

# TREND_SNIFFER

本技能定义了从“公域流量抱怨”中挖掘“私域建站机会”的执行逻辑。它不仅关注关键词，更关注**搜索意图 (Intent)** 和**竞争格局 (Landscape)**。

## 1. 意图挖掘准则 (Mining Principles)

- **Zero-Volume First**: 优先寻找在传统 SEO 工具中搜索量为 0，但在社交平台（Reddit, Quora, GitHub Issues）中存在真实痛苦的需求。
- **Complaint-to-Tool**: 当检测到形如“当初要是有个工具能处理 X就好了”或“为什么没软件能做 Y”的抱怨超过 3 次，将其列为 **High Priority**。

## 2. 竞争对手探测仪式 (Competitor Detection Ritual)

在决定投入资源建站前，Agent **必须** 模拟浏览器执行以下预检：

### 预检 A: 深度扫描 SERP (Top 5)
1. [ ] **Forum Dominance**: 前 5 名是否全是 Reddit, 知乎, Quora 的回帖？如果是，**GO**。
2. [ ] **Legacy UI**: 前 5 名是否存在界面陈旧（2010年视觉风格）、非移动端友好的工具站？如果是，**GO**。
3. [ ] **Big Tech Guard**: 前 5 名是否存在 Adobe, Microsoft, Canva, Notion 等官方垂直页面？如果是，**ABORT**。
4. [ ] **Polished Free Mix**: 是否已经有极其精美且完全免费的开源竞品工具？如果是，**ABORT**。

## 3. 自动化工厂触发逻辑 (Trigger Logic)

当预检结果满足 `GO` 条件时，自动触发 **pSEO (Programmatic SEO)** 流水线：
- **Template Selection**: 根据关键词类型（转换类、查询类、库类）选择 1 套通用 UI 模板。
- **Matrix Expansion**: 利用 `1 -> N` 逻辑，从核心能力衍生出长尾工具矩阵（例如：从 PDF 转换核心衍生出 100 种格式转换页面）。

## 4. 最佳实践 (Best Practices)

- **ROI First**: 永远不要折腾那些大号已经占领的地盘。
- **Iterative Growth**: 先上线简单的单页工具，通过 Search Console 监控到真实流量后再进行二次功能迭代。

---
> "Detect their complaints, occupy their search results, and build the infrastructure they didn't know they needed."
