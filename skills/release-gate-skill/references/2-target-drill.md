# 2目标最小演练步骤

**Version**: 1.0.0
**Created**: 2026-02-18

---

## 演练概述

本文档提供 2目标批量发布的验证演练步骤，覆盖以下场景：

1. **场景 A**: 全部通过 (all-or-nothing)
2. **场景 B**: 目标2失败 (all-or-nothing)
3. **场景 C**: 无 Permit (E001)

---

## 前置条件

- [ ] release-gate-skill 已部署
- [ ] Permit 服务可用
- [ ] 测试目标已注册
- [ ] Gate 引擎就绪

---

## 场景 A: 全部通过 (all-or-nothing)

### 步骤 A1: 准备输入

```yaml
run_id: "run-20260218-drill-a1"
release_type: "batch"
strategy: "all-or-nothing"
targets:
  - target_id: "skill-mean-reversion"
    target_type: "skill"
    version: "1.0.0"
  - target_id: "skill-momentum"
    target_type: "skill"
    version: "1.0.0"
permit_refs:
  - permit_id: "perm-20260218-drill"
    issued_at: "2026-02-18T16:00:00Z"
    issued_by: "drill@example.com"
    scope: "release:skill:*"
repo_url: "https://github.com/example/skills"
commit_sha: "abc123def456"
```

### 步骤 A2: 执行 Gate

```bash
# 调用 release-gate-skill
skillforge release-gate execute \
  --run-id "run-20260218-drill-a1" \
  --strategy "all-or-nothing" \
  --targets "skill-mean-reversion:1.0.0,skill-momentum:1.0.0" \
  --permit "perm-20260218-drill"
```

### 步骤 A3: 验证输出

```yaml
# 预期输出
gate_decision:
  decision_id: "dec-xxx"
  decision: "ALLOWED"
  decided_at: "2026-02-18T16:00:05Z"
  decided_by: "system"

release_allowed: true
overall_status: "PASS"

passed_targets:
  - target_id: "skill-mean-reversion"
    gate_results:
      - gate_name: "gate_permit"
        status: "PASS"
      - gate_name: "gate_risk_level"
        status: "PASS"
      - gate_name: "gate_rollback_ready"
        status: "PASS"
      - gate_name: "gate_monitor_threshold"
        status: "PASS"
      - gate_name: "gate_target_locked"
        status: "PASS"
  - target_id: "skill-momentum"
    gate_results:
      - gate_name: "gate_permit"
        status: "PASS"
      - gate_name: "gate_risk_level"
        status: "PASS"
      - gate_name: "gate_rollback_ready"
        status: "PASS"
      - gate_name: "gate_monitor_threshold"
        status: "PASS"
      - gate_name: "gate_target_locked"
        status: "PASS"

failed_targets: []

gates_passed: 10
gates_failed: 0
validation_latency_ms: 1523

evidence_ref: "evidence/run-20260218-drill-a1/evidence.jsonl"
execution_report_path: "reports/run-20260218-drill-a1/gate-report.json"
```

### 验收点 A

| 检查项 | 预期 | 状态 |
|--------|------|------|
| gate_decision.decision | ALLOWED | ☐ |
| release_allowed | true | ☐ |
| overall_status | PASS | ☐ |
| passed_targets 数量 | 2 | ☐ |
| failed_targets 数量 | 0 | ☐ |
| evidence_ref 存在 | 是 | ☐ |

---

## 场景 B: 目标2失败 (all-or-nothing)

### 步骤 B1: 准备输入

```yaml
run_id: "run-20260218-drill-b1"
release_type: "batch"
strategy: "all-or-nothing"
targets:
  - target_id: "skill-mean-reversion"
    target_type: "skill"
    version: "1.0.0"
  - target_id: "skill-invalid"
    target_type: "skill"
    version: "999.0.0"  # 不存在的版本
permit_refs:
  - permit_id: "perm-20260218-drill"
    issued_at: "2026-02-18T16:10:00Z"
    issued_by: "drill@example.com"
    scope: "release:skill:*"
repo_url: "https://github.com/example/skills"
commit_sha: "abc123def456"
```

### 步骤 B2: 执行 Gate

```bash
skillforge release-gate execute \
  --run-id "run-20260218-drill-b1" \
  --strategy "all-or-nothing" \
  --targets "skill-mean-reversion:1.0.0,skill-invalid:999.0.0" \
  --permit "perm-20260218-drill"
```

### 步骤 B3: 验证输出

```yaml
# 预期输出
gate_decision:
  decision_id: "dec-yyy"
  decision: "DENIED"
  decided_at: "2026-02-18T16:10:03Z"
  decided_by: "system"

release_allowed: false
overall_status: "FAIL"

passed_targets: []

failed_targets:
  - target_id: "skill-invalid"
    error_code: "E009"
    error_message: "Target not found: skill-invalid:999.0.0"
    gate_failed: "gate_target_locked"

gates_passed: 5  # 目标1全部通过
gates_failed: 1  # 目标2 Gate 5 失败
validation_latency_ms: 2341

error_code: "E008"
release_blocked_by: "GATE_CHAIN_FAILED"

evidence_ref: "evidence/run-20260218-drill-b1/evidence.jsonl"
execution_report_path: "reports/run-20260218-drill-b1/gate-report.json"
```

### 验收点 B

| 检查项 | 预期 | 状态 |
|--------|------|------|
| gate_decision.decision | DENIED | ☐ |
| release_allowed | false | ☐ |
| overall_status | FAIL | ☐ |
| passed_targets 数量 | 0 (all-or-nothing) | ☐ |
| failed_targets 数量 | 1 | ☐ |
| error_code | E008 或 E009 | ☐ |

---

## 场景 C: 无 Permit (E001)

### 步骤 C1: 准备输入

```yaml
run_id: "run-20260218-drill-c1"
release_type: "batch"
strategy: "all-or-nothing"
targets:
  - target_id: "skill-mean-reversion"
    target_type: "skill"
    version: "1.0.0"
  - target_id: "skill-momentum"
    target_type: "skill"
    version: "1.0.0"
permit_refs: []  # 空 Permit
repo_url: "https://github.com/example/skills"
commit_sha: "abc123def456"
```

### 步骤 C2: 执行 Gate

```bash
skillforge release-gate execute \
  --run-id "run-20260218-drill-c1" \
  --strategy "all-or-nothing" \
  --targets "skill-mean-reversion:1.0.0,skill-momentum:1.0.0"
  # 注意：无 --permit 参数
```

### 步骤 C3: 验证输出

```yaml
# 预期输出
gate_decision:
  decision_id: "dec-zzz"
  decision: "DENIED"
  decided_at: "2026-02-18T16:20:01Z"
  decided_by: "system"

release_allowed: false
overall_status: "FAIL"

passed_targets: []
failed_targets: []

error_code: "E001"
release_blocked_by: "PERMIT_REQUIRED"

gates_passed: 0
gates_failed: 0
validation_latency_ms: 12  # 快速失败

evidence_ref: "evidence/run-20260218-drill-c1/evidence.jsonl"
execution_report_path: "reports/run-20260218-drill-c1/gate-report.json"
```

### 验收点 C

| 检查项 | 预期 | 状态 |
|--------|------|------|
| gate_decision.decision | DENIED | ☐ |
| release_allowed | false | ☐ |
| error_code | E001 | ☐ |
| release_blocked_by | PERMIT_REQUIRED | ☐ |
| 快速失败 (latency < 100ms) | 是 | ☐ |

---

## 证据引用路径

演练完成后，检查以下路径：

```
reports/
├── run-20260218-drill-a1/
│   ├── gate-report.json      # Gate 执行报告
│   ├── evidence.jsonl        # 证据日志
│   └── decision.json         # 决策记录
├── run-20260218-drill-b1/
│   ├── gate-report.json
│   ├── evidence.jsonl
│   └── decision.json
└── run-20260218-drill-c1/
    ├── gate-report.json
    ├── evidence.jsonl
    └── decision.json
```

---

## 演练结果汇总

| 场景 | 描述 | 预期结果 | 状态 |
|------|------|----------|------|
| A | 全部通过 | ALLOWED | ☐ |
| B | 目标失败 | DENIED (all-or-nothing) | ☐ |
| C | 无 Permit | DENIED (E001) | ☐ |

---

## 演练签核

| 角色 | 签核 | 日期 |
|------|------|------|
| 执行人 | ________ | ________ |
| 审核人 | ________ | ________ |

---

*Generated by Release Gate Skill v1.1.0*
