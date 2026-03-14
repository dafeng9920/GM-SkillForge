---
name: evidence-freeze-manifest-skill
description: 冻结L3证据快照并生成MANIFEST校验清单。用于封板归档、审计复核和跨环境证据一致性证明。
---

# evidence-freeze-manifest-skill

## 触发条件

- killer tests 全绿后准备封板
- 需要对外提交证据包
- 需要防止“同名旧文件”混淆

## 输入

```yaml
input:
  source_dir: "reports/l3_gap_closure/{date}"
  snapshot_dir: "docs/{date}/verification/evidence_pass_snapshot"
  required_files:
    - A_constitution_hard_gate.json
    - B_registry_graph_integrity.json
    - C_incremental_delta_enforced.json
    - summary.json
    - summary.md
  manifest_file: "MANIFEST.json"
```

## 输出

```yaml
output:
  snapshot_files:
    - A_constitution_hard_gate.json
    - B_registry_graph_integrity.json
    - C_incremental_delta_enforced.json
    - summary.json
    - summary.md
  manifest:
    file: "MANIFEST.json"
    fields:
      - file
      - sha256
      - last_write_time_utc
      - size_bytes
      - missing
```

## DoD

- [ ] 五个必需文件均复制成功
- [ ] `MANIFEST.json` 生成成功
- [ ] 每个文件有 `sha256` 和时间戳
- [ ] 缺失文件时返回非0/FAIL信号

