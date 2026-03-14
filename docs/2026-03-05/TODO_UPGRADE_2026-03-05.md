# TODO UPGRADE（2026-03-05）

- [x] tg1-live-20260306-01 Verification
    - [x] [Review Decision](file:///d:/GM-SkillForge/docs/2026-03-05/verification/tg1_live_20260306_01_review_decision.json)
    - [x] [Final Gate](file:///d:/GM-SkillForge/docs/2026-03-05/verification/tg1_live_20260306_01_final_gate.json)
    - [x] [Supplemental: Reviewer Normalization](file:///d:/GM-SkillForge/docs/2026-03-05/verification/tg1_live_20260306_01_reviewer_normalization.json)

## 执行环境声明

| 环境 | 用途 | 约束 |
|---|---|---|
| **LOCAL-ANTIGRAVITY** | 规划与证据补齐 | 仅生成/验证证据文件，不执行云端任务 |
| **CLOUD-ROOT** | 仅执行经合同批准的任务 | 需 CloudLobster 合同 + 三重哈希许可 |

---

## 目标

在 `L4.5_ACHIEVED` 基线上，**优先补齐 D1/D2/D3/D6 的缺失证据文件**，不新增大范围功能开发。

---

## 状态枚举

`已完成` | `进行中` | `待完成` | `阻塞` | `证据缺失`

---

## 核心原则（Fail-Closed）

1. **无 EvidenceRef = 不计完成**
2. **任一 fail-open 路径 = 直接 DENY**
3. **证据文件必须包含时间戳 + 校验和**
4. **Gate 决策必须附带 ruling 说明**

---

## 任务清单（按优先级排序）

### P0 - 证据补齐（阻断性任务）

| 编号 | 任务 | 状态 | DoD | 输出文件路径 | Fail-Closed 条件 | Owner | 截止时间 |
|---|---|---|---|---|---|---|---|
| **D1** | 并发能力基线脚本（M1-M3） | **证据缺失** | 1. 脚本可执行 2. 能跑 100+ 任务 3. 产出成功率/P95/积压恢复时间 4. 有时间戳 + SHA256 校验和 | `reports/l5-load/baseline_2026-03-05.json` | - 无文件 = DENY<br>- 缺校验和 = DENY<br>- 无时间戳 = DENY<br>- 成功率 < 95% = REQUIRES_CHANGES | Antigravity-1 | 2026-03-06 23:59 UTC |
| **D2** | 自动重试与降级策略基线（M4-M6） | **证据缺失** | 1. 明确瞬态/非瞬态重试矩阵 2. 降级触发条件文档化 3. fail-closed 证明存在 4. 有时间戳 + SHA256 | `reports/l5-reliability/retry_degrade_2026-03-05.md` | - 无文件 = DENY<br>- 无 fail-closed 证明 = DENY<br>- 缺瞬态/非瞬态分类 = REQUIRES_CHANGES | vs--cc1 | 2026-03-06 23:59 UTC |
| **D3** | 回放一致性校验（M8） | **证据缺失** | 1. 对固定样本回放 2. 一致性 >= 99% 3. 若不足给 required_changes 4. 有时间戳 + SHA256 | `reports/l5-replay/baseline_2026-03-05.json` | - 无文件 = DENY<br>- 一致性 < 99% 且无 required_changes = DENY<br>- 无样本详情 = REQUIRES_CHANGES | Kior-A | 2026-03-06 23:59 UTC |
| **D6** | 当日 Gate 小结 | **证据缺失** | 1. 汇总 D1-D5 全部产出 2. 给出 ALLOW/REQUIRES_CHANGES/DENY 3. 附带 ruling 说明 + 证据链 4. 有时间戳 + 签名 | `docs/2026-03-05/verification/L5_day1_gate_decision.json` | - 任一前置任务缺失 = DENY<br>- 无 ruling 说明 = DENY<br>- 无证据链引用 = REQUIRES_CHANGES | Codex | 2026-03-07 00:30 UTC |

---

### P1 - 已有证据核验（非阻断但必须核验）

| 编号 | 任务 | 状态 | DoD | 输出文件路径 | Fail-Closed 条件 | Owner | 截止时间 |
|---|---|---|---|---|---|---|---|
| **V1** | L3 Gap Closure 证据核验 | 待完成 | 1. 核验 A/B/C 三项 killer test 通过 2. 证据文件完整性校验 3. 校验和匹配 4. 生成核验报告 | `reports/l3_gap_closure/2026-03-05/verification_report.json` | - 任一 killer test 失败 = DENY<br>- 证据文件缺失 = DENY<br>- 校验和不匹配 = DENY | Codex | 2026-03-06 18:00 UTC |
| **V2** | T2 执行报告核验 | 已完成 | 1. Registry/Graph integrity 验证 2. Tamper detection 功能确认 3. False positive 处理验证 | `docs/2026-02-25/verification/T2_execution_report.yaml` | - 无 tamper 阻断证明 = DENY<br>- 无 false positive 处理 = REQUIRES_CHANGES | vs--cc1 | 已完成 |

---

### P2 - 配置与文档更新（低优先级）

| 编号 | 任务 | 状态 | DoD | 输出文件路径 | Fail-Closed 条件 | Owner | 截止时间 |
|---|---|---|---|---|---|---|---|
| **U1** | 技能注册表配置核验 | 待完成 | 1. `skills/ + .agents/skills` 扫描输出一致 2. 冲突策略可解释 3. 生成校验记录 | `configs/dispatch_skill_registry.json` + `reports/config/registry_verification_2026-03-05.json` | - 扫描不一致 = REQUIRES_CHANGES<br>- 无冲突策略说明 = REQUIRES_CHANGES | Codex | 2026-03-07 23:59 UTC |
| **U2** | 文档时间戳更新 | 待完成 | 1. 所有相关文档添加时间戳 2. 版本号更新 3. 变更日志记录 | `docs/2026-03-05/CHANGELOG.md` | - 无时间戳 = REQUIRES_CHANGES<br>- 无版本号 = REQUIRES_CHANGES | Codex | 2026-03-07 23:59 UTC |

---

## 证据文件模板

### D1: 并发能力基线模板

```json
{
  "task_id": "D1-2026-03-05",
  "executor": "Antigravity-1",
  "timestamp": "2026-03-06T23:59:00Z",
  "sha256_checksum": "...",
  "concurrent_tasks": 100,
  "results": {
    "success_rate": 0.98,
    "p95_latency_ms": 245,
    "backlog_recovery_time_s": 12.5,
    "error_breakdown": {
      "timeout": 1,
      "resource_exhausted": 0,
      "transient_error": 1
    }
  },
  "evidence_refs": [...]
}
```

### D2: 重试降级策略模板

```markdown
# Retry & Degradation Baseline (2026-03-05)

**Generated**: 2026-03-06T23:59:00Z
**SHA256**: ...
**Owner**: vs--cc1

## Transient Retry Matrix

| Error Type | Retry Strategy | Max Attempts | Backoff |
|---|---|---|---|
| Timeout | Exponential | 3 | 1s, 2s, 4s |
| RateLimit | Exponential | 5 | 2s, 4s, 8s, 16s, 32s |
| NetworkError | Exponential | 3 | 1s, 2s, 4s |

## Non-Transient (No Retry)

| Error Type | Action | Fallback |
|---|---|---|
| AuthenticationFailed | Abort | Alert operator |
| InvalidInput | Abort | Return validation error |
| ResourceNotFound | Abort | Return 404 |

## Degradation Triggers

| Metric | Threshold | Action | Fail-Closed |
|---|---|---|---|
| error_rate_5m | > 5% | Enable circuit breaker | Block new requests |
| p99_latency | > 1000ms | Shed 10% traffic | Reject excess |
| queue_depth | > 1000 | Scale up + throttle | Reject excess |

## Fail-Closed Proof

1. All retries have upper bound attempts
2. All degradations reject excess (no silent drops)
3. Circuit breaker default state = CLOSED
```

### D3: 回放一致性模板

```json
{
  "task_id": "D3-2026-03-05",
  "executor": "Kior-A",
  "timestamp": "2026-03-06T23:59:00Z",
  "sha256_checksum": "...",
  "sample_size": 1000,
  "replay_results": {
    "consistent": 990,
    "inconsistent": 10,
    "consistency_rate": 0.99
  },
  "inconsistency_analysis": {
    "timing_related": 8,
    "state_related": 2,
    "required_changes": [
      {
        "issue": "timing_flakiness",
        "fix": "add_idempotency_key",
        "priority": "P1"
      }
    ]
  },
  "evidence_refs": [...]
}
```

### D6: Gate Decision 模板

```json
{
  "task_id": "D6-2026-03-05",
  "gate_name": "L5_Day1_Gate",
  "timestamp": "2026-03-07T00:30:00Z",
  "decision": "ALLOW",
  "ruling": {
    "verdict": "PASS",
    "summary": "All D1-D5 tasks completed with acceptable quality metrics",
    "blocking_issues": [],
    "non_blocking_issues": [
      {
        "task": "D3",
        "issue": "1% inconsistency due to timing",
        "action": "tracked for next iteration"
      }
    ]
  },
  "evidence_chain": [
    {
      "task": "D1",
      "ref": "reports/l5-load/baseline_2026-03-05.json",
      "status": "PASS",
      "sha256": "..."
    },
    {
      "task": "D2",
      "ref": "reports/l5-reliability/retry_degrade_2026-03-05.md",
      "status": "PASS",
      "sha256": "..."
    },
    {
      "task": "D3",
      "ref": "reports/l5-replay/baseline_2026-03-05.json",
      "status": "PASS",
      "sha256": "..."
    }
  ],
  "next_steps": {
    "if_ALLOW": "Proceed to L5 Day-2 (扩大并发规模 + 注入故障演练)",
    "if_REQUIRES_CHANGES": "仅修复阻断项，不扩任务面",
    "if_DENY": "停止推进，召开根因分析会议"
  }
}
```

---

## 执行顺序

```
Phase 1 (2026-03-06): 证据补齐
├── D1 (Antigravity-1) ───────┐
├── D2 (vs--cc1) ─────────────┤
├── D3 (Kior-A) ──────────────┤──┐
└── V1 (Codex) ───────────────┘  │
                                 ├──→ D6 (Codex) → Gate Decision
Phase 2 (2026-03-07): Gate 决策  │
└── D6 (Codex) ◄─────────────────┘
```

---

## 风险与拦截

| 风险等级 | 描述 | 拦截措施 |
|---|---|---|
| **CRITICAL** | 任一 P0 任务无证据文件 | 直接 DENY，不进入 Phase 2 |
| **CRITICAL** | 证据文件无时间戳/校验和 | 直接 DENY |
| **HIGH** | 任一 fail-open 路径发现 | REQUIRES_CHANGES + 根因分析 |
| **MEDIUM** | 一致性 < 99% | REQUIRES_CHANGES + required_changes 列表 |
| **LOW** | 文档未更新 | REQUIRES_CHANGES（不阻断） |

---

## CloudLobster 合同约束

如需在 CLOUD-ROOT 环境执行，必须满足：

1. **三重哈希许可**：`permit_hash` + `contract_hash` + `executor_hash` 全部匹配
2. **证据快照**：执行前冻结当前证据状态
3. **执行回执**：执行后生成 `execution_receipt.yaml`
4. **双重门禁**：CloudLobster Guard + Final Gate Adjudicator

---

## 明日入口（2026-03-06）

| 条件 | 动作 |
|---|---|
| **D6 = ALLOW** | 进入 L5 Day-2（扩大并发规模 + 注入故障演练） |
| **D6 = REQUIRES_CHANGES** | 仅修复阻断项，不扩任务面 |
| **D6 = DENY** | 停止推进，召开根因分析会议 |

---

## 2026-03-06 追加记录（Append-Only）

> 本节为追加记录，不回写已封账的 2026-03-05 历史条目。

### 新增完成项

- [x] `r1-cloud-smoke-20260306-0019` 云端闭环执行与双门禁复验
  - Gate1: PASS
  - Gate2: ALLOW
  - Overall: 2/2 PASS
  - Evidence: `docs/2026-03-06/verification/r1-cloud-smoke-20260306-0019_dual_gate_verification.json`

- [x] 归档补齐（Review + Final Gate + Verification Map）
  - `docs/2026-03-06/verification/r1_cloud_smoke_20260306_0019_review_decision.json`
  - `docs/2026-03-06/verification/r1_cloud_smoke_20260306_0019_final_gate.json`
  - `docs/VERIFICATION_MAP.md`（新增任务条目）

- [x] 控制面落地（低 token 操作）
  - `scripts/lobsterctl.py`（prepare/submit/status/fetch/verify）
  - `ui/lobster_console_streamlit.py`（页面 5 步 + 指令输入框）

- [x] 归档 Skill 固化
  - `skills/cloud-closed-loop-archive-skill/SKILL.md`
  - `skills/cloud-closed-loop-archive-skill/references/archive_templates.json`

### 当前阶段结论（2026-03-06）

- Cloud closed-loop 已从“单次可用”提升到“可重复执行 + 可归档固化”。
- 仍建议继续执行 `3单回归 + 1次关机场景` 达到稳定 GA 口径。

---

### 2026-03-06 架构修复记录（Arch Fix Log）

- [x] **FIX-001** `core/gate_engine.py` — GateEngine ImportError fallback ALLOW-all 漏洞修复
  - **风险等级**: 🔴 致命
  - **修复时间**: 2026-03-06T01:03Z
  - **执行环境**: LOCAL-ANTIGRAVITY
  - **变更内容**: 将 `except ImportError` 块中 ALLOW-by-default 的 fallback `GateEngine` 类替换为 `raise RuntimeError`，强制 fail-closed。任何 import 失败均抛出 `[FATAL]` 错误，不再静默绕过全部 Gate 门控。
  - **文件**: `d:/GM-SkillForge/core/gate_engine.py` L28–L47
  - **验证方式**: 手动删除/重命名 `skillforge-spec-pack` 路径，导入 `core.gate_engine` 应立即抛出 RuntimeError 而非成功返回带 `decision=ALLOW` 的结果
  - **关联报告**: `arch_review_gm_skillforge.md` — 问题 #1

- [x] **FIX-002** `simple_api.py` — 10D 认知分析伪评分标注
  - **风险等级**: 🔴 致命
  - **修复时间**: 2026-03-06T01:07Z
  - **变更内容**: `model` 字段改为 `mock-hash-scorer-v0`，`provider` 改为 `development-only`，新增 `warning` 字段包含明确的 MOCK 声明。分析摘要坈加 `[MOCK]` 前缀。
  - **文件**: `d:/GM-SkillForge/simple_api.py`
  - **关联报告**: `arch_review_gm_skillforge.md` — 问题 #2

- [x] **FIX-003** `simple_api.py` — Permit 验证仅靠令牌长度修复
  - **风险等级**: 🔴 致命
  - **修复时间**: 2026-03-06T01:07Z
  - **变更内容**: 将 `len(token) > 10` 替换为两步校验：① 正则格式校验 `^PERMIT-[0-9A-F]{8}$`，② registry 目录文件存在性校验（`permits/` 目录正则搜索）。
  - **文件**: `d:/GM-SkillForge/simple_api.py`
  - **关联报告**: `arch_review_gm_skillforge.md` — 问题 #3

- [x] **FIX-004** `simple_api.py` — CORS `allow_origins=["*"]` 改为 env-aware 配置
  - **风险等级**: 🟡 重要
  - **修复时间**: 2026-03-06T01:07Z
  - **变更内容**: 读取 `SKILLFORGE_ENV` 环境变量，`prod/staging/dev` 分别映射不同 origin 列表。`unknown` 或未设置环境 → 空列表 → fail-closed。`allow_methods` 和 `allow_headers` 同步收紧。
  - **文件**: `d:/GM-SkillForge/simple_api.py`
  - **关联报告**: `arch_review_gm_skillforge.md` — 问题 #4

---

*最后更新：2026-03-06T01:03Z（append-only）*
*执行环境：LOCAL-ANTIGRAVITY*
*状态：COMPLETED_LOCKED*
