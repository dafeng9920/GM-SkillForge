---
name: l4-evidence-freeze-skill
description: 冻结 L4 封板证据，生成 evidence_pass_snapshot、MANIFEST、BOARD_FREEZE 与 zip。
---

# l4-evidence-freeze-skill

## 触发条件

- `final_gate_decision = ALLOW`
- 需要封板快照、哈希清单和归档包

## 输入

```yaml
input:
  source_verification_dir: "docs/{date}/l4-n8n-execution/verification"
  snapshot_dir: "docs/{date}/l4-n8n-execution/evidence_pass_snapshot"
  include_files:
    - "L4-0*_execution_report.yaml"
    - "L4-0*_gate_decision.json"
    - "L4-0*_compliance_attestation.json"
    - "final_gate_decision.json"
```

## 输出

```yaml
output:
  - "evidence_pass_snapshot/MANIFEST.json"
  - "evidence_pass_snapshot/BOARD_FREEZE.json"
  - "evidence_pass_snapshot.zip"
```

## DoD

- [ ] 快照文件完整复制
- [ ] MANIFEST 含 sha256/size/time
- [ ] BOARD_FREEZE 含 board_id/decision/frozen_at
- [ ] zip 可用于外部审计归档

