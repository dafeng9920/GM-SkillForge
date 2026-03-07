# T2 Follow-up 任务回传模板（2026-03-07）

> 用途：
- 每个执行者完成各自 shard 后，直接按本模板填写 completion record
- 主控官（Codex）统一回收、审核、汇总、出 final gate

> 填写规则：
- 不要写空话，只写已经完成并可举证的内容
- 没有 `EvidenceRef` 的内容，不得写成“已完成”
- 若阻塞或部分完成，必须明确写 `remaining_risks / blockers`

---

## 基本信息

- Shard ID: `F1 / F2 / F3`
- Executor: `填写执行者名`
- Date: `2026-03-07`
- Status: `COMPLETED / PARTIAL / BLOCKED`
- Related Dispatch:
  - `docs/2026-03-07/T2_FOLLOWUP_DISPATCH_2026-03-07.md`
  - `docs/2026-03-07/T2_FOLLOWUP_PROMPT_PACK_2026-03-07.md`

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

## 2. Files Changed

- `path/to/file_1`
  - Action: `created / modified / moved / renamed`
  - Purpose: `这次为什么改它`

- `path/to/file_2`
  - Action: `created / modified / moved / renamed`
  - Purpose: `这次为什么改它`

- `path/to/file_3`
  - Action: `created / modified / moved / renamed`
  - Purpose: `这次为什么改它`

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
- `test/log/report path`

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

## 8. Handoff To Review

- Review ready: `YES / NO`
- Compliance ready: `YES / NO`
- Notes to reviewer:
  - `需要重点审查的点`
- Notes to compliance:
  - `需要重点核对的边界`

---

## 9. Shard-Specific Addendum

### F1 Addendum

- Canonical naming mapping:
  - `old -> new`
  - `old -> new`
- Authoritative contract path:
  - `填写主 authoritative 合同位置`
- Deprecated / migration-only path:
  - `若保留旧路径，写明非 authoritative`

### F2 Addendum

- Mainline promotion target:
  - `outer_intent_ingest / outer_contract_freeze`
- Old status:
  - `l42_planned / mapped / other`
- New status:
  - `mainline / validated / frozen / other`
- Gate path:
  - `填写`
- Evidence required:
  - `填写`

### F3 Addendum

- Parity / replay target:
  - `default-deny / evidence-first / time_semantics`
- Artifact created:
  - `test / report / log / doc`
- Reproduction path:
  - `如何复现`

---

## 10. Final Completion Statement

- Completion claim:
  - `我确认以上内容为本 shard 的真实完成记录；未举证部分不宣称完成。`

- Executor Signature:
  - `姓名 / 角色`

- Submitted at:
  - `时间戳`
