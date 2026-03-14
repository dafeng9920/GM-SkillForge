# Skill 分级治理（v1）

## 目的

解决“Skill 数量增长后混用导致主链路失控”的问题。  
本治理将所有 Skill 分为三层，并明确哪些可以进入主执行链路。

## 分级定义

1. `core`
- 定义：直接参与主调度、主门禁、最终裁决的技能。
- 规则：可 `enabled_for_mainline=true`。

2. `support`
- 定义：辅助性技能（分析、补单、生成文案、校验工具）。
- 规则：默认不接主链路，仅按需调用。

3. `experimental`
- 定义：模板、试验、草稿、尚未完成认证的技能。
- 规则：禁止接入主链路。

## 主链路规则

1. 仅 `tier=core` 且 `enabled_for_mainline=true` 的 Skill 可进入硬执行路径。
2. `support/experimental` 可调用，但不能成为“放行/阻断”的唯一依据。
3. 任意 Skill 若缺失最小元数据（`SKILL.md + openai.yaml`）不得晋升到 core。

## 晋升门（Promotion Gate）

从 `experimental/support -> core` 必须同时满足：

1. 认证审计通过（`PASS`）
2. 回归校验通过（无 `PARSE_ERR`、无缺失三件套）
3. 更新 `configs/dispatch_skill_registry.json`
4. 明确 `owner`、`entrypoint_scope` 与回滚策略

## 机读注册表

使用脚本生成：

```powershell
python scripts/generate_skill_tier_registry.py
```

输出文件：
- `configs/skill_tier_registry.json`

## 当前落地约束

1. 先把“已接主链路”技能收敛为小集合（core）。
2. 其余技能继续保留，但默认降级为 support/experimental。
3. 每次新增 Skill 必须先定 tier，再决定是否接主链路。

