# A7_scan.md - Multi-Factor Strategy 意图扫描

**任务**: A7 Multi-Factor Strategy Migration
**执行者**: Antigravity-1
**源文件**: `D:\NEW-GM\strategies\template_multi_factor.py`
**扫描时间**: 2026-02-18

---

## 扫描组件清单

| component_id | source_doc_ref | intent_summary | mapping_target | value_score | risk_level | migration_decision | evidence_ref |
|--------------|----------------|----------------|----------------|-------------|------------|-------------------|--------------|
| MF-001 | template_multi_factor.py:25-62 | MultiFactorStrategy 类定义与初始化，包含因子列表、权重配置、调仓参数 | skillforge/.../multi_factor.py:StrategyConfig | 9 | Low | **MIGRATE** | Lines 25-62: 显式类定义与参数 |
| MF-002 | template_multi_factor.py:63-100 | calculate_custom_factors(): 计算动量/价值/质量/低波/成长/流动性/技术因子 | skillforge/.../multi_factor.py:FactorCalculator | 10 | Low | **MIGRATE** | Lines 63-100: 完整因子计算逻辑 |
| MF-003 | template_multi_factor.py:102-109 | _calculate_rsi(): RSI技术指标计算 | skillforge/.../indicators/rsi.py | 8 | Low | **MIGRATE** | Lines 102-109: 标准RSI实现 |
| MF-004 | template_multi_factor.py:111-116 | _calculate_macd(): MACD技术指标计算 | skillforge/.../indicators/macd.py | 8 | Low | **MIGRATE** | Lines 111-116: 标准MACD实现 |
| MF-005 | template_multi_factor.py:118-125 | _calculate_bollinger_position(): 布林带位置计算 | skillforge/.../indicators/bollinger.py | 7 | Low | **MIGRATE** | Lines 118-125: 布林带逻辑 |
| MF-006 | template_multi_factor.py:127-149 | neutralize_factors(): 因子行业/规模中性化处理 | skillforge/.../multi_factor.py:FactorNeutralizer | 9 | Medium | **MIGRATE** | Lines 127-149: 中性化算法 |
| MF-007 | template_multi_factor.py:151-177 | calculate_factor_scores(): StandardScaler标准化+加权综合评分 | skillforge/.../multi_factor.py:ScoreCalculator | 10 | Low | **MIGRATE** | Lines 151-177: 核心评分逻辑 |
| MF-008 | template_multi_factor.py:179-261 | generate_signals(): 根据综合评分生成买入/卖出/持有信号 | skillforge/.../multi_factor.py:SignalGenerator | 10 | Low | **MIGRATE** | Lines 179-261: 信号生成完整流程 |
| MF-009 | template_multi_factor.py:263-308 | validate_strategy(): 策略验证、统计计算、警告检测 | skillforge/.../multi_factor.py:StrategyValidator | 8 | Low | **MIGRATE** | Lines 263-308: 验证逻辑 |
| MF-010 | template_multi_factor.py:311-419 | run_multi_factor_backtest(): 异步回测入口与报告生成 | skillforge/.../backtest/runner.py | 9 | Medium | **MIGRATE** | Lines 311-419: 回测流程 |

---

## 因子映射详情

### 动量因子 (Momentum)
| 指标ID | 指标名 | 计算方式 | source_ref |
|--------|--------|----------|------------|
| MOM-1 | momentum_20d | close.pct_change(20) | Line 68 |
| MOM-2 | momentum_60d | close.pct_change(60) | Line 69 |
| MOM-3 | momentum_120d | close.pct_change(120) | Line 70 |

### 价值因子 (Value)
| 指标ID | 指标名 | 计算方式 | source_ref |
|--------|--------|----------|------------|
| VAL-1 | value_pe | 模拟PE (需基本面数据) | Line 73 |
| VAL-2 | value_pb | 模拟PB (需基本面数据) | Line 74 |
| VAL-3 | value_ps | 模拟PS (需基本面数据) | Line 75 |

### 质量因子 (Quality)
| 指标ID | 指标名 | 计算方式 | source_ref |
|--------|--------|----------|------------|
| QUA-1 | quality_roe | 模拟ROE (需财务数据) | Line 78 |
| QUA-2 | quality_roa | 模拟ROA (需财务数据) | Line 79 |
| QUA-3 | quality_debt_ratio | 模拟负债率 | Line 80 |

### 低波因子 (LowVol)
| 指标ID | 指标名 | 计算方式 | source_ref |
|--------|--------|----------|------------|
| LV-1 | lowvol_volatility | returns.rolling(20).std() * sqrt(252) | Line 84 |
| LV-2 | lowvol_beta | 模拟Beta | Line 85 |

### 成长因子 (Growth)
| 指标ID | 指标名 | 计算方式 | source_ref |
|--------|--------|----------|------------|
| GRW-1 | growth_revenue | 模拟营收增长率 | Line 88 |
| GRW-2 | growth_earnings | 模拟盈利增长率 | Line 89 |

### 流动性因子 (Liquidity)
| 指标ID | 指标名 | 计算方式 | source_ref |
|--------|--------|----------|------------|
| LIQ-1 | liquidity_turnover | volume / 1000000 | Line 92 |
| LIQ-2 | liquidity_amihud | abs(returns)/(volume+1).rolling(20).mean() | Line 93 |

### 技术因子 (Technical)
| 指标ID | 指标名 | 计算方式 | source_ref |
|--------|--------|----------|------------|
| TCH-1 | technical_rsi | RSI(14) | Line 96, 102-109 |
| TCH-2 | technical_macd | EMA12-EMA26 | Line 97, 111-116 |
| TCH-3 | technical_bollinger_position | 布林带内位置 | Line 98, 118-125 |

---

## 核心逻辑映射

```
Input: FactorData (price_data, fundamental_data, universe)
│
├── Step 1: calculate_custom_factors()
│   ├── Momentum: 20d/60d/120d returns
│   ├── Value: PE/PB/PS (模拟)
│   ├── Quality: ROE/ROA/Debt (模拟)
│   ├── LowVol: Volatility/Beta
│   ├── Growth: Revenue/Earnings (模拟)
│   ├── Liquidity: Turnover/Amihud
│   └── Technical: RSI/MACD/Bollinger
│
├── Step 2: neutralize_factors()
│   ├── Industry Neutralization (市场均值)
│   └── Size Neutralization (市值代理)
│
├── Step 3: calculate_factor_scores()
│   ├── StandardScaler 标准化
│   └── 加权综合: Σ(factor_i * weight_i)
│
├── Step 4: generate_signals()
│   ├── score > threshold → signal=1 (BUY)
│   ├── score < -threshold → signal=-1 (SELL)
│   └── otherwise → signal=0 (HOLD)
│
Output: PortfolioWeights (composite_score, signal, factor_exposures)
```

---

## 默认因子权重配置

| 因子类别 | 因子名 | 默认权重 | source_ref |
|----------|--------|----------|------------|
| Momentum | momentum_20d | 0.20 | Line 45 |
| Value | value_pe | 0.20 | Line 46 |
| Quality | quality_roe | 0.15 | Line 47 |
| LowVol | lowvol_volatility | 0.15 | Line 48 |
| Growth | growth_revenue | 0.15 | Line 49 |
| Liquidity | liquidity_turnover | 0.15 | Line 50 |

**验证**: Σ weights = 0.20 + 0.20 + 0.15 + 0.15 + 0.15 + 0.15 = 1.00 ✓

---

## 风险评估

| 风险项 | 风险等级 | 说明 | 缓解措施 |
|--------|----------|------|----------|
| 基本面数据缺失 | Medium | Value/Quality/Growth 因子使用模拟数据 | 迁移时需集成真实基本面数据源 |
| 中性化简化 | Medium | 行业/规模中性化使用简化算法 | 需完善行业分类与市值数据 |
| 多股票支持 | Low | _generate_multi_stock_signals 简化处理 | 可正常迁移 |
| 标准化依赖 | Low | 依赖 sklearn.StandardScaler | 保持依赖或自实现 |

---

## 迁移决策汇总

| 统计项 | 数量 |
|--------|------|
| **MIGRATE** | 10 |
| **DEFER** | 0 |
| **REJECT** | 0 |
| **总计** | 10 |

---

## 关键发现

1. **六因子模型完整**: Momentum/Value/Quality/LowVol/Growth/Liquidity 六大因子类别均已实现
2. **技术因子增强**: RSI/MACD/Bollinger 技术指标作为补充因子
3. **可配置权重**: 因子权重通过 `factor_weights` 参数可灵活配置
4. **中性化处理**: 支持行业/规模双重中性化
5. **多股票支持**: 支持单股票与股票池两种模式

---

## 阻塞问题

**无阻塞问题** - 所有组件均可直接迁移

---

## 下一步行动

1. [ ] 创建 `skillforge/src/skills/strategies/multi_factor.py` 骨架
2. [ ] 迁移 FactorCalculator 模块
3. [ ] 迁移 SignalGenerator 模块
4. [ ] 集成真实基本面数据源
5. [ ] 完善行业分类数据
6. [ ] 编写单元测试

---

*Generated by Antigravity-1 | Wave 4 Batch 1 | 2026-02-18*
