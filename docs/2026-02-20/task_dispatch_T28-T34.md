# L4.5 SEEDS v0（P2）任务分派总表

> 任务编号: `L45-D6-SEEDS-P2-20260220-006`  
> 主控模式: Task Skill Spec（并行执行）  
> 唯一合并权: `vs--cc3`

---

## 1. 波次看板

| 波次 | 任务 | 执行者 | 依赖 | 预计时长 | 状态 | Gate Decision |
|------|------|--------|------|----------|------|---------------|
| Wave 1 | T28 | vs--cc3 | - | 85min | ⏳ 待启动 | - |
| Wave 1 | T29 | vs--cc1 | - | 85min | ⏳ 待启动 | - |
| Wave 1 | T30 | vs--cc2 | - | 80min | ⏳ 待启动 | - |
| Wave 1 | T31 | Kior-B | - | 85min | ⏳ 待启动 | - |
| Wave 1 | T32 | Kior-A | - | 80min | ⏳ 待启动 | - |
| Wave 2 | T33 | Kior-C | T28,T29,T30,T31,T32 | 90min | ⏳ 待启动 | - |
| Wave 3 | T34 | 主控官 | T33 | 45min | ⏳ 待启动 | - |

状态标记: `⏳ 待启动 | 🔄 执行中 | 📤 已提交 | ✅ ALLOW | ⚠️ REQUIRES_CHANGES | ❌ DENY`

---

## 2. 执行规则

1. `T28-T32` 并行执行。
2. 任一并行任务未提交，不得启动 `T33`。
3. `T33` 非 `ALLOW` 时，`T34` 不得签发 `READY_FOR_P2_AUTORUN=YES`。

---

## 3. 全局常量（所有任务共用）

```yaml
job_id: "L45-D6-SEEDS-P2-20260220-006"
skill_id: "l45_seeds_p2_operationalization"
seed_doc: "docs/SEEDS_v0.md"
```

---

## 4. 收口清单

1. `docs/2026-02-20/L45_SEEDS_P2_TECH_CLOSEOUT_v1.md`
2. `docs/2026-02-20/verification/T33_gate_decision.json`
3. `docs/2026-02-20/verification/T33_execution_report.yaml`
4. `docs/2026-02-20/L45_P2_MASTER_SIGNOFF_v1.md`
5. `docs/2026-02-20/tasks/各小队任务完成汇总_T28-T34.md`

---

## 5. 可调用 Skill 清单（统一调度入口）

统一清单引用：`docs/templates/dispatch_skill_catalog.md`  
本节仅维护 T28-T34 的批次特有映射。

| skill | 在 T28-T34 中的使用点 | 责任任务 |
|---|---|---|
| `seed-gate-validator-skill` | P2 收口前执行 strict 校验 | `T33` |
| `master-signoff-skill` | 基于 T33 结果签发终判 | `T34` |
| `task-pack-writer-skill` | 后续批次任务包生成（T35+） | 主控官 |
| `drill-evidence-collector-skill` | 演练证据结构化写回 | `T33/T34`（按需） |
| `experience-template-retriever-skill` | 按 IssueKey/FixKind 取历史模板 | `T28-T32`（按需） |

### 调用约束

1. `T33` 必须记录 `seed-gate-validator-skill` 输出证据。  
2. `T34` 签核必须引用 `T33_gate_decision.json`。  
3. 任一 skill 输出未落盘，不得标记该任务 `COMPLETED`。  
