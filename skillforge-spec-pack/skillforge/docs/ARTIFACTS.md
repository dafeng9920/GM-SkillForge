# SkillForge 产物清单

> 版本: 0.1.0

## 产物 Key 定义

| Key | 阶段 | 描述 | Schema |
|-----|------|------|--------|
| `build_record` | Stage 0 | 任务建档记录 | 自定义 |
| `provenance` | Stage 1 | 溯源信息 | common.schema.json#/definitions/Provenance |
| `scan_report` | Stage 2 | 仓库扫描报告 | 自定义 |
| `fit_score` | Stage 2 | 可转化性评分 (0-100) | integer |
| `skill_spec` | Stage 3 | Skill 规格文档 | 自定义 |
| `schemas` | Stage 3 | 输入输出 Schema | JSON Schema |
| `caps` | Stage 3 | 能力权限列表 | capabilities.json |
| `gate_decision` | Stage 4 | 门禁裁决 | gate_decision.schema.json |
| `scaffold_bundle_ref` | Stage 5 | 骨架包引用 | path string |
| `test_report` | Stage 6 | 测试报告 | 自定义 |
| `trace` | Stage 6 | 执行追踪 | trace_event.schema.json |
| `audit_pack` | Stage 7 | 审计包 | audit_pack.schema.json |
| `publish_result` | Stage 7 | 发布结果 | registry_publish.schema.json |

## 产物流转图

```
intake_repo
    └── build_record ──────────────────────────────────────┐
                                                           │
license_gate                                               │
    └── provenance ────────────────────────────────────────┤
                                                           │
repo_scan_fit_score                                        │
    ├── scan_report ───────────────────────────────────────┤
    └── fit_score ─────────────────────────────────────────┤
                                                           │
draft_skill_spec                                           │
    ├── skill_spec ────────────────────────────────────────┤
    ├── schemas ───────────────────────────────────────────┤
    └── caps ──────────────────────────────────────────────┤
                                                           │
constitution_risk_gate                                     │
    └── gate_decision ─────────────────────────────────────┤
                                                           │
scaffold_skill_impl                                        │
    └── scaffold_bundle_ref ───────────────────────────────┤
                                                           │
sandbox_test_and_trace                                     │
    ├── test_report ───────────────────────────────────────┤
    └── trace ─────────────────────────────────────────────┤
                                                           │
pack_audit_and_publish                                     │
    ├── audit_pack ◄───────────────────────────────────────┘
    │   (汇总: provenance + gate_decision + test_report + trace)
    └── publish_result
```

## 产物存储规范

### 文件命名

```
jobs/{job_id}/
├── build_record.json
├── provenance.json
├── scan_report.json
├── fit_score.json
├── skill_spec/
│   ├── SKILL.md
│   ├── input.json
│   └── output.json
├── capabilities.json
├── gate_decision.json
├── scaffold_bundle/
│   ├── skill.py
│   ├── manifest.json
│   └── executor/
├── tests/
│   └── test_skill.py
├── run_trace.jsonl
├── sandbox_report.json
├── audit_pack.zip
└── publish_result.json
```

## 产物校验

每个产物必须通过对应的 schema 校验：

```python
from tools.validate import validate_file

is_valid, errors = validate_file(
    "jobs/{job_id}/gate_decision.json",
    "schemas/gate_decision.schema.json"
)
```

## 版本兼容

产物中的 `schema_version` 必须与 gm-os-core 版本匹配。
