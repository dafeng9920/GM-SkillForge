# 发布系统总控看板 v1

> **更新时间**: 2026-02-18
> **状态**: OPERATIONAL

---

## 1. 运行实例汇总

| # | run_id | phase | permit_id | replay_pointer | 状态 | SLA报告 |
|---|--------|-------|-----------|----------------|------|---------|
| 1 | `RUN-20260218-CANARY-001` | Canary Release | `PERMIT-20260218-001` | `REPLAY-20260218-CANARY-001-SHA-a1b2c3d4` | ✅ PASS | [canary_release_audit_rollback_execution_report_v1.md](canary_release_audit_rollback_execution_report_v1.md) |
| 2 | `RUN-20260218-BATCH2-001` | Batch Release (2 Targets) | `PERMIT-20260218-BATCH-A-001` / `PERMIT-20260218-BATCH-B-001` | `REPLAY-20260218-BATCH2-001-SHA-x1y2z3a4` | ✅ PASS | [batch_release_2targets_execution_report_v1.md](batch_release_2targets_execution_report_v1.md) |
| 3 | `RUN-20260218-IAMOPA-001` | IAM/OPA Integration | `PERMIT-20260218-IAMOPA-001` | N/A (链路测试) | ✅ PASS | [iam_opa_integration_execution_report_v1.md](iam_opa_integration_execution_report_v1.md) |

---

## 2. 核心标识符索引

### 2.1 run_id 索引

| run_id | 类型 | 创建时间 | 关联 permit_id |
|--------|------|----------|----------------|
| `RUN-20260218-CANARY-001` | Canary | 2026-02-18T10:00:00Z | `PERMIT-20260218-001` |
| `RUN-20260218-BATCH2-001` | Batch | 2026-02-18T12:00:00Z | `PERMIT-20260218-BATCH-A-001`, `PERMIT-20260218-BATCH-B-001` |
| `RUN-20260218-IAMOPA-001` | Integration | 2026-02-18T14:00:00Z | `PERMIT-20260218-IAMOPA-001` |

### 2.2 permit_id 索引

| permit_id | run_id | key_id | 签发时间 | 过期时间 | 状态 |
|-----------|--------|--------|----------|----------|------|
| `PERMIT-20260218-001` | `RUN-20260218-CANARY-001` | `KEY-2026-PRIMARY` | 2026-02-18T10:00:00Z | 2026-02-18T22:00:00Z | VALID |
| `PERMIT-20260218-BATCH-A-001` | `RUN-20260218-BATCH2-001` | `KEY-2026-PRIMARY` | 2026-02-18T12:00:00Z | 2026-02-19T12:00:00Z | VALID |
| `PERMIT-20260218-BATCH-B-001` | `RUN-20260218-BATCH2-001` | `KEY-2026-PRIMARY` | 2026-02-18T12:00:00Z | 2026-02-19T12:00:00Z | VALID |
| `PERMIT-20260218-IAMOPA-001` | `RUN-20260218-IAMOPA-001` | `KEY-2026-PRIMARY` | 2026-02-18T14:00:01Z | 2026-02-19T02:00:01Z | VALID |

### 2.3 replay_pointer 索引

| replay_pointer | run_id | 类型 | 可回放 | EvidenceRef |
|----------------|--------|------|--------|-------------|
| `REPLAY-20260218-CANARY-001-SHA-a1b2c3d4` | `RUN-20260218-CANARY-001` | commit_sha | ✅ | `EV-CANARY-001-REPLAY` |
| `REPLAY-20260218-BATCH2-001-SHA-x1y2z3a4` | `RUN-20260218-BATCH2-001` | commit_sha | ✅ | `EV-BATCH-001-REPLAY` |

---

## 3. SLA 汇总

### 3.1 IAM/OPA 链路 SLA

| 指标 | P50 | P95 | P99 | SLA 目标 | 状态 |
|------|-----|-----|-----|----------|------|
| 签发延迟 | 85ms | 120ms | 180ms | <500ms | ✅ |
| 验签延迟 | 12ms | 25ms | 45ms | <100ms | ✅ |
| 端到端延迟 | 97ms | 145ms | 225ms | <600ms | ✅ |

### 3.2 发布执行 SLA

| run_id | 发布耗时 | 观察窗口 | 回滚耗时 | 状态 |
|--------|----------|----------|----------|------|
| `RUN-20260218-CANARY-001` | 5m23s | 30min | 1m35s | ✅ |
| `RUN-20260218-BATCH2-001` | 1m45s (并行) | N/A | N/A | ✅ |

### 3.3 Tombstone 存储 SLA

| 指标 | 目标 | 当前状态 |
|------|------|----------|
| 写入可用性 | 99.99% | 待部署 |
| 读取可用性 | 99.9% | 待部署 |
| 数据持久性 | 11 个 9 | 待部署 |

---

## 4. Fail-Closed 验证汇总

| run_id | E001 阻断 | E003 阻断 | all-or-nothing | EvidenceRef |
|--------|-----------|-----------|----------------|-------------|
| `RUN-20260218-CANARY-001` | ✅ PASS | ✅ PASS | N/A | `EV-CANARY-001-E001`, `EV-CANARY-001-E003` |
| `RUN-20260218-BATCH2-001` | ✅ PASS | ✅ PASS | ✅ PASS | `EV-BATCH-001-E001`, `EV-BATCH-001-E003` |
| `RUN-20260218-IAMOPA-001` | ✅ PASS | ✅ PASS | N/A | `EV-IAMOPA-001-E001`, `EV-IAMOPA-001-E003` |

---

## 5. 文档路径索引

### 5.1 规范文档

| 文档 | 路径 |
|------|------|
| Permit 签发链路规范 | [permit_issuance_chain_spec_v1.md](permit_issuance_chain_spec_v1.md) |
| Tombstone 持久化契约 | [tombstone_persistence_contract_v1.md](tombstone_persistence_contract_v1.md) |

### 5.2 运行单

| 文档 | 路径 |
|------|------|
| Canary Release 运行单 | [canary_release_run_sheet_v1.md](canary_release_run_sheet_v1.md) |
| Post-Release Audit 记录 | [post_release_audit_record_v1.md](post_release_audit_record_v1.md) |
| Rollback Drill 运行单 | [canary_rollback_drill_run_sheet_v1.md](canary_rollback_drill_run_sheet_v1.md) |
| Batch Release 运行单 | [batch_release_2targets_run_sheet_v1.md](batch_release_2targets_run_sheet_v1.md) |
| IAM/OPA 集成运行单 | [iam_opa_integration_run_sheet_v1.md](iam_opa_integration_run_sheet_v1.md) |

### 5.3 执行报告

| 文档 | 路径 |
|------|------|
| Canary+Audit+Rollback 执行报告 | [canary_release_audit_rollback_execution_report_v1.md](canary_release_audit_rollback_execution_report_v1.md) |
| Phase B→C→A 执行报告 | [phase_bca_execution_report_v1.md](phase_bca_execution_report_v1.md) |
| Batch Release 执行报告 | [batch_release_2targets_execution_report_v1.md](batch_release_2targets_execution_report_v1.md) |
| IAM/OPA 集成执行报告 | [iam_opa_integration_execution_report_v1.md](iam_opa_integration_execution_report_v1.md) |

---

## 6. 组件状态

| 组件 | 状态 | 说明 |
|------|------|------|
| IAM/OPA 签发服务 | 🟢 OPERATIONAL | 真实链路已验证 |
| Permit Gate | 🟢 OPERATIONAL | E001/E003 阻断成立 |
| Tombstone Store | 🟡 PENDING | 规范已定，待部署 |
| Batch Release Engine | 🟢 OPERATIONAL | 2 目标并行验证通过 |
| Rollback Engine | 🟢 OPERATIONAL | tombstone/回放链验证通过 |

---

## 7. 风险看板

| # | 风险 | 影响 | 状态 | 处置 |
|---|------|------|------|------|
| R001 | IAM 服务单点故障 | 高 | 🔴 OPEN | 多区域部署 |
| R002 | Tombstone 基础设施待部署 | 高 | 🟡 IN_PROGRESS | Kafka/EventStore 部署中 |
| R003 | Batch >2 目标未验证 | 中 | 🟡 OPEN | 后续扩展 |
| R004 | 签发服务降级时发布阻塞 | 中 | 🟡 OPEN | 队列+重试机制 |
| R005 | Key 泄露影响范围大 | 高 | 🟡 OPEN | 应急响应流程 |

---

## 8. 里程碑

| 里程碑 | 状态 | 完成时间 |
|--------|------|----------|
| M1: Fail-Closed 框架 | ✅ 完成 | 2026-02-17 |
| M2: Permit Contract v1 | ✅ 完成 | 2026-02-18 |
| M3: IAM/OPA 集成 | ✅ 完成 | 2026-02-18 |
| M4: Batch Release (2 目标) | ✅ 完成 | 2026-02-18 |
| M5: Tombstone 部署 | 🟡 进行中 | TBD |
| M6: 业务应用层 E2E | 🔵 待开始 | 2026-02-18 |
| M7: 多目标 Batch 扩展 | 🔵 待开始 | TBD |

---

*看板版本: v1 | 更新时间: 2026-02-18T15:00:00Z*
