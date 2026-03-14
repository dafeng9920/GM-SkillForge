# TODO（2026-02-25）

目标：落地 `可进化能力系统（Evolvable Skill Architecture）`，从“能生成 Skill”升级到“可持续进化/派生/重构”。
状态枚举：`已完成` | `进行中` | `待完成` | `阻塞`

## 明日主线（2026-02-26）

| 编号 | 任务 | 状态 | 完成标准（DoD） | 产物 |
|---|---|---|---|---|
| E1 | Skill DNA Schema v1 | 待完成 | 定义 `name/purpose/inputs/outputs/constraints/dependencies/evaluation_metrics/version` 必填；有 JSON Schema 校验 | `schemas/skill_dna.schema.json` |
| E2 | Capability Graph 基础层 | 待完成 | 支持节点/边注册、依赖查询、可替代关系表达；提供最小读写接口 | `skillforge/src/capability_graph/*` + `reports/capability_graph/baseline.json` |
| E3 | Evolution Trigger 引擎 | 待完成 | 支持三类触发：`需求变化/性能不足/风控违规`；触发规则可配置 | `skillforge/src/evolution/trigger_engine.py` + `configs/evolution_triggers.yaml` |
| E4 | 进化执行器（升级/分裂/合并） | 待完成 | 输入 trigger 后可产出 `Skill v2` 或 `子Skill` 或 `合并重构`；带兼容说明 | `skillforge/src/evolution/evolution_planner.py` |
| E5 | 版本与兼容策略 | 待完成 | 语义版本升级规则明确；接口变更必须含 deprecation/compatibility 字段 | `docs/architecture/skill_versioning_policy.md` |
| E6 | 回归门禁接入 | 待完成 | 新版/新派生 Skill 必须过接口兼容与回归测试，否则阻断发布 | `scripts/run_evolution_regression.py` + `reports/evolution_regression/*.json` |
| E7 | 功能派生闭环验证 | 待完成 | 输入“新增场景”时，能先判断组合可达；不可达则新建模块并注册图谱 | `reports/evolution_regression/derivation_demo.json` |

## 约束（Fail-Closed）

1. 缺 `Skill DNA` 结构体：不得进入进化流程。
2. 无图谱注册记录：不得宣称“派生完成”。
3. 无兼容声明或回归未通过：不得发布。

## 明日执行顺序

1. 先做 `E1 -> E2 -> E3`（定义与触发基础）。
2. 再做 `E4 -> E5`（进化与版本治理）。
3. 最后做 `E6 -> E7`（验证闭环与演示证据）。

