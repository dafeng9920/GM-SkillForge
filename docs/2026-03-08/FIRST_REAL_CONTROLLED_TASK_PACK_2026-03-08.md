# First Real Controlled Task Pack

- 日期：`2026-03-08`
- Task ID：`REAL-TASK-001`
- 模式：`PAYLOAD-FIRST + Controlled Bridge + Local Accept`
- 优先级：`P1`

## 1. 目标

在已通过 `SMOKE-GATE-001` 的云端治理底盘上，执行首个真实、低风险、强边界的业务任务，用于验证：

- 云端任务包能否按规范产出
- review/compliance 口径能否保持分权
- `pre_absorb_check` 与 `absorb` 是否能支持真实任务
- 本地主控能否完成最终吸收与业务验收

## 2. 任务类型

只允许选择以下类型之一：

1. 单模块文档/合同/路由一致性修正
2. 单模块低风险测试补齐
3. 单模块 evidence / completion / handoff 规范化修正

禁止：

- 跨子系统大改
- 基础设施改造
- 高敏感 auth / infra / deployment 目录变更
- 需要架构发明的新功能

## 3. 角色分工

- Executor：云端执行者（优先小龙虾，若不稳定则云端 Codex）
- Reviewer：独立 reviewer
- Compliance：独立 compliance
- Controller：本地 Codex / 主控

## 4. 交付要求

交付目录：

- `DROPZONE_ROOT/REAL-TASK-001/`

至少包含：

- `blueprint.md`
- `risk_statement.md`
- `changes.diff`
- `test_report.md`
- `completion_record.md`
- `manifest.json`
- `logs/`
- `evidence/`
- `resume_handoff.md`
- `checkpoint/state.yaml`
- `execution_runtime_report.json`
- `execution_runtime_summary.md`
- `execution_runtime_moments.md`

并要求统计：

- 开始时间 / 结束时间 / 总耗时
- 有效执行时长
- 修改文件数
- 代码增删行数
- 完成的子任务数
- 遇到的问题类型
- 使用了哪些 skill 解决问题

## 5. 成功判据

以下条件同时满足才算任务完成：

1. 任务包关键件齐全
2. reviewer 有独立证据化结论
3. compliance 有独立证据化结论
4. `pre_absorb_check.sh REAL-TASK-001` 通过
5. 本地主控完成 absorb 后，仍认可逻辑正确

## 6. 失败判据

任一情况发生即记 `BLOCKED`：

- 路径越权
- 缺关键件
- `manifest.json` 缺 `env`
- reviewer/compliance 混写
- 云端先报完成、主仓无证据

## 7. 建议顺序

1. 先由本地主控冻结具体 objective
2. 再由云端 executor 产出 `blueprint.md`
3. 主控签署 `PROCEED`
4. 云端执行
5. 独立 reviewer / compliance
6. 本地 absorb + final accept

## 8. 当前建议

首单任务应以“低风险规范化修正”开局，不应直接选择高复杂度真实编码任务。
