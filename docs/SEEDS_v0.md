## docs/SEEDS_v0.md

> 目标：在 **不扩大范围、不引入复杂系统** 的前提下，从 Day1 埋下“加强型能力”的种子。
> 原则：每颗种子都必须满足 **3 要素**：`落盘格式` + `1处写入点` + `1处读取点`。否则不做。
> 术语：Gate / Level / IssueKey / EvidenceRef / AuditPack / Revision / Tombstone / at_time。

### 执行状态快照（2026-02-20）

| 阶段 | 状态 | Gate Decision | 测试结果 | 说明 |
|------|------|---------------|----------|------|
| SEEDS P0（T17-T22） | ✅ 完成 | ALLOW | 98 passed | 5/5 种子满足 DoD |
| SEEDS P1（T23-T27） | ✅ 完成 | ALLOW | 108 passed | 4/4 种子满足 DoD |

**收口结论**：`SEEDS_v0` 的 P0 + P1 已完成并通过验收，可进入下一批（P2/运营化）阶段。

**证据链接**：
- `docs/2026-02-20/L45_SEEDS_P0_INTEGRATION_REPORT_v1.md`
- `docs/2026-02-20/verification/T22_gate_decision.json`
- `docs/2026-02-20/L45_SEEDS_P1_INTEGRATION_REPORT_v1.md`
- `docs/2026-02-20/verification/T27_gate_decision.json`
- `docs/2026-02-20/tasks/各小队任务完成汇总_T17-T22.md`
- `docs/2026-02-20/tasks/各小队任务完成汇总_T23-T27.md`

### P0（必须埋，影响后期重构成本）

1. **Registry（身份台账）**：统一 `skill_id + revision + pack_hash + permit + tombstone_state`。
2. **Ruleset 版本化**：每次 GateDecision 必带 `ruleset_revision`，口径可复现。
3. **Permit 强制钩子**：所有“副作用动作”统一走 `permit_required(action)`。
4. **Append-only Audit Events**：事实日志可回放，支撑复核与运营。
5. **Usage/Quota 计量**：先能算账，后面才能做会员/成本治理。

### P1（建议埋，未来防漂移/防失控）

6. **Regression Set 占位**：固定样例防输出漂移。
7. **UI 文案映射合同（i18n_key）**：避免硬编码漂移。
8. **Feature Flags**：半成品能力默认关，防污染主流程。
9. **Repro Env 指纹占位**：provenance 中记录环境指纹字段（实现后置）。

### DoD（埋种子收官标准）

* 每个模板文件落盘到位（见下方 templates）
* 审计跑一次后：`registry`、`audit_events`、`usage` 至少各新增 1 条记录
* GateDecision 中出现：`ruleset_revision` 与 `provenance.repro_env` 字段（可先占位）

---

# 对应的最小文件模板（直接复制到仓库）

## 1) registry/skills.jsonl（append-only）

```jsonl
{"skill_id":"SKILL-PLACEHOLDER","source":{"type":"repo","repo_url":"REPO_URL","commit_sha":"COMMIT_SHA"},"revision":"REV-000000","pack_hash":"PACK-SHA256","permit_id":"PERMIT-PLACEHOLDER","tombstone_state":"ACTIVE","created_at":"2026-02-20T00:00:00Z"}
```

**写入点（最小）**：`pack_audit_and_publish` 成功产出 pack 后追加一行
**读取点（最小）**：上架/执行前按 `skill_id` 查最新 `ACTIVE` revision

---

## 2) orchestration/ruleset_manifest.yml（审计口径版本）

```yaml
version: 1
ruleset_revision: "v1"
sources:
  audit_engine_protocol: "docs/AUDIT_ENGINE_PROTOCOL_v1.md"
  quality_gate_levels: "orchestration/quality_gate_levels.yml"
  error_policy: "orchestration/error_policy.yml"
  error_codes: "orchestration/error_codes.yml"
notes: "Bump ruleset_revision when any of the above changes."
```

**写入点**：每次 `GateDecision` 写入 `ruleset_revision`
**读取点**：UI/报告展示 + at-time 复现时校验口径一致

---

## 3) orchestration/feature_flags.yml（能力开关）

```yaml
version: 1
flags:
  enable_sandbox_test: true
  enable_n8n_execution: false
  enable_github_intake_external: false  # GitHub 审计仅系统内部：默认 false
```

**写入点**：gate 执行时读取开关决定是否跳过/降级（仍要写 EvidenceRef）
**读取点**：Work UI 显示当前启用能力（可选）

---

## 4) security/permit_policy.yml（permit_required 规则表）

```yaml
version: 1
actions_requiring_permit:
  - PUBLISH_LISTING
  - EXECUTE_VIA_N8N
  - EXPORT_WHITELIST
  - UPGRADE_REPLACE_ACTIVE
deny_without_permit_error_code: "PERMIT_REQUIRED"
```

**写入点**：动作入口统一检查 permit（中间件）
**读取点**：WorkComposer 的 Run/Publish 按钮灰显依据

---

## 5) logs/audit_events.jsonl（append-only 事实日志）

```jsonl
{"event_type":"GATE_FINISH","job_id":"JOB-PLACEHOLDER","gate_node":"intake_repo","decision":"PASS","error_code":null,"issue_keys":[],"evidence_refs":["EV-PLACEHOLDER"],"ts":"2026-02-20T00:00:00Z"}
```

**写入点**：每个 gate 结束必写（PASS/FAIL/SKIPPED 都写）
**读取点**：Gate Timeline UI / 复盘报告生成器

---

## 6) logs/usage.jsonl（计量/配额）

```jsonl
{"account_id":"ACC-PLACEHOLDER","action":"AUDIT_L3","units":1,"job_id":"JOB-PLACEHOLDER","ts":"2026-02-20T00:00:00Z"}
```

**写入点**：任务入队/接受时扣减（不是完成时）
**读取点**：会员/配额判断、成本统计

---

## 7) regression/README.md（回归集占位）

```md
# Regression Set (v0)
Purpose: prevent drift in audit/plan outputs.

- Keep inputs + expected summaries stable.
- Every upgrade must run: `gm validate --regression`.

Add cases under:
- regression/cases/<case_id>/{input.json, expected.md}
```

---

## 8) ui/contracts/i18n_keys.yml（UI 文案键占位）

```yaml
version: 1
keys:
  - gate.intake_repo.title
  - gate.license_gate.title
  - gate.repo_scan_fit_score.title
  - gate.draft_skill_spec.title
  - gate.constitution_risk_gate.title
  - gate.scaffold_skill_impl.title
  - gate.sandbox_test_and_trace.title
  - gate.pack_audit_and_publish.title
  - error.fallback.title
  - error.fallback.message
```

---

## 9) templates/provenance.json（repro_env 指纹占位）

```json
{
  "captured_at": "2026-02-20T00:00:00Z",
  "source": { "repo_url": "REPO_URL", "commit_sha": "COMMIT_SHA" },
  "ruleset_revision": "v1",
  "repro_env": {
    "python_version": "3.11",
    "deps_lock_hash": "LOCKHASH-PLACEHOLDER",
    "os": "OS-PLACEHOLDER",
    "tool_versions": { "gm_skillforge": "0.0.0" }
  }
}
```

**写入点**：intake_repo 或 pack_audit_and_publish 写入 provenance（字段可占位）
**读取点**：AuditPack manifest/provenance 展示 + at-time 复现核验

---


