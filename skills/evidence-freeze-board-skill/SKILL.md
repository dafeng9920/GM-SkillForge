---
name: evidence-freeze-board-skill
description: 生成封板快照、MANIFEST、BOARD_FREEZE 与归档压缩包，形成不可变审计资产。
---

# evidence-freeze-board-skill

## 触发条件

- `final_gate_decision=ALLOW`
- 需要做封板归档与哈希固化
- 需要形成可交付审计包

## 输入

```yaml
input:
  source_verification_dir: "docs/{date}/p0-governed-execution/verification"
  snapshot_dir: "docs/{date}/p0-governed-execution/evidence_pass_snapshot"
  include_patterns:
    - "T*_execution_report.yaml"
    - "T*_gate_decision.json"
    - "T*_compliance_attestation.json"
    - "final_gate_decision.json"
```

## 输出

```yaml
output:
  snapshot_dir: "evidence_pass_snapshot/"
  manifest: "evidence_pass_snapshot/MANIFEST.json"
  board_freeze: "evidence_pass_snapshot/BOARD_FREEZE.json"
  archive: "evidence_pass_snapshot.zip"
```

## DoD

- [ ] 快照文件齐全
- [ ] MANIFEST 包含 sha256/size/time
- [ ] BOARD_FREEZE 包含 board_id/decision/frozen_at
- [ ] zip 可用于外部归档

