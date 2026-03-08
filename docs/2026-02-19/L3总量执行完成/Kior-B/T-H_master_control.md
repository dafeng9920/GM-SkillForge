# T-H1/H2: 文档与签核

> **执行者**: Kior-B
> **波次**: Batch-C
> **优先级**: P2
> **依赖**: Batch-C 其余任务全部 PASS
> **预计时间**: 45 分钟

---

## 任务目标

1. **T-H1**: 生成 L3 总控汇总表并签核
2. **T-H2**: 回写 TODO.MD

---

## 输入合同

### 需要阅读的文件

| 文件 | 用途 |
|------|------|
| `docs/2026-02-18/phase1_release_governor_signoff_v1.md` | 参考格式 |
| `docs/2026-02-16/TODO.MD` | 待更新文件 |
| `docs/2026-02-19/L3_A1_gate_verification_report.md` | A 验收证据 |
| `docs/2026-02-19/L3_B2_contract_validation_report.md` | B 验收证据 |
| `docs/2026-02-19/L3_C1_evidence_ref_chain_verification.md` | C 验收证据 |
| `docs/2026-02-19/L3_D1_reproducibility_test_report.md` | D 验收证据 |
| `docs/2026-02-19/L3_E1_skill_pack_acceptance.md` | E 验收证据 |
| `docs/2026-02-19/L3_F_metrics_summary.md` | F 验收证据 |
| `docs/2026-02-19/L3_G1_canary_drill_archive.md` | G 验收证据 |

### 贯穿常量

```yaml
phase: "L3"
signoff_date: "2026-02-19"
```

---

## 输出合同

### 交付物

| 文件路径 | 类型 | 说明 |
|----------|------|------|
| `docs/2026-02-19/L3_master_control_summary.md` | 新建 | L3 总控汇总表 |

### 总控汇总表格式

```yaml
master_control_summary:
  # 基本信息
  phase: "L3"
  date: "2026-02-19"
  operator: "Kior-B"

  # 批次状态
  batches:
    - name: "Batch-A"
      tasks: ["T-A1", "T-A2", "T-B1", "T-B2", "T-C1", "T-C2"]
      status: "PASS | FAIL"
    - name: "Batch-B"
      tasks: ["T-D1", "T-D2", "T-E1", "T-E2"]
      status: "PASS | FAIL"
    - name: "Batch-C"
      tasks: ["T-F1", "T-F2", "T-G1", "T-G2", "T-G3", "T-H1", "T-H2"]
      status: "PASS | FAIL"

  # 验收勾选
  acceptance_checklist:
    A_governance_gates: bool
    B_intent_contracts: bool
    C_evidence_audit: bool
    D_reproducibility: bool
    E_skill_ci: bool
    F_metrics: bool
    G_drills: bool
    H_documentation: bool

  # 最终决策
  final_decision:
    all_passed: bool
    blocking_issues: array
    release_allowed: bool
    conclusion: "YES | NO"

  # 签核
  signoff:
    signer: string
    timestamp: string
```

### TODO.MD 更新内容

```markdown
### L. L3 收官（2026-02-19）

> **总控汇总**: `docs/2026-02-19/L3_master_control_summary.md`

**批次状态**:
- [√] **Batch-A**: 治理门禁 + 合同 + 证据 → PASS
- [√] **Batch-B**: 复现 + Skill+CI → PASS
- [√] **Batch-C**: 指标 + 演练 + 签核 → PASS

**验收结果**:
- A-H 全部完成
- 无可绕过门禁的 OPEN 阻断项
- 放行结论: YES/NO

**签核**:
- 签核人: Kior-B
- 签核时间: 2026-02-19Txx:xx:xxZ
```

---

## 硬约束

1. 必须引用所有批次验收证据
2. 必须明确放行结论
3. TODO.MD 必须记录完整

---

## 红线 (Deny List)

- [ ] 不得遗漏任何验收项
- [ ] 不得伪造签核
- [ ] 不得跳过证据引用

---

## 质量门禁

### 人工检查

- [ ] A-H 全部完成勾选
- [ ] 批次状态全部 PASS
- [ ] 放行结论明确
- [ ] 签核信息完整
- [ ] TODO.MD 已更新

---

## 回传格式

```yaml
task_id: "T-H1/H2"
executor: "Kior-B"
status: "完成 | 部分完成 | 阻塞"

deliverables:
  - path: "docs/2026-02-19/L3_master_control_summary.md"
    action: "新建"
  - path: "docs/2026-02-16/TODO.MD"
    action: "修改"

evidence_ref: "EV-L3-H1-H2-xxx"

notes: "特殊情况说明"
```

---

## 验收标准

- [ ] 总控汇总表创建
- [ ] A-H 全部勾选
- [ ] 放行结论明确
- [ ] TODO.MD 已更新

---

*任务生成时间: 2026-02-19*
