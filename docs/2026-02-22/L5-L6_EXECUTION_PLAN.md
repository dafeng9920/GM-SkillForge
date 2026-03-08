# L5-L6 Execution Plan（2026-02-25）

目标：从当前 `L4.5_ACHIEVED` 推进到 `L5`，再推进到 `L6`。  
基线日期：2026-02-25。  
约束：继续遵守三权分立与 A/B Guard，所有结论必须可追溯到 EvidenceRef。

---

## 1. 阶段门槛（Stage Gates）

### Stage A：L4.5 收口（前置门槛）

状态：`COMPLETED`（已达成）。

收口结果：

1. 最终 Gate：`docs/2026-02-22/verification/L4P5_final_gate_decision.json = ALLOW`。
2. 依赖链闭合：`T93=ALLOW -> T94=PASS -> T98=ALLOW -> T99=PASS -> T100=COMPLETED`。
3. 三权分立证据齐全：Execution/Review/Compliance 记录完整，且无 fail-open 路径。
4. 统一治理资产已落地：`governance-orchestrator-skill + dispatch registry + dispatch/gate CLI`。

历史门槛（已完成）：

1. `n8n production endpoints` 从 `NOT_IMPLEMENTED` 升级为 `VERIFIED`。
2. `P2` 证据包冻结完成（含索引与 hash）。
3. 至少 1 次远端 CI/PR 流水线通过并留存证据。
4. `run_3day_compliance_review.py --run-tests` 结果中 `critical_or_high_failed=0`。

Gate 决策：已 `ALLOW`，当前推进 Stage B。

### Stage B：L5（规模化可靠运行）

必须全部满足，才允许进入 L6：

1. 并发能力达标（见指标 M1~M3）。
2. 自动重试/降级策略达标（见指标 M4~M6）。
3. 运行时压测与回放一致性达标（见指标 M7~M9）。
4. 连续 7 天 nightly gate 无 CRITICAL/HIGH 阻断。

Gate 决策：`ALLOW` 才可进入 Stage C。

### Stage C：L6（长期稳定自治）

判定标准：

1. 连续 30 天稳定运行，无未处置的 CRITICAL 事件。
2. 关键路径具备自动回滚与自动恢复，且演练通过。
3. 漂移监控与容量预测生效，告警闭环可审计。
4. 月度治理审计可复现（同输入同结论偏差在阈值内）。

Gate 决策：`FINAL_PASS` 即可宣告 L6 达成。

---

## 2. 指标定义（Metrics & SLO）

| ID | 指标 | L5 门槛 | L6 门槛 | 采集来源 |
|---|---|---|---|---|
| M1 | 并发任务成功率 | >= 99.0%（1000 次） | >= 99.5%（月度） | orchestrator/n8n 执行日志 |
| M2 | P95 端到端时延 | <= 5s | <= 3s | run trace + APM |
| M3 | 队列积压恢复时间 | <= 10 分钟 | <= 5 分钟 | queue metrics |
| M4 | 自动重试恢复率 | >= 85% | >= 92% | retry telemetry |
| M5 | 降级触发正确率 | >= 95% | >= 98% | incident replay |
| M6 | 人工介入率 | <= 10% | <= 5% | ops records |
| M7 | 压测失败率 | <= 1% | <= 0.5% | load test report |
| M8 | 回放一致性 | >= 99% | >= 99.5% | replay compare |
| M9 | 证据链完整率 | 100% | 100% | audit pack scan |
| M10 | 夜间 gate 通过率 | >= 95%（7天） | >= 98%（30天） | CI/nightly |

说明：任何 `M9 < 100%` 直接 `DENY`。

---

## 3. 任务拆解（Work Breakdown）

## Wave 1：L4.5 收口（已完成）

1. N1：实现 n8n production endpoints（替换 Mock 链路）。
2. N1-V：补充 n8n 端到端验证与 probe 证据（目标 `VERIFIED`）。
3. N2：冻结 P2 证据包（索引、hash、签署）。
4. N3：触发远端 CI/PR，固化主干可追溯证据。

完成交付（关键）：

- `docs/2026-02-22/verification/n8n_probe_report.json`（VERIFIED）
- `docs/2026-02-22/verification/P2_CLOSING_FREEZE.md`
- 远端流水线运行证据（URL/截图/日志摘要）
- `docs/2026-02-22/verification/L4P5_final_gate_decision.json`（ALLOW）
- `docs/2026-02-22/verification/T100_execution_report.yaml`

## Wave 2：L5 核心能力（3-7 天）

1. 并发执行模型升级：多任务并发、队列隔离、背压控制。
2. 重试与降级策略：分层重试（瞬态/非瞬态），降级路径可审计。
3. 压测与回放：建立固定压测场景 + 回放一致性校验脚本。
4. CI Nightly 门禁：自动化执行 M1~M10 核心检查。
5. Skill 产品化接入（调度能力固化）：
   - `S1`：为 `governance-orchestrator-skill` 维护跨平台发现元数据（保留与旧 skill 兼容映射）。
   - `S2`：统一发现器（扫描 `skills/ + .agents/skills`，合并为单一 registry 视图）。
   - `S3`：在 `skillforge` CLI 提供 `dispatch next/validate` 与 `gate final` 子命令，直接调用调度与最终裁决流程。

### Wave 2.1：Skill 产品化验收口径（S1-S3）

1. `S1 openai.yaml` 验收：
   - 文件存在：`skills/governance-orchestrator-skill/agents/openai.yaml`
   - 字段最小集：`name / description / version / default_prompt`
   - 通过现有 CI Skill 校验脚本。
2. `S2 统一发现器` 验收：
   - 可同时扫描 `skills/` 与 `.agents/skills`
   - 输出单一映射文件：`configs/dispatch_skill_registry.json`
   - 冲突策略可解释（同名 skill 的优先级与来源标注）。
3. `S3 CLI 子命令` 验收：
   - `skillforge dispatch next --date ... --dispatch ... --prompts ...` 可运行
   - `skillforge dispatch validate --date ... --dispatch ... --prompts ... --dispatch-registry ...` 可运行
   - `skillforge gate final --date ... --scope ...` 可运行
   - 输出与 `scripts/dispatch_next.py`、`validate_dispatch_pack.py`、`scripts/gate_final_decision.py` 一致。

交付：

- `reports/l5-load/` 压测报告
- `reports/l5-replay/` 回放一致性报告
- nightly gate 报告与失败工单链路
- `skills/governance-orchestrator-skill/agents/openai.yaml`
- `configs/dispatch_skill_registry.json`
- `scripts/dispatch_next.py`（CLI 接入后保留为底层实现）
- `scripts/gate_final_decision.py`
- `scripts/skillforge_audit.py` 或对应 CLI 入口文件中的 `dispatch/gate` 子命令实现证据

## Wave 3：L6 长稳自治（2-4 周）

1. 自动回滚：关键失败场景触发回滚并记录证据链。
2. 长期稳定性：连续 30 天运行观测与周报机制。
3. 漂移与容量治理：策略漂移监控、容量预测、阈值自适应。
4. 自治审计：月度闭环复盘，确保“证据先于解释”。

交付：

- `reports/l6-stability/30d_stability_report.json`
- `reports/l6-autonomy/rollback_drill_*.md`
- `docs/{date}/verification/l6_monthly_audit.json`

---

## 4. 证据模板（Evidence Templates）

### 4.1 Gate Decision（JSON）

```json
{
  "stage": "L5",
  "decision": "ALLOW",
  "decided_at": "2026-02-22T00:00:00Z",
  "summary": {
    "total_checks": 10,
    "failed": 0,
    "critical_or_high_failed": 0
  },
  "metrics": {
    "M1_success_rate": 99.2,
    "M2_p95_latency_ms": 3200
  },
  "evidence_refs": [
    {"id": "EV-L5-001", "kind": "FILE", "locator": "reports/l5-load/latest.json"},
    {"id": "EV-L5-002", "kind": "FILE", "locator": "reports/l5-replay/latest.json"}
  ],
  "required_changes": []
}
```

### 4.2 Execution Report（YAML）

```yaml
task_id: "L5-W2-T03"
executor: "Antigravity-1"
status: "完成"
deliverables:
  - path: "skillforge/src/api/routes/n8n_orchestration.py"
    action: "修改"
gate_self_check:
  - command: "pytest -q skillforge/tests/test_n8n_orchestration.py"
    result: "passed"
  - command: "python scripts/run_3day_compliance_review.py --run-tests"
    result: "critical_or_high_failed=0"
evidence_refs:
  - id: "EV-L5-W2-T03-001"
    kind: "LOG"
    locator: "reports/l5-load/latest.log"
```

### 4.3 Compliance Attestation（JSON）

```json
{
  "task_id": "L5-W2-T03",
  "compliance_officer": "Kior-C",
  "decision": "PASS",
  "reasons": ["No fail-open path detected", "Evidence chain complete"],
  "evidence_refs": [
    {"id": "EV-C-001", "kind": "FILE", "locator": "docs/compliance_reviews/review_latest.json"}
  ],
  "contract_hash": "sha256:...",
  "reviewed_at": "2026-02-22T00:00:00Z",
  "required_changes": []
}
```

---

## 5. 风险与拦截规则（Fail-Closed）

1. 任一阶段缺失 `review + compliance + execution` 证据，直接 `DENY`。
2. 任一 CRITICAL 指标不达标，直接 `DENY`。
3. 证据链完整率非 100%，直接 `DENY`。
4. 仅描述性结论、无 EvidenceRef，不得进入下一阶段。

## 5.1 API Constitution v1（对外 API 硬准则）

对外 API 一律遵守：

1. `BYOD`（Bring Your Own Data）  
客户数据由客户侧存储与处理，平台不提供“默认代持数据”路径。

2. `Zero-Retention`  
平台默认不保留客户原始数据；仅允许保留最小治理元数据（如 `run_id/evidence_ref/hash`）。

3. `No-Inspection`  
平台不窥视客户业务明文，仅处理执行所需的最小结构化元数据与证据摘要。

上线门禁：

- 任何 API 产品不满足 `BYOD + Zero-Retention + No-Inspection`，一律 `DENY` 上线。

---

## 6. 即刻执行口令

1. 保持 `dispatch registry + gate final` 作为默认治理入口，禁止绕过。
2. 启动 Wave 2 的并发/重试/压测任务并接入 nightly。
3. 以 7 天（L5）和 30 天（L6）双周期证据驱动升级裁决。
