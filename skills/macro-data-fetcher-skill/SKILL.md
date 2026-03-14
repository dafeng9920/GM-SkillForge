---
name: macro-data-fetcher-skill
description: 获取宏观经济数据（GDP、CPI、利率、就业数据等）
---

# macro-data-fetcher-skill

## 触发条件

- 宏观策略分析
- 风险平价配置
- 经济周期判断

## 输入

```yaml
input:
  indicators: ["GDP", "CPI", "UNRATE", "FEDFUNDS"]
  countries: ["US", "CN", "EU"]
  start_date: "2020-01-01"
  end_date: "2024-03-09"
```

## 输出

```yaml
output:
  status: "SUCCESS"
  data:
    US_GDP:
      latest: 27.94  # 万亿
      growth_rate: 2.5
      next_release: "2024-04-01"
```

## 核心功能

### 数据源

- **FRED (Federal Reserve)**: 美国经济数据
- **Bloomberg API**: 全球宏观数据
- **OECD**: 国际经济数据
- **Trading Economics**: 新兴市场数据

### 指标类型

| 类别 | 指标 |
|------|------|
| 增长 | GDP, GDI, 工业产值 |
| 通胀 | CPI, PCE, PPI |
| 就业 | 失业率, 非农就业 |
| 利率 | 联邦基金利率, 国债收益率 |
| 景气 | PMI, 消费者信心 |

## DoD

- [ ] 支持 FRED 数据源
- [ ] 覆盖主要宏观指标
- [ ] 数据自动更新
- [ ] 历史数据归档
