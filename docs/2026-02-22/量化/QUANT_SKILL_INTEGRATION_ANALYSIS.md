# 量化交易生态与 SkillForge 集成分析

> 文档版本: v1.0
> 创建日期: 2026-02-22
> 状态: 分析草案

---

## 1. 执行摘要

本文档分析三个开源金融项目与 GM-SkillForge 系统的集成潜力，构建一个**可审计、可追溯、可复现**的 AI 驱动量化交易生态。

**核心结论**: 三者与 SkillForge 高度互补，可形成完整的"数据 → 预测 → 执行 → 审计"闭环。

---

## 2. 三大仓库概览

### 2.1 对比矩阵

| 维度 | Kronos | OpenBB | VeighNa |
|------|--------|--------|---------|
| **定位** | 预测模型 | 数据平台 | 交易框架 |
| **核心能力** | 金融K线预测 | 多源数据聚合 | 策略执行与风控 |
| **许可证** | MIT | AGPLv3 | MIT |
| **商业使用** | ✅ 完全自由 | ⚠️ 需开源修改 | ✅ 完全自由 |
| **学术背景** | AAAI 2026 | - | 十周年 4.0 |
| **AI 能力** | 原生 AI 预测 | AI Agent 集成 | vnpy.alpha ML模块 |

### 2.2 各仓库详细说明

#### 2.2.1 Kronos

**GitHub**: https://github.com/shiyu-coder/Kronos

- **描述**: 第一个专门针对金融K线数据的开源基础模型
- **训练数据**: 45+ 全球交易所
- **模型家族**:
  - Kronos-mini (4.1M params, context 2048)
  - Kronos-small (24.7M params, context 512)
  - Kronos-base (102.3M params, context 512)
  - Kronos-large (499.2M params, 未开源)
- **核心创新**: 两阶段框架
  1. Tokenizer 将 OHLCV 数据量化为分层离散 tokens
  2. 自回归 Transformer 在 tokens 上预训练

```python
# 原始使用方式
from model import Kronos, KronosTokenizer, KronosPredictor

tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
predictor = KronosPredictor(model, tokenizer, max_context=512)

pred_df = predictor.predict(
    df=x_df,
    x_timestamp=x_timestamp,
    y_timestamp=y_timestamp,
    pred_len=120
)
```

#### 2.2.2 OpenBB

**GitHub**: https://github.com/OpenBB-finance/OpenBB

- **描述**: 面向分析师、量化研究员和 AI Agent 的金融数据平台
- **架构**: "Connect once, consume everywhere" 基础设施层
- **数据消费端**:
  - Python 环境 (量化)
  - OpenBB Workspace (分析师)
  - Excel (分析师)
  - MCP servers (AI Agent)
  - REST APIs (其他应用)
- **企业版**: OpenBB Workspace (https://pro.openbb.co)

```python
# 原始使用方式
from openbb import obb

output = obb.equity.price.historical("AAPL")
df = output.to_dataframe()
```

#### 2.2.3 VeighNa (vnpy)

**GitHub**: https://github.com/vnpy/vnpy

- **描述**: 基于 Python 的开源量化交易平台开发框架
- **版本**: 4.3.0 (AI-Powered)
- **4.0 新增 vnpy.alpha 模块**:
  - `dataset`: 因子特征工程 (Alpha 158)
  - `model`: ML模型训练 (Lasso/LightGBM/MLP)
  - `strategy`: 策略投研开发
  - `lab`: 投研流程管理
  - `notebook`: 量化投研 Demo
- **覆盖市场**:
  - 国内: CTP, XTP, 恒生UFT, 易盛, 顶点, 华鑫, 东证, 东方财富 等
  - 海外: Interactive Brokers, 易盛9.0外盘, 直达期货
- **策略类型**: CTA, 价差交易, 期权, 组合策略, 算法交易, 脚本策略

```python
# 原始使用方式
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy_ctp import CtpGateway
from vnpy_ctastrategy import CtaStrategyApp

event_engine = EventEngine()
main_engine = MainEngine(event_engine)
main_engine.add_gateway(CtpGateway)
main_engine.add_app(CtaStrategyApp)
```

---

## 3. 与 SkillForge 的协同架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AI 驱动的量化交易完整流水线                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐             │
│   │   OpenBB    │ ──→ │   Kronos    │ ──→ │   VeighNa   │             │
│   │  (数据层)    │     │  (预测层)    │     │  (执行层)    │             │
│   │             │     │             │     │             │             │
│   │ - 多源聚合   │     │ - K线预测   │     │ - 策略执行   │             │
│   │ - 标准化接口 │     │ - 置信区间  │     │ - 风险管理   │             │
│   │ - AI Agent  │     │ - 概率预测   │     │ - 组合管理   │             │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘             │
│          │                   │                   │                     │
│          ▼                   ▼                   ▼                     │
│   ┌─────────────────────────────────────────────────────────┐         │
│   │                   SkillForge 精炼层                      │         │
│   │  ┌────────────┐ ┌────────────┐ ┌────────────┐          │         │
│   │  │ openbb-    │ │ kronos-    │ │ veighna-   │          │         │
│   │  │ fetch      │ │ predict    │ │ execute    │          │         │
│   │  │ (数据Skill)│ │ (预测Skill)│ │ (执行Skill)│          │         │
│   │  └────────────┘ └────────────┘ └────────────┘          │         │
│   │                                                         │         │
│   │              ┌─────────────────────┐                    │         │
│   │              │   编排 & 治理引擎    │                    │         │
│   │              │  (Orchestrator)     │                    │         │
│   │              └──────────┬──────────┘                    │         │
│   │                         │                               │         │
│   │              ┌──────────▼──────────┐                    │         │
│   │              │  Gate (合规检查)     │                    │         │
│   │              │  Evidence (证据链)   │                    │         │
│   │              │  Replay (可复现)     │                    │         │
│   │              └─────────────────────┘                    │         │
│   └─────────────────────────────────────────────────────────┘         │
│                                   │                                     │
│                                   ▼                                     │
│                        ┌─────────────────┐                              │
│                        │  L3 Audit Pack  │                              │
│                        │  (审计报告)      │                              │
│                        └─────────────────┘                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 价值映射表

| 原始能力 | SkillForge 精炼后 | 新增价值 |
|----------|------------------|----------|
| OpenBB 数据获取 | `openbb-fetch` Skill | 数据来源追溯、API限流控制、错误码标准化 |
| Kronos K线预测 | `kronos-predict` Skill | 输入输出合同、预测证据链、置信度阈值Gate |
| VeighNa 策略执行 | `veighna-execute` Skill | 交易审计日志、风控Gate检查、回撤限制 |
| 三者组合 | `quant-pipeline` 编排 | 端到端可复现、合规报告自动生成 |

---

## 4. Skill 合同设计

### 4.1 openbb-fetch Skill

```json
// schemas/openbb-fetch.input.schema.json
{
  "skill_id": "openbb-fetch",
  "version": "1.0.0",
  "input": {
    "data_type": {
      "type": "string",
      "enum": ["equity.price.historical", "equity.fundamental", "economy.indicators", "crypto.price"],
      "description": "数据类型端点"
    },
    "symbols": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1,
      "maxItems": 100,
      "description": "标的代码列表"
    },
    "provider": {
      "type": "string",
      "enum": ["yahoo", "alpha_vantage", "fmp", "polygon"],
      "default": "yahoo",
      "description": "数据提供商"
    },
    "start_date": { "type": "string", "format": "date" },
    "end_date": { "type": "string", "format": "date" }
  },
  "controls": {
    "max_rows": { "type": "integer", "default": 50000, "maximum": 100000 },
    "timeout_ms": { "type": "integer", "default": 30000, "maximum": 120000 },
    "rate_limit": { "type": "string", "default": "10/min" },
    "retry_count": { "type": "integer", "default": 3, "maximum": 5 }
  }
}
```

```json
// schemas/openbb-fetch.output.schema.json
{
  "status": { "enum": ["completed", "failed", "rate_limited", "partial"] },
  "data": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "symbol": { "type": "string" },
        "timestamp": { "type": "string", "format": "date-time" },
        "open": { "type": "number" },
        "high": { "type": "number" },
        "low": { "type": "number" },
        "close": { "type": "number" },
        "volume": { "type": "number" }
      }
    }
  },
  "provenance": {
    "provider": { "type": "string" },
    "fetched_at": { "type": "string", "format": "date-time" },
    "source_url": { "type": "string" }
  },
  "evidence_ref": {
    "type": "string",
    "format": "uri",
    "description": "证据引用路径"
  },
  "metrics": {
    "rows_fetched": { "type": "integer" },
    "latency_ms": { "type": "integer" }
  }
}
```

### 4.2 kronos-predict Skill

```json
// schemas/kronos-predict.input.schema.json
{
  "skill_id": "kronos-predict",
  "version": "1.0.0",
  "input": {
    "symbol": { "type": "string", "description": "标的代码" },
    "lookback": { "type": "integer", "minimum": 50, "maximum": 512, "default": 400 },
    "pred_len": { "type": "integer", "minimum": 1, "maximum": 240, "default": 120 },
    "interval": {
      "type": "string",
      "enum": ["1min", "5min", "15min", "30min", "1h", "4h", "1d"],
      "default": "5min"
    },
    "model_version": {
      "type": "string",
      "enum": ["kronos-mini", "kronos-small", "kronos-base"],
      "default": "kronos-small"
    },
    "data_source": {
      "type": "object",
      "properties": {
        "type": { "enum": ["inline", "reference", "skill_output"] },
        "ref": { "type": "string" }
      }
    }
  },
  "controls": {
    "max_timeout_ms": { "type": "integer", "default": 60000 },
    "confidence_threshold": { "type": "number", "minimum": 0, "maximum": 1, "default": 0.5 }
  }
}
```

```json
// schemas/kronos-predict.output.schema.json
{
  "status": { "enum": ["completed", "low_confidence", "context_overflow", "failed"] },
  "predictions": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "timestamp": { "type": "string", "format": "date-time" },
        "open": { "type": "number" },
        "high": { "type": "number" },
        "low": { "type": "number" },
        "close": { "type": "number" },
        "volume": { "type": "number" }
      }
    }
  },
  "confidence_metrics": {
    "mean": { "type": "number" },
    "std": { "type": "number" },
    "percentile_25": { "type": "number" },
    "percentile_75": { "type": "number" }
  },
  "model_info": {
    "version": { "type": "string" },
    "commit_sha": { "type": "string" },
    "tokenizer_version": { "type": "string" }
  },
  "input_hash": {
    "type": "string",
    "description": "输入数据 SHA256 指纹，用于可复现验证"
  },
  "evidence_ref": { "type": "string", "format": "uri" },
  "gate_decision": {
    "verdict": { "enum": ["ALLOW", "DENY", "WARN"] },
    "checks": {
      "confidence_passed": { "type": "boolean" },
      "context_valid": { "type": "boolean" }
    }
  }
}
```

### 4.3 veighna-execute Skill

```json
// schemas/veighna-execute.input.schema.json
{
  "skill_id": "veighna-execute",
  "version": "1.0.0",
  "input": {
    "action": {
      "type": "string",
      "enum": ["buy", "sell", "cancel", "modify"]
    },
    "symbol": { "type": "string" },
    "quantity": { "type": "integer", "minimum": 1 },
    "order_type": {
      "type": "string",
      "enum": ["market", "limit", "stop", "stop_limit"]
    },
    "price": { "type": "number", "description": "限价单必填" },
    "strategy_id": { "type": "string" },
    "signal_source": {
      "type": "object",
      "description": "信号来源引用",
      "properties": {
        "skill_id": { "type": "string" },
        "run_id": { "type": "string" }
      }
    }
  },
  "controls": {
    "max_order_value": { "type": "number", "default": 100000 },
    "max_position_ratio": { "type": "number", "default": 0.1 },
    "risk_checks": {
      "type": "array",
      "items": {
        "enum": ["position_limit", "daily_loss_limit", "drawdown_limit", "liquidity_check"]
      },
      "default": ["position_limit", "daily_loss_limit"]
    }
  }
}
```

```json
// schemas/veighna-execute.output.schema.json
{
  "status": { "enum": ["filled", "partial", "pending", "rejected", "cancelled"] },
  "order": {
    "order_id": { "type": "string" },
    "symbol": { "type": "string" },
    "action": { "type": "string" },
    "quantity": { "type": "integer" },
    "filled_quantity": { "type": "integer" },
    "price": { "type": "number" },
    "avg_fill_price": { "type": "number" }
  },
  "gate_decision": {
    "verdict": { "enum": ["ALLOW", "DENY", "WARN"] },
    "violations": {
      "type": "array",
      "items": {
        "rule_id": { "type": "string" },
        "severity": { "enum": ["critical", "warning", "info"] },
        "message": { "type": "string" }
      }
    },
    "checks_passed": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "risk_snapshot": {
    "position_before": { "type": "number" },
    "position_after": { "type": "number" },
    "pnl_today": { "type": "number" },
    "drawdown": { "type": "number" }
  },
  "evidence_ref": { "type": "string", "format": "uri" },
  "timestamp": { "type": "string", "format": "date-time" }
}
```

---

## 5. Issue Catalog (问题目录)

```yaml
# orchestration/issue_catalog.yml
issues:
  # OpenBB 相关
  - issue_key: "OPENBB_RATE_LIMITED"
    severity: "warn"
    category: "data"
    message: "API 请求频率超限"
    next_action: "等待冷却后重试或切换数据源"

  - issue_key: "OPENBB_PROVIDER_UNAVAILABLE"
    severity: "error"
    category: "data"
    message: "数据提供商服务不可用"
    next_action: "切换到备用数据源"

  - issue_key: "OPENBB_INVALID_SYMBOL"
    severity: "error"
    category: "data"
    message: "无效的标的代码"
    next_action: "检查标的代码格式"

  - issue_key: "OPENBB_DATA_GAP"
    severity: "warn"
    category: "data"
    message: "数据存在缺失时段"
    next_action: "记录缺失范围，考虑插值或标记"

  # Kronos 相关
  - issue_key: "KRONOS_CONTEXT_OVERFLOW"
    severity: "error"
    category: "prediction"
    message: "输入上下文超过模型最大长度"
    next_action: "减少 lookback 参数"

  - issue_key: "KRONOS_LOW_CONFIDENCE"
    severity: "warn"
    category: "prediction"
    message: "预测置信度低于阈值"
    next_action: "人工复核或调整模型参数"

  - issue_key: "KRONOS_TOKENIZER_MISMATCH"
    severity: "error"
    category: "prediction"
    message: "Tokenizer 与模型版本不匹配"
    next_action: "检查模型和 tokenizer 版本一致性"

  - issue_key: "KRONOS_PREDICTION_TIMEOUT"
    severity: "error"
    category: "prediction"
    message: "预测超时"
    next_action: "减少 pred_len 或增加 timeout"

  # VeighNa 相关
  - issue_key: "VEIGHNA_POSITION_LIMIT_BREACH"
    severity: "critical"
    category: "execution"
    message: "仓位超限"
    next_action: "阻止订单，告警人工干预"

  - issue_key: "VEIGHNA_DAILY_LOSS_LIMIT"
    severity: "critical"
    category: "execution"
    message: "达到每日亏损限制"
    next_action: "暂停交易，风控复核"

  - issue_key: "VEIGHNA_DRAWDOWN_LIMIT"
    severity: "critical"
    category: "execution"
    message: "回撤超过阈值"
    next_action: "减仓或暂停策略"

  - issue_key: "VEIGHNA_ORDER_REJECTED"
    severity: "error"
    category: "execution"
    message: "交易所拒绝订单"
    next_action: "检查订单参数和账户状态"

  - issue_key: "VEIGHNA_CONNECTION_LOST"
    severity: "critical"
    category: "execution"
    message: "交易连接断开"
    next_action: "自动重连，记录未完成订单"

  # 编排相关
  - issue_key: "ORCH_PRECONDITION_FAILED"
    severity: "error"
    category: "orchestration"
    message: "前置条件不满足"
    next_action: "检查上游 Skill 输出"

  - issue_key: "ORCH_GATE_DENIED"
    severity: "critical"
    category: "orchestration"
    message: "Gate 检查未通过"
    next_action: "查看违规详情，人工干预"
```

---

## 6. 编排场景示例

### 6.1 场景：AI 驱动的短线策略

```yaml
# orchestration/pipelines/ai_short_term_strategy.yaml
pipeline:
  id: "ai-short-term-v1"
  name: "AI 驱动短线策略"
  description: "基于 Kronos 预测的 A 股短线交易策略"
  version: "1.0.0"

  triggers:
    - type: "schedule"
      cron: "*/5 9-15 * * 1-5"  # 交易时间每5分钟
    - type: "manual"

  steps:
    - step: 1
      skill: "openbb-fetch"
      alias: "fetch_market_data"
      input:
        data_type: "equity.price.historical"
        symbols: ["600977.XSHG"]
        provider: "xt"  # 迅投研
        lookback: 400
      output_to: "market_data"
      on_failure: "abort"

    - step: 2
      skill: "kronos-predict"
      alias: "predict_price"
      input:
        symbol: "600977.XSHG"
        lookback: 400
        pred_len: 24  # 预测未来2小时 (5min * 24)
        interval: "5min"
        model_version: "kronos-small"
        data_source:
          type: "skill_output"
          ref: "${steps.1.output}"
      output_to: "predictions"
      gate:
        - check: "confidence_metrics.mean >= 0.65"
          on_fail: "WARN"
          action: "human_review"
        - check: "confidence_metrics.std <= 0.2"
          on_fail: "WARN"
      on_failure: "skip_downstream"

    - step: 3
      skill: "veighna-strategy"
      alias: "generate_signal"
      input:
        strategy: "alpha_lgb_v1"
        predictions: "${steps.2.output.predictions}"
        confidence: "${steps.2.output.confidence_metrics}"
      output_to: "signals"
      on_failure: "skip_downstream"

    - step: 4
      skill: "veighna-execute"
      alias: "execute_trade"
      input:
        action: "${steps.3.output.signal.action}"
        symbol: "${steps.3.output.signal.symbol}"
        quantity: "${steps.3.output.signal.quantity}"
        order_type: "limit"
        price: "${steps.3.output.signal.price}"
        strategy_id: "ai-short-term-v1"
        signal_source:
          skill_id: "kronos-predict"
          run_id: "${run_id}"
      gate:
        - check: "position_limit"
        - check: "daily_loss_limit"
        - check: "drawdown_limit <= 0.05"
      on_deny:
        action: "halt"
        alert: "human"
      on_failure: "alert"

    - step: 5
      skill: "audit-pack-generator"
      alias: "generate_audit"
      input:
        run_id: "${run_id}"
        include_steps: [1, 2, 3, 4]
        format: "L3"
      output_to: "audit_pack"
      on_failure: "warn"

  outputs:
    - name: "audit_pack"
      ref: "${steps.5.output}"
    - name: "trade_result"
      ref: "${steps.4.output}"
```

### 6.2 证据链示例

```json
{
  "evidence_chain": {
    "run_id": "quant-2026-02-22-001",
    "pipeline": "ai-short-term-v1",
    "timestamp": "2026-02-22T14:30:00Z",

    "chain": [
      {
        "step": 1,
        "skill": "openbb-fetch",
        "evidence_ref": "evidence://quant/2026-02-22/001/step-1",
        "hash": "sha256:a1b2c3...",
        "summary": {
          "provider": "xt",
          "symbols": ["600977.XSHG"],
          "rows": 400,
          "time_range": ["2026-02-21T09:30:00", "2026-02-22T14:25:00"]
        }
      },
      {
        "step": 2,
        "skill": "kronos-predict",
        "evidence_ref": "evidence://quant/2026-02-22/001/step-2",
        "hash": "sha256:d4e5f6...",
        "input_hash": "sha256:a1b2c3...",
        "summary": {
          "model": "kronos-small",
          "pred_len": 24,
          "confidence_mean": 0.72,
          "gate_decision": "ALLOW"
        }
      },
      {
        "step": 3,
        "skill": "veighna-strategy",
        "evidence_ref": "evidence://quant/2026-02-22/001/step-3",
        "hash": "sha256:g7h8i9...",
        "summary": {
          "strategy": "alpha_lgb_v1",
          "signal": "BUY",
          "quantity": 100,
          "target_price": 10.25
        }
      },
      {
        "step": 4,
        "skill": "veighna-execute",
        "evidence_ref": "evidence://quant/2026-02-22/001/step-4",
        "hash": "sha256:j0k1l2...",
        "summary": {
          "order_id": "20260222001",
          "status": "filled",
          "filled_price": 10.24,
          "gate_decision": "ALLOW",
          "checks_passed": ["position_limit", "daily_loss_limit", "drawdown_limit"]
        }
      }
    ],

    "audit_pack_ref": "evidence://quant/2026-02-22/001/audit-pack",
    "replay_manifest": "evidence://quant/2026-02-22/001/replay-manifest.json"
  }
}
```

---

## 7. VeighNa 与 SkillForge 治理层映射

VeighNa 内置的风控模块与 SkillForge 治理层高度契合：

| VeighNa 模块 | 功能 | SkillForge 对应 |
|-------------|------|----------------|
| `risk_manager` | 交易流控、下单数量、撤单限制 | `50_governance/gate_verdict_v1` |
| `portfolio_manager` | 组合管理、盈亏统计 | `70_read_models/orchestration_view_v1` |
| `cta_backtester` | 策略回测 | `replay_manifest` (回测即复现) |
| 交易日志 | 所有委托/成交记录 | `audit_event_v1` |
| Gateway 连接状态 | 交易接口状态 | `trace_context_v1` |

**整合建议**:
1. 将 VeighNa 的 `risk_manager` 检查规则映射到 SkillForge Gate 规则
2. 每笔交易自动生成 `audit_event` 并链接到 `evidence_ref`
3. 回测结果作为 `replay_manifest` 存储，支持策略验证

---

## 8. 许可证兼容性分析

| 仓库 | 许可证 | 商业使用 | 集成建议 |
|------|--------|---------|---------|
| Kronos | MIT | ✅ 自由 | 可直接集成到核心 |
| OpenBB | AGPLv3 | ⚠️ 需开源 | 作为独立数据适配器，隔离 AGPL 污染 |
| VeighNa | MIT | ✅ 自由 | 可直接集成到核心 |

**OpenBB 隔离方案**:
```
┌─────────────────────────────────────────────────┐
│  SkillForge Core (MIT)                          │
│  ┌─────────────┐  ┌─────────────┐              │
│  │kronos-predict│  │veighna-exe  │              │
│  └─────────────┘  └─────────────┘              │
└────────────────┬────────────────────────────────┘
                 │ REST API (网络边界)
┌────────────────▼────────────────────────────────┐
│  openbb-adapter (AGPLv3 隔离区)                 │
│  ┌─────────────┐                                │
│  │openbb-fetch │                                │
│  └─────────────┘                                │
└─────────────────────────────────────────────────┘
```

---

## 9. 实施路线图

### Phase 1: 基础设施 (2周)
- [ ] 创建 `schemas/openbb-fetch.*.schema.json`
- [ ] 创建 `schemas/kronos-predict.*.schema.json`
- [ ] 创建 `schemas/veighna-execute.*.schema.json`
- [ ] 定义 `issue_catalog.yml` (量化专用)
- [ ] 编写 contract tests

### Phase 2: Skill 包装 (3周)
- [ ] 实现 `openbb-fetch` Skill (含 AGPL 隔离)
- [ ] 实现 `kronos-predict` Skill
- [ ] 实现 `veighna-execute` Skill
- [ ] 实现 Gate 规则映射

### Phase 3: 编排与治理 (2周)
- [ ] 实现 `quant-pipeline` 编排器
- [ ] 实现证据链自动生成
- [ ] 实现 L3 Audit Pack 生成
- [ ] 实现 Replay 能力

### Phase 4: 测试与上线 (1周)
- [ ] 端到端集成测试
- [ ] 回测验证
- [ ] 合规审计
- [ ] 文档完善

---

## 10. 风险与缓解

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| OpenBB AGPLv3 污染 | 高 | 通过网络边界隔离，作为独立服务 |
| 预测模型不可靠 | 中 | 置信度阈值 Gate，人工复核机制 |
| 交易系统故障 | 高 | Fail-closed 设计，自动熔断 |
| 数据源不稳定 | 中 | 多数据源切换，本地缓存 |
| 合规要求变化 | 中 | Gate 规则可配置，审计日志完整 |

---

## 11. 参考资料

- [Kronos GitHub](https://github.com/shiyu-coder/Kronos)
- [Kronos Paper (arXiv)](https://arxiv.org/abs/2508.02739)
- [OpenBB GitHub](https://github.com/OpenBB-finance/OpenBB)
- [OpenBB Documentation](https://docs.openbb.co)
- [VeighNa GitHub](https://github.com/vnpy/vnpy)
- [VeighNa Documentation](https://www.vnpy.com)
- [GM-SkillForge README](../README.md)
- [SkillForge 架构文档](../skillforge-spec-pack/skillforge/docs/ARCHITECTURE.md)

---

## 附录 A: 术语表

| 术语 | 定义 |
|------|------|
| OHLCV | Open, High, Low, Close, Volume - K线数据五要素 |
| K-line | 蜡烛图/K线，金融时序数据的基本单位 |
| Gate | SkillForge 的合规检查关卡 |
| Evidence Ref | 证据引用，指向审计证据的 URI |
| Replay | 复现能力，重放历史执行过程 |
| L3 Audit Pack | Level 3 审计包，包含完整证据链和复现能力 |
| Fail-closed | 失败时安全关闭，不产生意外副作用 |
| Alpha 158 | 微软 Qlib 项目的 158 个因子特征集合 |

---

*文档结束*
