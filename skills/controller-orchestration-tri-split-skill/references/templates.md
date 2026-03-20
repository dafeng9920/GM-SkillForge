# controller-orchestration-tri-split 模板

## 1. 主控官速览模板

```md
## 主控官速览

### 当前模块
- 模块名：...
- 当前阶段：...
- 当前目标：...

### 本轮缺口
| Task | 缺口类型 | 执行人 | 必须写回 |
|---|---|---|---|
| T1 | Review | ... | `.../T1_review_report.md` |
| T1 | Compliance | ... | `.../T1_compliance_attestation.md` |

### 主控官一句话判断标准
- 上表全部补齐，才算能进入终验
```

## 2. 任务总表模板

```md
| Task | Scope | Execution | Review | Compliance | 并行/串行 | 目标 | 状态 |
|---|---|---|---|---|---|---|---|
| T1 | ... | ... | ... | ... | 并行（第一波） | ... | 未开始 |
| T2 | ... | ... | ... | ... | 串行（依赖 T1） | ... | 未开始 |
```

表下必须再补：
- 统一回收路径
- Codex 回收规则
- 当前主控裁决
- 当前波次 / 下一波次放行条件

## 2.1 Task Envelope 模板

```yaml
task_envelope:
  task_id: "T1"
  module: "module_name"
  role: "execution"
  assignee: "vs--cc1"
  depends_on: []
  parallel_group: "PG-01"
  source_of_truth:
    - "docs/.../MODULE_SCOPE.md"
    - "docs/.../MODULE_BOUNDARY_RULES.md"
  writeback:
    execution_report: "docs/.../verification/T1_execution_report.md"
    review_report: "docs/.../verification/T1_review_report.md"
    compliance_attestation: "docs/.../verification/T1_compliance_attestation.md"
    final_gate: "docs/.../verification/T1_final_gate.md"
  acceptance_criteria:
    - "all required files exist"
    - "no scope violation"
  hard_constraints:
    - "no runtime"
    - "no frozen mutation"
  escalation_trigger:
    - "scope_violation"
    - "blocking_dependency"
    - "ambiguous_spec"
  next_hop: "review"
```

## 3. 任务卡模板

```md
# 任务 T{N}

## 唯一事实源
- ...

## 角色
- Execution: ...
- Review: ...
- Compliance: ...

## Task Envelope
```yaml
task_envelope:
  task_id: "T{N}"
  module: "..."
  role: "execution"
  assignee: "..."
  depends_on: []
  parallel_group: "PG-01"
  source_of_truth:
    - "..."
  writeback:
    execution_report: "..."
    review_report: "..."
    compliance_attestation: "..."
    final_gate: "..."
  acceptance_criteria:
    - "..."
  hard_constraints:
    - "..."
  escalation_trigger:
    - "scope_violation"
  next_hop: "review"
```

## 目标
- ...

## 禁止项
- ...

## 并行 / 串行依赖
- ...

## 标准写回路径
- execution: `.../T{N}_execution_report.md`
- review: `.../T{N}_review_report.md`
- compliance: `.../T{N}_compliance_attestation.md`

## 发给 Execution 的提示词
...

## 发给 Review 的提示词
...

## 发给 Compliance 的提示词
...
```

## 4. Review 提示词模板

```text
你是任务 T{N} 的审查者 {reviewer}。

你只做 review，不做 execution，不做 compliance。

必须写入：
- `.../T{N}_review_report.md`

必须包含：
1. task_id
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. 审查重点
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

## 5. Compliance 提示词模板

```text
你是任务 T{N} 的合规官 {compliance_officer}。

你只做 B Guard 式硬审。

必须写入：
- `.../T{N}_compliance_attestation.md`

必须包含：
1. task_id
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

## 6. Final Gate 检查清单

主控官终验前只检查：
1. 是否有完整 `execution / review / compliance`
2. 依赖顺序是否满足
3. 是否有阻断性越界问题
4. 模块报告是否和当前事实一致
5. 任务板状态是否和回收件一致

缺任一项，不终验。

## 7. 默认状态流转清单

```text
PENDING
  -> ACCEPTED
  -> IN_PROGRESS
  -> WRITEBACK_DONE
  -> REVIEW_TRIGGERED
  -> REVIEW_DONE
  -> COMPLIANCE_TRIGGERED
  -> COMPLIANCE_DONE
  -> GATE_READY
```

## 8. 默认升级包模板

```yaml
escalation:
  task_id: "T1"
  current_role: "review"
  current_state: "BLOCKED"
  trigger: "blocking_dependency"
  blocking_reason: "..."
  evidence_ref: "path:line"
  suggested_next_action: "..."
```
