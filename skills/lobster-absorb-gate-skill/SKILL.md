---
name: lobster-absorb-gate-skill
description: 用于在云端任务包从 dropzone 吸收到主仓前执行门禁检查，确保 manifest 白名单、路径安全、关键件完整、review/compliance 状态明确，并严格区分 pre-absorb check 与本地最终业务验收。适用于所有云端任务包的吸收前检查与主控吸收流程。
---

# lobster-absorb-gate-skill

## 目标

把吸收动作变成 **受控门禁**，而不是“看起来差不多就拷进主仓”。

## 作用范围

只负责：

- `pre_absorb_check`
- 路径安全检查
- manifest 白名单检查
- 关键件完整性检查
- reviewer/compliance 状态检查

不负责：

- 最终业务验收
- final gate
- permit 批准

## 输入

至少需要：

- `dropzone/<task_id>/manifest.json`
- `dropzone/<task_id>/completion_record.md`
- `dropzone/<task_id>/logs/`
- `dropzone/<task_id>/evidence/`

如果是需要 resume 的任务，还应有：

- `checkpoint/state.yaml`
- `resume_handoff.md`
- `execution_receipt.json`

## pre_absorb_check 必查项

### 1. 路径安全

- 所有文件都在 `dropzone/<task_id>/` 之下
- 不允许 `..`、绝对路径逃逸、系统目录写入

### 2. manifest 白名单

只吸收：

- `manifest.json` 中 `artifacts` 与 `evidence` 明确列出的文件

manifest 外文件默认不吸收。

### 3. 关键件完整性

缺任一关键件，直接阻断：

- `blueprint.md`
- `risk_statement.md`
- `changes.diff`
- `test_report.md`
- `completion_record.md`
- `manifest.json`

文档型交付至少要有：

- `execution_receipt.json`
- `completion_record.md`
- `resume_handoff.md`
- `checkpoint/state.yaml`

### 4. 签署与状态

吸收前至少要能判断：

- 是否已 `WAITING_REVIEW`
- reviewer 是否已给明确结论
- compliance 是否已给明确结论

没有清楚状态，不得 absorb。

## 吸收动作定义

吸收成功只表示：

- 交付包格式合格
- 路径安全
- 关键件齐
- 主仓可见

吸收成功不表示：

- 业务逻辑正确
- 风险可接受
- 可以发布

## 本地最终裁决

最终结论必须由本地 Codex / controller 作出。

标准状态建议：

- `ABSORB_READY`
- `ABSORBED_PENDING_LOCAL_ACCEPT`
- `CLOSED`
- `DENIED`

## 红线

- 不允许把 `pre_absorb_check PASS` 写成 `final pass`
- 不允许吸收 manifest 外文件
- 不允许无 reviewer/compliance 结论就伪装 close

## 参考

- `docs/2026-03-08/DOCKER_VOLUME_桥接实施包_v1.md`
- `docs/2026-03-08/CLOUD_MULTI_AGENT_OVERSIGHT_PROTOCOL_v1.md`
- `skills/lobster-task-package-skill/SKILL.md`
