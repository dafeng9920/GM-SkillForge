# 量化系统 MVP 实施计划

> 版本: v1.0
> 日期: 2026-02-22
> 目标: 8 周内交付可运行的量化策略系统 MVP

---

## 1. MVP 核心原则

```
┌─────────────────────────────────────────────────────────────────┐
│                        MVP 定义                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  最小可行产品 (Minimum Viable Product)                          │
│                                                                 │
│  必须满足:                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ✓ 完成一个完整策略周期                                    │   │
│  │   数据 → 预测 → 信号 → 风控 → 执行 → 审计                │   │
│  │                                                           │   │
│  │ ✓ 基本的故障保护 (Fail-Closed)                           │   │
│  │   Gate 检查 + 风控拦截 + 人工干预                         │   │
│  │                                                           │   │
│  │ ✓ 可追溯和可复现                                          │   │
│  │   审计日志 + 证据链 + Replay 能力                         │   │
│  │                                                           │   │
│  │ ✓ 可扩展架构                                              │   │
│  │   Skill 合同标准化 + 编排器预留                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  不要求:                                                         │
│  ✗ 多策略并行                                                   │
│  ✗ 高频交易                                                     │
│  ✗ 复杂组合优化                                                 │
│  ✗ 生产级高可用                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Skills 优先级排序

### 2.1 优先级定义

| 级别 | 定义 | MVP 包含 | 数量 |
|------|------|----------|------|
| **P0** | 核心必需，无则系统不可用 | ✓ | 10 |
| **P1** | 重要功能，显著提升可用性 | ✓ | 8 |
| **P2** | 增强功能，优化体验 | ✗ | 9 |
| **P3** | 锦上添花，后期迭代 | ✗ | 8 |
| **合计** | - | - | **35** |

### 2.2 完整优先级清单

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          Skills 优先级矩阵                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  P0 - 核心必需 (MVP 必须实现)                                    [10 个]     │
│  ────────────────────────────────────────────────────────────────            │
│                                                                              │
│  数据层 [2]                                                                  │
│  ├── P0-01 openbb-fetch        数据获取 (唯一数据源)                        │
│  └── P0-02 data-validator      数据校验 (防止垃圾进垃圾出)                   │
│                                                                              │
│  研发层 [2]                                                                  │
│  ├── P0-03 kronos-predict      价格预测 (核心AI能力)                         │
│  └── P0-04 signal-generator    信号生成 (预测→交易信号)                      │
│                                                                              │
│  执行层 [2]                                                                  │
│  ├── P0-05 veighna-execute     交易执行 (唯一执行通道)                       │
│  └── P0-06 order-router        订单路由 (简化版)                             │
│                                                                              │
│  风控层 [2]                                                                  │
│  ├── P0-07 risk-guard          实时风控 (Gate 检查)                          │
│  └── P0-08 drawdown-limiter    回撤控制 (防止爆仓)                           │
│                                                                              │
│  治理层 [2]                                                                  │
│  ├── P0-09 audit-logger        审计日志 (所有操作留痕)                       │
│  └── P0-10 evidence-manager    证据管理 (证据链)                             │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  P1 - 重要功能 (MVP 应该实现)                                    [8 个]      │
│  ────────────────────────────────────────────────────────                    │
│                                                                              │
│  数据层 [2]                                                                  │
│  ├── P1-01 data-cleaner        数据清洗 (处理缺失值/异常)                    │
│  └── P1-02 data-syncer         增量同步 (减少API调用)                        │
│                                                                              │
│  研发层 [2]                                                                  │
│  ├── P1-03 backtest-engine     回测引擎 (策略验证)                           │
│  └── P1-04 evaluator-metrics   策略评估 (Sharpe/最大回撤等)                  │
│                                                                              │
│  风控层 [2]                                                                  │
│  ├── P1-05 var-calculator      VaR计算 (风险量化)                            │
│  └── P1-06 exposure-tracker    敞口追踪 (仓位监控)                           │
│                                                                              │
│  治理层 [2]                                                                  │
│  ├── P1-07 replay-engine       复现引擎 (问题排查)                           │
│  └── P1-08 alert-router        告警路由 (问题通知)                           │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  P2 - 增强功能 (V1.1 迭代)                                       [9 个]      │
│  ─────────────────────────────────────────────                               │
│                                                                              │
│  数据层 [2]                                                                  │
│  ├── P2-01 data-versioner      数据版本控制                                  │
│  └── P2-02 data-enricher       数据增强 (衍生指标)                           │
│                                                                              │
│  研发层 [3]                                                                  │
│  ├── P2-03 factor-miner        因子挖掘                                      │
│  ├── P2-04 feature-engineer    特征工程                                      │
│  └── P2-05 optimizer-param     参数优化                                      │
│                                                                              │
│  执行层 [1]                                                                  │
│  └── P2-06 slippage-analyzer   滑点分析                                      │
│                                                                              │
│  风控层 [1]                                                                  │
│  └── P2-07 liquidity-monitor   流动性监控                                    │
│                                                                              │
│  治理层 [2]                                                                  │
│  ├── P2-08 compliance-reporter 合规报告                                      │
│  └── P2-09 monitor-dashboard   监控面板                                      │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  P3 - 锦上添花 (V2.0+)                                           [8 个]      │
│  ─────────────────────────────────                                            │
│                                                                              │
│  研发层 [3]                                                                  │
│  ├── P3-01 strategy-designer   策略设计器 (代码生成)                         │
│  ├── P3-02 notebook-manager    笔记本管理                                    │
│  └── P3-03 execution-algo      执行算法 (TWAP/VWAP)                          │
│                                                                              │
│  组合层 [4]                                                                  │
│  ├── P3-04 portfolio-allocator 资产配置                                      │
│  ├── P3-05 position-manager    仓位管理                                      │
│  ├── P3-06 rebalance-engine    再平衡                                        │
│  └── P3-07 attribution-analyzer 业绩归因                                     │
│                                                                              │
│  风控层 [1]                                                                  │
│  └── P3-08 stress-tester       压力测试                                      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 MVP 技能清单 (P0 + P1 = 18 个)

```yaml
# MVP Skills 清单
mvp_skills:
  p0_core:  # 10个 - 无则不可用
    - openbb-fetch
    - data-validator
    - kronos-predict
    - signal-generator
    - veighna-execute
    - order-router
    - risk-guard
    - drawdown-limiter
    - audit-logger
    - evidence-manager

  p1_important:  # 8个 - 显著提升可用性
    - data-cleaner
    - data-syncer
    - backtest-engine
    - evaluator-metrics
    - var-calculator
    - exposure-tracker
    - replay-engine
    - alert-router
```

---

## 3. MVP 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MVP 系统架构 (18 Skills)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SkillForge 编排引擎                               │   │
│  │                                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │   │
│  │  │  Composer   │  │  Gate       │  │  Evidence   │                 │   │
│  │  │  (编排器)    │  │  (关卡)      │  │  (证据)      │                 │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         MVP Skills 层                                │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ 数据层 (P0: 2, P1: 2)                                        │   │   │
│  │  │                                                               │   │   │
│  │  │  [P0] openbb-fetch ──→ [P1] data-cleaner ──→ [P0] data-     │   │   │
│  │  │        │                      │                 validator    │   │   │
│  │  │        │                      │                      │        │   │   │
│  │  │        └──────────────────────┴──────────────────────┘        │   │   │
│  │  │                               │                               │   │   │
│  │  │                        [P1] data-syncer                       │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                      │                               │   │
│  │                                      ▼                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ 研发层 (P0: 2, P1: 2)                                        │   │   │
│  │  │                                                               │   │   │
│  │  │  [P0] kronos-predict ──→ [P0] signal-generator               │   │   │
│  │  │        │                        │                              │   │   │
│  │  │        ▼                        ▼                              │   │   │
│  │  │  [P1] backtest-engine    [P1] evaluator-metrics              │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                      │                               │   │
│  │                                      ▼                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ 风控层 (P0: 2, P1: 2) - Gate 体系                            │   │   │
│  │  │                                                               │   │   │
│  │  │  ┌──────────────────────────────────────────────────────┐   │   │   │
│  │  │  │              Gate 1: Pre-trade                        │   │   │   │
│  │  │  │  [P0] risk-guard ──→ [P0] drawdown-limiter            │   │   │   │
│  │  │  │        │                   │                           │   │   │   │
│  │  │  │        ▼                   ▼                           │   │   │   │
│  │  │  │  [P1] var-calculator  [P1] exposure-tracker           │   │   │   │
│  │  │  └──────────────────────────────────────────────────────┘   │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                      │                               │   │
│  │                        ALLOW ────────┤                               │   │
│  │                                      ▼                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ 执行层 (P0: 2)                                               │   │   │
│  │  │                                                               │   │   │
│  │  │  [P0] order-router ──→ [P0] veighna-execute                  │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                      │                               │   │
│  │                                      ▼                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ 治理层 (P0: 2, P1: 2)                                        │   │   │
│  │  │                                                               │   │   │
│  │  │  [P0] audit-logger ──→ [P0] evidence-manager                 │   │   │
│  │  │        │                      │                               │   │   │
│  │  │        ▼                      ▼                               │   │   │
│  │  │  [P1] replay-engine     [P1] alert-router                    │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 8周实施计划

### 4.1 总体时间线

```
Week 1-2: 基础设施 + 数据层 (P0)
Week 3-4: 研发层 (P0)
Week 5-6: 风控层 + 执行层 (P0)
Week 7:   治理层 (P0) + 集成测试
Week 8:   P1 功能 + MVP 验收
```

### 4.2 详细计划

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Week 1-2: 基础设施 + 数据层                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 1: 基础设施                                                           │
│  ─────────────────                                                          │
│  Day 1-2:                                                                   │
│  ├── [ ] 安装 Docker + Docker Compose                                       │
│  ├── [ ] 部署 TDengine (时序数据库)                                         │
│  ├── [ ] 部署 PostgreSQL (元数据库)                                         │
│  ├── [ ] 部署 Redis (缓存)                                                  │
│  └── [ ] 部署 MinIO (对象存储)                                              │
│                                                                             │
│  Day 3-4:                                                                   │
│  ├── [ ] 配置 SkillForge 核心引擎                                           │
│  ├── [ ] 创建数据库 schema                                                  │
│  ├── [ ] 编写基础设施健康检查脚本                                           │
│  └── [ ] 验证所有服务连通性                                                 │
│                                                                             │
│  Day 5:                                                                     │
│  ├── [ ] 编写 docker-compose.yml                                            │
│  ├── [ ] 编写部署文档                                                       │
│  └── [ ] 基础设施验收                                                       │
│                                                                             │
│  Week 2: 数据层 P0 Skills                                                   │
│  ─────────────────────                                                      │
│  Day 1-3: P0-01 openbb-fetch                                                │
│  ├── [ ] schemas/openbb-fetch.input.schema.json                            │
│  ├── [ ] schemas/openbb-fetch.output.schema.json                           │
│  ├── [ ] src/skills/data/openbb_fetch.py                                    │
│  ├── [ ] tests/test_openbb_fetch.py                                         │
│  └── [ ] docs/skills/openbb-fetch.md                                        │
│                                                                             │
│  Day 4-5: P0-02 data-validator                                              │
│  ├── [ ] schemas/data-validator.*.schema.json                              │
│  ├── [ ] src/skills/data/data_validator.py                                  │
│  ├── [ ] tests/test_data_validator.py                                       │
│  └── [ ] 数据层集成测试                                                     │
│                                                                             │
│  交付物:                                                                    │
│  ├── ✓ 基础设施可一键启动                                                   │
│  ├── ✓ 2 个 P0 数据 Skills 可用                                             │
│  └── ✓ 数据获取→校验 流程打通                                               │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 3-4: 研发层 (P0)                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 3: P0-03 kronos-predict                                               │
│  ───────────────────────────────                                            │
│  Day 1-2:                                                                   │
│  ├── [ ] 下载 Kronos 模型 (Kronos-small)                                    │
│  ├── [ ] 本地验证模型可用性                                                 │
│  └── [ ] 设计预测结果输出格式                                               │
│                                                                             │
│  Day 3-5:                                                                   │
│  ├── [ ] schemas/kronos-predict.input.schema.json                          │
│  ├── [ ] schemas/kronos-predict.output.schema.json                         │
│  ├── [ ] src/skills/research/kronos_predict.py                              │
│  ├── [ ] tests/test_kronos_predict.py                                       │
│  └── [ ] 置信度计算逻辑                                                     │
│                                                                             │
│  Week 4: P0-04 signal-generator                                             │
│  ─────────────────────────────────                                          │
│  Day 1-3:                                                                   │
│  ├── [ ] 设计信号生成规则 (趋势/反转/突破)                                  │
│  ├── [ ] schemas/signal-generator.*.schema.json                            │
│  ├── [ ] src/skills/research/signal_generator.py                            │
│  └── [ ] tests/test_signal_generator.py                                     │
│                                                                             │
│  Day 4-5:                                                                   │
│  ├── [ ] 研发层集成测试                                                     │
│  ├── [ ] 端到端测试: 数据→预测→信号                                         │
│  └── [ ] 性能基准测试                                                       │
│                                                                             │
│  交付物:                                                                    │
│  ├── ✓ 2 个 P0 研发 Skills 可用                                             │
│  ├── ✓ 数据→预测→信号 流程打通                                              │
│  └── ✓ 预测准确率基准                                                       │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 5-6: 风控层 + 执行层 (P0)                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 5: 风控层 P0 Skills                                                   │
│  ─────────────────────                                                      │
│  Day 1-2: P0-07 risk-guard                                                  │
│  ├── [ ] 设计 Gate 规则格式                                                 │
│  ├── [ ] schemas/risk-guard.*.schema.json                                   │
│  ├── [ ] src/skills/risk/risk_guard.py                                      │
│  ├── [ ] 实现 Gate 决策引擎                                                 │
│  └── [ ] tests/test_risk_guard.py                                           │
│                                                                             │
│  Day 3-4: P0-08 drawdown-limiter                                            │
│  ├── [ ] schemas/drawdown-limiter.*.schema.json                            │
│  ├── [ ] src/skills/risk/drawdown_limiter.py                                │
│  ├── [ ] 实现回撤计算逻辑                                                   │
│  └── [ ] tests/test_drawdown_limiter.py                                     │
│                                                                             │
│  Day 5:                                                                     │
│  ├── [ ] 风控层集成测试                                                     │
│  └── [ ] Gate 拒绝场景测试                                                  │
│                                                                             │
│  Week 6: 执行层 P0 Skills                                                   │
│  ─────────────────────                                                      │
│  Day 1-2: P0-06 order-router (简化版)                                       │
│  ├── [ ] schemas/order-router.*.schema.json                                │
│  ├── [ ] src/skills/execution/order_router.py                               │
│  └── [ ] tests/test_order_router.py                                         │
│                                                                             │
│  Day 3-5: P0-05 veighna-execute                                             │
│  ├── [ ] 安装 VeighNa + CTP Gateway                                         │
│  ├── [ ] 配置 SimNow 仿真账户                                               │
│  ├── [ ] schemas/veighna-execute.*.schema.json                             │
│  ├── [ ] src/skills/execution/veighna_execute.py                            │
│  ├── [ ] tests/test_veighna_execute.py                                      │
│  └── [ ] 仿真环境测试                                                       │
│                                                                             │
│  交付物:                                                                    │
│  ├── ✓ 4 个 P0 风控+执行 Skills 可用                                        │
│  ├── ✓ Gate 体系运行                                                        │
│  ├── ✓ 仿真交易验证                                                         │
│  └── ✓ 风控拦截测试通过                                                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 7: 治理层 (P0) + 集成测试                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Day 1-2: P0-09 audit-logger                                                │
│  ├── [ ] schemas/audit-logger.*.schema.json                                 │
│  ├── [ ] src/skills/governance/audit_logger.py                              │
│  ├── [ ] 设计审计日志格式                                                   │
│  └── [ ] tests/test_audit_logger.py                                         │
│                                                                             │
│  Day 3-4: P0-10 evidence-manager                                            │
│  ├── [ ] schemas/evidence-manager.*.schema.json                            │
│  ├── [ ] src/skills/governance/evidence_manager.py                          │
│  ├── [ ] 实现证据链生成逻辑                                                 │
│  └── [ ] tests/test_evidence_manager.py                                     │
│                                                                             │
│  Day 5: 端到端集成测试                                                      │
│  ├── [ ] 完整流程测试: 数据→预测→信号→风控→执行→审计                        │
│  ├── [ ] Gate 拦截测试                                                      │
│  ├── [ ] 证据链完整性测试                                                   │
│  └── [ ] 性能测试                                                           │
│                                                                             │
│  交付物:                                                                    │
│  ├── ✓ 10 个 P0 Skills 全部可用                                             │
│  ├── ✓ 完整流程可运行                                                       │
│  ├── ✓ Gate 体系完整                                                        │
│  └── ✓ 证据链可追溯                                                         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Week 8: P1 功能 + MVP 验收                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Day 1-2: P1-01 data-cleaner + P1-02 data-syncer                            │
│  ├── [ ] schemas/data-cleaner.*.schema.json                                │
│  ├── [ ] src/skills/data/data_cleaner.py                                    │
│  ├── [ ] schemas/data-syncer.*.schema.json                                  │
│  └── [ ] src/skills/data/data_syncer.py                                     │
│                                                                             │
│  Day 3: P1-03 backtest-engine + P1-04 evaluator-metrics                     │
│  ├── [ ] schemas/backtest-engine.*.schema.json                             │
│  ├── [ ] src/skills/research/backtest_engine.py                             │
│  ├── [ ] schemas/evaluator-metrics.*.schema.json                           │
│  └── [ ] src/skills/research/evaluator_metrics.py                           │
│                                                                             │
│  Day 4: P1-05~08 风控+治理层                                                │
│  ├── [ ] var-calculator (简化版)                                            │
│  ├── [ ] exposure-tracker                                                   │
│  ├── [ ] replay-engine                                                      │
│  └── [ ] alert-router                                                       │
│                                                                             │
│  Day 5: MVP 验收                                                            │
│  ├── [ ] 功能验收 (18 Skills)                                               │
│  ├── [ ] 性能验收 (延迟/吞吐)                                               │
│  ├── [ ] 稳定性验收 (故障恢复)                                              │
│  ├── [ ] 合规验收 (审计/证据)                                               │
│  └── [ ] 文档验收                                                           │
│                                                                             │
│  交付物:                                                                    │
│  ├── ✓ 18 个 MVP Skills 全部可用                                            │
│  ├── ✓ 完整量化流程可运行                                                   │
│  ├── ✓ 仿真交易通过                                                         │
│  ├── ✓ L3 Audit Pack 可生成                                                 │
│  └── ✓ 用户手册 v1.0                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. 每个 Skill 的详细规格

### 5.1 P0 Skills 规格

#### P0-01: openbb-fetch

```yaml
skill_id: openbb-fetch
priority: P0
layer: data

purpose: 从 OpenBB 获取金融数据

input_contract:
  required:
    - data_type: string  # equity.price.historical, economy.indicators
    - symbols: array<string>  # ["AAPL", "MSFT"]
  optional:
    - provider: string  # yahoo, alpha_vantage (default: yahoo)
    - start_date: date
    - end_date: date
  controls:
    - max_symbols: 100
    - timeout_ms: 30000
    - rate_limit: "10/min"

output_contract:
  status: enum [completed, failed, rate_limited, partial]
  data: array<object>
  provenance:
    provider: string
    fetched_at: datetime
    source_url: string
  evidence_ref: uri
  metrics:
    rows_fetched: integer
    latency_ms: integer

dependencies:
  - OpenBB (AGPLv3 - 需隔离)

error_codes:
  - OPENBB_RATE_LIMITED
  - OPENBB_PROVIDER_UNAVAILABLE
  - OPENBB_INVALID_SYMBOL

implementation_notes: |
  1. 作为独立微服务部署，隔离 AGPL 污染
  2. 内置重试机制 (3次)
  3. 支持多数据源切换
```

#### P0-02: data-validator

```yaml
skill_id: data-validator
priority: P0
layer: data

purpose: 校验数据质量，防止垃圾进垃圾出

input_contract:
  required:
    - df: DataFrame  # 输入数据
    - schema: object  # 校验规则
  optional:
    - strict_mode: boolean  # default: false
  controls:
    - max_rows: 100000

output_contract:
  status: enum [valid, invalid, partial]
  validation_result:
    total_rows: integer
    valid_rows: integer
    invalid_rows: integer
    issues: array<object>
  cleaned_df: DataFrame  # 可选，清洗后的数据
  evidence_ref: uri

validation_rules:
  - MISSING_VALUE_CHECK: 检查缺失值比例
  - OUTLIER_CHECK: 检查异常值 (3σ)
  - CONTINUITY_CHECK: 检查时间序列连续性
  - SCHEMA_CHECK: 检查字段类型和格式

error_codes:
  - DATA_VALIDATION_FAILED
  - DATA_TOO_MANY_MISSING
  - DATA_CONTINUITY_BROKEN
```

#### P0-03: kronos-predict

```yaml
skill_id: kronos-predict
priority: P0
layer: research

purpose: 使用 Kronos 模型预测未来K线

input_contract:
  required:
    - symbol: string
    - ohlcv_data: DataFrame  # 历史数据
  optional:
    - lookback: integer  # default: 400, max: 512
    - pred_len: integer  # default: 120, max: 240
    - interval: enum [1min, 5min, 15min, 1h, 1d]  # default: 5min
    - model_version: enum [kronos-mini, kronos-small, kronos-base]
  controls:
    - max_timeout_ms: 60000
    - confidence_threshold: 0.5

output_contract:
  status: enum [completed, low_confidence, context_overflow, failed]
  predictions: array<object>  # [{timestamp, open, high, low, close, volume}]
  confidence_metrics:
    mean: number
    std: number
    percentile_25: number
    percentile_75: number
  model_info:
    version: string
    commit_sha: string
  input_hash: string  # SHA256
  evidence_ref: uri
  gate_decision:
    verdict: enum [ALLOW, DENY, WARN]
    checks: object

dependencies:
  - Kronos (MIT)
  - PyTorch

error_codes:
  - KRONOS_CONTEXT_OVERFLOW
  - KRONOS_LOW_CONFIDENCE
  - KRONOS_TOKENIZER_MISMATCH
  - KRONOS_PREDICTION_TIMEOUT
```

#### P0-04: signal-generator

```yaml
skill_id: signal-generator
priority: P0
layer: research

purpose: 根据预测结果生成交易信号

input_contract:
  required:
    - predictions: array<object>  # 来自 kronos-predict
    - confidence: object  # 置信度指标
  optional:
    - strategy: enum [trend, reversal, breakout]  # default: trend
    - confidence_threshold: number  # default: 0.6
    - risk_reward_ratio: number  # default: 2.0
  controls:
    - max_signals_per_run: 10

output_contract:
  status: enum [generated, no_signal, low_confidence]
  signals: array<object>
    - symbol: string
    - action: enum [BUY, SELL, HOLD]
    - quantity: integer
    - target_price: number
    - stop_loss: number
    - confidence: number
    - reasoning: string
  evidence_ref: uri

signal_rules:
  trend:
    - 预测上涨 > 2% 且 置信度 > 0.6 → BUY
    - 预测下跌 > 2% 且 置信度 > 0.6 → SELL
  reversal:
    - 连续上涨后预测下跌 → SELL
    - 连续下跌后预测上涨 → BUY
  breakout:
    - 预测突破阻力位 → BUY
    - 预测跌破支撑位 → SELL

error_codes:
  - SIGNAL_NO_PREDICTION
  - SIGNAL_LOW_CONFIDENCE
  - SIGNAL_CONFLICTING
```

#### P0-05: veighna-execute

```yaml
skill_id: veighna-execute
priority: P0
layer: execution

purpose: 通过 VeighNa 执行交易订单

input_contract:
  required:
    - action: enum [BUY, SELL]
    - symbol: string
    - quantity: integer
    - order_type: enum [MARKET, LIMIT]
  optional:
    - price: number  # LIMIT 订单必填
    - gateway: string  # default: CTP
  controls:
    - max_order_value: 100000
    - timeout_ms: 10000

output_contract:
  status: enum [filled, partial, pending, rejected, cancelled]
  order:
    order_id: string
    symbol: string
    action: string
    quantity: integer
    filled_quantity: integer
    price: number
    avg_fill_price: number
  gate_decision:
    verdict: enum [ALLOW, DENY, WARN]
    violations: array<object>
    checks_passed: array<string>
  evidence_ref: uri
  timestamp: datetime

dependencies:
  - VeighNa (MIT)
  - CTP Gateway / SimNow

error_codes:
  - VEIGHNA_ORDER_REJECTED
  - VEIGHNA_CONNECTION_LOST
  - VEIGHNA_TIMEOUT
  - VEIGHNA_INSUFFICIENT_FUNDS
```

#### P0-06: order-router

```yaml
skill_id: order-router
priority: P0
layer: execution

purpose: 智能订单路由 (MVP 简化版)

input_contract:
  required:
    - signal: object  # 来自 signal-generator
  optional:
    - routing_strategy: enum [simple, smart]  # default: simple
    - split_enabled: boolean  # default: false

output_contract:
  status: enum [routed, split, rejected]
  orders: array<object>  # 路由后的订单列表
  evidence_ref: uri

routing_logic:
  simple:
    - 直接转发信号为单个订单
  smart:  # V2
    - 根据流动性拆分
    - 选择最优执行时机

error_codes:
  - ROUTER_INVALID_SIGNAL
  - ROUTER_LIQUIDITY_INSUFFICIENT
```

#### P0-07: risk-guard

```yaml
skill_id: risk-guard
priority: P0
layer: risk

purpose: 实时风控检查 (Gate 引擎)

input_contract:
  required:
    - trade_request: object
    - portfolio_state: object
  optional:
    - risk_rules: array<string>  # 启用的规则
  controls:
    - check_timeout_ms: 1000

output_contract:
  gate_decision:
    verdict: enum [ALLOW, DENY, WARN]
    violations: array<object>
      - rule_id: string
      - severity: enum [critical, warning]
      - message: string
      - actual_value: number
      - threshold: number
    checks_passed: array<string>
  evidence_ref: uri

gate_rules:
  - POSITION_LIMIT: 单标的仓位 <= 10%
  - DAILY_LOSS_LIMIT: 单日亏损 <= 5%
  - DRAWDOWN_LIMIT: 最大回撤 <= 10%
  - CONCENTRATION_LIMIT: 单行业 <= 30%

error_codes:
  - GATE_POSITION_BREACH
  - GATE_LOSS_BREACH
  - GATE_DRAWDOWN_BREACH
```

#### P0-08: drawdown-limiter

```yaml
skill_id: drawdown-limiter
priority: P0
layer: risk

purpose: 回撤控制，防止爆仓

input_contract:
  required:
    - current_pnl: number
    - peak_pnl: number
  optional:
    - threshold: number  # default: 0.1 (10%)
    - cooldown_minutes: integer  # default: 60

output_contract:
  status: enum [ok, warning, breach]
  current_drawdown: number
  action: enum [continue, pause, halt]
  cooldown_until: datetime  # 如果触发暂停
  evidence_ref: uri

logic:
  - drawdown < 5%: continue
  - 5% <= drawdown < 10%: warning
  - drawdown >= 10%: halt + cooldown

error_codes:
  - DRAWDOWN_BREACH
  - DRAWDOWN_COOLDOWN
```

#### P0-09: audit-logger

```yaml
skill_id: audit-logger
priority: P0
layer: governance

purpose: 记录所有操作的审计日志

input_contract:
  required:
    - event_type: enum [skill_run, gate_decision, trade_execution, alert]
    - event_data: object
  optional:
    - correlation_id: string
    - user_id: string

output_contract:
  audit_record:
    record_id: string
    event_type: string
    event_data: object
    timestamp: datetime
    correlation_id: string
    trace_context: object
  storage_ref: uri

audit_events:
  - SKILL_RUN_START
  - SKILL_RUN_COMPLETE
  - SKILL_RUN_FAILED
  - GATE_DECISION
  - TRADE_EXECUTION
  - ALERT_TRIGGERED

retention:
  hot: 7 days  # TDengine
  warm: 90 days  # TDengine
  cold: 7 years  # MinIO (合规要求)
```

#### P0-10: evidence-manager

```yaml
skill_id: evidence-manager
priority: P0
layer: governance

purpose: 管理证据链，支持审计和复现

input_contract:
  required:
    - run_id: string
    - skill_outputs: array<object>
  optional:
    - include_artifacts: boolean  # default: true

output_contract:
  evidence_pack:
    pack_id: string
    run_id: string
    chain: array<object>
      - step: integer
      - skill_id: string
      - evidence_ref: uri
      - hash: string
      - timestamp: datetime
    integrity_check:
      hash_algorithm: string
      root_hash: string
      verified: boolean
  storage_ref: uri

evidence_types:
  - input_snapshot: 输入数据快照
  - output_snapshot: 输出数据快照
  - model_checkpoint: 模型检查点
  - gate_decision: Gate 决策记录
  - execution_log: 执行日志

features:
  - 证据链不可篡改 (SHA256)
  - 支持 L3 Audit Pack 生成
  - 支持 Replay 引用
```

### 5.2 P1 Skills 规格 (简化版)

```yaml
# P1 Skills - 简化规格

P1-01 data-cleaner:
  purpose: 数据清洗 (缺失值填充、异常值处理)
  input: raw_df, cleaning_rules
  output: cleaned_df, cleaning_report

P1-02 data-syncer:
  purpose: 增量数据同步
  input: last_timestamp, symbols
  output: delta_df, sync_status

P1-03 backtest-engine:
  purpose: 策略回测
  input: strategy, data, config
  output: backtest_result, trades_log

P1-04 evaluator-metrics:
  purpose: 策略评估指标
  input: backtest_result
  output: metrics_report (Sharpe, MaxDD, WinRate, etc.)

P1-05 var-calculator:
  purpose: VaR/CVaR 计算
  input: portfolio, confidence_level
  output: var_report

P1-06 exposure-tracker:
  purpose: 敞口追踪
  input: positions, market_data
  output: exposure_report

P1-07 replay-engine:
  purpose: 执行复现
  input: run_id, replay_config
  output: replay_result

P1-08 alert-router:
  purpose: 告警路由
  input: alert_event, rules
  output: notifications (slack, email, sms)
```

---

## 6. 验收标准

### 6.1 功能验收

```yaml
acceptance_criteria:
  data_layer:
    - [ ] openbb-fetch 能获取 A 股实时行情
    - [ ] data-validator 能检测缺失值和异常值
    - [ ] 数据获取→校验 流程可运行

  research_layer:
    - [ ] kronos-predict 能生成 120 步预测
    - [ ] signal-generator 能输出 BUY/SELL 信号
    - [ ] 预测→信号 流程可运行

  risk_layer:
    - [ ] risk-guard 能拦截超限订单
    - [ ] drawdown-limiter 能触发暂停
    - [ ] Gate 决策可追溯

  execution_layer:
    - [ ] order-router 能转发订单
    - [ ] veighna-execute 能在仿真环境成交
    - [ ] 仿真交易完整流程可运行

  governance_layer:
    - [ ] audit-logger 能记录所有事件
    - [ ] evidence-manager 能生成证据链
    - [ ] L3 Audit Pack 可生成

  end_to_end:
    - [ ] 数据→预测→信号→风控→执行→审计 完整流程
    - [ ] Gate 拦截场景测试通过
    - [ ] 证据链完整性验证通过
```

### 6.2 性能验收

```yaml
performance_criteria:
  latency:
    - data_fetch: < 5s (1000 rows)
    - prediction: < 10s (512 context)
    - gate_check: < 100ms
    - order_execution: < 1s

  throughput:
    - signals_per_hour: > 100
    - concurrent_strategies: > 3

  reliability:
    - uptime: > 99% (交易时段)
    - recovery_time: < 5min
```

### 6.3 合规验收

```yaml
compliance_criteria:
  audit:
    - [ ] 所有交易有审计日志
    - [ ] 审计日志不可篡改
    - [ ] 审计日志保留 7 年

  evidence:
    - [ ] 每笔交易有证据链
    - [ ] 证据链 SHA256 校验通过
    - [ ] 支持 Replay 复现

  risk:
    - [ ] Gate 规则可配置
    - [ ] Gate 决策有记录
    - [ ] 违规事件有告警
```

---

## 7. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| OpenBB AGPL 污染 | 高 | 高 | 独立微服务隔离 |
| Kronos 模型效果不佳 | 中 | 中 | 置信度阈值 + 人工复核 |
| VeighNa 接口变化 | 低 | 高 | 版本锁定 + 抽象层 |
| 8周时间紧张 | 高 | 中 | 优先 P0，P1 可延后 |
| 仿真环境不稳定 | 中 | 中 | 多准备几个 SimNow 账户 |

---

## 8. 资源需求

### 8.1 人力

```
┌─────────────────────────────────────────┐
│  角色           │  投入  │  周期       │
├─────────────────────────────────────────┤
│  全栈开发       │  1人   │  8周全勤    │
│  或             │        │             │
│  后端开发       │  1人   │  8周全勤    │
│  + AI/ML 工程师 │  1人   │  Week 3-4   │
└─────────────────────────────────────────┘
```

### 8.2 硬件

```yaml
minimum_requirements:
  cpu: 8 cores
  memory: 32 GB
  storage: 500 GB SSD
  gpu: NVIDIA RTX 3060+ (12GB VRAM)  # 用于 Kronos 推理

recommended:
  cpu: 16 cores
  memory: 64 GB
  storage: 1 TB NVMe
  gpu: NVIDIA RTX 4070+ (16GB VRAM)
```

### 8.3 软件/服务

```yaml
software:
  - Docker Desktop
  - Python 3.11+
  - CUDA 12.0+

accounts:
  - SimNow 仿真账户 (免费)
  - OpenBB (免费/开源)
  - 数据源 (迅投研/RQData 等，可选)
```

---

## 9. 下一步行动

1. **确认**: 是否接受 8 周时间线？
2. **启动**: Week 1 基础设施搭建
3. **并行**: 开始学习 Kronos 和 VeighNa 文档
4. **准备**: 申请 SimNow 仿真账户

---

*MVP 计划完成 - 准备启动实施*
