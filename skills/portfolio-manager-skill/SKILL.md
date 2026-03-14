---
name: portfolio-manager-skill
description: 组合管理（资产配置、再平衡、组合构建）
---

# portfolio-manager-skill

## 触发条件

- 构建投资组合
- 组合再平衡
- 风险调整

## 输入

```yaml
input:
  assets: ["AAPL", "MSFT", "GOOGL", "TSLA"]
  strategy: "equal_weight"
  rebalance_frequency: "monthly"
  constraints:
    max_weight_per_asset: 0.4
    min_weight_per_asset: 0.05
    sector_diversification: true
```

## 输出

```yaml
output:
  status: "SUCCESS"
  weights:
    AAPL: 0.25
    MSFT: 0.25
    GOOGL: 0.25
    TSLA: 0.25
  next_rebalance: "2024-04-01"
```

## 核心功能

### 配置方法

| 方法 | 说明 |
|------|------|
| 等权重 | 所有资产权重相同 |
| 市值加权 | 按市值分配权重 |
| 风险平价 | 按风险贡献分配 |
| 最小方差 | 最小化组合方差 |
| 最大分散度 | 最大化分散度 |
| Black-Litterman | 结合观点的贝叶斯方法 |

### 再平衡

- 定期再平衡
- 偏离度触发
- 波动率触发

## DoD
- [ ] 支持多种配置方法
- [ ] 支持组合约束
- [ ] 自动再平衡
- [ ] 组合绩效监控
