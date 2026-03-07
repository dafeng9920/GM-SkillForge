# T3 / T2 Wave 2 任务回传模板（2026-03-07）

> 用途：
- 供 `T3-A/B/C/D` 与 `T2W2-A/B/C` 各执行者完成 shard 后直接填写
- 主控官（Codex）统一回收、审核、汇总、出 final gate

> 适用 Shard：
- `T3-A`
- `T3-B`
- `T3-C`
- `T3-D`
- `T2W2-A`
- `T2W2-B`
- `T2W2-C`

> 填写规则：
- 不写空话，只写已经完成并可举证的内容
- 没有 `EvidenceRef` 的内容，不得宣称完成
- 若是文档/模板类任务，也必须给出真实文件路径与关键段落证据
- 若阻塞或部分完成，必须明确写 `remaining_risks / blockers`

---

## 基本信息

- Shard ID: `T3-A / T3-B / T3-C / T3-D / T2W2-A / T2W2-B / T2W2-C`
- Executor: `填写执行者名`
- Date: `2026-03-07`
- Status: `COMPLETED / PARTIAL / BLOCKED`
- Related Dispatch:
  - `docs/2026-03-07/T3_T2_WAVE2_DISPATCH_2026-03-07.md`
  - `docs/2026-03-07/T3_T2_WAVE2_PROMPT_PACK_2026-03-07.md`

---

## 1. Execution Summary

- Objective:
  - `一句话说明本 shard 的目标`

- Scope completed:
  - `已完成项 1`
  - `已完成项 2`
  - `已完成项 3`

- Out of scope touched:
  - `若无，写 none`
  - `若有，必须说明原因`

---

## 2. Files Changed / Created

- `path/to/file_1`
  - Action: `created / modified / moved / renamed`
  - Purpose: `为什么改这个文件`

- `path/to/file_2`
  - Action: `created / modified / moved / renamed`
  - Purpose: `为什么改这个文件`

- `path/to/file_3`
  - Action: `created / modified / moved / renamed`
  - Purpose: `为什么改这个文件`

---

## 3. Key Results

- Result 1:
  - `写清楚 before -> after`

- Result 2:
  - `写清楚 before -> after`

- Result 3:
  - `写清楚 before -> after`

---

## 4. Verification

- Self-check commands:
  - `命令 1`
  - `命令 2`
  - `命令 3`

- Self-check result:
  - `通过 / 未通过 / 部分通过`

- Manual verification:
  - `手工确认点 1`
  - `手工确认点 2`

---

## 5. EvidenceRef

- `file:path:line`
- `file:path:line`
- `file:path:line`
- `report/log/artifact path`

> 要求：
- 至少给出能直接定位关键变更的 EvidenceRef
- 若有测试、日志、验证报告，也一并列出

---

## 6. Acceptance Check

- Acceptance item 1:
  - Status: `PASS / FAIL / PARTIAL`
  - Note: `说明`

- Acceptance item 2:
  - Status: `PASS / FAIL / PARTIAL`
  - Note: `说明`

- Acceptance item 3:
  - Status: `PASS / FAIL / PARTIAL`
  - Note: `说明`

---

## 7. Remaining Risks / Blockers

- `风险或阻塞项 1`
- `风险或阻塞项 2`
- `若无，写 none`

---

## 8. Handoff

- Review ready: `YES / NO`
- Compliance ready: `YES / NO`
- Notes to reviewer:
  - `需要重点审查的点`
- Notes to compliance:
  - `需要重点核对的边界`

---

## 9. Shard-Specific Addendum

### T3-A Addendum

- Smoke task:
  - `任务 ID / 名称`
- Stable operator sequence:
  - `步骤 1`
  - `步骤 2`
  - `步骤 3`
- Friction removed:
  - `列出实际清掉的问题`

### T3-B Addendum

- Pre-shutdown checklist path:
  - `填写`
- Morning fetch/verify checklist path:
  - `填写`
- Failure branch checklist path:
  - `填写`

### T3-C Addendum

- Batch template path:
  - `填写`
- Wave order:
  - `填写`
- Archive targets:
  - `填写`
- Aggregation path:
  - `填写`

### T3-D Addendum

- Current-state docs updated:
  - `列出文件`
- Historical docs intentionally preserved:
  - `列出文件`
- Removed stale operator assumptions:
  - `列出要点`

### T2W2-A Addendum

- Remaining docs-backed entries reviewed:
  - `列出 intent / path`
- Disposition:
  - `promote now / keep docs-backed with reason / defer`
- Owner path / next step:
  - `填写`

### T2W2-B Addendum

- Shortlist order:
  - `1. ...`
  - `2. ...`
  - `3. ...`
- Defer list:
  - `列出 defer intents`
- Selection rationale:
  - `fit / contribution / operational value`

### T2W2-C Addendum

- Preconditions path:
  - `填写`
- T3 dependency mapping:
  - `T3-A -> ...`
  - `T3-B -> ...`
  - `T3-C -> ...`
- Start gate for Wave 2:
  - `填写`

---

## 10. Final Completion Statement

- Completion claim:
  - `我确认以上内容为本 shard 的真实完成记录；未举证部分不宣称完成。`

- Executor Signature:
  - `姓名 / 角色`

- Submitted at:
  - `时间戳`
