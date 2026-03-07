# Lobster Overnight Shift Plan

## 时间窗口

- 开始时间: `2026-03-07 23:07`
- 主控重新上线时间: `2026-03-08 18:30`
- 总窗口: 约 `19.5` 小时

## 总目标

本次不是追求“大而全”，而是保证：

1. 小龙虾在云端持续推进，不因主控离线而停工
2. 任何中断都能留下 handoff，次日可恢复
3. 不做假闭环，不越权，不擅自扩 scope

## 总策略

本窗口只允许：

- `1` 个主开发任务
- `1` 个低风险备选收尾任务

禁止：

- 同时并发多个开发主任务
- 跨模块大改
- 追加新需求
- 在 `17:30` 之后开启新开发任务

## 分工

- 主控官: `Codex / LOCAL-ANTIGRAVITY`
- 云端执行臂: `小龙虾 / CLOUD-ROOT`
- 审查: 次日由 `Kior-C` 接手
- 合规: 次日由 `Antigravity-*` 接手

## 任务容量上限

### 主任务容量

- 修改文件数: `3-6`
- 允许命令数: `2-4`
- 测试范围: 仅目标测试或单模块测试
- 预期工作量: `4-6` 小时有效开发

### 备选任务容量

- 修改文件数: `1-3`
- 类型限定:
  - 补测试
  - 补文档
  - 补 execution report / completion record / evidence mapping
- 不允许新功能扩张

## 班次切分

### Phase 0. 预检与冻结

- 时间: `23:07 - 23:40`
- 目标:
  - 只做预检
  - 读取合同
  - 装载上下文
  - 明确唯一主任务

必须完成：

- `task_contract.json` 已冻结
- `allowed_paths` 已冻结
- `allowed_commands` 已冻结
- `resume_handoff.md` 初始版本已创建
- 当前任务被标记为 `MAIN_TASK`

### Phase 1. 夜间主执行窗口

- 时间: `23:40 - 06:30`
- 目标:
  - 只推进主任务
  - 不开第二主任务

允许动作：

- 改合同范围内文件
- 跑允许命令
- 记录 checkpoint
- 写 `execution_receipt`

硬规则：

- 每完成一个实质步骤就写一次 checkpoint
- 一旦接近 token 阈值，先写 handoff 再继续
- 如遇 scope 漂移，立即 `BLOCKED`

### Phase 2. 强制 handoff 窗口

- 时间: `06:30 - 08:00`
- 目标:
  - 不管任务是否完成，都必须落一次完整 handoff

必须更新：

- `resume_handoff.md`
- `checkpoint/state.yaml`
- `execution_receipt.json`
- `changed_files`
- `remaining_work`

### Phase 3. 白天备选任务窗口

- 时间: `08:00 - 17:30`
- 前提:
  - 主任务已完成或已进入 `WAITING_REVIEW`

只允许做：

- 备选任务 A: 补测试
- 备选任务 B: 补文档 / 补回传 / 补 evidence

禁止：

- 新开复杂功能
- 改动主任务合同之外的范围

### Phase 4. 收口冻结窗口

- 时间: `17:30 - 18:30`
- 目标:
  - 停止新开发
  - 只整理产物与 handoff

只允许做：

- 更新 `resume_handoff.md`
- 更新 `completion_record.md`
- 整理 `execution_receipt.json`
- 标记 `READY_TO_RESUME` 或 `WAITING_REVIEW`

## 自动转移规则

### 从主任务转入备选任务

只有同时满足以下条件，才允许自动进入备选任务：

- 主任务状态为 `DONE` 或 `WAITING_REVIEW`
- 目标测试已跑完
- 当前 handoff 已落盘
- 备选任务明确写在合同的 `secondary_allowed_work` 中

### 立即停止条件

出现以下任一条件，立即停止并写 handoff：

- `model_context_window_exceeded`
- token 达到 `hard_stop_threshold_pct`
- 合同外需求出现
- 测试失败根因不清且连续卡住
- 容器 / agent 异常

## 产物要求

本窗口结束前，至少应存在：

- `task_contract.json`
- `execution_receipt.json`
- `stdout.log`
- `stderr.log`
- `audit_event.json`
- `completion_record.md`
- `resume_handoff.md`
- `checkpoint/state.yaml`

## 次日上线后的接手顺序

主控上线后按这个顺序接手：

1. 读 `task_contract.json`
2. 读 `resume_handoff.md`
3. 读 `checkpoint/state.yaml`
4. 看 `execution_receipt.json`
5. 看工作树和测试结果
6. 再决定是：
   - 继续执行
   - 转 review
   - 转 compliance
   - 直接 BLOCK

## 成功标准

本窗口算成功，不要求“全部完成”，只要求：

1. 主任务持续推进，没有因为主控离线而停摆
2. 任一中断都留下可续跑 handoff
3. 次日 `18:30` 主控可直接恢复，不需要重新摸索上下文

## 失败标准

以下任一出现，即判本窗口排班失败：

- 没有 handoff 就退出
- 合同外修改
- 执行者写 reviewer/compliance 结论
- 任务做了一半但没有留下恢复入口
- 在 `17:30` 后仍然开新开发任务
