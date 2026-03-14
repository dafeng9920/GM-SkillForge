---
name: sentiment-data-fetcher-skill
description: 获取市场情绪数据（新闻、社交媒体、分析师评级）
---

# sentiment-data-fetcher-skill

## 触发条件

- 情绪分析策略需要数据
- 市场热点追踪
- 风险事件监控

## 输入

```yaml
input:
  symbols: ["AAPL", "MSFT"]
  sources: ["news", "twitter", "analyst_ratings"]
  lookback_hours: 24
  min_sentiment_score: -1
  max_sentiment_score: 1
```

## 输出

```yaml
output:
  status: "SUCCESS"
  data:
    AAPL:
      overall_sentiment: 0.65
      news_count: 15
      social_mentions: 1234
      analyst_recommendations: {buy: 12, hold: 5, sell: 1}
      trending: true
```

## 核心功能

### 数据源

- **News API**: 财经新闻
- **Twitter/X API**: 社交媒体讨论
- **Seeking Alpha**: 分析师文章
- **Finviz**: 新闻聚合

### 情绪分析

- NLP 情绪评分 (-1 到 +1)
- 关键词提取
- 主题分类
- 趋势检测

## DoD

- [ ] 支持至少 2 个数据源
- [ ] 情绪评分准确性 > 70%
- [ ] 实时数据更新（< 5分钟延迟）
- [ ] 历史数据持久化
