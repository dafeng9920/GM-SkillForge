# T77: L3 AuditPack 一键生成验证

---
task_id: "T77"
executor: "Kior-A"
reviewer: "vs--cc1"
compliance_officer: "Kior-C"
wave: "Wave AuditPack"
depends_on: ["T71"]
estimated_minutes: 40
---

## 1. 任务目标

实现 L3 AuditPack 一键生成验证系统，自动聚合所有任务的三权记录并生成完整审计包。

## 2. A/B Guard 结构

### A Guard（提案约束）
- AuditPack 必须包含所有已完成任务的交付物
- 必须验证三权记录完整性
- 必须生成可追溯的审计报告

### B Guard（执行约束）
- 无完整三权记录的任务不得入包
- AuditPack 必须通过 SHA256 校验
- 任何校验失败必须阻断并报告

## 3. L3 AuditPack 定义

L3 AuditPack 是三级审计包，包含：

```yaml
l3_auditpack:
  level: 3
  scope: "task_batch"
  components:
    - execution_reports: "所有 execution_report.yaml"
    - gate_decisions: "所有 gate_decision.json"
    - compliance_attestations: "所有 compliance_attestation.json"
    - evidence_chain: "evidence_chain_report.json"
    - summary: "聚合统计报告"
```

## 4. 输入规格

```yaml
input:
  description: "生成 L3 AuditPack 并验证完整性"
  context_files:
    - path: "docs/2026-02-22/verification/"
      purpose: "扫描所有验证文件"
    - path: "docs/2026-02-22/tasks/"
      purpose: "扫描所有任务书"
  constants:
    auditpack_version: "1.0.0"
    verification_dir: "docs/2026-02-22/verification"
```

## 5. 输出交付物

```yaml
output:
  deliverables:
    - path: "docs/2026-02-22/verification/l3_auditpack_report.json"
      type: "新建"
      purpose: "L3 AuditPack 完整报告"
    - path: "docs/2026-02-22/verification/T77_execution_report.yaml"
      type: "新建"
      purpose: "执行报告"
    - path: "docs/2026-02-22/verification/T77_gate_decision.json"
      type: "新建"
      purpose: "Gate 决策"
    - path: "docs/2026-02-22/verification/T77_compliance_attestation.json"
      type: "新建"
      purpose: "合规证明"
  constraints:
    - "必须扫描所有 T*-prefixed 验证文件"
    - "三权记录必须齐全才能标记 PASS"
    - "输出 JSON 必须包含 SHA256 校验和"
```

## 6. 禁止操作

```yaml
deny:
  - "不得遗漏任何已完成的任务"
  - "不得伪造三权记录"
  - "不得绕过校验失败"
```

## 7. Gate 检查

```yaml
gate:
  auto_checks:
    - command: "验证 l3_auditpack_report.json 存在"
      expect: "file_exists"
    - command: "验证所有任务三权记录齐全"
      expect: "all_present"
  manual_checks:
    - "三权记录完整性审查"
    - "审计包结构正确性检查"
```

## 8. AuditPack 数据结构

```json
{
  "auditpack_id": "L3-AUDIT-2026-02-22-001",
  "version": "1.0.0",
  "level": 3,
  "generated_at": "2026-02-22T...Z",
  "generated_by": "T77_Kior-A",

  "summary": {
    "total_tasks": 10,
    "tasks_with_full_three_powers": 9,
    "tasks_missing_records": 1,
    "overall_status": "PASS|PARTIAL|FAIL"
  },

  "tasks": [
    {
      "task_id": "T71",
      "execution_report": { "status": "present", "sha256": "..." },
      "gate_decision": { "status": "present", "decision": "ALLOW" },
      "compliance_attestation": { "status": "present", "decision": "PASS" },
      "three_powers_complete": true
    }
  ],

  "evidence_chain": {
    "chain_id": "evidence-chain-...",
    "total_entries": 5,
    "integrity": "VALID"
  },

  "integrity_check": {
    "all_sha256_verified": true,
    "chain_valid": true,
    "timestamp": "..."
  },

  "auditpack_sha256": "sha256:..."
}
```

## 9. 三权完整性规则

一个任务的三权记录完整当且仅当：

1. **Execution Report** 存在且 status = "完成"
2. **Gate Decision** 存在且 decision = "ALLOW"
3. **Compliance Attestation** 存在且 decision = "PASS"

缺失任一项，则 `three_powers_complete = false`
