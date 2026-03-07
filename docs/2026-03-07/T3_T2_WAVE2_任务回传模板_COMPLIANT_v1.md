# T3 / T2 Wave 2 任务回传模板（2026-03-07）- Antigravity-1 合规版

> 版本: v1.0-compliant
> 合规审查: Antigravity-1
> 审查日期: 2026-03-07
> 审查结果: PASS with hard evidence requirements

---

## 用途说明

- 供 `T3-A/B/C/D` 与 `T2W2-A/B/C` 各执行者完成 shard 后填写
- 主控官（Codex）统一回收、审核、汇总、出 final gate
- **强制要求：所有宣称必须有 EvidenceRef 支持**

---

## 适用 Shard

- `T3-A` - Smoke 任务跑通 + 稳定操作序列验证
- `T3-B` - Pre-shutdown / Morning fetch / Failure 分支 checklist
- `T3-C` - 批量任务模板 + Wave 归档
- `T3-D` - 文档状态同步 + 过期操作假设清理
- `T2W2-A` - 文档支撑的 intent 复盘
- `T2W2-B` - 晋升候选 shortlist 生成
- `T2W2-C` - Wave 2 启动前置条件核对

---

## 填写规则（强制）

1. **不写空话**：只写已经完成并可举证的内容
2. **EvidenceRef 强制**：没有 `EvidenceRef` 的内容，不得宣称完成
3. **Gate Decision 强制**：必须挂载 entry + exit gate decision 文件
4. **稳定宣称强制**：任何 "stable" / "稳定" / "可靠" 宣称必须附证据
5. **风险透明**：若阻塞或部分完成，必须明确写 `remaining_risks / blockers`

---

## 基本信息

| 字段 | 值 |
|------|-----|
| Shard ID | `T3-A / T3-B / T3-C / T3-D / T2W2-A / T2W2-B / T2W2-C` |
| Executor | `填写执行者名` |
| Date | `2026-03-07` |
| Status | `COMPLETED / PARTIAL / BLOCKED` |
| Permit ID | `从任务 permit 填写，若无则填 PENDING` |

### Related Contract & Artifacts

| 类型 | 路径 | Hash/Digest (可选) |
|------|------|-------------------|
| Original Dispatch | `docs/2026-03-07/T3_T2_WAVE2_DISPATCH_2026-03-07.md` | |
| Prompt Pack | `docs/2026-03-07/T3_T2_WAVE2_PROMPT_PACK_2026-03-07.md` | |
| Execution Receipt | `填写实际 receipt 路径` | |
| Entry Gate Decision | `填写 entry_gate_decision.json 路径` | |
| Exit Gate Decision | `填写 exit_gate_decision.json 路径` | |
| Compliance Attestation | `填写 compliance_attestation.json 路径` | |

---

## 1. Execution Summary

### Objective
- `一句话说明本 shard 的目标`

### Scope completed
- `已完成项 1` → EvidenceRef: `file:path:line`
- `已完成项 2` → EvidenceRef: `file:path:line`
- `已完成项 3` → EvidenceRef: `file:path:line`

### Out of scope touched
- `若无，写 none`
- `若有，必须说明原因` → EvidenceRef: `rationale path`

---

## 2. Files Changed / Created

| 文件路径 | Action | Purpose | EvidenceRef |
|----------|--------|---------|-------------|
| `path/to/file_1` | `created/modified/moved/renamed` | `为什么改` | `file:path:line` |
| `path/to/file_2` | `created/modified/moved/renamed` | `为什么改` | `file:path:line` |
| `path/to/file_3` | `created/modified/moved/renamed` | `为什么改` | `file:path:line` |

---

## 3. Key Results

| Result | Before → After | EvidenceRef |
|--------|----------------|-------------|
| Result 1 | `描述 before → after` | `file:path:line` |
| Result 2 | `描述 before → after` | `file:path:line` |
| Result 3 | `描述 before → after` | `file:path:line` |

---

## 4. Verification

### Self-check commands

```bash
# 命令 1
`填写实际命令`

# 命令 2
`填写实际命令`

# 命令 3
`填写实际命令`
```

### Self-check result

| 检查项 | 结果 | 证据路径 |
|--------|------|----------|
| 检查项 1 | `PASS / FAIL / PARTIAL` | `log/output path` |
| 检查项 2 | `PASS / FAIL / PARTIAL` | `log/output path` |
| 检查项 3 | `PASS / FAIL / PARTIAL` | `log/output path` |

### Manual verification

| 检查点 | 结果 | 验证人 | 证据路径 |
|--------|------|--------|----------|
| `手工确认点 1` | `PASS / FAIL` | `谁验证的` | `screenshot/log path` |
| `手工确认点 2` | `PASS / FAIL` | `谁验证的` | `screenshot/log path` |

---

## 5. EvidenceRef

### Contract & Receipt (强制)

- Original contract: `docs/2026-03-07/T3_T2_WAVE2_DISPATCH_2026-03-07.md`
- Execution receipt: `path/to/receipt/{shard_id}_receipt.json`
- Permit reference: `path/to/permit/{permit_id}.json` (如有)

### Gate Decisions (强制)

- Entry gate: `path/to/gate/{shard_id}_entry_gate_decision.json`
- Exit gate: `path/to/gate/{shard_id}_exit_gate_decision.json`
- Compliance attestation: `path/to/attestation/{shard_id}_compliance_attestation.json`

### Code Changes

- `file:path:line`
- `file:path:line`
- `file:path:line`

### Test / Verification Reports

- Test report: `path/to/test_report_{shard_id}.json`
- Smoke test output: `path/to/smoke_test_{shard_id}.log`
- Gate trace: `path/to/gate_trace_{shard_id}.json`

### Artifacts

- Artifact 1: `path/to/artifact_1`
- Artifact 2: `path/to/artifact_2`
- Artifact digest: `sha256:...` (如适用)

---

## 6. Acceptance Check

### Antigravity-1 硬性要求

| Acceptance Item | Status | EvidenceRef | Note |
|-----------------|--------|-------------|------|
| 闭链完成（contract → receipt → gate） | `PASS / FAIL / PARTIAL` | `receipt path + gate decision path` | `说明` |
| 无未证"稳定"宣称 | `PASS / FAIL / PARTIAL` | `所有"稳定"宣称的证据列表` | `说明` |
| 未绕过 permit/gate | `PASS / FAIL / PARTIAL` | `所有 gate pass 记录` | `说明` |
| 时间窗口合规 (N3) | `PASS / FAIL / PARTIAL` | `执行时间戳 + permit 时间窗口` | `说明` |
| Artifact 完整性 (N2) | `PASS / FAIL / PARTIAL` | `artifact manifest + digest` | `说明` |
| 命令白名单合规 (N1) | `PASS / FAIL / PARTIAL` | `执行命令列表 vs allowlist` | `说明` |

### Shard-Specific Acceptance

| Acceptance item | Status | EvidenceRef | Note |
|-----------------|--------|-------------|------|
| Item 1 | `PASS / FAIL / PARTIAL` | `file:path:line` | `说明` |
| Item 2 | `PASS / FAIL / PARTIAL` | `file:path:line` | `说明` |
| Item 3 | `PASS / FAIL / PARTIAL` | `file:path:line` | `说明` |

---

## 7. Remaining Risks / Blockers

| 风险/阻塞项 | 影响 | 缓解措施 | EvidenceRef |
|-------------|------|----------|-------------|
| `风险 1` | `high/medium/low` | `如何缓解` | `相关文档/代码路径` |
| `风险 2` | `high/medium/low` | `如何缓解` | `相关文档/代码路径` |

> **无风险时必须写**：`NONE - 证据路径: [所有检查项均 PASS 的 gate decision path]`

---

## 8. Handoff

### Review Readiness

| 检查项 | 结果 | 证据 |
|--------|------|------|
| EvidenceRef 完整 | `YES / NO` | `证据清单路径` |
| 所有 PASS 有对应证据 | `YES / NO` | `交叉验证表` |
| Gate decision 已生成 | `YES / NO` | `gate decision 路径` |

### Compliance Readiness

| 检查项 | 结果 | 证据 |
|--------|------|------|
| 闭链验证通过 | `YES / NO` | `receipt + gate decision 路径` |
| 无绕过 permit/gate | `YES / NO` | `执行 trace 路径` |
| 时间窗口合规 | `YES / NO` | `N3 验证报告路径` |
| 未引入临时手法 | `YES / NO` | `代码审查报告路径` |

### Notes to reviewer
- `需要重点审查的点` → EvidenceRef: `相关文件路径`

### Notes to compliance
- `需要重点核对的边界` → EvidenceRef: `相关文件路径`

---

## 9. Shard-Specific Addendum

### T3-A Addendum

#### Smoke Task
- 任务 ID / 名称: `填写`
- Evidence: `smoke test 报告路径`

#### Stable Operator Sequence (Antigravity-1 硬性要求)

| Step | 操作名称 | 证据类型 | 证据路径 | 稳定性指标 |
|------|----------|----------|----------|-----------|
| 1 | `步骤名称` | `gate_decision/smoke_test/log` | `具体路径` | `连续通过 N 次 / 时间窗口 T` |
| 2 | `步骤名称` | `gate_decision/smoke_test/log` | `具体路径` | `连续通过 N 次 / 时间窗口 T` |
| 3 | `步骤名称` | `gate_decision/smoke_test/log` | `具体路径` | `连续通过 N 次 / 时间窗口 T` |

> **禁止宣称**："已稳定" / "稳定运行" 无证据支持

#### Friction Removed

| 问题 | 状态 | EvidenceRef |
|------|------|-------------|
| `问题 1` | `CLEARED / MITIGATED / DEFERRED` | `file:path:line` |
| `问题 2` | `CLEARED / MITIGATED / DEFERRED` | `file:path:line` |
| `问题 3` | `CLEARED / MITIGATED / DEFERRED` | `file:path:line` |

### T3-B Addendum

#### Pre-shutdown Checklist
- 路径: `填写`
- 最近验证: `日期 + 验证人`
- Evidence: `验证报告路径`

#### Morning Fetch/Verify Checklist
- 路径: `填写`
- 最近验证: `日期 + 验证人`
- Evidence: `验证报告路径`

#### Failure Branch Checklist
- 路径: `填写`
- 最近验证: `日期 + 验证人`
- Evidence: `验证报告路径`

### T3-C Addendum

#### Batch Template
- 路径: `填写`
- Wave order: `填写`
- 最近使用: `日期 + 结果`
- Evidence: `执行记录路径`

#### Archive Targets
- 目标列表: `填写`
- 归档路径: `填写`
- Evidence: `归档 manifest 路径`

#### Aggregation Path
- 路径: `填写`
- 最近验证: `日期 + 结果`
- Evidence: `验证报告路径`

### T3-D Addendum

#### Current-State Docs Updated

| 文件 | 更新内容 | EvidenceRef |
|------|----------|-------------|
| `path/to/doc_1` | `更新描述` | `file:path:line` |
| `path/to/doc_2` | `更新描述` | `file:path:line` |
| `path/to/doc_3` | `更新描述` | `file:path:line` |

#### Historical Docs Intentionally Preserved

| 文件 | 保留原因 | 保留期限 | EvidenceRef |
|------|----------|----------|-------------|
| `path/to/doc_1` | `原因` | `期限` | `决策记录路径` |
| `path/to/doc_2` | `原因` | `期限` | `决策记录路径` |

#### Removed Stale Operator Assumptions

| 假设 | 移除原因 | EvidenceRef |
|------|----------|-------------|
| `假设 1` | `为什么过时` | `file:path:line` |
| `假设 2` | `为什么过时` | `file:path:line` |
| `假设 3` | `为什么过时` | `file:path:line` |

### T2W2-A Addendum

#### Remaining Docs-Backed Entries Reviewed

| Intent | 路径 | 状态 | 证据 | 决策 |
|--------|------|------|------|------|
| `intent 名称` | `文档路径` | `review 结果` | `审查记录路径` | `promote now / keep docs-backed / defer` |

#### Disposition Summary
- Promote now: `数量 / 列表`
- Keep docs-backed: `数量 / 列表 + 原因`
- Defer: `数量 / 列表 + 原因`

#### Owner Path / Next Step
- Owner: `填写`
- Next step: `填写`
- Evidence: `任务分配路径`

### T2W2-B Addendum

#### Shortlist Order

| 优先级 | Intent | 晋升理由 | EvidenceRef |
|--------|--------|----------|-------------|
| 1 | `intent 名称` | `fit / contribution / operational` | `分析文档路径` |
| 2 | `intent 名称` | `fit / contribution / operational` | `分析文档路径` |
| 3 | `intent 名称` | `fit / contribution / operational` | `分析文档路径` |

#### Defer List
| Intent | 延期原因 | 复查条件 |
|--------|----------|----------|
| `intent 1` | `原因` | `条件` |
| `intent 2` | `原因` | `条件` |

#### Selection Rationale
- Fit metric: `描述`
- Contribution metric: `描述`
- Operational value: `描述`
- Evidence: `分析文档路径`

### T2W2-C Addendum

#### Preconditions Path
- 路径: `填写`
- 验证状态: `PASS / FAIL / PARTIAL`
- Evidence: `验证报告路径`

#### T3 Dependency Mapping

| T3 Shard | 依赖项 | 状态 | EvidenceRef |
|----------|--------|------|-------------|
| T3-A | `依赖 1` | `READY / BLOCKED` | `检查路径` |
| T3-B | `依赖 2` | `READY / BLOCKED` | `检查路径` |
| T3-C | `依赖 3` | `READY / BLOCKED` | `检查路径` |

#### Start Gate for Wave 2
- Gate 条件: `填写`
- 验证状态: `PASS / FAIL / PARTIAL`
- Gate decision 路径: `填写`
- Evidence: `gate decision 路径`

---

## 10. Final Completion Statement

### Completion Claim

我确认以上内容为本 shard 的真实完成记录：
- ✅ 所有宣称均有 EvidenceRef 支持
- ✅ 未举证部分不宣称完成
- ✅ 未引入绕过 permit/gate 的临时手法
- ✅ 所有 "稳定" 宣称均有证据支持

### Executor Signature
- 姓名 / 角色: `填写`
- 签名时间戳: `ISO8601 格式`

### Compliance Endorsement
- Antigravity-1 审查状态: `PENDING / APPROVED / REJECTED`
- 审查意见: `由合规官填写`

### Submitted at
- 时间戳: `ISO8601 格式`
- 时区: `UTC`

---

## 附录：Antigravity-1 合规检查清单

### 闭链验证 (Closed-Loop)

- [ ] Original contract 引用正确
- [ ] Execution receipt 存在且可验证
- [ ] Entry + Exit gate decision 挂载
- [ ] Compliance attestation 挂载
- [ ] Contract → Receipt → Gate 链路完整

### 稳定宣称验证 (Stability Claims)

- [ ] 所有 "稳定" / "stable" 宣称都有证据
- [ ] 证据类型明确（gate_decision / smoke_test / log）
- [ ] 稳定性指标明确（连续通过次数 / 时间窗口）
- [ ] 无未证实的稳定宣称

### Permit/Gate 绕过检查 (Bypass Detection)

- [ ] 所有执行步骤有 permit 引用
- [ ] 无未经验证的临时手法
- [ ] 命令白名单合规（N1）
- [ ] 时间窗口合规（N3）
- [ ] Artifact 完整性（N2）

### 证据完整性 (Evidence Integrity)

- [ ] 所有 PASS 声称有 EvidenceRef
- [ ] 证据路径可访问
- [ ] 证据内容与声称一致
- [ ] 无空证据或占位符

---

**模板版本历史**：
- v1.0-compliant (2026-03-07): Antigravity-1 合规审查通过
- v0.9-original (2026-03-07): 原始版本，被 Antigravity-1 拒绝
