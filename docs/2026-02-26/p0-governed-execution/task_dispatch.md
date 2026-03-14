# 2026-02-26 Task Dispatch（P0 Governed Execution）

job_id: P0-L6-AUTH-20260226-001  
mode: strict  
owner: Codex (Orchestrator)  
protocol: multi-ai-collaboration.md v3

## 0. 法规与门禁（全任务强制）

- Guard A: `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- Guard B: `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`（若缺失，整批阻断）
- 治理规则：
1. 无 `ComplianceAttestation(PASS)` 不得执行。
2. 涉及副作用动作时，无 `permit=VALID` 不得执行。
3. 无 `EvidenceRef` 不得宣称完成。
4. 顺序固定为 `Review -> Compliance -> Execution`。
5. 调度策略固定为 `Wave内并发，Wave间门禁`（禁止全局串行）。

## 1. 今日目标

1. 完成 P0 ISSUE-00 到 ISSUE-10 的真实性闭环（仅 L6 范围）。
2. 产出最终裁决：`docs/2026-02-26/p0-governed-execution/verification/final_gate_decision.json`。

## 2. PreflightChecklist（发单前必做）

1. `ScopeCheck`：仅处理 P0（ISSUE-00~10），不得扩展到 L4/L5 实现。
2. `DependencyCheck`：当前 Wave 的前置任务是否全部 `ALLOW`。
3. `GuardCheck`：Guard A/B 文档可访问；不可访问则 `DENY`。
4. `EvidenceCheck`：任务卡中是否声明三件套产物路径。
5. `PermitCheck`：涉及副作用操作的任务卡是否写明 permit 条件。
6. `ParallelCheck`：当前 Wave 任务卡是否一次性并发派发完成。

## 3. ExecutionContract（军团统一执行契约）

- Intent：
1. 按本调度单推进 T01~T11，逐波放行，不跨波执行。
2. 每个任务都必须提交三权记录。
- Constraints：
1. 禁止跳过 Review 和 Compliance 直接执行。
2. 禁止无证据宣称“已完成”。
3. 任一任务 `REQUIRES_CHANGES/FAIL` 仅打回该任务，不回滚已 `ALLOW` 任务。
- Rollback：
1. 任务级回滚：只回滚失败任务对应改动。
2. 波次级冻结：当前 Wave 未全 `ALLOW`，下一 Wave 不得发单。

## 4. RequiredChanges（本轮必须达成）

1. 每个 Txx 必须落盘：
- `verification/Txx_execution_report.yaml`
- `verification/Txx_gate_decision.json`
- `verification/Txx_compliance_attestation.json`
2. `T09` 必须给出协议测试 T1-T5 全绿证据。
3. `T10` 必须给出 CI fail-closed gate 证据。
4. `T11` 必须给出第三方独立验真脚本可运行证据。

## 5. 波次编排（可直接转发）

| Wave | Task | Issue | Execution | Review | Compliance | Depends On | 目标 |
|---|---|---|---|---|---|---|---|
| 1 | T01 | ISSUE-00 | Antigravity-2 | vs--cc2 | Kior-C | - | 宪法防绕过基线（policy_check + fail-closed + audit fields） |
| 1 | T02 | ISSUE-01 | vs--cc1 | Antigravity-2 | Kior-C | T01 | Canonical JSON 一致性 |
| 1 | T03 | ISSUE-02 | vs--cc3 | Kior-A | Kior-C | T01,T02 | Envelope + Body 结构 |
| 2 | T04 | ISSUE-03 | Kior-B | vs--cc3 | Kior-C | T02,T03 | 混合加密（AES-256-GCM + RSA-OAEP-256） |
| 2 | T05 | ISSUE-04 | Antigravity-1 | vs--cc1 | Kior-C | T02,T03 | Ed25519 签名/验签 |
| 2 | T06 | ISSUE-05 | Kior-A | Antigravity-1 | Kior-C | T03,T05 | Nonce challenge 防重放 |
| 2 | T07 | ISSUE-06 | vs--cc2 | Kior-B | Kior-C | T01,T05 | Node Registry 与身份校验 |
| 3 | T08 | ISSUE-07 | vs--cc1 | vs--cc3 | Kior-C | T03,T05 | 回执哈希改为 SHA-256(canonical) |
| 3 | T09 | ISSUE-08 | Kior-C | Antigravity-1 | Antigravity-2 | T04,T05,T06,T07,T08 | 协议 T1-T5 全绿 |
| 3 | T10 | ISSUE-09 | vs--cc3 | vs--cc2 | Antigravity-2 | T09 | CI 强制 Gate 接入 |
| 4 | T11 | ISSUE-10 | Kior-B | Kior-A | Kior-C | T09,T10 | 第三方独立验真脚本 |

## 6. 任务卡索引（分层转发）

使用规则：
1. 只转发“当前 Wave 且已满足依赖”的任务卡。
2. 每次转发必须带上第 7 节“一键转发模板”。
3. 同一任务只给对应执行者，审查与合规走独立角色链路。

### 6.1 按 Wave 索引（主控官默认视图）

Wave 1（先发）：
- `docs/2026-02-26/p0-governed-execution/tasks/T01_Antigravity-2.md`
- `docs/2026-02-26/p0-governed-execution/tasks/T02_vs--cc1.md`
- `docs/2026-02-26/p0-governed-execution/tasks/T03_vs--cc3.md`

Wave 2（仅在 Wave 1 全 ALLOW 后发）：
- `docs/2026-02-26/p0-governed-execution/tasks/T04_Kior-B.md`
- `docs/2026-02-26/p0-governed-execution/tasks/T05_Antigravity-1.md`
- `docs/2026-02-26/p0-governed-execution/tasks/T06_Kior-A.md`
- `docs/2026-02-26/p0-governed-execution/tasks/T07_vs--cc2.md`

Wave 3（仅在 Wave 2 全 ALLOW 后发）：
- `docs/2026-02-26/p0-governed-execution/tasks/T08_vs--cc1.md`
- `docs/2026-02-26/p0-governed-execution/tasks/T09_Kior-C.md`
- `docs/2026-02-26/p0-governed-execution/tasks/T10_vs--cc3.md`

Wave 4（收口）：
- `docs/2026-02-26/p0-governed-execution/tasks/T11_Kior-B.md`

### 6.2 按执行者索引（定向派单视图）

Antigravity-2：
- `docs/2026-02-26/p0-governed-execution/tasks/T01_Antigravity-2.md`

Antigravity-1：
- `docs/2026-02-26/p0-governed-execution/tasks/T05_Antigravity-1.md`

vs--cc1：
- `docs/2026-02-26/p0-governed-execution/tasks/T02_vs--cc1.md`
- `docs/2026-02-26/p0-governed-execution/tasks/T08_vs--cc1.md`

vs--cc2：
- `docs/2026-02-26/p0-governed-execution/tasks/T07_vs--cc2.md`

vs--cc3：
- `docs/2026-02-26/p0-governed-execution/tasks/T03_vs--cc3.md`
- `docs/2026-02-26/p0-governed-execution/tasks/T10_vs--cc3.md`

Kior-A：
- `docs/2026-02-26/p0-governed-execution/tasks/T06_Kior-A.md`

Kior-B：
- `docs/2026-02-26/p0-governed-execution/tasks/T04_Kior-B.md`
- `docs/2026-02-26/p0-governed-execution/tasks/T11_Kior-B.md`

Kior-C：
- `docs/2026-02-26/p0-governed-execution/tasks/T09_Kior-C.md`

### 6.3 并发派单规则（效率优先）

1. 同一 Wave 的全部任务一次性并发派发，不按任务号串行等待。
2. 每个任务内部仍遵守 `Review -> Compliance -> Execution`。
3. 跨 Wave 只看门禁：上一 Wave 未全 `ALLOW`，下一 Wave 不得启动。
4. 允许“先完成先审查”，不要求同 Wave 内完成顺序一致。
5. 主控官每 60-90 分钟做一次并发收敛（补发、催办、替换超时执行者）。

## 7. 一键转发模板（复制即发）

```text
[P0 Dispatch] {TASK_ID} / {ROLE}
job_id: P0-L6-AUTH-20260226-001
mode: strict (Review -> Compliance -> Execution)
task_card: docs/2026-02-26/p0-governed-execution/tasks/{TASK_FILE}

硬约束：
1) 无 Compliance PASS 不得执行
2) 无 permit=VALID 不得做副作用操作
3) 无 EvidenceRef 不得宣称完成

回传三件套：
- docs/2026-02-26/p0-governed-execution/verification/{TASK_ID}_execution_report.yaml
- docs/2026-02-26/p0-governed-execution/verification/{TASK_ID}_gate_decision.json
- docs/2026-02-26/p0-governed-execution/verification/{TASK_ID}_compliance_attestation.json
```

## 8. 放行与裁决规则

1. Wave 内任务并发推进（不串行）。
2. Wave 1 全部 `ALLOW` 才可进入 Wave 2。
3. Wave 2 全部 `ALLOW` 才可进入 Wave 3。
4. Wave 3 全部 `ALLOW` 才可进入 Wave 4。
5. 未完成项不阻塞同 Wave 其他任务执行与审查。
6. 仅在“跨 Wave 放行”时执行全量门禁检查。
7. 任一任务缺三件套：`DENY`（阻断放行）。
8. 任一任务 `compliance != PASS`：`REQUIRES_CHANGES`。
9. 任一任务无 `EvidenceRef`：`REQUIRES_CHANGES`。

## 9. 主控官日内 SOP

1. 发单：当前 Wave 全任务并发发出（一次发齐）。
2. 收件：检查三件套是否齐全。
3. 审核：按硬规则给 `ALLOW/REQUIRES_CHANGES/DENY`。
4. 收敛：先处理快任务，超时任务并行替补，不拖慢全局节奏。
5. 放行：仅在当前 Wave 全 `ALLOW` 时推进下一 Wave。
6. 收口：执行最终汇总并输出 `verification/final_gate_decision.json`。
