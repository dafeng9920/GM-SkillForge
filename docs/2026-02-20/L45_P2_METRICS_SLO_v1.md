# L4.5 SEEDS P2 Metrics & SLO 文档

> Job ID: L45-D6-SEEDS-P2-20260220-006
> Skill ID: l45_seeds_p2_operationalization
> 日期: 2026-02-20

---

## 1. 概述

本文档定义 SEEDS 三账本（registry/audit_events/usage）的健康指标、SLO 目标与阈值告警规则。

---

## 2. 三账本指标

### 2.1 Registry（skills.jsonl）

| 指标 | 描述 | 单位 | SLO 目标 |
|------|------|------|----------|
| `registry_size` | 注册技能总数 | count | >= 1 |
| `registry_active_count` | ACTIVE 状态技能数 | count | >= 1 |
| `registry_tombstoned_count` | TOMBSTONED 状态技能数 | count | N/A |

### 2.2 Audit Events（audit_events.jsonl）

| 指标 | 描述 | 单位 | SLO 目标 |
|------|------|------|----------|
| `audit_events_count` | 审计事件总数 | count | >= 1 |
| `audit_events_pass_count` | PASS 决策数 | count | N/A |
| `audit_events_fail_count` | FAIL 决策数 | count | N/A |
| `audit_events_skip_count` | SKIPPED 决策数 | count | N/A |
| `audit_events_latest_ts` | 最新事件时间戳 | ISO-8601 | - |
| `audit_events_age_hours` | 最新事件距今小时数 | hours | < 24 |

### 2.3 Usage（usage.jsonl）

| 指标 | 描述 | 单位 | SLO 目标 |
|------|------|------|----------|
| `usage_count` | 用量记录总数 | count | >= 0 |
| `usage_total_units` | 总计量单位数 | units | >= 0 |

---

## 3. 计算指标（Computed Metrics）

### 3.1 ingest_rate

**定义**: 每分钟事件摄入率（最近 1 小时内）

**公式**:
```
ingest_rate = recent_events_count / 60
```

**SLO 目标**: >= 0（可配置）

**阈值配置**:
```yaml
thresholds:
  ingest_rate_min: 0.0  # events/minute
```

### 3.2 error_rate

**定义**: 失败事件比例

**公式**:
```
error_rate = fail_count / total_events_count
```

**SLO 目标**: <= 5%

**阈值配置**:
```yaml
thresholds:
  error_rate_max: 0.05  # 5%
```

**告警规则**:
- Warning: error_rate > 5%
- Critical: error_rate > 10%

### 3.3 missing_evidence_rate

**定义**: 缺少证据引用的事件比例

**公式**:
```
missing_evidence_rate = missing_evidence_count / total_events_count
```

**SLO 目标**: <= 1%

**阈值配置**:
```yaml
thresholds:
  missing_evidence_rate_max: 0.01  # 1%
```

---

## 4. 阈值配置

### 4.1 默认阈值

| 阈值 | 默认值 | 说明 |
|------|--------|------|
| `ingest_rate_min` | 0.0 | 最小摄入率 |
| `error_rate_max` | 0.05 | 最大错误率 (5%) |
| `missing_evidence_rate_max` | 0.01 | 最大缺失证据率 (1%) |
| `registry_size_min` | 1 | 最小注册表大小 |
| `audit_events_age_max_hours` | 24 | 最新事件最大年龄 |

### 4.2 环境变量配置

```bash
export SKILLFORGE_THRESHOLD_INGEST_RATE_MIN=0.1
export SKILLFORGE_THRESHOLD_ERROR_RATE_MAX=0.03
export SKILLFORGE_THRESHOLD_MISSING_EVIDENCE_RATE_MAX=0.005
export SKILLFORGE_THRESHOLD_REGISTRY_SIZE_MIN=5
export SKILLFORGE_THRESHOLD_AUDIT_EVENTS_AGE_MAX_HOURS=12
```

### 4.3 代码配置

```python
from skillforge.src.ops.seeds_metrics import MetricThresholds, SeedsMetricsCollector

thresholds = MetricThresholds(
    ingest_rate_min=0.1,
    error_rate_max=0.03,
    missing_evidence_rate_max=0.005,
)

collector = SeedsMetricsCollector(thresholds=thresholds)
snapshot = collector.collect()
```

---

## 5. 告警规则

### 5.1 告警级别

| 级别 | 触发条件 | 响应时间 |
|------|----------|----------|
| `warning` | 指标超过阈值 | 24h 内处理 |
| `critical` | 指标超过阈值 2 倍 | 1h 内处理 |

### 5.2 告警示例

```json
{
  "metric_name": "error_rate",
  "current_value": 0.08,
  "threshold": 0.05,
  "severity": "warning",
  "message": "Error rate 0.0800 exceeds threshold 0.05",
  "timestamp": "2026-02-20T10:00:00Z"
}
```

---

## 6. 快照复核

### 6.1 快照结构

每个快照包含：
- **timestamp**: 快照时间戳
- **registry**: 注册表指标
- **audit_events**: 审计事件指标
- **usage**: 用量指标
- **computed**: 计算指标（ingest_rate, error_rate, missing_evidence_rate）
- **raw_values**: 原始值（用于复核）
- **alerts**: 告警列表
- **healthy**: 整体健康状态

### 6.2 复核要求

1. 快照必须包含原始值（raw_values）
2. 不得只输出图表不输出原始指标值
3. 快照必须可 JSON 序列化
4. 快照可持久化到文件供审计

---

## 7. 实现文件

| 文件 | 类型 | 说明 |
|------|------|------|
| `skillforge/src/ops/seeds_metrics.py` | 代码 | 指标收集器 |
| `skillforge/tests/test_seeds_metrics.py` | 测试 | 38 个测试用例 |
| `docs/2026-02-20/L45_P2_METRICS_SLO_v1.md` | 文档 | 本文档 |

---

## 8. 验收检查

### 8.1 自动检查

```bash
python -m pytest -q skillforge/tests/test_seeds_metrics.py
# 预期: 38 passed
```

### 8.2 手动检查

- [x] 至少输出 ingest_rate/error_rate/missing_evidence_rate
- [x] 阈值可配置（环境变量、代码）
- [x] 快照可复核（包含 raw_values）
- [x] 不只输出图表，输出原始指标值

---

*文档生成时间: 2026-02-20*
