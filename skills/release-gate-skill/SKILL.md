# release-gate-skill

> 版本: v1.2.0
> 冻结时间: 2026-02-18
> 继承自: Phase-1 业务意图运行
> 增强: 支持批量发布、Canary 发布

---

## 触发条件

- **Canary 发布**: `release_type=canary` - 金丝雀发布前检查
- **Batch 发布**: `release_type=batch` - 批量发布前检查
- **单目标发布**: `release_type=single` - 单目标发布前检查
- **Hotfix 发布**: `release_type=hotfix` - 热修复发布前检查
- 需要 Fail-Closed 保障
- 需要 Permit 强约束验证

---

## 输入契约

```yaml
input:
  # 核心输入
  run_id: string              # 运行ID（必填，格式: run-YYYYMMDD-HHMMSS-xxxx）
  permit_refs: array          # Permit 引用列表（必填）
    - permit_id: string
      issued_at: string
      issued_by: string
      scope: string

  # 目标配置
  targets: array              # 发布目标列表（必填）
    - target_id: string
      target_type: string     # skill | service | function
      version: string

  # 仓库信息
  repo_url: string            # 仓库URL（必填）
  commit_sha: string          # 提交SHA（必填）

  # 发布配置
  release_type: string        # canary | batch | single | hotfix | rollback（必填）
  strategy: string            # all-or-nothing | best-effort | canary-first（默认: all-or-nothing）
  gate_profile: string        # standard | fast | comprehensive | custom（默认: standard）

  # 可选
  skip_gates: array           # 跳过的门禁（需要特殊 permit）
  timeout_seconds: int        # 超时时间（默认: 300）
```

---

## 输出契约

```yaml
output:
  # 核心决策
  gate_decision:
    decision_id: string          # 决策唯一 ID
    decision: string             # ALLOWED | DENIED | CONDITIONAL
    decided_at: string           # 决策时间
    decided_by: string           # 决策者

  release_allowed: bool          # 是否允许发布
  overall_status: string         # PASS | FAIL | PARTIAL

  # 目标级别结果
  passed_targets: array          # 通过的目标列表
    - target_id: string
      gate_results: array

  failed_targets: array          # 失败的目标列表
    - target_id: string
      error_code: string
      error_message: string
      gate_failed: string

  # 统计信息
  validation_latency_ms: int     # 校验延迟
  gates_passed: int              # 通过门禁数
  gates_failed: int              # 失败门禁数

  # 证据引用
  evidence_ref: string           # 证据引用
  execution_report_path: string  # 执行报告路径
```

---

## Fail-Closed 条件

| 条件 | 行为 |
|------|------|
| permit_refs == null 或空 | gate_decision=DENIED, error_code=E001 |
| permit 签名无效 | gate_decision=DENIED, error_code=E003 |
| permit 已过期 | gate_decision=DENIED, error_code=E004 |
| permit 已撤销 | gate_decision=DENIED, error_code=E007 |

**核心约束**: no-permit-no-release

---

## 发布策略

### All-or-Nothing (默认)

**适用**: Canary 发布、关键批量发布

```yaml
strategy: all-or-nothing
behavior:
  - 所有目标必须全部通过门禁
  - 任一目标失败 → 整体 DENIED
  - 保证原子性
  - 单目标失败 → 全部阻断
```

**阻断矩阵**:
| 目标1 | 目标2 | 结果 |
|-------|-------|------|
| PASS | PASS | ALLOW |
| PASS | FAIL | DENIED |
| FAIL | PASS | DENIED |
| FAIL | FAIL | DENIED |

### Best-Effort

**适用**: 非关键更新、渐进式发布

```yaml
strategy: best-effort
behavior:
  - 通过的目标继续发布
  - 失败的目标被排除
  - 返回 PARTIAL 状态
  - 无目标通过 → DENIED
```

### Canary-First

**适用**: 灰度发布

```yaml
strategy: canary-first
behavior:
  - 第一个目标作为 Canary 必须通过
  - Canary 失败 → 整体 DENIED
  - Canary 通过 → 其他目标使用 best-effort
```

---

## Gate 链顺序

| 顺序 | Gate | 说明 | 阻断级别 |
|------|------|------|----------|
| 1 | Gate Permit | Permit 校验 | CRITICAL |
| 2 | Gate Risk Level | 风险等级 (L2) | HIGH |
| 3 | Gate Rollback Ready | 回滚就绪 | HIGH |
| 4 | Gate Monitor Threshold | 监控阈值 | MEDIUM |
| 5 | Gate Target Locked | 目标锁定 | HIGH |

**批量执行**: 每个目标独立执行 Gate 链，然后按策略聚合结果

---

## Evidence 字段要求

```yaml
evidence:
  run_id: string           # 必须贯穿全链路
  permit_id: string        # 关联 Permit
  replay_pointer: string   # 回放指针
  targets:
    - target_id: string
      gate_results:        # 各 Gate 结果
        - gate_name: string
          status: PASS | FAIL
          duration_ms: int
          error_code: string | null
  final_decision: string   # 最终决策
  strategy_used: string    # 使用的策略
```

---

## 错误码（不可修改语义）

| 错误码 | 语义 | release_allowed | 阻断类型 |
|--------|------|-----------------|----------|
| E001 | PERMIT_REQUIRED | false | 全局阻断 |
| E002 | PERMIT_INVALID_FORMAT | false | 全局阻断 |
| E003 | PERMIT_INVALID_SIGNATURE | false | 全局阻断 |
| E004 | PERMIT_EXPIRED | false | 全局阻断 |
| E005 | PERMIT_SCOPE_MISMATCH | false | 目标阻断 |
| E006 | PERMIT_SUBJECT_MISMATCH | false | 目标阻断 |
| E007 | PERMIT_REVOKED | false | 全局阻断 |
| E008 | GATE_CHAIN_FAILED | false | 目标阻断 |
| E009 | TARGET_NOT_FOUND | false | 目标阻断 |

---

## 批量场景阻断矩阵

### E001 (No Permit) 阻断

| 场景 | 目标数 | E001 触发 | 结果 |
|------|--------|-----------|------|
| Canary | 1 | 是 | DENIED (全局) |
| Batch (2目标) | 2 | 是 | DENIED (全局) |
| Batch (N目标) | N | 是 | DENIED (全局) |

**说明**: E001 是全局阻断，任何目标触发都会导致整个发布被拒绝

### E003 (Invalid Signature) 阻断

| 策略 | 目标1 | 目标2 | 结果 |
|------|-------|-------|------|
| all-or-nothing | E003 | - | DENIED (全局) |
| all-or-nothing | PASS | E003 | DENIED (全局) |
| best-effort | E003 | PASS | PARTIAL (目标1排除) |
| best-effort | PASS | E003 | PARTIAL (目标2排除) |
| canary-first | E003 | - | DENIED (Canary失败) |

**说明**: E003 在 all-or-nothing 策略下是全局阻断，在 best-effort 下是目标阻断

---

## 验证步骤

### 单目标发布

1. **Permit 校验**: permit_refs 存在且有效
2. **签名验证**: 验证 JWT 签名
3. **过期检查**: 未超过 expires_at
4. **Scope 匹配**: permit.scope 包含请求动作
5. **Gate 链执行**: 按顺序执行 5 Gate
6. **证据生成**: 生成 EvidenceRef
7. **决策输出**: gate_decision + release_allowed

### 批量发布 (2目标示例)

1. **全局 Permit 校验**: 检查 permit_refs 覆盖所有目标
2. **目标1 Gate 链执行**: 独立执行 5 Gate，记录结果
3. **目标2 Gate 链执行**: 独立执行 5 Gate，记录结果
4. **策略聚合**: 按 strategy 聚合结果
5. **证据生成**: 生成批量 EvidenceRef
6. **决策输出**: gate_decision + passed_targets + failed_targets

---

## 实现引用

- **实现文件**: `skillforge/src/skills/gates/gate_permit.py`
- **契约文件**: `docs/2026-02-18/contracts/permit_contract_v1.yml`
- **验收报告**: `docs/2026-02-18/permit_gate_implementation_report_v1.md`
- **检查清单**: `references/release-gate-checklist.md`
- **错误矩阵**: `references/error-branch-matrix.md`

---

## 验收标准

- [ ] T1-T9 测试全部通过（19/19）
- [ ] 错误码 E001-E009 覆盖
- [ ] E001 阻断成立（no permit -> release_allowed=false）
- [ ] E003 阻断成立（bad signature -> release_allowed=false）
- [ ] EvidenceRef 生成正确
- [ ] 2目标批量发布演练通过
- [ ] all-or-nothing 策略验证
- [ ] best-effort 策略验证

---

## 最小演练步骤 (2目标)

### 场景 1: 全部通过 (all-or-nothing)

```yaml
# 输入
run_id: "run-20260218-160000-test"
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
  - permit_id: "perm-20260218-155500"
    issued_at: "2026-02-18T15:55:00Z"
    issued_by: "test@example.com"
    scope: "release:skill:*"

# 预期输出
gate_decision:
  decision: ALLOWED
release_allowed: true
overall_status: PASS
passed_targets: ["skill-mean-reversion", "skill-momentum"]
failed_targets: []
```

### 场景 2: 目标2失败 (all-or-nothing)

```yaml
# 输入
run_id: "run-20260218-161000-test"
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
  - permit_id: "perm-20260218-160500"
    issued_at: "2026-02-18T16:05:00Z"
    issued_by: "test@example.com"
    scope: "release:skill:*"

# 预期输出
gate_decision:
  decision: DENIED
release_allowed: false
overall_status: FAIL
passed_targets: []
failed_targets:
  - target_id: "skill-invalid"
    error_code: "E009"
    error_message: "Target not found"
    gate_failed: "gate_target_locked"
```

### 场景 3: 无 Permit (E001)

```yaml
# 输入
run_id: "run-20260218-162000-test"
release_type: "batch"
targets:
  - target_id: "skill-mean-reversion"
    target_type: "skill"
    version: "1.0.0"
  - target_id: "skill-momentum"
    target_type: "skill"
    version: "1.0.0"
permit_refs: []  # 空 permit

# 预期输出
gate_decision:
  decision: DENIED
release_allowed: false
overall_status: FAIL
error_code: "E001"
release_blocked_by: "PERMIT_REQUIRED"
```

---

## 证据引用路径

执行报告路径格式:
```
reports/{run_id}/gate-report.json
reports/{run_id}/evidence.jsonl
reports/{run_id}/decision.json
```

示例:
- `reports/run-20260218-160000-test/gate-report.json`
- `reports/run-20260218-160000-test/evidence.jsonl`

---

## L4 Integration Mode (Frontend-Backend Merge)

> 此模式为 L4 前后端合并联调专用，不影响原有 release-gate 主流程。

### Trigger

触发关键词:
- `L4 merge`
- `front-back integration`
- `A/B/C/D scenarios`
- `frontend backend contract`

### Required Inputs

```yaml
input:
  # 核心输入
  repo_url: string            # 仓库URL（必填）
  commit_sha: string          # 提交SHA（必填）
  at_time: string             # 时间戳（可选，默认当前时间）
  requester_id: string        # 请求者ID（必填）

  # 可选 LLM 配置
  llm_provider: string        # openai | mock（默认: mock）
  llm_model: string           # 模型名称
```

### Fixed 5-Step Flow

1. **Contract Freeze** - 冻结前后端契约
2. **Generate** - `/api/v1/cognition/generate` → 10d cognition
3. **Adopt** - `/api/v1/work/adopt` → work item
4. **Execute** - `/api/v1/work/execute` → permit validation
5. **Merge Gate Writeback** - 写入验收清单

### Fail-Closed Rules

| 场景 | 错误码 | release_allowed |
|------|--------|-----------------|
| No permit | E001 | false |
| Bad signature | E003 | false |
| Missing LLM config | L4_LLM_CONFIG_MISSING | false |
| LLM API failed | L4_LLM_CALL_FAILED | false |

**核心约束**: 无 permit 禁止发布，签名无效禁止发布

### Acceptance

- [ ] 场景 A: 正常链路 Generate → Adopt → Execute → `ok=true`
- [ ] 场景 B: 无 Permit (E001) → `error_code=E001`
- [ ] 场景 C: 坏签名 (E003) → `error_code=E003`
- [ ] 场景 D: Mock LLM 成功 → `dimensions=10`
- [ ] `run_id` + `evidence_ref` 非空
- [ ] `tests/test_l4_api_smoke.py` 全部通过
- [ ] Final: `READY_FOR_L4_MERGE=YES`

### Output Artifacts

| 文件 | 用途 |
|------|------|
| `docs/2026-02-19/L4/frontend_backend_contract_freeze_v1.md` | 契约冻结文档 |
| `docs/2026-02-19/L4/l4_front_backend_integration_report_v1.md` | 联调报告 |
| `docs/2026-02-19/L4/L4_Merge_Gate_最终验收清单_v1.md` | Merge Gate 清单 |
| `docs/2026-02-19/L4/l4_llm_integration_report_v1.md` | LLM 集成报告 |

---

## Experience Capture Mode (L4.5 Governance Baseline)

> 该模式不是“自动改代码/自训练”，仅做可复核经验沉淀与模板检索。

### Trigger

满足任一条件即触发经验捕获:

- 8 Gate 任一节点 `PASS/FAIL`
- 发生修复动作（`APPLY_PATCH` / `UPDATE_SCAFFOLD`）
- `sandbox_test_and_trace` 产出关键日志
- `pack_audit_and_publish` 完成打包

### Capture Contract

```yaml
capture_experience:
  issue_key: string              # 必填，问题归一键
  evidence_ref: string | null    # 必填语义；为空时按 MISSING_EVIDENCE 拒收
  gate_node: string              # 必填，发生门节点
  summary: string                # 必填，一句话经验摘要
  fix_kind: string               # 必填，枚举:
                                 # ADD_CONTRACT | ADD_TESTS | UPDATE_SCAFFOLD
                                 # APPLY_PATCH | PUBLISH_PACK | GATE_DECISION
  content_hash: string           # 自动生成（去重）
```

### Retrieval Contract

```yaml
retrieve_templates:
  issue_key: string | null       # 精确匹配或前缀匹配（支持 "SCAFFOLD-*"）
  fix_kind: string | null        # FixKind 过滤
  gate_node: string | null       # Gate 节点过滤
  limit: int                     # 默认 5，返回最近优先

output:
  experience_templates: array
```

### Fail-Closed Rules

| 条件 | 行为 |
|------|------|
| `evidence_ref` 缺失 | 标记 `MISSING_EVIDENCE`，仅写入 `rejected_entries`，不得进入已固化经验 |
| `fix_kind` 非法值 | 自动降级为 `GATE_DECISION` 并保留原始上下文 |
| `content_hash` 重复 | `SKIPPED_DUPLICATE`，不重复写入 |

### 固化产物

- `AuditPack/experience/evolution.json`：append-only 机器可读经验库
- `AuditPack/experience/SKILL.md`：人类可读聚合摘要
- 在 `pack_audit_and_publish` 阶段进入 L3 AuditPack（作为审计产物的一部分）

### Consumption Rules

- `audit_skill_pack` 在 gate 前检索历史模板，输出建议修复上下文。
- `scaffold_skill_impl` 读取 `IssueKey/FixKind` 模板（当前默认: `SCAFFOLD-*` + `UPDATE_SCAFFOLD`）。
- `required_changes` 结构与措辞保持统一，降低整改漂移。

### 实现引用

- `skillforge/src/skills/experience_capture.py`
- `skillforge/src/skills/gates/gate_scaffold.py`
- `tests/gates/test_experience_capture.py`
- `tests/gates/test_experience_template_reader_integration.py`
