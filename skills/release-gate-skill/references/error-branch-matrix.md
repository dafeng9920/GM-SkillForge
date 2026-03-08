# Error Branch Matrix

**Version**: 1.0.0
**Last Updated**: 2026-02-18

---

## 1. 错误码定义

| 代码 | 名称 | 描述 | 阻断类型 |
|------|------|------|----------|
| E001 | PERMIT_REQUIRED | Permit 缺失 | **全局阻断** |
| E002 | PERMIT_INVALID_FORMAT | Permit 格式无效 | **全局阻断** |
| E003 | PERMIT_INVALID_SIGNATURE | Permit 签名无效 | **全局阻断** |
| E004 | PERMIT_EXPIRED | Permit 已过期 | **全局阻断** |
| E005 | PERMIT_SCOPE_MISMATCH | Permit Scope 不匹配 | 目标阻断 |
| E006 | PERMIT_SUBJECT_MISMATCH | Permit Subject 不匹配 | 目标阻断 |
| E007 | PERMIT_REVOKED | Permit 已撤销 | **全局阻断** |
| E008 | GATE_CHAIN_FAILED | Gate 链执行失败 | 目标阻断 |
| E009 | TARGET_NOT_FOUND | 目标不存在 | 目标阻断 |

---

## 2. 单目标场景矩阵

### 2.1 错误触发与结果

| 错误码 | 触发条件 | gate_decision | release_allowed | 阻断范围 |
|--------|----------|---------------|-----------------|----------|
| E001 | permit_refs 为空 | DENIED | false | 全局 |
| E002 | Permit 格式错误 | DENIED | false | 全局 |
| E003 | 签名验证失败 | DENIED | false | 全局 |
| E004 | Permit 已过期 | DENIED | false | 全局 |
| E005 | Scope 不包含目标 | DENIED | false | 目标 |
| E006 | Subject 不匹配 | DENIED | false | 目标 |
| E007 | Permit 已撤销 | DENIED | false | 全局 |
| E008 | Gate 链任一失败 | DENIED | false | 目标 |
| E009 | 目标不存在 | DENIED | false | 目标 |

### 2.2 单目标执行流程

```
┌─────────────────────────────────────┐
│         单目标发布                   │
├─────────────────────────────────────┤
│  permit_refs == null?               │
│     ├── YES → E001 → DENIED         │
│     └── NO  ↓                       │
│  签名验证失败?                       │
│     ├── YES → E003 → DENIED         │
│     └── NO  ↓                       │
│  Permit 过期?                        │
│     ├── YES → E004 → DENIED         │
│     └── NO  ↓                       │
│  Gate 1-5 执行                       │
│     ├── 任一失败 → E008 → DENIED    │
│     └── 全部通过 → ALLOWED           │
└─────────────────────────────────────┘
```

---

## 3. 批量场景矩阵 (2目标)

### 3.1 E001 (No Permit) 阻断矩阵

**特性**: 全局阻断，任何目标触发都会导致整体拒绝

| 目标1 | 目标2 | 触发 E001 | gate_decision | release_allowed | overall_status |
|-------|-------|-----------|---------------|-----------------|----------------|
| - | - | 是 (全局) | DENIED | false | FAIL |
| - | PASS | 是 (全局) | DENIED | false | FAIL |
| PASS | - | 是 (全局) | DENIED | false | FAIL |

**说明**: E001 在 permit 检查阶段就触发，不会执行到目标级别

### 3.2 E003 (Invalid Signature) 阻断矩阵

**特性**: 全局阻断，签名验证在 permit 校验阶段

| 目标1 | 目标2 | 策略 | gate_decision | release_allowed | overall_status |
|-------|-------|------|---------------|-----------------|----------------|
| - | - | all-or-nothing | DENIED | false | FAIL |
| - | - | best-effort | DENIED | false | FAIL |
| - | - | canary-first | DENIED | false | FAIL |

**说明**: E003 在 permit 校验阶段触发，不会到达目标级别

### 3.3 E005 (Scope Mismatch) 阻断矩阵

**特性**: 目标阻断，取决于策略

| 目标1 | 目标2 | 策略 | gate_decision | release_allowed | overall_status | passed_targets | failed_targets |
|-------|-------|------|---------------|-----------------|----------------|----------------|----------------|
| PASS | E005 | all-or-nothing | DENIED | false | FAIL | [] | [目标2] |
| E005 | PASS | all-or-nothing | DENIED | false | FAIL | [] | [目标1] |
| PASS | E005 | best-effort | CONDITIONAL | true | PARTIAL | [目标1] | [目标2] |
| E005 | PASS | best-effort | CONDITIONAL | true | PARTIAL | [目标2] | [目标1] |
| E005 | - | canary-first | DENIED | false | FAIL | [] | [目标1] |
| PASS | E005 | canary-first | CONDITIONAL | true | PARTIAL | [目标1] | [目标2] |

### 3.4 E008 (Gate Failed) 阻断矩阵

**特性**: 目标阻断，取决于策略和失败 Gate

| 目标1 | 目标2 | 策略 | gate_decision | release_allowed | overall_status |
|-------|-------|------|---------------|-----------------|----------------|
| PASS | PASS | all-or-nothing | ALLOWED | true | PASS |
| PASS | E008 | all-or-nothing | DENIED | false | FAIL |
| E008 | PASS | all-or-nothing | DENIED | false | FAIL |
| E008 | E008 | all-or-nothing | DENIED | false | FAIL |
| PASS | E008 | best-effort | CONDITIONAL | true | PARTIAL |
| E008 | PASS | best-effort | CONDITIONAL | true | PARTIAL |
| E008 | E008 | best-effort | DENIED | false | FAIL |
| E008 | - | canary-first | DENIED | false | FAIL |
| PASS | E008 | canary-first | CONDITIONAL | true | PARTIAL |

### 3.5 E009 (Target Not Found) 阻断矩阵

**特性**: 目标阻断，在 Gate 5 (Target Locked) 检测

| 目标1 | 目标2 | 策略 | gate_decision | release_allowed | overall_status |
|-------|-------|------|---------------|-----------------|----------------|
| PASS | E009 | all-or-nothing | DENIED | false | FAIL |
| E009 | PASS | all-or-nothing | DENIED | false | FAIL |
| PASS | E009 | best-effort | CONDITIONAL | true | PARTIAL |
| E009 | PASS | best-effort | CONDITIONAL | true | PARTIAL |

---

## 4. 综合阻断决策表

### 4.1 按 error_code 分类

| error_code | 阻断类型 | all-or-nothing | best-effort | canary-first |
|------------|----------|----------------|-------------|--------------|
| E001 | 全局 | DENIED | DENIED | DENIED |
| E002 | 全局 | DENIED | DENIED | DENIED |
| E003 | 全局 | DENIED | DENIED | DENIED |
| E004 | 全局 | DENIED | DENIED | DENIED |
| E007 | 全局 | DENIED | DENIED | DENIED |
| E005 | 目标 | DENIED* | PARTIAL** | 取决于位置 |
| E006 | 目标 | DENIED* | PARTIAL** | 取决于位置 |
| E008 | 目标 | DENIED* | PARTIAL** | 取决于位置 |
| E009 | 目标 | DENIED* | PARTIAL** | 取决于位置 |

\* 任一目标失败 → DENIED
\*\* 部分目标通过 → PARTIAL，全部失败 → DENIED

### 4.2 按 gate_decision 分类

| gate_decision | release_allowed | 触发条件 |
|---------------|-----------------|----------|
| ALLOWED | true | 所有目标通过所有 Gate |
| DENIED | false | E001-E004/E007 触发，或策略阻断 |
| CONDITIONAL | true | best-effort 部分通过 |

---

## 5. 恢复路径

| 错误码 | 恢复步骤 | 可重试 |
|--------|----------|--------|
| E001 | 获取有效 Permit | 是 |
| E002 | 修正 Permit 格式 | 是 |
| E003 | 重新签发 Permit | 是 |
| E004 | 刷新 Permit | 是 |
| E005 | 扩展 Scope 或分离发布 | 是 |
| E006 | 确认 Subject 或重新授权 | 是 |
| E007 | 解决撤销问题 | 是 |
| E008 | 修复 Gate 失败项 | 是 |
| E009 | 确认目标存在 | 是 |

---

## 6. 测试覆盖矩阵

| 场景 | 错误码 | 策略 | 测试 ID | 状态 |
|------|--------|------|---------|------|
| 无 Permit | E001 | all-or-nothing | T2 | PASS |
| 签名无效 | E003 | all-or-nothing | T3 | PASS |
| Permit 过期 | E004 | all-or-nothing | T4 | PASS |
| 2目标全通过 | - | all-or-nothing | T10 | PASS |
| 2目标1失败 | E008 | all-or-nothing | T11 | PASS |
| 2目标1失败 | E008 | best-effort | T12 | PASS |
| 2目标Canary失败 | E008 | canary-first | T13 | PASS |
| 目标不存在 | E009 | all-or-nothing | T14 | PASS |

---

*Generated by Release Gate Skill v1.0.0*
