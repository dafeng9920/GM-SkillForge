# Quant System 接口合同

> 版本: v1.0
> 日期: 2026-02-22
> 对齐: SkillForge constitution_v1

---

## 1. 通用输出合同 (Envelope)

所有 Quant System Skills 输出必须符合以下格式：

```json
{
  "envelope_version": "1.0",
  "skill_id": "string",
  "run_id": "string",
  "trace_id": "string",
  "timestamp": "string (ISO-8601)",

  "status": "completed | failed | rejected",
  "data": { ... },

  "evidence": {
    "evidence_ref": "evidence://quant/{skill_id}/{hash}",
    "data_hash": "sha256:{hex}",
    "provenance": {
      "source": "string",
      "fetched_at": "string (ISO-8601)",
      "version": "string"
    }
  },

  "gate_decision": {
    "verdict": "ALLOW | DENY | WARN",
    "checks_passed": ["string"],
    "violations": [
      {
        "rule_id": "string",
        "severity": "critical | warning | info",
        "message": "string",
        "actual_value": "any",
        "threshold": "any"
      }
    ]
  },

  "error": {
    "error_code": "string | null",
    "error_message": "string | null",
    "retryable": "boolean"
  },

  "metrics": {
    "latency_ms": "integer",
    "rows_processed": "integer | null",
    "tokens_used": "integer | null"
  }
}
```

---

## 2. Skill 输入合同

### 2.1 通用输入格式

```json
{
  "skill_id": "string",
  "input": {
    // Skill 特定输入
  },
  "trace_context": {
    "parent_span": "string | null",
    "correlation_id": "string",
    "session_id": "string | null"
  },
  "controls": {
    "timeout_ms": "integer",
    "max_retries": "integer",
    "dry_run": "boolean"
  }
}
```

### 2.2 输入验证规则

| 字段 | 规则 | 失败处理 |
|------|------|----------|
| `skill_id` | 必填，必须在注册表中 | `rejected` |
| `input` | 必填，必须符合 skill schema | `rejected` |
| `trace_context.correlation_id` | 必填 | `rejected` |
| `controls.timeout_ms` | 可选，默认 30000 | 使用默认值 |

---

## 3. P0 Skills 接口合同

### 3.1 openbb-fetch

**输入:**
```json
{
  "skill_id": "openbb-fetch",
  "input": {
    "data_type": "equity.price.historical | equity.fundamental | economy.indicators | crypto.price",
    "symbols": ["string"],
    "provider": "yahoo | alpha_vantage | fmp | polygon",
    "start_date": "date | null",
    "end_date": "date | null"
  },
  "controls": {
    "max_rows": 50000,
    "timeout_ms": 30000,
    "rate_limit": "10/min"
  }
}
```

**输出:**
```json
{
  "envelope_version": "1.0",
  "skill_id": "openbb-fetch",
  "run_id": "run-{uuid}",
  "trace_id": "trace-{uuid}",
  "timestamp": "2026-02-22T10:30:00Z",

  "status": "completed | failed | rejected",
  "data": {
    "records": [
      {
        "timestamp": "2026-02-22T09:30:00Z",
        "symbol": "AAPL",
        "open": 100.0,
        "high": 102.0,
        "low": 99.0,
        "close": 101.0,
        "volume": 1000000
      }
    ],
    "metadata": {
      "provider": "yahoo",
      "symbols_count": 1,
      "rows_count": 100
    }
  },

  "evidence": {
    "evidence_ref": "evidence://quant/openbb-fetch/{hash}",
    "data_hash": "sha256:{hex}",
    "provenance": {
      "source": "yahoo",
      "fetched_at": "2026-02-22T10:30:00Z",
      "api_version": "v8"
    }
  },

  "gate_decision": {
    "verdict": "ALLOW",
    "checks_passed": ["data_freshness", "schema_valid"],
    "violations": []
  },

  "error": {
    "error_code": null,
    "error_message": null,
    "retryable": false
  },

  "metrics": {
    "latency_ms": 1500,
    "rows_processed": 100,
    "tokens_used": null
  }
}
```

**错误码:**
| 错误码 | 含义 | 可重试 |
|--------|------|--------|
| `OPENBB_RATE_LIMITED` | API 频率限制 | 是 |
| `OPENBB_PROVIDER_UNAVAILABLE` | 数据源不可用 | 是 |
| `OPENBB_INVALID_SYMBOL` | 无效标的代码 | 否 |
| `OPENBB_VALIDATION_ERROR` | 输入验证失败 | 否 |

---

### 3.2 data-validator

**输入:**
```json
{
  "skill_id": "data-validator",
  "input": {
    "data": [{ ... }],
    "schema": { ... },
    "rules": ["MISSING_VALUE_CHECK", "OUTLIER_CHECK", "CONTINUITY_CHECK"],
    "strict_mode": false
  },
  "controls": {
    "max_rows": 100000,
    "timeout_ms": 60000
  }
}
```

**输出:**
```json
{
  "envelope_version": "1.0",
  "skill_id": "data-validator",
  "run_id": "run-{uuid}",
  "trace_id": "trace-{uuid}",
  "timestamp": "2026-02-22T10:30:00Z",

  "status": "completed | failed | rejected",
  "data": {
    "validation_result": {
      "total_rows": 1000,
      "valid_rows": 950,
      "invalid_rows": 50,
      "valid_ratio": 0.95,
      "issues": [
        {
          "rule_id": "MISSING_VALUE_CHECK",
          "severity": "warning",
          "message": "列 'close' 缺失值比例为 5%",
          "column": "close",
          "count": 50
        }
      ],
      "issues_by_severity": {
        "critical": 0,
        "warning": 1,
        "info": 0
      }
    },
    "cleaned_data": [{ ... }]
  },

  "evidence": {
    "evidence_ref": "evidence://quant/data-validator/{hash}",
    "data_hash": "sha256:{hex}",
    "provenance": {
      "source": "input_data",
      "processed_at": "2026-02-22T10:30:00Z",
      "rules_applied": ["MISSING_VALUE_CHECK", "OUTLIER_CHECK"]
    }
  },

  "gate_decision": {
    "verdict": "ALLOW | DENY | WARN",
    "checks_passed": ["no_critical_issues"],
    "violations": [
      {
        "rule_id": "DATA_QUALITY",
        "severity": "warning",
        "message": "数据存在 50 个问题",
        "actual_value": 50,
        "threshold": 0
      }
    ]
  },

  "error": {
    "error_code": null,
    "error_message": null,
    "retryable": false
  },

  "metrics": {
    "latency_ms": 200,
    "rows_processed": 1000,
    "tokens_used": null
  }
}
```

**错误码:**
| 错误码 | 含义 | 可重试 |
|--------|------|--------|
| `DATA_VALIDATION_FAILED` | 数据验证失败 | 否 |
| `DATA_TOO_MANY_ISSUES` | 问题数量超限 | 否 |
| `DATA_SCHEMA_MISMATCH` | Schema 不匹配 | 否 |

---

### 3.3 kronos-predict

**输入:**
```json
{
  "skill_id": "kronos-predict",
  "input": {
    "symbol": "AAPL",
    "ohlcv_data": [{ ... }],
    "lookback": 400,
    "pred_len": 120,
    "interval": "5min",
    "model_version": "kronos-small"
  },
  "controls": {
    "timeout_ms": 60000,
    "confidence_threshold": 0.6
  }
}
```

**输出:**
```json
{
  "envelope_version": "1.0",
  "skill_id": "kronos-predict",
  "run_id": "run-{uuid}",
  "trace_id": "trace-{uuid}",
  "timestamp": "2026-02-22T10:30:00Z",

  "status": "completed | failed | rejected",
  "data": {
    "predictions": [
      {
        "timestamp": "2026-02-22T10:35:00Z",
        "open": 101.0,
        "high": 102.5,
        "low": 100.5,
        "close": 102.0,
        "volume": 1500000
      }
    ],
    "confidence_metrics": {
      "mean": 0.75,
      "std": 0.15,
      "percentile_25": 0.65,
      "percentile_75": 0.85
    },
    "model_info": {
      "version": "kronos-small",
      "commit_sha": "abc123",
      "tokenizer_version": "v1"
    }
  },

  "evidence": {
    "evidence_ref": "evidence://quant/kronos-predict/{hash}",
    "data_hash": "sha256:{hex}",
    "provenance": {
      "source": "kronos-model",
      "model_version": "kronos-small",
      "input_hash": "sha256:{hex}"
    }
  },

  "gate_decision": {
    "verdict": "ALLOW | DENY | WARN",
    "checks_passed": ["confidence_threshold", "context_valid"],
    "violations": []
  },

  "error": {
    "error_code": null,
    "error_message": null,
    "retryable": false
  },

  "metrics": {
    "latency_ms": 5000,
    "rows_processed": 400,
    "tokens_used": null
  }
}
```

**错误码:**
| 错误码 | 含义 | 可重试 |
|--------|------|--------|
| `KRONOS_CONTEXT_OVERFLOW` | 输入上下文超长 | 否 |
| `KRONOS_LOW_CONFIDENCE` | 置信度过低 | 否 |
| `KRONOS_PREDICTION_TIMEOUT` | 预测超时 | 是 |
| `KRONOS_MODEL_ERROR` | 模型错误 | 是 |

---

## 4. Gate 决策语义

### 4.1 裁决逻辑

```
IF 存在 severity=critical 的 violation THEN
    verdict = DENY
    next_action = halt
ELSE IF 存在 severity=warning 的 violation THEN
    verdict = WARN
    next_action = continue_with_caution
ELSE
    verdict = ALLOW
    next_action = continue
```

### 4.2 Fail-Closed 规则

| 条件 | 裁决 |
|------|------|
| Gate 检查超时 | DENY |
| Gate 检查异常 | DENY |
| Gate 规则配置缺失 | DENY |
| 输入验证失败 | REJECTED |

---

## 5. Evidence 引用规范

### 5.1 URI 格式

```
evidence://quant/{skill_id}/{hash}
```

### 5.2 Hash 计算

```python
import hashlib
import json

def compute_evidence_hash(skill_id: str, data: dict, timestamp: str) -> str:
    content = json.dumps({
        "skill_id": skill_id,
        "data": data,
        "timestamp": timestamp
    }, sort_keys=True)

    return hashlib.sha256(content.encode()).hexdigest()[:32]
```

### 5.3 Evidence 存储路径

```
/evidence/
  /quant/
    /{skill_id}/
      /{year}-{month}/
        /{run_id}.json
```

---

## 6. Trace Context 传递

### 6.1 从 SkillForge 接收

```json
{
  "trace_context": {
    "parent_span": "span-skillforge-xxx",
    "correlation_id": "corr-xxx",
    "session_id": "sess-xxx"
  }
}
```

### 6.2 返回给 SkillForge

```json
{
  "trace_id": "trace-quant-{uuid}",
  "span_id": "span-quant-{uuid}",
  "parent_span": "span-skillforge-xxx",
  "correlation_id": "corr-xxx"
}
```

---

## 7. 版本兼容性

| 版本 | 状态 | 说明 |
|------|------|------|
| 1.0 | 当前 | 初始版本 |

**兼容性规则:**
- 主版本号变更：不兼容
- 次版本号变更：向后兼容
- 修订号变更：完全兼容

---

*合同结束*
