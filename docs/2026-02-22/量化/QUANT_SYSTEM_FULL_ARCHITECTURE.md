# 量化策略系统完整架构设计

> 版本: v1.0
> 日期: 2026-02-22
> 定位: 个人/小团队量化，SkillForge 为核心编排引擎
> 覆盖: 策略研发 + 风险管理 + 系统稳定性 + 合规审计

---

## 1. 系统全景图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          量化策略系统完整架构 (SkillForge 为核心)                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          用户交互层 (UI Layer)                           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │   │
│  │  │ Web 控制台│  │ Jupyter  │  │ CLI 工具 │  │ 告警通知 │  │ 报表导出 │ │   │
│  │  │ Dashboard│  │ Notebook │  │   CLI    │  │  Alert   │  │  Report  │ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                        │
│                                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                     SkillForge 编排引擎 (核心层)                          │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐   │   │
│  │  │                     8-Stage 编排流水线                            │   │   │
│  │  │  Intake → License → Scan → Draft → Gate → Scaffold → Test → Pack │   │   │
│  │  └──────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                          │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │  │ 30_composer │ │ 40_artifact │ │ 50_governance│ │ 60_runtime  │        │   │
│  │  │  智能编排器  │ │  产物构建器  │ │   治理引擎   │ │  运行时引擎  │        │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  │                                                                          │   │
│  │  ┌──────────────────────────────────────────────────────────────────┐   │   │
│  │  │  Gate 体系: Preflight → Constitution → Execution → Compliance    │   │   │
│  │  └──────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                        │
│                                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          Skill 能力层 (6 大模块)                          │   │
│  │                                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ 模块 1: 数据层 (Data Layer)                                      │    │   │
│  │  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │   │
│  │  │ │openbb-   │ │data-     │ │data-     │ │data-     │            │    │   │
│  │  │ │fetch     │ │cleaner   │ │validator │ │versioner │            │    │   │
│  │  │ │数据获取   │ │数据清洗   │ │数据校验   │ │版本控制   │            │    │   │
│  │  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ 模块 2: 研发层 (Research Layer)                                  │    │   │
│  │  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │   │
│  │  │ │factor-   │ │kronos-   │ │backtest- │ │optimizer-│            │    │   │
│  │  │ │miner     │ │predict   │ │engine    │ │param     │            │    │   │
│  │  │ │因子挖掘   │ │价格预测   │ │回测引擎   │ │参数优化   │            │    │   │
│  │  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │    │   │
│  │  │ ┌──────────┐ ┌──────────┐ ┌──────────┐                         │    │   │
│  │  │ │strategy- │ │evaluator-│ │notebook- │                         │    │   │
│  │  │ │designer  │ │metrics   │ │manager   │                         │    │   │
│  │  │ │策略设计器 │ │策略评估   │ │笔记本管理 │                         │    │   │
│  │  │ └──────────┘ └──────────┘ └──────────┘                         │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ 模块 3: 组合层 (Portfolio Layer)                                 │    │   │
│  │  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │   │
│  │  │ │portfolio-│ │position- │ │rebalance-│ │attribution│            │    │   │
│  │  │ │allocator │ │manager   │ │engine    │ │analyzer  │            │    │   │
│  │  │ │资产配置   │ │仓位管理   │ │再平衡     │ │业绩归因   │            │    │   │
│  │  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ 模块 4: 执行层 (Execution Layer)                                 │    │   │
│  │  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │   │
│  │  │ │veighna-  │ │order-    │ │slippage- │ │execution-│            │    │   │
│  │  │ │execute   │ │router    │ │analyzer  │ │algo      │            │    │   │
│  │  │ │交易执行   │ │订单路由   │ │滑点分析   │ │执行算法   │            │    │   │
│  │  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ 模块 5: 风控层 (Risk Layer)                                      │    │   │
│  │  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │   │
│  │  │ │risk-     │ │var-      │ │stress-   │ │liquidity-│            │    │   │
│  │  │ │guard     │ │calculator│ │tester    │ │monitor   │            │    │   │
│  │  │ │实时风控   │ │VaR计算    │ │压力测试   │ │流动性监控 │            │    │   │
│  │  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │    │   │
│  │  │ ┌──────────┐ ┌──────────┐                                      │    │   │
│  │  │ │drawdown- │ │exposure- │                                      │    │   │
│  │  │ │limiter   │ │tracker   │                                      │    │   │
│  │  │ │回撤控制   │ │敞口追踪   │                                      │    │   │
│  │  │ └──────────┘ └──────────┘                                      │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ 模块 6: 治理层 (Governance Layer)                                │    │   │
│  │  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │   │
│  │  │ │audit-    │ │evidence- │ │replay-   │ │compliance│            │    │   │
│  │  │ │logger    │ │manager   │ │engine    │ │reporter  │            │    │   │
│  │  │ │审计日志   │ │证据管理   │ │复现引擎   │ │合规报告   │            │    │   │
│  │  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │    │   │
│  │  │ ┌──────────┐ ┌──────────┐                                      │    │   │
│  │  │ │monitor-  │ │alert-    │                                      │    │   │
│  │  │ │dashboard │ │router    │                                      │    │   │
│  │  │ │监控面板   │ │告警路由   │                                      │    │   │
│  │  │ └──────────┘ └──────────┘                                      │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                        │
│                                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          基础设施层 (Infra Layer)                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │ 时序数据库 │  │ 消息队列  │  │ 缓存层   │  │ 文件存储  │  │ 配置中心  │  │   │
│  │  │TDengine  │  │  Redis   │  │  Redis   │  │  MinIO   │  │  Consul  │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 完整 Skill 清单

### 2.1 数据层 Skills (6 个)

| Skill ID | 职责 | 输入 | 输出 | 依赖 |
|----------|------|------|------|------|
| `openbb-fetch` | 多源数据获取 | symbols, data_type, provider | OHLCV DataFrame | OpenBB |
| `data-cleaner` | 数据清洗（缺失值、异常值） | raw_df, rules | cleaned_df | pandas |
| `data-validator` | 数据质量校验 | df, schema | validation_report | jsonschema |
| `data-versioner` | 数据版本控制 | df, snapshot_id | version_ref | dvc/git |
| `data-enricher` | 数据增强（衍生指标） | df, indicators | enriched_df | talib |
| `data-syncer` | 增量数据同步 | last_timestamp | delta_df | - |

### 2.2 研发层 Skills (9 个)

| Skill ID | 职责 | 输入 | 输出 | 依赖 |
|----------|------|------|------|------|
| `factor-miner` | 因子挖掘与筛选 | price_df, universe | factor_list | alphalens |
| `kronos-predict` | K线价格预测 | ohlcv_df, pred_len | predictions_df | Kronos |
| `backtest-engine` | 策略回测 | strategy, data, config | backtest_result | VeighNa |
| `optimizer-param` | 参数网格搜索 | strategy, param_grid | optimal_params | optuna |
| `strategy-designer` | 策略代码生成 | strategy_spec | strategy_code | - |
| `evaluator-metrics` | 策略指标计算 | backtest_result | metrics_report | quantstats |
| `notebook-manager` | 研究笔记本管理 | notebook_spec | notebook_url | jupyter |
| `signal-generator` | 交易信号生成 | predictions, rules | signals | - |
| `feature-engineer` | 特征工程 | raw_data, feature_config | features | - |

### 2.3 组合层 Skills (4 个)

| Skill ID | 职责 | 输入 | 输出 | 依赖 |
|----------|------|------|------|------|
| `portfolio-allocator` | 资产配置优化 | assets, constraints | weights | cvxpy |
| `position-manager` | 仓位管理 | signals, capital, risk | position_sizes | - |
| `rebalance-engine` | 再平衡执行 | current_weights, target_weights | rebalance_orders | - |
| `attribution-analyzer` | 业绩归因分析 | returns, factors | attribution_report | - |

### 2.4 执行层 Skills (4 个)

| Skill ID | 职责 | 输入 | 输出 | 依赖 |
|----------|------|------|------|------|
| `veighna-execute` | 订单执行 | order_spec | execution_result | VeighNa |
| `order-router` | 智能订单路由 | order, venues | routed_order | - |
| `slippage-analyzer` | 滑点分析 | expected_vs_actual | slippage_report | - |
| `execution-algo` | 执行算法 (TWAP/VWAP) | order, algo_type | child_orders | - |

### 2.5 风控层 Skills (6 个)

| Skill ID | 职责 | 输入 | 输出 | 依赖 |
|----------|------|------|------|------|
| `risk-guard` | 实时风控检查 | trade_request, risk_rules | gate_decision | - |
| `var-calculator` | VaR/CVaR 计算 | portfolio, confidence | var_report | - |
| `stress-tester` | 压力测试 | portfolio, scenarios | stress_report | - |
| `liquidity-monitor` | 流动性监控 | order_book, volume | liquidity_score | - |
| `drawdown-limiter` | 回撤控制 | current_pnl, threshold | limit_decision | - |
| `exposure-tracker` | 敞口追踪 | positions, market_data | exposure_report | - |

### 2.6 治理层 Skills (6 个)

| Skill ID | 职责 | 输入 | 输出 | 依赖 |
|----------|------|------|------|------|
| `audit-logger` | 审计日志记录 | event, context | audit_record | - |
| `evidence-manager` | 证据链管理 | skill_outputs | evidence_pack | - |
| `replay-engine` | 执行复现 | run_id, replay_config | replay_result | - |
| `compliance-reporter` | 合规报告生成 | audit_records, period | compliance_report | - |
| `monitor-dashboard` | 监控数据聚合 | metrics_sources | dashboard_data | - |
| `alert-router` | 告警路由分发 | alert_event, rules | notifications | - |

**总计: 35 个 Skills**

---

## 3. 核心数据流

### 3.1 策略研发流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                        策略研发完整流程                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐         │
│  │ 数据获取 │ ─→ │ 因子挖掘 │ ─→ │ 策略设计 │ ─→ │ 回测验证 │         │
│  │openbb-  │    │factor-  │    │strategy-│    │backtest-│         │
│  │fetch    │    │miner    │    │designer │    │engine   │         │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘         │
│       │              │              │              │               │
│       ▼              ▼              ▼              ▼               │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐         │
│  │数据校验  │    │特征工程  │    │信号生成  │    │指标评估  │         │
│  │data-    │    │feature- │    │signal-  │    │evaluator│         │
│  │validator│    │engineer │    │generator│    │-metrics │         │
│  └─────────┘    └─────────┘    └─────────┘    └────┬────┘         │
│                                                     │               │
│                                                     ▼               │
│                                              ┌─────────┐           │
│                                              │ 参数优化 │           │
│                                              │optimizer│           │
│                                              │-param   │           │
│                                              └────┬────┘           │
│                                                   │                 │
│                                                   ▼                 │
│                                              ┌─────────┐           │
│                                              │ 策略冻结 │           │
│                                              │ (版本锁定)│           │
│                                              └─────────┘           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 实盘交易流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                        实盘交易完整流程                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    信号生成阶段                               │  │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐                 │  │
│  │  │ 数据同步 │ ─→ │ 价格预测 │ ─→ │ 信号生成 │                 │  │
│  │  │data-    │    │kronos-  │    │signal-  │                 │  │
│  │  │syncer   │    │predict  │    │generator│                 │  │
│  │  └─────────┘    └─────────┘    └────┬────┘                 │  │
│  └───────────────────────────────────┬──────────────────────────┘  │
│                                      │                              │
│                                      ▼                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    组合决策阶段                               │  │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐                 │  │
│  │  │资产配置  │ ─→ │仓位计算  │ ─→ │再平衡检查 │                 │  │
│  │  │portfolio│    │position-│    │rebalance│                 │  │
│  │  │-alloc   │    │manager  │    │-engine  │                 │  │
│  │  └─────────┘    └─────────┘    └────┬────┘                 │  │
│  └───────────────────────────────────┬──────────────────────────┘  │
│                                      │                              │
│                                      ▼                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    风控把关阶段 (Gate 1)                       │  │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐   │  │
│  │  │实时风控  │ ─→ │VaR检查  │ ─→ │敞口检查  │ ─→ │回撤检查  │   │  │
│  │  │risk-    │    │var-     │    │exposure-│    │drawdown-│   │  │
│  │  │guard    │    │calculator│    │tracker  │    │limiter  │   │  │
│  │  └────┬────┘    └─────────┘    └─────────┘    └─────────┘   │  │
│  │       │                                                      │  │
│  │       ▼ Gate Decision: ALLOW / DENY / WARN                   │  │
│  └───────┼──────────────────────────────────────────────────────┘  │
│          │                                                          │
│          ▼ (ALLOW)                                                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    订单执行阶段                               │  │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐                 │  │
│  │  │订单路由  │ ─→ │执行算法  │ ─→ │交易执行  │                 │  │
│  │  │order-   │    │execution│    │veighna- │                 │  │
│  │  │router   │    │-algo    │    │execute  │                 │  │
│  │  └─────────┘    └─────────┘    └────┬────┘                 │  │
│  └───────────────────────────────────┬──────────────────────────┘  │
│                                      │                              │
│                                      ▼                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    合规审计阶段 (Gate 2)                       │  │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐   │  │
│  │  │审计日志  │ ─→ │证据管理  │ ─→ │滑点分析  │ ─→ │合规报告  │   │  │
│  │  │audit-   │    │evidence-│    │slippage-│    │compliance│   │  │
│  │  │logger   │    │manager  │    │analyzer │    │-reporter │   │  │
│  │  └─────────┘    └─────────┘    └─────────┘    └─────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Gate 规则体系

### 4.1 三级 Gate 结构

```yaml
# orchestration/gate_rules/quant_default.yml
gate_levels:
  # Level 1: 交易前检查 (Pre-trade)
  pre_trade:
    - rule_id: "POSITION_LIMIT"
      description: "单标的仓位上限"
      check: "position_size <= max_position_ratio * total_capital"
      severity: "critical"
      on_fail: "DENY"

    - rule_id: "DAILY_LOSS_LIMIT"
      description: "单日亏损上限"
      check: "daily_pnl >= -max_daily_loss"
      severity: "critical"
      on_fail: "DENY"

    - rule_id: "DRAWDOWN_LIMIT"
      description: "最大回撤限制"
      check: "current_drawdown <= max_drawdown"
      severity: "critical"
      on_fail: "DENY"

    - rule_id: "LIQUIDITY_CHECK"
      description: "流动性检查"
      check: "order_size <= avg_daily_volume * 0.05"
      severity: "warning"
      on_fail: "WARN"

    - rule_id: "CONCENTRATION_LIMIT"
      description: "持仓集中度"
      check: "single_sector_weight <= 0.3"
      severity: "warning"
      on_fail: "WARN"

  # Level 2: 执行中检查 (In-flight)
  in_flight:
    - rule_id: "SLIPPAGE_ALERT"
      description: "滑点告警"
      check: "actual_slippage <= expected_slippage * 1.5"
      severity: "warning"
      on_fail: "ALERT"

    - rule_id: "EXECUTION_TIMEOUT"
      description: "执行超时"
      check: "execution_time <= max_execution_time"
      severity: "warning"
      on_fail: "ALERT"

  # Level 3: 交易后检查 (Post-trade)
  post_trade:
    - rule_id: "AUDIT_TRAIL_COMPLETE"
      description: "审计轨迹完整"
      check: "evidence_chain_complete == true"
      severity: "critical"
      on_fail: "ALERT_HUMAN"

    - rule_id: "RECONCILIATION"
      description: "持仓对账"
      check: "expected_position == actual_position"
      severity: "critical"
      on_fail: "ALERT_HUMAN"
```

### 4.2 Gate 决策流

```
交易请求
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Gate 1: Pre-trade                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │仓位检查  │  │亏损检查  │  │回撤检查  │  │流动性检查 │       │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │
│       │            │            │            │             │
│       └────────────┴────────────┴────────────┘             │
│                          │                                  │
│               ┌──────────▼──────────┐                      │
│               │  Gate Decision 1    │                      │
│               │  ALLOW / DENY / WARN│                      │
│               └──────────┬──────────┘                      │
└──────────────────────────┼──────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              │ DENY       │ ALLOW      │ WARN
              ▼            ▼            ▼
         ┌─────────┐  ┌─────────┐  ┌─────────┐
         │ 阻止交易 │  │ 继续执行 │  │ 人工确认 │
         └─────────┘  └────┬────┘  └─────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Gate 2: In-flight                        │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ 滑点监控         │  │ 执行超时监控     │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           └─────────────────────┘                            │
│                       │                                      │
│            ┌──────────▼──────────┐                          │
│            │  Gate Decision 2    │                          │
│            │  CONTINUE / ALERT   │                          │
│            └──────────┬──────────┘                          │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Gate 3: Post-trade                       │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ 审计轨迹检查     │  │ 持仓对账         │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           └─────────────────────┘                            │
│                       │                                      │
│            ┌──────────▼──────────┐                          │
│            │  Audit Pack 生成    │                          │
│            │  L3 合规包          │                          │
│            └─────────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. 监控与告警体系

### 5.1 监控指标

```yaml
# orchestration/monitoring/metrics.yml
metrics:
  # 策略层面
  strategy:
    - name: "strategy_pnl"
      type: "gauge"
      description: "策略实时盈亏"
    - name: "strategy_sharpe"
      type: "gauge"
      description: "策略夏普比率"
    - name: "strategy_drawdown"
      type: "gauge"
      description: "策略当前回撤"
    - name: "strategy_win_rate"
      type: "gauge"
      description: "策略胜率"
    - name: "strategy_trades_count"
      type: "counter"
      description: "策略交易次数"

  # 执行层面
  execution:
    - name: "order_latency_ms"
      type: "histogram"
      description: "订单延迟分布"
    - name: "fill_rate"
      type: "gauge"
      description: "订单成交率"
    - name: "slippage_bps"
      type: "histogram"
      description: "滑点分布 (基点)"
    - name: "rejection_rate"
      type: "gauge"
      description: "订单拒绝率"

  # 风控层面
  risk:
    - name: "portfolio_var_95"
      type: "gauge"
      description: "组合 VaR (95%置信度)"
    - name: "portfolio_var_99"
      type: "gauge"
      description: "组合 VaR (99%置信度)"
    - name: "exposure_ratio"
      type: "gauge"
      description: "敞口比率"
    - name: "leverage_ratio"
      type: "gauge"
      description: "杠杆比率"

  # 系统层面
  system:
    - name: "skill_execution_time_ms"
      type: "histogram"
      description: "Skill 执行时间"
    - name: "skill_error_rate"
      type: "gauge"
      description: "Skill 错误率"
    - name: "gate_deny_rate"
      type: "gauge"
      description: "Gate 拒绝率"
    - name: "evidence_chain_completeness"
      type: "gauge"
      description: "证据链完整率"
```

### 5.2 告警规则

```yaml
# orchestration/alerting/rules.yml
alert_rules:
  # 紧急告警 (立即人工干预)
  critical:
    - alert_id: "DRAWDOWN_BREACH"
      condition: "strategy_drawdown > 0.1"
      message: "回撤超过 10%，需要人工干预"
      channels: ["slack", "sms", "phone"]

    - alert_id: "GATE_DENY_SPIKE"
      condition: "gate_deny_rate > 0.3 in 5m"
      message: "Gate 拒绝率异常，可能策略失效"
      channels: ["slack", "email"]

    - alert_id: "EXECUTION_FAILURE"
      condition: "order_rejection_count > 5 in 10m"
      message: "订单连续被拒绝，检查交易接口"
      channels: ["slack", "sms"]

  # 警告告警 (需要关注)
  warning:
    - alert_id: "HIGH_SLIPPAGE"
      condition: "avg_slippage_bps > 10 in 1h"
      message: "平均滑点过高，考虑调整执行算法"
      channels: ["slack"]

    - alert_id: "LOW_FILL_RATE"
      condition: "fill_rate < 0.8 in 1h"
      message: "成交率下降，检查市场流动性"
      channels: ["slack"]

    - alert_id: "PREDICTION_CONFIDENCE_LOW"
      condition: "kronos_confidence_mean < 0.5 in 30m"
      message: "预测置信度下降，考虑暂停交易"
      channels: ["slack", "email"]

  # 信息告警 (记录)
  info:
    - alert_id: "DAILY_PNL_SUMMARY"
      condition: "time == 15:05"  # 收盘后
      message: "每日盈亏汇总"
      channels: ["email"]

    - alert_id: "STRATEGY_REBALANCE"
      condition: "rebalance_triggered == true"
      message: "策略触发再平衡"
      channels: ["slack"]
```

---

## 6. 数据存储架构

### 6.1 存储选型

```
┌─────────────────────────────────────────────────────────────┐
│                      数据存储架构                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              时序数据库 (热数据)                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │              TDengine                       │    │   │
│  │  │  - 实时行情 (Tick/K线)                       │    │   │
│  │  │  - 交易流水                                  │    │   │
│  │  │  - 监控指标                                  │    │   │
│  │  │  - 审计日志                                  │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │  保留策略: 热数据 7 天, 温数据 90 天, 冷数据 S3     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              关系型数据库 (元数据)                    │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │              PostgreSQL                     │    │   │
│  │  │  - 策略配置                                  │    │   │
│  │  │  - 用户权限                                  │    │   │
│  │  │  - Gate 规则                                 │    │   │
│  │  │  - Skill 注册表                              │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              对象存储 (证据 & 产物)                   │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │              MinIO                          │    │   │
│  │  │  - Audit Pack (L3 合规包)                   │    │   │
│  │  │  - Evidence 文件                            │    │   │
│  │  │  - 回测报告                                  │    │   │
│  │  │  - 策略快照                                  │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              缓存层 (高频访问)                        │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │              Redis                          │    │   │
│  │  │  - 实时持仓                                  │    │   │
│  │  │  - Gate 决策缓存                            │    │   │
│  │  │  - 会话状态                                  │    │   │
│  │  │  - 消息队列 (Pub/Sub)                       │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 数据生命周期

```
┌────────────────────────────────────────────────────────────┐
│                    数据生命周期管理                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  实时数据 (0-1天)                                          │
│  ┌──────────┐                                             │
│  │  Redis   │ ← 内存缓存，毫秒级访问                       │
│  └────┬─────┘                                             │
│       │                                                    │
│       ▼                                                    │
│  热数据 (1-7天)                                            │
│  ┌──────────┐                                             │
│  │TDengine  │ ← SSD存储，秒级访问                          │
│  │ (hot)    │                                             │
│  └────┬─────┘                                             │
│       │                                                    │
│       ▼                                                    │
│  温数据 (7-90天)                                           │
│  ┌──────────┐                                             │
│  │TDengine  │ ← HDD存储，分钟级访问                        │
│  │ (warm)   │                                             │
│  └────┬─────┘                                             │
│       │                                                    │
│       ▼                                                    │
│  冷数据 (90天+)                                            │
│  ┌──────────┐                                             │
│  │  MinIO   │ ← 对象存储，小时级访问                       │
│  │ (S3)     │   (用于合规归档)                             │
│  └──────────┘                                             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 7. 实施路线图

### Phase 0: 基础设施准备 (1周)

```
目标: 搭建核心基础设施

任务:
├── [ ] 安装 TDengine (时序数据库)
├── [ ] 安装 PostgreSQL (元数据库)
├── [ ] 安装 Redis (缓存+消息队列)
├── [ ] 安装 MinIO (对象存储)
├── [ ] 配置 SkillForge 核心引擎
└── [ ] 验证基础设施连通性

交付物:
├── docker-compose.yml (一键启动)
├── 基础设施健康检查脚本
└── 网络拓扑文档
```

### Phase 1: 数据层实现 (2周)

```
目标: 实现数据获取和管理的 6 个 Skills

Week 1:
├── [ ] openbb-fetch Skill (数据获取)
│   ├── schemas/openbb-fetch.input.schema.json
│   ├── schemas/openbb-fetch.output.schema.json
│   ├── implementation/openbb_fetch.py
│   └── tests/test_openbb_fetch.py
│
├── [ ] data-cleaner Skill (数据清洗)
│   ├── schemas/data-cleaner.*.schema.json
│   ├── implementation/data_cleaner.py
│   └── tests/test_data_cleaner.py
│
└── [ ] data-validator Skill (数据校验)

Week 2:
├── [ ] data-versioner Skill (版本控制)
├── [ ] data-enricher Skill (数据增强)
├── [ ] data-syncer Skill (增量同步)
└── [ ] 集成测试 & 文档

交付物:
├── 6 个数据层 Skills
├── 合同测试通过
├── 数据管道可运行
└── API 文档
```

### Phase 2: 研发层实现 (3周)

```
目标: 实现策略研发的 9 个 Skills

Week 1:
├── [ ] factor-miner Skill (因子挖掘)
├── [ ] feature-engineer Skill (特征工程)
└── [ ] kronos-predict Skill (价格预测)

Week 2:
├── [ ] backtest-engine Skill (回测引擎)
├── [ ] evaluator-metrics Skill (策略评估)
└── [ ] optimizer-param Skill (参数优化)

Week 3:
├── [ ] strategy-designer Skill (策略设计)
├── [ ] signal-generator Skill (信号生成)
├── [ ] notebook-manager Skill (笔记本管理)
└── [ ] 研发流程端到端测试

交付物:
├── 9 个研发层 Skills
├── 完整研发流程可运行
├── 回测报告示例
└── 研发手册
```

### Phase 3: 执行层实现 (2周)

```
目标: 实现交易执行的 4 个 Skills

Week 1:
├── [ ] veighna-execute Skill (交易执行)
│   ├── 集成 VeighNa CTP Gateway
│   ├── 实现 Gate 1 (Pre-trade) 检查
│   └── 仿真环境测试
│
├── [ ] order-router Skill (订单路由)
└── [ ] execution-algo Skill (执行算法)

Week 2:
├── [ ] slippage-analyzer Skill (滑点分析)
├── [ ] Gate 体系完整实现
└── [ ] 实盘模拟测试

交付物:
├── 4 个执行层 Skills
├── Gate 体系运行
├── 仿真交易验证
└── 交易执行手册
```

### Phase 4: 风控+治理层实现 (2周)

```
目标: 实现风控和治理的 12 个 Skills

Week 1 (风控层):
├── [ ] risk-guard Skill (实时风控)
├── [ ] var-calculator Skill (VaR计算)
├── [ ] stress-tester Skill (压力测试)
├── [ ] liquidity-monitor Skill (流动性)
├── [ ] drawdown-limiter Skill (回撤控制)
└── [ ] exposure-tracker Skill (敞口追踪)

Week 2 (治理层):
├── [ ] audit-logger Skill (审计日志)
├── [ ] evidence-manager Skill (证据管理)
├── [ ] replay-engine Skill (复现引擎)
├── [ ] compliance-reporter Skill (合规报告)
├── [ ] monitor-dashboard Skill (监控面板)
└── [ ] alert-router Skill (告警路由)

交付物:
├── 12 个风控+治理 Skills
├── 完整 Gate 体系
├── L3 Audit Pack 生成
└── 合规报告示例
```

### Phase 5: 组合层 + 集成测试 (1周)

```
目标: 实现组合管理，完成端到端集成

任务:
├── [ ] portfolio-allocator Skill
├── [ ] position-manager Skill
├── [ ] rebalance-engine Skill
├── [ ] attribution-analyzer Skill
├── [ ] 端到端集成测试
├── [ ] 压力测试
├── [ ] 文档完善

交付物:
├── 4 个组合层 Skills
├── 完整系统可运行
├── 集成测试报告
└── 用户手册 v1.0
```

---

## 8. 技术选型总结

| 层级 | 组件 | 技术选型 | 说明 |
|------|------|----------|------|
| **数据获取** | 行情源 | OpenBB + 迅投研 | 多源聚合 |
| **预测模型** | K线预测 | Kronos | AAAI 2026 |
| **交易执行** | 交易框架 | VeighNa 4.0 | 国产最强 |
| **时序数据库** | 行情存储 | TDengine | 高性能 |
| **元数据库** | 配置存储 | PostgreSQL | 稳定可靠 |
| **缓存** | 高频访问 | Redis | 通用方案 |
| **对象存储** | 证据归档 | MinIO | S3 兼容 |
| **消息队列** | 事件驱动 | Redis Pub/Sub | 轻量方案 |
| **编排引擎** | 核心调度 | SkillForge | 自研 |
| **监控** | 指标采集 | Prometheus | 行业标准 |
| **可视化** | Dashboard | Grafana | 灵活强大 |
| **告警** | 通知分发 | AlertManager | 可扩展 |

---

## 9. 风险与缓解

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| OpenBB AGPL 污染 | 高 | 独立服务，API 边界隔离 |
| Kronos 模型漂移 | 中 | 定期重训，置信度监控 |
| VeighNa 接口变化 | 中 | 版本锁定，抽象层封装 |
| 单点故障 | 高 | 主备部署，自动切换 |
| 数据源中断 | 中 | 多源备份，本地缓存 |
| 策略过拟合 | 中 | 样本外测试，Walk-forward |
| 合规要求变化 | 中 | Gate 规则可配置 |

---

## 10. 下一步行动

1. **确认基础设施**: 是否使用推荐的 TDengine + PostgreSQL + Redis + MinIO？
2. **优先级排序**: 35 个 Skills 中，哪些是 MVP 必须的？
3. **资源评估**: 开发周期预估 9 周，是否可接受？
4. **风险偏好**: Gate 规则的阈值设置，需要根据你的风险偏好定制

---

*文档结束 - 待确认后开始实施*
