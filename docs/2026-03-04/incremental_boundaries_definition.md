# Fixed-Caliber 增量边界定义 (N+1/N+2/N+3)

**执行环境**: LOCAL-ANTIGRAVITY
**当前口径**: AG2-FIXED-CALIBER-TG1-20260304
**策略**: 增量安全边界，每轮独立验证

---

## 增量边界定义

### N+1: 命令白名单强制验证

**目标**: 确保所有云端执行严格遵守命令白名单

| 组件 | 要求 | 验证方式 |
|------|------|----------|
| 命令执行 | 仅允许 allowlist 中的命令 | verify_execution_receipt.py |
| 白名单完整性 | 每次任务必须包含 allowlist | task_contract.json 验证 |
| 越界检测 | 任何越界命令 → DENY | audit_event.json 检查 |

**验收标准**:
- ✅ 所有执行的命令都在 allowlist 中
- ✅ 白名单不为空
- ✅ 无越界命令执行

**证据文件**: `docs/2026-03-04/verification/N+1_command_allowlist_verification.json`

---

### N+2: 四件套完整性验证

**目标**: 确保每次任务回传完整的四件套

| 组件 | 要求 | 验证方式 |
|------|------|----------|
| execution_receipt.json | 必须存在且格式正确 | schema 验证 |
| stdout.log | 必须存在（可为空） | 文件存在检查 |
| stderr.log | 必须存在（可为空） | 文件存在检查 |
| audit_event.json | 必须存在且包含审计轨迹 | JSON 验证 |

**验收标准**:
- ✅ 四件套全部存在
- ✅ execution_receipt 包含必需字段
- ✅ audit_event 包含完整的审计轨迹

**证据文件**: `docs/2026-03-04/verification/N+2_artifact_completeness_verification.json`

---

### N+3: 时间窗口执行限制

**目标**: 确保云端执行在合理时间窗口内完成

| 组件 | 要求 | 验证方式 |
|------|------|----------|
| max_duration_sec | 最大执行时长限制 | execution_receipt.time_elapsed |
| max_commands | 最大命令数量限制 | execution_receipt.executed_commands |
| 超时检测 | 超时立即中止并报告 | 实时监控 |

**验收标准**:
- ✅ 实际执行时间 ≤ max_duration_sec
- ✅ 实际命令数量 ≤ max_commands
- ✅ 超时任务正确中止

**证据文件**: `docs/2026-03-04/verification/N+3_time_window_enforcement.json`

---

## 执行流程

```
N+1 → 验证命令白名单 → ALLOW/DENY
  ↓
N+2 → 验证四件套完整性 → ALLOW/DENY
  ↓
N+3 → 验证时间窗口 → ALLOW/DENY
  ↓
全过 → 增量边界上线
任一不过 → 保持原状，修补后重试
```

---

## 当前状态

| 边界 | 状态 | 说明 |
|------|------|------|
| N+1 | 待上线 | 命令白名单强制验证 |
| N+2 | 待上线 | 四件套完整性验证 |
| N+3 | 待上线 | 时间窗口执行限制 |

---

## 下一步

1. 实现 N+1 验证逻辑
2. 实现 N+2 验证逻辑
3. 实现 N+3 验证逻辑
4. 每个边界独立运行并归档
5. 全部通过后归档到 verification_index

---

**策略**: 增量式安全，每轮独立验证，FAIL_CLOSED 保护**
