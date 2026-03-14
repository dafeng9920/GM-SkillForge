---
name: financial-data-fetcher-skill
description: 获取公司财务数据（财报、财务指标、估值数据）
---

# financial-data-fetcher-skill

## 触发条件

- 策略需要财务数据进行分析
- 季度财报更新时
- 估值模型计算需要

## 输入

```yaml
input:
  symbols: ["AAPL", "MSFT"]
  data_types: ["income_statement", "balance_sheet", "cash_flow", "ratios", "metrics"]
  period: "quarterly"  # quarterly, annual
  fiscal_year: 2024
  include_estimates: true
```

## 输出

```yaml
output:
  status: "SUCCESS"
  data:
    AAPL:
      income_statement:
        period: "Q4 2023"
        revenue: 119575000000
        net_income: 33916000000
        eps: 2.18
      ratios:
        pe_ratio: 28.5
        pb_ratio: 45.2
        roe: 0.156
        debt_to_equity: 1.87
  metadata:
    fetch_time: "2024-03-09T10:30:00Z"
    source: "yfinance"
    currency: "USD"
```

## 核心功能

### 数据类型

| 类型 | 说明 | 频率 |
|------|------|------|
| income_statement | 利润表 | 季度/年度 |
| balance_sheet | 资产负债表 | 季度/年度 |
| cash_flow | 现金流量表 | 季度/年度 |
| ratios | 财务比率 | 实时 |
| metrics | 估值指标 | 实时 |
| estimates | 分析师预期 | 日更新 |

### 数据源

- **Yahoo Finance**: 免费财务数据
- **Financial Modeling Prep**: 专业财务数据 API（付费）
- **SEC EDGAR**: 官方财报文件（原始）
- **Alpha Vantage**: 基础财务指标

## 实现细节

### 1. 财务数据获取

```python
class FinancialDataFetcher:
    async def fetch_financials(self, symbol: str, statement_type: str)
    async def fetch_ratios(self, symbol: str)
    async def fetch_metrics(self, symbol: str)
```

### 2. 数据标准化

- 统一货币单位（USD）
- 标准化时间周期（季度/年度）
- 计算衍生指标

### 3. 缓存策略

- 财报数据缓存 24 小时
- 实时指标缓存 1 小时
- 分析师预期缓存 6 小时

## DoD

- [ ] 支持至少 2 个数据源
- [ ] 获取三大财报数据
- [ ] 计算关键财务比率
- [ ] 货币单位标准化
- [ ] 数据持久化到 PostgreSQL
- [ ] 错误处理和重试机制
