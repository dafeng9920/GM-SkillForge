# L4.5 Frontend v1.0 任务分派总表（T35-T40）

> 任务编号: `L45-FE-V10-20260220-007`  
> 主控模式: Task Skill Spec（并行执行）  
> 范围基线: `docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md` `v1.7`（v1.0 先行）  
> 唯一合并权: `vs--cc3`

---

## 1. 波次看板

| 波次 | 任务 | 执行者 | 依赖 | 预计时长 | 状态 | Gate Decision |
|------|------|--------|------|----------|------|---------------|
| Wave 1 | T35 | vs--cc3 | - | 90min | ⏳ 待启动 | - |
| Wave 1 | T36 | vs--cc1 | - | 90min | ⏳ 待启动 | - |
| Wave 1 | T37 | vs--cc2 | - | 90min | ⏳ 待启动 | - |
| Wave 1 | T38 | Kior-B | - | 90min | ⏳ 待启动 | - |
| Wave 1 | T39 | Kior-A | - | 85min | ⏳ 待启动 | - |
| Wave 2 | T40 | Kior-C | T35,T36,T37,T38,T39 | 90min | ⏳ 待启动 | - |

状态标记: `⏳ 待启动 | 🔄 执行中 | 📤 已提交 | ✅ ALLOW | ⚠️ REQUIRES_CHANGES | ❌ DENY`

---

## 2. 执行规则

1. `T35-T39` 并行执行，均为 v1.0 前端先行能力。  
2. 任一并行任务未提交，不得启动 `T40`。  
3. `T40` 非 `ALLOW` 时，不得标记 `READY_FOR_FE_V1.0=YES`。  
4. 所有页面/组件路由命名必须按业务域（`/execute`、`/audit`、`/system`），v1.0 不暴露 `n8n` 顶层路由。  
5. 所有 BLOCK 场景必须统一复用 `BlockReasonCard`，不得各页自定义错误结构。  
6. 所有任务必须遵循执行法案：先 Proposal 合同，再 Compliance 复查，再 Execution。  
7. 无 `ComplianceAttestation=PASS` 的提交不得进入合并。  
8. 涉及副作用动作（发布/外部 API/执行臂）必须附 `permit=VALID` 证据。  

---

## 2.1 执行法案（A/B）强约束

统一引用：
- `docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

每个任务（T35-T40）提交前必须补齐以下产物：
1. `ExecutionContract`（结构化合同，含 execution/review/compliance 三角色）
2. `ComplianceAttestation`（`decision=PASS` + `evidence_refs` + `contract_hash`）
3. `EvidenceRefs`（至少覆盖 build 结果 + 页面/交互证据）
4. `Permit`（仅当任务触发 PUBLISH/EXTERNAL_API 时要求 `VALID`）

推荐落盘位置（按 task_id）：
- `docs/2026-02-20/verification/Txx_execution_contract.json`
- `docs/2026-02-20/verification/Txx_compliance_attestation.json`
- `docs/2026-02-20/verification/Txx_evidence_refs.json`
- `docs/2026-02-20/verification/Txx_permit.json`（按需）

不满足上述任一 MUST：
- 任务状态只能标记 `⚠️ REQUIRES_CHANGES`
- 不得进入 `T40` 主控签核

---
## 3. 全局常量（所有任务共用）

```yaml
job_id: "L45-FE-V10-20260220-007"
skill_id: "l45_frontend_v10_execution_pack"
requirements_doc: "docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md"
ui_root: "ui/app"
```

---

## 4. 收口清单

1. `docs/2026-02-20/L45_FRONTEND_V10_INTEGRATION_REPORT_v1.md`
2. `docs/2026-02-20/verification/T40_gate_decision.json`
3. `docs/2026-02-20/verification/T40_execution_report.yaml`
4. `docs/2026-02-20/tasks/各小队任务完成汇总_T35-T40.md`
5. `docs/2026-02-20/verification/T35-T40_execution_guard_index.yaml`（新增：法案产物索引）

---

## 5. 可调用 Skill 清单（统一调度入口）

本批次可调用 Skill 清单见 `docs/templates/dispatch_skill_catalog.md`；本文件仅维护批次特有映射。

| skill | 在 T35-T40 中的使用点 | 责任任务 |
|---|---|---|
| `task-pack-writer-skill` | 任务包结构与模板一致性检查 | `T35` |
| `experience-template-retriever-skill` | 复用历史 IssueKey/FixKind 前端整改模板 | `T36-T39` |
| `drill-evidence-collector-skill` | run_id/evidence_ref 链路验收证据归档 | `T38,T40` |
| `seed-gate-validator-skill` | 收口前 strict 校验（build/lint/关键回归） | `T40` |
| `master-signoff-skill` | T40 主控终判输出 | `T40` |

### 调用约束

1. 所有页面必须附 `run_id/evidence_ref` 可交互链路设计或实现证据。  
2. 仅在 `T40_gate_decision=ALLOW` 时可更新汇总终判为 `READY_FOR_FE_V1.0=YES`。  
3. 任一任务缺少可复验命令与产物路径，不得标记 `COMPLETED`。  
