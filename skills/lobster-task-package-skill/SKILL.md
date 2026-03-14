---
name: lobster-task-package-skill
description: 用于强制小龙虾或其他云端 executor 按 dropzone/<task_id>/ 生成可审计任务包，而不是直接改主仓或口头播报完成。适用于云端执行编码、补测试、产出 changes.diff/test_report/logs/evidence/manifest/completion_record 等待本地主控吸收的场景。
---

# lobster-task-package-skill

## 目标

把云端执行结果固定成 **待验收任务包**，而不是直接入仓代码。

一句话原则：

- 云端负责：按边界执行、产出证据、保证任务包完整
- 本地负责：最终业务验收与是否入仓

## 默认交付目录

所有产物进入：

- `dropzone/<task_id>/`

不得直接写主仓代码树。

## 最小必需件

任务包至少包含：

- `blueprint.md`
- `risk_statement.md`
- `changes.diff`
- `test_report.md`
- `completion_record.md`
- `manifest.json`
- `logs/`
- `evidence/`

如果任务被拆成文档型/证据型子任务，也至少要保证：

- `execution_receipt.json`
- `completion_record.md`
- `resume_handoff.md`
- `checkpoint/state.yaml`

## Phase 0-4

### Phase 0：蓝图会审

先写：

- 改什么
- 为什么改
- 怎么测
- 怎么回滚

没有 `blueprint.md`，不得进入执行。

### Phase 1：隔离生产

云端只在 dropzone 里产物化，不直接碰 authoritative repo。

### Phase 2：双重卫检

必须准备：

- reviewer 证据
- compliance 证据

不能只靠“执行者说自己做完了”。

### Phase 3：联署结项

`completion_record.md` 至少要表明：

- 执行完成到哪一步
- 还缺什么
- 是否已进入 `WAITING_REVIEW / WAITING_COMPLIANCE`

### Phase 4：主控吸收

由本地执行：

- `pre_absorb_check.sh`
- `absorb.sh`

executor 不得自称“最终验收完成”。

## manifest 规则

`manifest.json` 必须列出：

- `artifacts`
- `evidence`
- `task_id`
- `status`
- `generated_by`

只允许 manifest 白名单中出现的文件进入吸收流程。

## completion_record 规则

可以写：

- `EXECUTION COMPLETE`
- `HOST ABSORB MANUAL`
- `REVIEW PENDING`
- `COMPLIANCE PENDING`

不可以写：

- `FINAL PASS`
- `已验收完成`
- `已批准发布`

## resume / interruption

一旦 token/context 中断风险出现，必须补：

- `resume_handoff.md`
- `checkpoint/state.yaml`

不能只给口头说明。

## 红线

- 不能直接写主仓
- 不能缺关键件
- 不能把 pre_absorb 当 final accept
- 不能自称 reviewer/compliance/final gate

## 参考

- `docs/2026-03-08/DOCKER_VOLUME_受控物理桥接方案_v1.md`
- `docs/2026-03-08/CLOUD_MULTI_AGENT_OVERSIGHT_PROTOCOL_v1.md`
- `skills/lobster-cloud-execution-governor-skill/SKILL.md`
