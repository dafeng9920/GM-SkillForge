# L4.5 外部 Skill 治理导入（Batch-1）任务分派总表

> 任务编号: `L45-D3-EXT-SKILL-GOV-20260220-003`  
> 主控模式: Task Skill Spec（并行执行）  
> 唯一合并权: `vs--cc3`

---

## 1. 波次看板

| 波次 | 任务 | 执行者 | 依赖 | 预计时长 | 状态 | Gate Decision |
|------|------|--------|------|----------|------|---------------|
| Wave 1 | T12 | vs--cc3 | - | 90min | ⏳ 待启动 | - |
| Wave 1 | T13 | vs--cc1 | - | 80min | ⏳ 待启动 | - |
| Wave 1 | T14 | vs--cc2 | - | 85min | ⏳ 待启动 | - |
| Wave 1 | T15 | Kior-B | - | 90min | ⏳ 待启动 | - |
| Wave 2 | T16 | Kior-C | T12,T13,T14,T15 | 90min | ⏳ 待启动 | - |

状态标记: `⏳ 待启动 | 🔄 执行中 | 📤 已提交 | ✅ ALLOW | ⚠️ REQUIRES_CHANGES | ❌ DENY`

---

## 2. 并行规则

1. `T12-T15` 为并行任务，可同时启动。
2. 任一并行任务未提交，不得启动 `T16`。
3. 任一任务 Gate Decision 非 `ALLOW`，`T16` 必须输出 `REQUIRES_CHANGES` 或 `DENY`。
4. 失败项必须写明阻塞原因与整改建议，不得留空。

---

## 3. 全局常量（所有任务共用）

```yaml
job_id: "L45-D3-EXT-SKILL-GOV-20260220-003"
skill_id: "l45_external_skill_governance_batch1"
fixed_inputs:
  - repo_url
  - commit_sha
  - at_time
  - external_skill_ref
```

---

## 4. 收口清单（T16）

1. `docs/2026-02-20/L45_EXTERNAL_SKILL_GOV_INTEGRATION_REPORT_v1.md`
2. `docs/2026-02-20/verification/T16_gate_decision.json`
3. `docs/2026-02-20/verification/T16_execution_report.yaml`
4. `docs/2026-02-20/tasks/各小队任务完成汇总_T12-T16.md`

---

## 5. 目标判定

```yaml
target_verdict:
  implementation_ready: "YES|NO"
  regression_ready: "YES|NO"
  baseline_ready: "YES|NO"
  ready_for_next_batch: "YES|NO"
```

