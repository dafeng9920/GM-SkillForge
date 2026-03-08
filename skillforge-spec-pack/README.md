# GM OS Core - 合同与政策仓库

> Schema 版本: 0.1.0

GM OS SkillForge 项目的核心合同、策略、测试仓库。

## 快速开始

```bash
# 安装依赖
pip install -e .

# 运行测试
pytest -q

# 校验所有 examples
python tools/validate.py --all

# 校验单个文件
python tools/validate.py --schema schemas/gate_decision.schema.json --json examples/gate_decision.json
```

## 目录结构

```
skillforge-spec-pack/
├── schemas/                    # JSON Schema 定义
│   ├── common.schema.json      # 通用类型
│   ├── gate_decision.schema.json   # 门禁裁决
│   ├── audit_pack.schema.json      # 审计包
│   ├── registry_publish.schema.json # 注册发布
│   ├── execution_pack.schema.json  # 执行包
│   ├── trace_event.schema.json     # 追踪事件
│   └── granularity_rules.schema.json # 颗粒度规则
│
├── orchestration/              # 编排配置
│   ├── pipeline_v0.yml         # 8 节点流水线定义
│   ├── nodes/                  # 节点 Schema (8个)
│   ├── error_policy.yml        # 错误策略
│   ├── error_policy.schema.json
│   ├── schema_lint_policy.yml  # Schema Lint 策略
│   ├── controls_catalog.yml    # 控制字段目录
│   ├── controls_catalog.schema.json
│   ├── quality_gate_levels.yml # 5 级质量门禁
│   ├── quality_gate_levels.schema.json
│   └── examples/               # 配置示例
│
├── error_codes.yml             # 错误码定义
│
├── contract_tests/             # 契约测试
│   ├── valid_examples/         # 有效示例 (应通过)
│   ├── invalid_examples/       # 无效示例 (应失败)
│   └── test_contracts.py       # pytest 测试
│
├── tools/
│   └── validate.py             # Schema 校验工具
│
├── skillforge/                 # SkillForge 骨架 (B组)
│   ├── docs/
│   └── src/
│
├── README.md
├── VERSIONING.md
└── pyproject.toml
```

## 四大硬合同

| 合同 | Schema | 用途 |
|------|--------|------|
| GateDecision | gate_decision.schema.json | 门禁裁决结果 |
| AuditPack | audit_pack.schema.json | 审计包（溯源+门禁+测试+执行） |
| RegistryPublish | registry_publish.schema.json | 发布请求与结果 |
| ExecutionPack | execution_pack.schema.json | 执行配置与约束 |

## 八节点编排流水线

| Stage | Node ID | 名称 |
|-------|---------|------|
| 0 | intake_repo | 入口与任务建档 |
| 1 | license_gate | 溯源与许可证门禁 |
| 2 | repo_scan_fit_score | 结构探测与可转化性评分 |
| 3 | draft_skill_spec | Skill 规格草案生成 |
| 4 | constitution_risk_gate | 宪法门禁与风险分级 |
| 5 | scaffold_skill_impl | 生成 Skill 实现骨架 |
| 6 | sandbox_test_and_trace | 测试样例与沙箱试跑 |
| 7 | pack_audit_and_publish | 审计包与发布 |

## 质量门禁 5 级

| Level | 名称 | 描述 |
|-------|------|------|
| 1 | Entry | 结构完整 |
| 2 | Standardized | 合同对齐 |
| 3 | Trusted | 安全合规 |
| 4 | Professional | 性能确定 (>=20 runs) |
| 5 | Industrial | 工业级 (>=1000 runs, 99.9%) |

## 关键约束

- **contracts-first**: 先合同与策略，不做业务实现
- **一切可验证**: 每个 policy/schema 都必须有 valid/invalid example
- **不引入新范围**: 不新增新系统功能

## 如何贡献

1. 修改 schema/policy 后，必须更新对应的 example
2. 运行 `pytest -q` 确保所有测试通过
3. 运行 `python tools/validate.py --all` 校验 examples

## 许可证

MIT
