---
name: factor-analyzer-skill
description: 因子分析（单因子检验、多因子模型、因子归因）
---

# factor-analyzer-skill

## 触发条件

- 量化策略研发
- 因子有效性检验
- 组合收益归因

## 输入

```yaml
input:
  factors:
    - name: "momentum"
      data: [...]
    - name: "value"
      data: [...]
    - name: "quality"
      data: [...]
  returns: [...]
  method: "ic_analysis"  # ic_analysis, regression, attribution
```

## 输出

```yaml
output:
  status: "SUCCESS"
  ic_analysis:
    momentum:
      ic: 0.05
      ic_ir: 0.82
      rank_ic: 0.048
      t_stat: 3.52
      p_value: 0.0002
    value:
      ic: 0.03
      ic_ir: 0.65
      ...
  multi_factor_r2: 0.15
  factor_exposure:
    momentum: 0.5
    value: 0.3
    quality: 0.2
```

## 核心功能

### 因子类型

| 类别 | 因子示例 |
|------|----------|
| 动量 | Momentum, ROC, 52周高点 |
| 价值 | PE, PB, PCF, PS |
| 质量 | ROE, ROA, 毛利率, 负债率 |
| 成长 | 营收增长, 利润增长 |
| 情绪 | 换手率, 分析师评级 |
| 技术 | MA趋势, RSI, 波动率 |

### 分析方法

- **IC分析**: 相关系数、IR比率、t检验
- **回归分析**: 多因子回归、因子载荷
- **收益归因**: 因子贡献分解

## DoD

- [ ] 支持至少 10 个常用因子
- [ ] IC/IR 统计显著性检验
- [ ] 多因子回归分析
- [ ] 因子正交化处理
- [ ] 因子有效性评分
