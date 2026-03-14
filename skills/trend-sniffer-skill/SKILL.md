---
name: trend-sniffer-skill
description: 意图引擎与竞争对手探测协议。用于识别高价值的'零搜索量'利基市场，并基于搜索结果质量决定是否触发自动化建站流程。
---

# trend-sniffer-skill

## 触发条件

- 需要从公域流量抱怨中挖掘私域建站机会
- 需要识别零搜索量但高需求的关键词
- 需要评估竞争格局决定是否建站

## 输入

```yaml
input:
  target_industry: "SaaS|Marketing|SEO"
  monitoring_sources:
    - "reddit"
    - "quora"
    - "github_issues"
  complaint_threshold: 3
  serp_check_depth: 5
```

## 输出

```yaml
output:
  high_priority_keywords:
    - keyword: "AI SEO tool for small business"
      complaint_count: 7
      zero_volume: true
      serp_analysis: "FORUM_DOMINANCE"
      recommendation: "GO"
  competitors_analysis:
    forum_dominance: true
    legacy_ui: true
    big_tech_guard: false
    polished_free_competition: false
  trigger_decision: "GO|ABORT"
  next_action: "TRIGGER_PSEO_PIPELINE|MONITOR_ONLY"
```

## 意图挖掘准则

- **Zero-Volume First**: 优先寻找在传统 SEO 工具中搜索量为 0，但在社交平台中存在真实痛苦的需求
- **Complaint-to-Tool**: 当检测到形如"当初要是有个工具能处理 X就好了"的抱怨超过 3 次，列为 **High Priority**

## 竞争对手探测仪式

### 预检 A: 深度扫描 SERP (Top 5)
1. [ ] **Forum Dominance**: 前 5 名是否全是 Reddit, 知乎, Quora 的回帖？如果是，**GO**
2. [ ] **Legacy UI**: 前 5 名是否存在界面陈旧、非移动端友好的工具站？如果是，**GO**
3. [ ] **Big Tech Guard**: 前 5 名是否存在 Adobe, Microsoft, Canva, Notion 等官方垂直页面？如果是，**ABORT**
4. [ ] **Polished Free Mix**: 是否已经有极其精美且完全免费的开源竞品工具？如果是，**ABORT**

## 自动化工厂触发逻辑

当预检结果满足 `GO` 条件时，自动触发 **pSEO (Programmatic SEO)** 流水线：
- **Template Selection**: 根据关键词类型选择通用 UI 模板
- **Matrix Expansion**: 利用 `1 -> N` 逻辑，从核心能力衍生出长尾工具矩阵

## 最佳实践

- **ROI First**: 永远不要折腾那些大号已经占领的地盘
- **Iterative Growth**: 先上线简单的单页工具，通过 Search Console 监控到真实流量后再进行二次功能迭代

## DoD

- [ ] 零搜索量关键词已识别
- [ ] 抱怨计数已验证
- [ ] SERP Top 5 预检已完成
- [ ] 竞争对手分析已完成
- [ ] 触发决策已输出
- [ ] 下一行动已明确

---

> "Detect their complaints, occupy their search results, and build the infrastructure they didn't know they needed."
