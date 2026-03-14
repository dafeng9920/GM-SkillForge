---
name: optimizer-skill
description: 参数优化（网格搜索、遗传算法、贝叶斯优化）
---

# optimizer-skill

## 触发条件

- 策略参数调优
- 寻找最优参数组合
- 参数稳健性检验

## 输入

```yaml
input:
  strategy: "dual_ma"
  parameters:
    fast_period: [5, 10, 15, 20]
    slow_period: [20, 30, 40, 50]
  optimization_method: "grid_search"
  objective: "sharpe_ratio"
  constraints:
    - fast_period < slow_period
    - max_drawdown < 0.2
```

## 输出

```yaml
output:
  best_params:
    fast_period: 10
    slow_period: 30
  best_score: 1.52
  all_results:
    - params: {...}
      score: 1.52
      metrics: {...}
```

## 核心功能

### 优化方法

| 方法 | 说明 | 适用场景 |
|------|------|----------|
| 网格搜索 | 遍历所有参数组合 | 参数空间小 |
| 随机搜索 | 随机采样 | 参数空间大 |
| 贝叶斯优化 | 基于模型的优化 | 昂贵的目标函数 |
| 遗传算法 | 进化算法 | 复杂约束 |

### 目标函数

- 夏普比率
- 总收益
- 最大回撤
- 信息比率
- 卡尔玛比率

## DoD
- [ ] 支持网格搜索
- [ ] 支持随机搜索
- [ ] 支持贝叶斯优化
- [ ] 并行计算
- [ ] 参数稳健性检验
