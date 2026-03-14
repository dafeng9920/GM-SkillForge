---
name: lobster-cloud-execution-governor-skill
description: 让小龙虾在云端按冻结合同做受控编码开发，并在 token 限额、上下文溢出、任务中断时自动进入 checkpoint -> handoff -> recovery -> resume 闭环；执行臂可开发，不可裁决。
---

# lobster-cloud-execution-governor-skill

## 目标

把小龙虾固定为 **CLOUD-ROOT 受控执行开发臂**：

`冻结任务合同 -> 云端执行编码/测试 -> 回传执行证据 -> 本地 review/compliance -> 如遇 token/上下文中断则 checkpoint + 复活续跑`

这不是自治发布 skill，而是 **fail-closed 的云端开发执行 skill**。

## 小龙虾能做什么

- 按 `task_contract` / `execution_receipt` / `frozen scope` 做代码实现
- 修改合同允许范围内的文件
- 运行合同允许的命令
- 产出：
  - `execution_receipt.json`
  - `stdout.log`
  - `stderr.log`
  - `audit_event.json`
  - `completion_record.md`
  - `resume_handoff.md`
- 在 token 限额或上下文溢出前主动保存 checkpoint
- 读取既有上下文并继续未完成任务

## 小龙虾不能做什么

- 不能自己签发 permit
- 不能自己写 final gate = ALLOW
- 不能替 reviewer / compliance officer 下结论
- 不能绕过 `task_contract`
- 不能擅自扩 scope
- 不能把“代码已完成”包装成“可以发布”
- 不能只靠聊天记忆恢复任务，必须回到落盘证据

## 适用场景

- 云端需要连续编码开发，而本地不想一直盯
- 任务可能跨多轮、多次会话完成
- OpenClaw / 小龙虾可能遇到：
  - `model_context_window_exceeded`
  - token 接近上限
  - 会话中断
  - 容器重启
  - 人工暂停后次日续跑

## 依赖的现有 skill / 组件

执行此 skill 时，默认联动以下现有能力：

- `cloud-lobster-closed-loop-skill`
  - 负责 task contract、四件套回传、本地 review/final gate
- `openclaw-cloud-bridge-skill`
  - 负责云端 task contract / receipt 边界
- `openclaw-runtime-recovery-skill`
  - 负责 `model_context_window_exceeded`、容器异常、权限/端口故障恢复
- `openclaw-memory-cron-skill`
  - 负责定时清理历史上下文
- `budget-guard-skill`
  - 负责 token / duration 熔断

## 输入

```yaml
input:
  task_id: "m2-feature-20260307-001"
  objective: "实现指定功能并补测试"
  contract_path: ".tmp/openclaw-dispatch/<task_id>/task_contract.json"
  repo_root: "/root/openclaw-box"
  allowed_paths:
    - "skillforge/src/**"
    - "skillforge/tests/**"
    - "docs/**"
  allowed_commands:
    - "pytest skillforge/tests/test_xxx.py"
    - "python scripts/xxx.py"
  max_tokens_per_session: 200000
  warning_threshold_pct: 80
  hard_stop_threshold_pct: 92
  checkpoint_dir: ".tmp/openclaw-dispatch/<task_id>/checkpoint"
  handoff_note_path: ".tmp/openclaw-dispatch/<task_id>/resume_handoff.md"
```

## 输出

```yaml
output:
  status: "EXECUTED|PARTIAL|RECOVERED|BLOCKED|FAILED"
  task_state: "DONE|INTERRUPTED|READY_TO_RESUME|WAITING_REVIEW"
  changed_files:
    - "skillforge/src/..."
  last_completed_step: "edit|test|artifact_freeze|handoff_written"
  remaining_work:
    - "补剩余单测"
    - "等待 reviewer 决定"
  evidence_refs:
    - ".tmp/openclaw-dispatch/<task_id>/execution_receipt.json"
    - ".tmp/openclaw-dispatch/<task_id>/resume_handoff.md"
  recovery_action:
    - "clear_memory"
    - "reload_context"
    - "resume_from_checkpoint"
```

## 执行总原则

### 1. 先读合同，再动手

必须先读取：

- `task_contract.json`
- 最近一次 `execution_receipt.json`（如果存在）
- 最近一次 `completion_record.md`（如果存在）
- 最近一次 `resume_handoff.md`（如果存在）

如果这四类文件不存在，按“首轮执行”处理；若存在，则按“续跑”处理。

### 2. 只信落盘证据，不信纯会话记忆

续跑时的 authoritative context 只来自：

1. `task_contract.json`
2. `execution_receipt.json`
3. `resume_handoff.md`
4. `completion_record.md`
5. 真实代码工作树状态

不允许只凭聊天上下文猜测任务做到哪。

### 3. 任何中断都要写 handoff

出现以下任一情况，必须先写 `resume_handoff.md` 再退出：

- token 使用达到 `warning_threshold_pct`
- 检测到 `model_context_window_exceeded`
- 任务执行超过约定时长
- 云端容器 / agent 即将重启
- 人工决定暂停

## 标准流程

### Step 1. 预检与上下文装载

1. 读取 `task_contract.json`
2. 检查 `allowed_paths` 与 `allowed_commands`
3. 如果存在历史产物，装载：
   - `execution_receipt.json`
   - `completion_record.md`
   - `resume_handoff.md`
4. 形成当前任务状态：
   - 已完成什么
   - 未完成什么
   - 下一步应该做什么

### Step 2. 编码开发执行

只允许做三类事：

- 改合同允许范围内的代码 / 文档 / 测试
- 跑合同允许的验证命令
- 生成执行证据与状态文件

如果任务超出合同：

- 立即停止
- 在 `resume_handoff.md` 标明 `scope_blocked=true`
- 回传 `BLOCKED`

### Step 3. 持续 checkpoint

每完成一个实质步骤都要记录：

- 已修改文件列表
- 已执行命令
- 命令结果摘要
- 当前剩余工作
- 是否可进入下一步

建议 checkpoint 最小粒度：

- 一次代码编辑完成
- 一次测试完成
- 一次产物冻结完成

### Step 4. Token / 上下文熔断与恢复

#### 4.1 预警阈值

达到 `warning_threshold_pct` 时：

- 立即停止新增大段推理
- 写 `resume_handoff.md`
- 写 `checkpoint/state.yaml`
- 压缩上下文为“任务事实摘要”

#### 4.2 硬停止阈值

达到 `hard_stop_threshold_pct` 或已出现 `model_context_window_exceeded` 时：

1. 触发 `budget-guard-skill`
2. 若为 OpenClaw 记忆膨胀：
   - 运行 `openclaw-runtime-recovery-skill`
   - 必要时执行 `scripts/clear_openclaw_memory.sh`
3. 写清以下字段到 handoff：
   - `last_completed_step`
   - `changed_files`
   - `pending_commands`
   - `remaining_work`
   - `resume_entrypoint`

#### 4.3 自动读取上下文并复活

新会话 / 新轮次恢复时，按以下顺序读取：

1. `task_contract.json`
2. `resume_handoff.md`
3. `checkpoint/state.yaml`
4. `execution_receipt.json`
5. git diff / 当前工作树

恢复后必须先回答 5 个问题，再继续编码：

1. 当前任务目标是什么
2. 已经完成了什么
3. 哪些文件已经改动
4. 上一轮停在什么步骤
5. 下一步唯一允许的动作是什么

不能回答清楚这 5 个问题，就不能继续执行。

### Step 5. 执行完成后的回传

至少回传：

- `execution_receipt.json`
- `stdout.log`
- `stderr.log`
- `audit_event.json`
- `completion_record.md`
- `resume_handoff.md`（若任务未完全结束则必须存在）

## resume_handoff 必须包含的字段

参考模板：
`references/resume_handoff_template.md`

最小字段：

```yaml
task_id: "..."
contract_ref: "..."
status: "INTERRUPTED|READY_TO_RESUME|WAITING_REVIEW|DONE"
last_completed_step: "..."
changed_files:
  - "..."
executed_commands:
  - "..."
remaining_work:
  - "..."
blocked_by:
  - "scope"
  - "token_budget"
resume_entrypoint: "先读 X 文件，再跑 Y 命令"
review_boundary:
  reviewer_required: true
  compliance_required: true
```

## 自动续跑判定

满足以下条件才允许自动续跑：

- `task_contract.json` 仍然有效
- 没有 reviewer/compliance 明确 DENY
- `resume_handoff.md.status == READY_TO_RESUME`
- 剩余工作仍在原合同范围内

以下情况不允许自动续跑，必须转人工：

- 合同变化
- 任务 scope 已扩张
- 已进入 review / compliance 决策阶段
- 上轮 handoff 记录 `blocked_by=scope`
- 关键测试连续失败且根因不清

## DoD

- [ ] 明确区分“执行臂”与“裁决臂”
- [ ] 所有执行均受 `task_contract` 限制
- [ ] 遇到 token / context 风险时会先写 checkpoint 与 handoff
- [ ] 新会话能从落盘证据自动恢复上下文
- [ ] 未完成任务能按 `resume_entrypoint` 继续
- [ ] 不会在 pending 状态下伪装 PASS / final close

## 失败即阻断的红线

- 没有 `task_contract.json` 直接执行
- 没写 `resume_handoff.md` 就退出
- 只靠聊天记忆续跑
- 擅自改合同外文件
- 擅自签 permit / final gate
- completion record 中混入 review/compliance 结论

## 参考

- 云端闭环：`skills/cloud-lobster-closed-loop-skill/SKILL.md`
- 云端桥接：`skills/openclaw-cloud-bridge-skill/SKILL.md`
- 运行恢复：`skills/openclaw-runtime-recovery-skill/SKILL.md`
- 定时清理：`skills/openclaw-memory-cron-skill/SKILL.md`
- token 熔断：`skills/budget-guard-skill/SKILL.md`
- handoff 模板：`references/resume_handoff_template.md`
- 串行队列：`references/overnight_serial_queue_protocol.md`
