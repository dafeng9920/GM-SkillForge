# T-C1/C2: 证据与审计包验证

> **执行者**: Kior-A
> **波次**: Batch-A
> **优先级**: P0
> **预计时间**: 60 分钟

---

## 任务目标

1. **T-C1**: 验证每次运行均产出可回指 EvidenceRef 链
2. **T-C2**: 验证 AuditPack 哈希校验可用

---

## 输入合同

### 需要阅读的文件

| 文件 | 用途 |
|------|------|
| `docs/2026-02-18/business_phase1_execution_report_v1.md` | 检查 Evidence 链证据 |
| `docs/2026-02-18/business_phase1_acceptance_report_v1.md` | 检查验收证据 |
| `skillforge/src/skills/gates/` | 理解 Evidence 生成逻辑 |

### 贯穿常量

```yaml
run_id: "RUN-20260218-BIZ-PHASE1-001"
audit_pack_ref: "audit-10465f76"
```

---

## 输出合同

### 交付物

| 文件路径 | 类型 | 说明 |
|----------|------|------|
| `docs/2026-02-19/L3_C1_evidence_ref_chain_verification.md` | 新建 | EvidenceRef 链验证报告 |
| `docs/2026-02-19/L3_C2_auditpack_hash_verification.md` | 新建 | AuditPack 哈希校验报告 |

### EvidenceRef 链验证格式

```yaml
evidence_chain_verification:
  chain_stages:
    - stage: "Intent 提交"
      evidence_ref: "EV-PHASE1-001-INTENT"
      status: VALID | INVALID
    - stage: "Permit 签发"
      evidence_ref: "EV-PHASE1-A-PERMIT"
      status: VALID | INVALID
    - stage: "Gate 校验"
      evidence_ref: "EV-PHASE1-B-FINAL"
      status: VALID | INVALID
    - stage: "发布执行"
      evidence_ref: "EV-PHASE1-C-RELEASE"
      status: VALID | INVALID
    - stage: "Tombstone"
      evidence_ref: "EV-PHASE1-C-TOMB"
      status: VALID | INVALID
  conclusion:
    chain_complete: bool
    all_valid: bool
```

### AuditPack 哈希校验格式

```yaml
auditpack_verification:
  audit_pack_ref: string
  schema_version: string
  content_hash: string
  hash_algorithm: "sha256"
  verification:
    computed_hash: string
    stored_hash: string
    match: bool
```

---

## 硬约束

1. 必须验证完整证据链（6 阶段）
2. 必须验证哈希校验逻辑可用

---

## 红线 (Deny List)

- [ ] 不得修改已有 Evidence 文件
- [ ] 不得伪造 Evidence 数据

---

## 质量门禁

### 人工检查

- [ ] 证据链 6 阶段完整
- [ ] 所有 EvidenceRef 可回指
- [ ] AuditPack 哈希校验逻辑可用
- [ ] 报告格式正确

---

## 回传格式

```yaml
task_id: "T-C1/C2"
executor: "Kior-A"
status: "完成 | 部分完成 | 阻塞"

deliverables:
  - path: "docs/2026-02-19/L3_C1_evidence_ref_chain_verification.md"
    action: "新建"
  - path: "docs/2026-02-19/L3_C2_auditpack_hash_verification.md"
    action: "新建"

evidence_ref: "EV-L3-C1-C2-xxx"

notes: "特殊情况说明"
```

---

## 验收标准

- [ ] 证据链验证报告创建
- [ ] 6 阶段证据链完整
- [ ] AuditPack 哈希校验报告创建
- [ ] 哈希校验逻辑可用

---

*任务生成时间: 2026-02-19*
