# Codex/claude 接手提示词

> 复制以下内容发给 Codex/claude，让它快速理解项目并开始工作

---

## 项目概述

你是 **GM OS SkillForge** 项目的开发 AI。这个项目是一个 **contracts-first 的 Skill 生产线**，目标是将 GitHub 仓库转化为可发布、可验收、可审计的 GM OS Skill。

### 核心原则

1. **contracts-first**: 先合同与策略（schemas/policies/tests），不做业务实现
2. **一切可验证**: 每个 policy/schema 都必须有 valid/invalid example
3. **不引入新范围**: 不新增新系统功能，只整理并落盘已确定的规范

---

## 项目结构

```
GM-SkillForge/
├── skillforge-spec-pack/        # 核心合同仓库（你的工作重点）
│   ├── schemas/                 # JSON Schema 定义（7个）
│   │   ├── common.schema.json   # 通用类型
│   │   ├── gate_decision.schema.json   # 门禁裁决
│   │   ├── audit_pack.schema.json      # 审计包
│   │   ├── registry_publish.schema.json # 注册发布
│   │   ├── execution_pack.schema.json  # 执行包
│   │   ├── trace_event.schema.json     # 追踪事件
│   │   └── granularity_rules.schema.json
│   │
│   ├── orchestration/           # 编排配置
│   │   ├── pipeline_v0.yml      # 8节点流水线定义
│   │   ├── nodes/               # 8个节点 Schema
│   │   ├── error_policy.yml     # 错误策略
│   │   ├── schema_lint_policy.yml
│   │   ├── controls_catalog.yml # 控制字段目录
│   │   ├── quality_gate_levels.yml  # 5级质量门禁
│   │   └── examples/            # 配置示例
│   │
│   ├── error_codes.yml          # 错误码定义（20+）
│   ├── contract_tests/          # 契约测试
│   │   ├── valid_examples/
│   │   ├── invalid_examples/
│   │   └── test_contracts.py
│   │
│   ├── tools/validate.py        # Schema 校验工具
│   ├── README.md
│   ├── HANDOVER_REPORT.md       # 验收报告
│   └── pyproject.toml
│
├── skillforge-spec-pack/skillforge/  # 产品骨架（预留）
│   ├── docs/
│   └── src/
│
├── docs/                        # 文档
├── README.md                    # 主文档
└── Makefile                     # CI 命令
```

---

## 四大硬合同

| 合同 | Schema 文件 | 用途 |
|------|-------------|------|
| GateDecision | gate_decision.schema.json | 门禁裁决结果（ALLOW/DENY/REQUIRES_CHANGES）|
| AuditPack | audit_pack.schema.json | 审计包（溯源+门禁+测试+执行记录）|
| RegistryPublish | registry_publish.schema.json | 发布请求与结果 |
| ExecutionPack | execution_pack.schema.json | 执行配置与约束 |

---

## 八节点编排流水线

| Stage | Node ID | 名称 | 产出 |
|-------|---------|------|------|
| 0 | intake_repo | 入口与任务建档 | build_record.json |
| 1 | license_gate | 许可证门禁 | provenance.json |
| 2 | repo_scan_fit_score | 扫描与评分 | scan_report.json, fit_score |
| 3 | draft_skill_spec | Skill 规格生成 | SKILL.md, schemas, capabilities |
| 4 | constitution_risk_gate | 宪法门禁 | gate_decision.json, risk_tier |
| 5 | scaffold_skill_impl | 实现骨架 | scaffold_bundle/ |
| 6 | sandbox_test_and_trace | 沙箱测试 | tests/, run_trace.jsonl, sandbox_report.json |
| 7 | pack_audit_and_publish | 审计发布 | audit_pack.zip, publish_result.json |

---

## 质量门禁 5 级

| Level | 名称 | 要求 |
|-------|------|------|
| 1 | Entry | 结构完整，manifest 可解析 |
| 2 | Standardized | 双层 Schema，controls 合规 |
| 3 | Trusted | 静态审计通过，宪法门禁 ALLOW |
| 4 | Professional | 压力测试 >= 20 次，成功率 >= 95% |
| 5 | Industrial | 边缘测试 >= 1000 次，成功率 >= 99.9% |

---

## 如何运行

```bash
# 进入核心目录
cd skillforge-spec-pack

# 安装依赖
pip install -e .

# 运行所有测试（必须全绿）
pytest -q

# 校验所有 examples
python tools/validate.py --all

# CI 一键检查（根目录）
make ci
```

---

## 你的任务优先级

### Phase 1: 理解与验证（先做）
1. 阅读 `skillforge-spec-pack/README.md` 和 `HANDOVER_REPORT.md`
2. 运行 `pytest -q` 确保 24 个测试全部通过
3. 检查所有 schema 文件的结构

### Phase 2: 补充 Examples（次做）
每个 schema 至少需要 2 个 valid + 2 个 invalid examples：
- 当前只有 gate_decision 有 examples
- 需要补充：audit_pack, registry_publish, execution_pack, trace_event

### Phase 3: 实现预留目录（后做）
- `skillforge/src/adapters/github_fetch/` - GitHub 拉取
- `skillforge/src/adapters/sandbox_runner/` - 沙箱执行
- `skillforge/src/orchestration/` - 编排器实现

---

## 关键约束

1. **单向依赖**: skillforge 只能依赖 gm-os-core，禁止反向 import
2. **错误码统一**: 所有错误必须使用 `error_codes.yml` 定义的码
3. **版本格式**: 所有 schema_version 必须是 `0.1.x` 格式
4. **测试必须全绿**: 任何修改后，`pytest -q` 必须全部通过

---

## 常用命令速查

| 命令 | 用途 |
|------|------|
| `pytest -q` | 运行所有契约测试 |
| `python tools/validate.py --all` | 校验所有 examples |
| `python tools/validate.py --schema X --json Y` | 校验单个文件 |
| `make ci` | CI 完整检查 |
| `make clean` | 清理缓存 |

---

## 文件引用关系

```
error_codes.yml ←─ error_policy.yml ←─ quality_gate_levels.yml
      ↑                    ↑                    ↑
      └────────────────────┴────────────────────┘
                     所有 error_code 必须存在于 error_codes.yml

pipeline_v0.yml ─→ nodes/*.schema.json ─→ error_policy.yml
      ↑                                        ↑
      └──────── node_id 必须一致 ──────────────┘
```

---

## 开始工作

确认你已理解以上内容后，请回复：

> "我已理解 GM OS SkillForge 项目结构。当前状态：24 测试通过。准备开始 Phase 1/2/3。"

然后告诉我你想从哪个 Phase 开始。
