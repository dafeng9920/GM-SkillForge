# Lobster Serial Task Pack

## 说明

本文件给小龙虾提供 **可直接执行的具体任务包**，不是行为规则摘要。

执行顺序固定为：

`P1 -> P2 -> P3 -> P4`

只有前一个任务达到 `DONE`、`WAITING_REVIEW`，或 `BLOCKED` 且已写完整 `resume_handoff.md` 后，才允许进入下一个。

通用约束仍然服从：

- `skills/lobster-cloud-execution-governor-skill/SKILL.md`
- `skills/cloud-lobster-closed-loop-skill/SKILL.md`

---

## P1. T3-A Priority 1 稳定化修正

### 任务目标

把当前云端执行链路里真正阻碍 unattended overnight 的 Priority 1 问题落掉，重点是：

- `fetch artifact precheck`
- `environment check enhancement`
- `submit / status / fetch / verify` 路径里的最小阻塞点

### 范围

允许处理：

- `scripts/lobsterctl.py`
- 与 `submit/status/fetch/verify` 直接相关的脚本/文档
- 与执行前环境检查直接相关的少量支持文件

不允许处理：

- 无关 UI 大改
- 新增大范围功能
- 与当前云端执行链无关的模块

### 完成定义

满足以下任意一种即可算此任务执行完成：

1. 已落地至少一个 Priority 1 修正，并有验证证据
2. 已明确定位实现阻塞点，并留下可续跑 handoff，供下一轮继续

### 必须产物

- `execution_receipt.json`
- `completion_record.md`
- `resume_handoff.md`
- `checkpoint/state.yaml`
- `changed_files`
- `remaining_work`

### 禁止事项

- 不得声称“整条云端 lane 已稳定”
- 不得写 review / compliance / final gate 结论
- 不得扩大到 T3 其他 shard

---

## P2. 接入 lobster-cloud-execution-governor-skill 到现有夜间执行链

### 任务目标

把现有夜间执行文档链正式接入权威技能 `lobster-cloud-execution-governor-skill`，确保后续夜间任务的 handoff / checkpoint / resume 口径一致。

### 范围

优先处理：

- `docs/2026-03-07/LOBSTER_OVERNIGHT_SHIFTPLAN_2026-03-07.md`
- `docs/2026-03-07/LOBSTER_OVERNIGHT_PROMPT_PACK_2026-03-07.md`
- `docs/2026-03-07/L4_MINI_云端小龙虾执行臂定义.md`
- 其他直接引用夜间执行规则的文档

不允许处理：

- 与夜间执行无关的总纲文档大改
- 重新设计治理架构

### 完成定义

- 关键夜间执行文档已明确引用新 governor skill
- `resume_handoff` / `checkpoint` / `resume` 口径一致
- 不再出现“只说能续跑，但没有统一规则入口”的情况

### 必须产物

- `execution_receipt.json`
- `completion_record.md`
- `resume_handoff.md`
- 列出被更新的文档路径

### 禁止事项

- 不得借机改写 review/compliance 流程
- 不得修改与本任务无关的历史归档

---

## P3. T2 Wave 2 docs-backed entries 基线盘点

### 任务目标

盘点剩余 `docs-backed` 且不属于 F1 scope 的 intent entries，形成下一轮 Wave 2 的清晰输入。

### 范围

只做：

- 基线清点
- 分类
- 记录理由

分类固定为：

- `promote now`
- `keep docs-backed with reason`
- `defer`

不做：

- 真正主线化迁移
- review/compliance 裁决
- 实现代码改造

### 完成定义

- 每个剩余 docs-backed entry 都有 disposition
- 每个 disposition 都有简要理由
- 结果能直接作为下一轮 Wave 2 输入

### 必须产物

- `baseline_inventory.md` 或等价结构化清单
- `execution_receipt.json`
- `completion_record.md`
- `resume_handoff.md`

### 禁止事项

- 不得把“待定”伪装成“已决定”
- 不得把 docs-backed entry 写成“已 mainline”

---

## P4. Completion / Handoff / Evidence 整理

### 任务目标

整理最近一批执行任务的：

- completion record
- resume handoff
- evidence refs
- checkpoint 路径

让主控第二天接手时，不需要重新摸索状态。

### 范围

只做整理和统一，不做新增主线开发。

优先整理：

- 本夜窗产生的任务产物
- `.tmp/openclaw-dispatch/<task_id>/`
- 对应 `docs/2026-03-07` / `docs/2026-03-08` 下的执行文档

### 完成定义

- 每个任务都有清晰的：
  - 当前状态
  - 最新 handoff
  - 主要证据路径
  - 下一步入口

### 必须产物

- `execution_receipt.json`
- `completion_record.md`
- `resume_handoff.md`
- 一份整理后的 evidence/handoff 索引

### 禁止事项

- 不得补写不存在的产物
- 不得提前写“已闭环”

---

## 串行切换规则

### P1 -> P2

仅当：

- `P1 = DONE`
或
- `P1 = WAITING_REVIEW`
或
- `P1 = BLOCKED` 且已写完整 `resume_handoff.md`

### P2 -> P3

同上。

### P3 -> P4

同上。

---

## 最终状态标记

每个任务只允许标记为：

- `DONE`
- `WAITING_REVIEW`
- `READY_TO_RESUME`
- `BLOCKED`

不允许写：

- `PASS`
- `FINAL ALLOW`
- `COMPLIANCE PASSED`

---

## 下发建议

如果今晚资源只够做 2 个任务，优先级固定为：

1. `P1`
2. `P2`

如果资源够做 3 个任务：

1. `P1`
2. `P2`
3. `P3`

`P4` 视为尾料整理任务。
