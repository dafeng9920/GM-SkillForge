# Overnight Serial Queue Protocol

## 核心目标
在主控（The Brain）离线期间，允许执行臂（The Hand）按照 **P1 -> P2 -> P3 -> P4** 的严格顺序推进工作项，实现“云端满负荷、逻辑不越位”。

## 队列优先级 (Priority Queue)

### P1: 主开发任务 (Mainline Advancement)
- **定位**：最高优先级、边界冻结的核心开发。
- **限制**：
  - 修改文件：3-6 个
  - 允许命令：2-4 条
  - 只允许跑与目标直接相关的测试。
- **退出条件**：完成后进入 `WAITING_REVIEW`，或 `READY_TO_RESUME`。

### P2: 候补任务 (Refinement & Promotion)
- **定位**：Intent 晋升后的补丁、一致性修复、单模块单测补齐。
- **限制**：
  - 修改文件：2-4 个
  - 允许命令：1-3 条
- **准入**：P1 = `DONE` 或 `WAITING_REVIEW`。

### P3: 文档与审计整理 (Documentation & Audit)
- **定位**：整理 Execution Report、Completion Record、Evidence Mapping。
- **限制**：**严禁开启新功能开发**。
- **准入**：P2 = `DONE` 或 `WAITING_REVIEW`。

### P4: 兜底清理 (Cleanup & Handoff Optimization)
- **定位**：TODO 清理、路径修正、强化次日 handoff。
- **准入**：P3 = `DONE`。

## 切换与强制熔断规则 (Switching & Fail-Closed)

1. **串行强制**：严禁并行执行。必须在前一任务达到稳定态（DONE/WAITING_REVIEW/BLOCKED）并落盘 handoff 后，方可探测下一任务。
2. **BLOCKED 处理**：任一任务发生 `BLOCKED`，必须写完 handoff 并记录 `blocked_by` 后，才可决定是否降级进入后续低风险任务（P3/P4）。
3. **Scope 熔断**：严禁擅自扩展任务边界。若发生 Scope 漂移，必须立即停止当前任务。
4. **中断保存**：遇到 Token 越位、上下文膨胀或会话中断风险，必须先回传 `resume_handoff.md`。

## 产物强制要求 (Artifact Baseline)
每个任务必须独立产生：
- `execution_receipt.json`
- `completion_record.md`
- `resume_handoff.md`
- `checkpoint/state.yaml`

## 法律效力
本协议作为 `lobster-cloud-execution-governor-skill` 的动态运行补丁，效力高于任何口头暗示，执行臂违背上述规则将被记录为 `governance_violation`。
