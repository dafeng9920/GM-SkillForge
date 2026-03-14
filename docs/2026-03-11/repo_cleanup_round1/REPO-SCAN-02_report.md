# REPO-SCAN-02: 非 skill 业务剥离清单

> **扫描任务**: 识别系统中的"非 skill 业务"，形成剥离候选清单
> **执行时间**: 2026-03-11
> **扫描范围**: adapters/quant/, demo_trading_data/, export-seo/, pseo/, 根目录 HTML/JSON 文件
> **硬约束**: 不修改代码，不删除文件，不重命名目录，只做边界识别与分类

---

## 执行摘要

| 扫描范围 | 发现非 skill 业务 | 推荐独立仓迁移 | 推荐归档 |
|----------|-------------------|----------------|----------|
| adapters/quant/ | 1 个完整交易系统 | 1 | - |
| demo_trading_data/ | 交易运行时数据 | 1 (随 quant) | - |
| export-seo/ | 独立 SEO 产品 | 1 | - |
| pseo/ | 独立 SEO 产品 | 1 (与 export-seo 合并) | - |
| 根目录 HTML 文件 | SEO 前端页面 | 8 (随 pseo) | 10+ (audit reports) |
| 量化支持脚本 | 量化基础设施工具 | 4 (随 quant) | - |

**总计**: 8 个主要非 skill 业务模块

---

## 剥离候选清单

### 1. quant-trading-system (量化交易系统)

| 字段 | 值 |
|------|-----|
| **path** | `adapters/quant/` |
| **business_type** | A股量化交易系统（独立业务线） |
| **in_scope_for_skillforge** | `no` |
| **recommended_bucket** | `独立仓迁移` |
| **reason** | 完整的A股量化交易系统，包含数据获取、策略计算、模拟交易、风险管理、回测引擎、Web监控等独立功能栈。与 SkillForge 的 skill 编排/执行主线无强耦合，可独立为 `genesismind-bot/a-share-quant-trader` 或类似仓。 |

**子组件清单**:
```
adapters/quant/
├── strategies/          # 策略模块（11个策略文件）
│   ├── demo_a_share_strategy.py
│   ├── demo_trap_detector.py
│   ├── enhanced_multi_factor_strategy.py
│   ├── etf_rotation.py
│   ├── live_a_share_trader.py
│   ├── multi_factor_momentum.py
│   ├── signal_generator.py
│   ├── stock_selector.py
│   ├── trap_detector.py
│   └── tests/
├── trading/             # 交易系统（12个交易模块）
│   ├── demo_trading_system.py
│   ├── fast_data_fetcher.py
│   ├── live_trading_system.py
│   ├── quant_trading_system.py
│   ├── quant_trading_system_enhanced.py
│   ├── quant_trading_system_fast.py
│   ├── run_enhanced_relaxed.py
│   ├── simulated_broker.py
│   ├── start_trading.py
│   ├── trade_journal.py
│   ├── trading_dashboard.py
│   └── web_monitor.py
├── data/                # 数据获取（5个数据源适配器）
│   ├── china_stock_fetcher.py
│   ├── data_validator.py
│   ├── institution_data_fetcher.py
│   ├── kronos_fetch.py
│   └── openbb_fetch.py
├── backtest/            # 回测引擎（21个回测模块）
│   ├── data.py
│   ├── debug_*.py (8个)
│   ├── engine.py
│   ├── events.py
│   ├── final_test.py
│   ├── full_cycle_test.py
│   ├── metrics.py
│   ├── parameter_optimization.py
│   ├── run_backtest.py
│   ├── simple_test.py
│   ├── super_debug.py
│   ├── test_*.py (4个)
│   └── validation.py
├── phase4/              # Phase4 决策模块
│   ├── closed_loop/
│   ├── confirmation/
│   ├── decision/
│   ├── engine.py
│   ├── perception/
│   └── validation.py
├── tests/
├── contracts.py
├── README.md
├── README_TRADING_SYSTEM.md
├── requirements.txt
└── setup_trading_system.py
```

---

### 2. quant-demo-data (交易演示数据)

| 字段 | 值 |
|------|-----|
| **path** | `demo_trading_data/`, `trading_data/` |
| **business_type** | 量化交易演示/历史数据 |
| **in_scope_for_skillforge** | `no` |
| **recommended_bucket** | `独立仓迁移`（随 quant-trading-system） |
| **reason** | A股交易系统的运行时数据目录（snapshots, trades, reports），属于量化交易系统的一部分，应随 `adapters/quant/` 一起迁移。 |

**目录结构**:
```
demo_trading_data/
├── reports/
├── snapshots/
└── trades/

trading_data/
├── reports/
├── snapshots/
└── trades/
```

---

### 3. pseo-matrix (AI SEO 检查器)

| 字段 | 值 |
|------|-----|
| **path** | `pseo/`, `export-seo/` |
| **business_type** | AI搜索可见性检查工具（独立产品） |
| **in_scope_for_skillforge** | `no` |
| **recommended_bucket** | `独立仓迁移` |
| **reason** | 已有独立 README 声明为 "standalone Fishing Net module"，是 SEO 审计产品的独立前端 + scanner logic，含 Cloudflare Pages Functions。已有独立 `.git` 目录，设计为独立部署。建议独立为 `genesismind-bot/pseo-matrix` 或 `genesismind-bot/ai-seo-checker`。 |

**目录结构**:
```
pseo/
├── .git/
├── .gitignore
├── functions/          # Cloudflare Pages Functions
├── index.html
├── index_zh.html
├── nextjs-ai-seo-checker.html
├── package.json
├── README.md
├── scanner/            # Scanner logic
├── shopify-ai-seo-checker.html
├── svelte-ai-seo-checker.html
├── vite-ai-seo-checker.html
└── wordpress-ai-seo-checker.html

export-seo/             # 与 pseo/ 内容高度相似，建议合并
├── .git/
├── .gitignore
├── functions/
├── index.html
├── index_zh.html
├── nextjs-ai-seo-checker.html
├── package.json
├── README.md
├── scanner/
├── shopify-ai-seo-checker.html
├── svelte-ai-seo-checker.html
├── vite-ai-seo-checker.html
└── wordpress-ai-seo-checker.html
```

---

### 4. pseo-root-htmls (根目录 SEO HTML 文件)

| 字段 | 值 |
|------|-----|
| **path** | 根目录 `*.html` (index.html, nextjs-ai-seo-checker.html 等 8 个文件) |
| **business_type** | SEO 检查器前端页面 |
| **in_scope_for_skillforge** | `no` |
| **recommended_bucket** | `独立仓迁移`（随 pseo-matrix） |
| **reason** | 这些 HTML 文件是 pseo-matrix 产品的不同框架变体页面，与 SkillForge skill 主线无关。应随 `pseo/` 一起迁移。 |

**文件清单**:
```
根目录 HTML 文件 (SEO 相关):
├── index.html                           # SEO checker 主页
├── nextjs-ai-seo-checker.html           # Next.js 版本
├── shopify-ai-seo-checker.html          # Shopify 版本
├── svelte-ai-seo-checker.html           # Svelte 版本
├── vite-ai-seo-checker.html             # Vite 版本
└── wordpress-ai-seo-checker.html        # WordPress 版本
```

---

### 5. audit-reports (SEO 审计报告)

| 字段 | 值 |
|------|-----|
| **path** | 根目录 `Audit_Report_*.html` (10+ 个文件) |
| **business_type** | SEO 审计报告（历史产出物） |
| **in_scope_for_skillforge** | `no` |
| **recommended_bucket** | `归档` |
| **reason** | 特定客户的 SEO 审计报告输出，属于一次性交付产物。建议移至 `audit/` 或删除。若需保留，应归档至独立审计报告存储，不应占用主仓根目录。 |

**文件清单**:
```
根目录 Audit Report 文件:
├── Audit_Report_Final.html
├── Audit_Report_genesismind_ai.html
├── audit-ai-dev-tools.html
├── audit-cybersecurity-zero-trust.html
├── audit-devops-cicd-observability.html
├── audit-ecommerce-platforms.html
├── audit-fintech-legal.html
├── audit-gaming-infrastructure.html
├── audit-healthtech-telemedicine-ai.html
├── audit-martech-automation-personalization.html
└── audit-saas-security.html
```

---

### 6. quant-root-scripts (根目录量化脚本)

| 字段 | 值 |
|------|-----|
| **path** | 根目录 `check_akshare_funcs.py`, `check_institution.py` |
| **business_type** | 量化交易数据查询工具 |
| **in_scope_for_skillforge** | `no` |
| **recommended_bucket** | `独立仓迁移`（随 quant-trading-system） |
| **reason** | 这两个脚本是量化交易系统的辅助工具，用于检查 AKShare 函数和查询机构持仓数据。应随 `adapters/quant/` 一起迁移。 |

**文件清单**:
```
根目录量化脚本:
├── check_akshare_funcs.py    # AKShare 函数查找工具
└── check_institution.py      # A股机构持仓数据查询工具
```

---

### 7. quant-infra-scripts (量化基础设施脚本)

| 字段 | 值 |
|------|-----|
| **path** | `scripts/check_quant_stack.py`, `scripts/start_quant_stack.*` |
| **business_type** | 量化系统基础设施运维脚本 |
| **in_scope_for_skillforge** | `no` |
| **recommended_bucket** | `独立仓迁移`（随 quant-trading-system） |
| **reason** | 专门用于量化系统基础设施（PostgreSQL, Redis, TDengine）的健康检查和启动脚本，不属于 SkillForge 主线。 |

**文件清单**:
```
scripts/ 中的量化脚本:
├── check_quant_stack.py      # 量化基础设施健康检查
└── start_quant_stack.*       # 量化基础设施启动脚本 (sh + ps1)
```

---

### 8. quant-infra-docker (量化 Docker 配置)

| 字段 | 值 |
|------|-----|
| **path** | `docker/` |
| **business_type** | 量化交易系统 Docker 编排 |
| **in_scope_for_skillforge** | `no` |
| **recommended_bucket** | `独立仓迁移`（随 quant-trading-system） |
| **reason** | Docker Compose 配置专门为量化系统设计（quant-stack.yml，含 PostgreSQL, Redis, TDengine, Prometheus, Grafana），应随量化系统一起迁移。 |

**目录结构**:
```
docker/
├── data/              # PostgreSQL data
├── grafana/           # Grafana dashboards
├── prometheus/        # Prometheus configs
├── quant-stack.yml    # 量化系统 Docker Compose
├── redis/             # Redis data
└── sql/               # SQL schemas
```

---

## 边界保留项（不剥离）

以下目录经分析 **保留在 SkillForge 主线**：

| path | reason |
|------|--------|
| `core/` | 核心运行时接口（contract_compiler, dsl_validator, runtime_interface 等），属于 SkillForge 基础设施 |
| `tools/` | 通用工具（canonicalize, hash_calc 等），支持 SkillForge 全局功能 |
| `contracts/` | SkillForge 的 DSL 和 intent 定义，属于主线 |
| `dropzone/` | 任务执行暂存区，属于主线执行流程 |
| `permits/` | Permit 系统存储，属于主线治理 |
| `artifacts/` | 任务产出物存储，属于主线证据链 |
| `audit/`, `audit_pack/` | 主线审计系统（compliance reviews, audit packs） |
| `workflows/` | 工作流编排定义 |
| `schemas/` | Schema 定义，属于主线 |
| `skillforge/` | 主线 Skill 核心代码库 |
| `templates/` | 主线模板（audit 报告模板等） |
| `requirements/` | 主线依赖定义 |
| `db/` | 主线数据库 (skillforge.sqlite) |

---

## 剥离建议汇总

### 推荐独立仓迁移（2个仓）

#### 1. `genesismind-bot/a-share-quant-trader`

**包含内容**:
```
adapters/quant/
demo_trading_data/
trading_data/
docker/
check_akshare_funcs.py
check_institution.py
scripts/check_quant_stack.py
scripts/start_quant_stack.*
```

**迁移理由**:
- 完整的 A股量化交易系统，有独立的 README 和文档
- 包含完整的策略、交易、回测、数据获取、监控功能栈
- 有独立的 Docker 编排配置
- 与 SkillForge 主线无强耦合

---

#### 2. `genesismind-bot/pseo-matrix` 或 `genesismind-bot/ai-seo-checker`

**包含内容**:
```
pseo/
export-seo/
根目录 SEO HTML 文件:
  - index.html
  - nextjs-ai-seo-checker.html
  - shopify-ai-seo-checker.html
  - svelte-ai-seo-checker.html
  - vite-ai-seo-checker.html
  - wordpress-ai-seo-checker.html
```

**迁移理由**:
- 已有独立 README 声明为 standalone module
- 有独立的 `.git` 目录，设计为独立部署
- 是完整的 SEO 审计产品（前端 + scanner + Cloudflare Functions）
- `pseo/` 和 `export-seo/` 内容高度相似，建议合并后迁移

---

### 推荐归档/清理

| path | 处理建议 |
|------|----------|
| 根目录 `Audit_Report_*.html` (10+ 个文件) | 移至 `audit/reports/` 或删除 |

---

## 统计摘要

| 分类 | 数量 | 详情 |
|------|------|------|
| **独立仓迁移候选** | 2 个业务线 | quant-trading, pseo-matrix |
| **归档候选** | 1 类文件 | audit reports (10+ HTML) |
| **保留主线** | ~15 个目录/文件组 | core, tools, contracts, skillforge 等 |
| **涉及文件总数** | ~100+ | 包括子目录 |

---

## 依赖关系分析

### quant-trading-system 外部依赖
- `akshare` - A股数据源
- `pandas`, `numpy` - 数据处理
- `streamlit`, `plotly` - Web 界面
- PostgreSQL, Redis, TDengine - 基础设施（通过 docker/）

### pseo-matrix 外部依赖
- Cloudflare Pages - 部署平台
- Cloudflare Functions - Serverless API
- 无强后端依赖

---

## 风险评估

| 剥离项 | 风险等级 | 风险描述 |
|--------|----------|----------|
| quant-trading-system | 低 | 与 SkillForge 主线耦合度低，README 明确为独立 adapter |
| pseo-matrix | 低 | 已设计为独立部署，有独立 .git 目录 |
| audit reports | 极低 | 静态产出物，无运行时依赖 |

---

## 下一步行动建议

1. **REPO-SCAN-03**: 验证 `pseo/` 与 `export-seo/` 的内容差异，确定合并策略
2. **REVIEW**: 审查本报告，确认剥离边界
3. **COMPLIANCE**: 确认剥离操作不影响 Antigravity-1 闭链要求
4. **执行**: 按独立仓迁移计划执行 Git 操作

---

**报告生成时间**: 2026-03-11
**扫描器**: REPO-SCAN-02
**状态**: 待 REVIEW
