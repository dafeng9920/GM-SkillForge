# L3 总量任务分派总表

> **生成时间**: 2026-02-19
> **总控官**: VSCode-1 (vs--cc3)
> **唯一合并权**: VSCode-1

---

## 0. 角色分配

| 角色 | 对应 | 职责 | 任务数 |
|------|------|------|--------|
| **总控官** | vs--cc3 | 总控 + 放行裁决 | 0 (只验收) |
| **vs--cc1** | vs--cc1 | A 治理门禁 + E Skill+CI + G 演练 | 4 |
| **vs--cc2** | vs--cc2 | B 合同意图 | 1 |
| **Kior-A** | Kior-A | C 证据审计包 | 1 |
| **Kior-C** | Kior-C | D 复现回放 + F 指标窗口 | 1 |
| **Kior-B** | Kior-B | H 文档签核 | 1 |

---

## 1. 批次编排

### Batch-A (P0, 先做, 串行完成后放行)

| 任务 | 执行者 | 状态 | Gate Decision |
|------|--------|------|---------------|
| T-A1: 8/9 Gate 稳定运行 | vs--cc1 | ⏳ 待启动 | — |
| T-A2: no-permit-no-release 生效 | vs--cc1 | ⏳ 待 A1 完成 | — |
| T-B1/B2: 核心 Intents 合同冻结 | vs--cc2 | ⏳ 待启动 | — |
| T-C1/C2: 证据与审计包验证 | Kior-A | ⏳ 待启动 | — |

**Batch-A 放行条件**: 4 项任务全部 PASS

---

### Batch-B (Batch-A PASS 后并行)

| 任务 | 执行者 | 状态 | Gate Decision |
|------|--------|------|---------------|
| T-D1/D2: 复现与 at_time 验证 | Kior-C | ⏳ 待 Batch-A PASS | — |
| T-E1: 3+1 Skill 包验收 | vs--cc1 | ⏳ 待 Batch-A PASS | — |
| T-E2: skillization CI gate | vs--cc1 | ⏳ 待 E1 完成 | — |

**Batch-B 放行条件**: 3 项任务全部 PASS

---

### Batch-C (Batch-B PASS 后串行)

| 任务 | 执行者 | 状态 | Gate Decision |
|------|--------|------|---------------|
| T-F1/F2: Throughput + Closure Rate | Kior-C | ⏳ 待 Batch-B PASS | — |
| T-G1: Canary 演练归档 | vs--cc1 | ⏳ 待 Batch-B PASS | — |
| T-G2: Rollback 演练归档 | vs--cc1 | ⏳ 待 G1 完成 | — |
| T-G3: Batch 2目标演练归档 | vs--cc1 | ⏳ 待 G2 完成 | — |
| T-H1: 总控汇总表签核 | Kior-B | ⏳ 待 F+G 完成 | — |
| T-H2: TODO 回写 | Kior-B | ⏳ 待 H1 完成 | — |

**Batch-C 放行条件**: 6 项任务全部 PASS

---

## 2. 进度看板

### 状态标记

- ⏳ 待启动
- 🔄 执行中
- 📤 已提交
- ✅ ALLOW
- ⚠️ REQUIRES_CHANGES
- ❌ DENY

### 当前状态

```
Batch-A: ⏳ 待启动 (0/4 完成)
  └── T-A1: ⏳
  └── T-A2: ⏳
  └── T-B1/B2: ⏳
  └── T-C1/C2: ⏳

Batch-B: ⏳ 阻塞 (等待 Batch-A)
  └── T-D1/D2: ⏳
  └── T-E1: ⏳
  └── T-E2: ⏳

Batch-C: ⏳ 阻塞 (等待 Batch-B)
  └── T-F1/F2: ⏳
  └── T-G1: ⏳
  └── T-G2: ⏳
  └── T-G3: ⏳
  └── T-H1: ⏳
  └── T-H2: ⏳
```

---

## 3. 任务书索引

| 执行者 | 任务书路径 |
|--------|----------|
| vs--cc1 | `docs/2026-02-19/L3总量执行完成/vs--cc1/` |
| vs--cc2 | `docs/2026-02-19/L3总量执行完成/vs--cc2/` |
| Kior-A | `docs/2026-02-19/L3总量执行完成/Kior-A/` |
| Kior-B | `docs/2026-02-19/L3总量执行完成/Kior-B/` |
| Kior-C | `docs/2026-02-19/L3总量执行完成/Kior-C/` |

### 文件清单

```
docs/2026-02-19/L3总量执行完成/
├── task_dispatch.md              # 本文件
├── vs--cc1/
│   ├── T-A1_gate_verification.md
│   ├── T-A2_no_permit_verification.md
│   ├── T-E1_skill_pack_acceptance.md
│   └── T-G_drill_archive.md
├── vs--cc2/
│   └── T-B1_intent_contracts.md
├── Kior-A/
│   └── T-C_evidence_audit.md
├── Kior-C/
│   └── T-D_F_reproducibility_metrics.md
└── Kior-B/
    └── T-H_master_control.md
```

---

## 4. 放行规则

### 批次门禁

```yaml
batch_gate:
  Batch-A:
    condition: "T-A1, T-A2, T-B1/B2, T-C1/C2 全部 PASS"
    blocking: true
    next: "启动 Batch-B"

  Batch-B:
    condition: "T-D1/D2, T-E1, T-E2 全部 PASS"
    blocking: true
    next: "启动 Batch-C"

  Batch-C:
    condition: "T-F1/F2, T-G1, T-G2, T-G3, T-H1, T-H2 全部 PASS"
    blocking: true
    next: "L3 收官"
```

### 最终门禁

```yaml
final_gate:
  condition: "Batch-A + Batch-B + Batch-C 全部 PASS"
  conclusion:
    release_allowed: true | false
    blocking_issues: array
  signoff:
    signer: "总控官"
    timestamp: ISO8601
```

---

## 5. 执行规则

1. **每项必须回传**: 修改清单 + 证据路径 + PASS/FAIL + 风险
2. **未过验收不得进入下一批**
3. **唯一合并权**: VSCode-1 (vs--cc3)
4. **禁止越权**: 执行者不得修改其他执行者的任务范围

---

*生成时间: 2026-02-19*
