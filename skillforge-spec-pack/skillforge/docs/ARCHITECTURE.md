# SkillForge 架构说明

> 版本: 0.1.0

## 概述

SkillForge 是 GM OS 生态中的 Skill 生产线产品，负责：
- 从 GitHub Repo 生成可发布的 GM OS Skill
- 执行八节点编排流水线 (Stage 0-7)
- 产出审计包、追踪记录、质量认证

## 调用关系

```
┌─────────────────────────────────────────────────────────┐
│                     SkillForge                          │
│  (产品层 - apps/skillforge)                             │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ GitHub  │  │ Parser  │  │Builder  │  │  CLI    │    │
│  │Fetcher  │  │         │  │         │  │         │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘    │
│       │            │            │            │          │
│       └────────────┴────────────┴────────────┘          │
│                         │                                │
│                         ▼                                │
│              ┌────────────────────┐                     │
│              │   Orchestrator     │                     │
│              │  (8-node pipeline) │                     │
│              └────────┬───────────┘                     │
└───────────────────────┼─────────────────────────────────┘
                        │
                        │ 调用 contracts
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    gm-os-core                            │
│  (内核层 - contracts + policies)                         │
├─────────────────────────────────────────────────────────┤
│  schemas/     orchestration/    error_codes.yml         │
│  (四大合同)   (8节点+策略)      (错误码)                  │
└─────────────────────────────────────────────────────────┘
```

## 八节点流水线

| Stage | Node | 产物 |
|-------|------|------|
| 0 | intake_repo | build_record.json |
| 1 | license_gate | provenance.json |
| 2 | repo_scan_fit_score | scan_report.json, fit_score |
| 3 | draft_skill_spec | SKILL.md, schemas, capabilities |
| 4 | constitution_risk_gate | gate_decision.json, risk_tier |
| 5 | scaffold_skill_impl | scaffold_bundle/ |
| 6 | sandbox_test_and_trace | tests/, run_trace.jsonl, sandbox_report.json |
| 7 | pack_audit_and_publish | audit_pack.zip, publish_result.json |

## 关键约束

1. **单向依赖**: SkillForge → gm-os-core，禁止反向 import
2. **合同优先**: 所有接口必须符合 gm-os-core 的 schema
3. **错误码统一**: 所有错误必须使用 error_codes.yml 定义的码

## 扩展点

- `adapters/`: 外部系统集成（GitHub、Sandbox、Registry）
- `orchestration/`: 编排器实现

## 参考

- [ARTIFACTS.md](./ARTIFACTS.md) - 产物清单
- [UI_STATES.md](./UI_STATES.md) - UI 状态机
- ../../README.md - 核心仓库说明
