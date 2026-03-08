# 2026-02-15 行动计划

> 生成时间: 2026-02-15 21:36
> 主控官: Claude (Antigravity)
> 项目: GM OS SkillForge

---

## 📊 现状审计

### 已完成 ✅

| 类别 | 数量 | 状态 |
|------|------|------|
| 核心 Schema | 7 个 | ✅ 全部就位 (v0.1.0) |
| 节点 Schema | 8 个 | ✅ Stage 0-7 全覆盖 |
| 策略文件 | 5 个 | ✅ pipeline + error_policy + schema_lint + controls + quality_gate |
| 错误码 | 20+ | ✅ error_codes.yml 完整 |
| 策略 Schema | 3 个 | ✅ error_policy / controls_catalog / quality_gate_levels |
| 契约测试类 | 9 个 (37 tests) | ✅ test_contracts.py |
| 架构文档 | 3 个 | ✅ ARCHITECTURE / ARTIFACTS / UI_STATES |
| 验收报告 | 1 个 | ✅ HANDOVER_REPORT.md |

### 关键缺口 ❌

| 缺口 | 严重程度 | 说明 |
|------|----------|------|
| **Examples 严重不足** | 🔴 高 | 只有 gate_decision 有 2v+2i，其余 5 个 schema 为零 |
| **orchestration/examples/ 空** | 🔴 高 | 流水线示例目录空，无法验证端到端数据流 |
| **skillforge/src/ 空** | 🟡 中 | adapters/ 和 orchestration/ 只有 .gitkeep |
| **CI/CD 未配置** | 🟡 中 | 无 GitHub Actions 或 CI 配置文件 |
| **pytest 未实际运行验证** | 🟡 中 | 今天需要先跑一次确认 24 tests 全绿 |

---

## 🎯 今日目标

> **核心交付：让 contracts-first 体系从"骨架"变为"可验证"**

### Wave 1：验证基线（优先级 P0）

| # | 任务 | 执行者 | 预估 | 产出 |
|---|------|--------|------|------|
| T1 | 安装依赖 + `pytest -q` 全绿 | 主控官 | 10min | 基线测试报告 |
| T2 | `python tools/validate.py --all` 通过 | 主控官 | 5min | 校验报告 |

### Wave 2：补充 Examples（优先级 P0）

> **原则：每个 schema ≥ 2 valid + 2 invalid examples**

| # | Schema | 当前 | 补充 | 执行者 |
|---|--------|------|------|--------|
| T3 | audit_pack.schema.json | 0v+0i | +2v+2i | vs--cc1 |
| T4 | registry_publish.schema.json | 0v+0i | +2v+2i | vs--cc2 |
| T5 | execution_pack.schema.json | 0v+0i | +2v+2i | vs--cc3 |
| T6 | trace_event.schema.json | 0v+0i | +2v+2i | Kior-A |
| T7 | granularity_rules.schema.json | 0v+0i | +2v+2i | Kior-B |

**交付标准：**
- 每个 valid example 通过 `python tools/validate.py --schema X --json Y`
- 每个 invalid example 校验失败（返回非零）
- `pytest -q` 保持全绿（测试框架会自动扫描新 examples）

### Wave 3：流水线端到端示例（优先级 P1）

| # | 任务 | 执行者 | 预估 | 产出 |
|---|------|--------|------|------|
| T8 | 创建 `orchestration/examples/tech_seo_audit/` 示例集 | Kior-C | 30min | 流水线 golden example |

**内容：**
- 每个 Stage (0-7) 的输入/输出示例 JSON
- 完整的端到端数据流演示
- issue_key 与 issue_catalog.yml 对齐

### Wave 4：CI 配置 + 验收（优先级 P1）

| # | 任务 | 执行者 | 预估 | 产出 |
|---|------|--------|------|------|
| T9 | 创建 `.github/workflows/ci.yml` | vs--cc1 | 15min | CI 配置 |
| T10 | 最终验收：全部 pytest 通过 + validate 通过 | 主控官 | 15min | 验收报告 |

---

## 📋 任务依赖图

```
Wave 1:  T1 → T2          (串行，主控官验证基线)
              │
              ▼
Wave 2:  T3,T4,T5,T6,T7   (并行，5 人分头写 examples)
              │
              ▼
Wave 3:  T8                (依赖 Wave 2 的 schema 理解)
              │
              ▼
Wave 4:  T9, T10           (CI + 最终验收)
```

---

## 🚫 今日红线

1. **不写业务实现** — 今天只补合同+examples+CI，不碰 skillforge/src/
2. **不修改 Schema** — 只新增 examples，不改现有 schema 定义
3. **不引入新依赖** — requirements.txt 不新增包
4. **每次改动后 pytest 必须全绿**

---

## 📁 预期文件变动

```
skillforge-spec-pack/
├── contract_tests/
│   ├── valid_examples/
│   │   ├── gate_decision_valid_1.json     (已有)
│   │   ├── gate_decision_valid_2.json     (已有)
│   │   ├── audit_pack_valid_1.json        ← NEW
│   │   ├── audit_pack_valid_2.json        ← NEW
│   │   ├── registry_publish_valid_1.json  ← NEW
│   │   ├── registry_publish_valid_2.json  ← NEW
│   │   ├── execution_pack_valid_1.json    ← NEW
│   │   ├── execution_pack_valid_2.json    ← NEW
│   │   ├── trace_event_valid_1.json       ← NEW
│   │   ├── trace_event_valid_2.json       ← NEW
│   │   ├── granularity_rules_valid_1.json ← NEW
│   │   └── granularity_rules_valid_2.json ← NEW
│   └── invalid_examples/
│       ├── gate_decision_invalid_1.json   (已有)
│       ├── gate_decision_invalid_2.json   (已有)
│       ├── audit_pack_invalid_1.json      ← NEW
│       ├── audit_pack_invalid_2.json      ← NEW
│       ├── registry_publish_invalid_1.json ← NEW
│       ├── registry_publish_invalid_2.json ← NEW
│       ├── execution_pack_invalid_1.json  ← NEW
│       ├── execution_pack_invalid_2.json  ← NEW
│       ├── trace_event_invalid_1.json     ← NEW
│       ├── trace_event_invalid_2.json     ← NEW
│       ├── granularity_rules_invalid_1.json ← NEW
│       └── granularity_rules_invalid_2.json ← NEW
│
├── orchestration/
│   └── examples/
│       └── tech_seo_audit/                ← NEW (Wave 3)
│           ├── stage0_intake_input.json
│           ├── stage0_intake_output.json
│           └── ...
│
└── .github/
    └── workflows/
        └── ci.yml                         ← NEW (Wave 4)
```

---

## ✅ 验收标准

| 检查项 | 命令 | 预期 |
|--------|------|------|
| 全部 pytest 通过 | `pytest -q` | 24+ tests passed |
| 全部 examples 校验 | `python tools/validate.py --all` | 全部 PASS |
| Valid 数量 ≥ 12 | 计数 valid_examples/ | ≥ 12 个 JSON |
| Invalid 数量 ≥ 12 | 计数 invalid_examples/ | ≥ 12 个 JSON |
| CI 可运行 | `make ci` | exit 0 |

---

*计划由主控官 Claude (Antigravity) 基于项目审计生成*
