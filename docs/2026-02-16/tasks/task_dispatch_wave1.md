# Wave 1: L5 Hard Gate 干跑 (Dry Run) — 任务分派总表

> **主控官**: Claude (Antigravity)
> **宪法依据**: `constitution_v1.md` §2.5「宪法先于能力」
> **Spec**: `skill_acceptance_L5_hard_gate_v3.md`

## 进度看板

| 波次 | 任务 | 执行者 | 状态 | Gate Decision |
|------|------|--------|------|---------------|
| Wave 1 | T-W1-A: 干跑分析 (Dry Run) | vs--cc1 | ⏳ 待启动 | — |
| Wave 1 | T-W1-B: 映射表 (Mapping) | vs--cc2 | ⏳ 待启动 | — |
| Wave 1 | T-W1-C: 证据生成 (Evidence) | Kior-C | ⏳ 待启动 | — |

## 依赖关系

```
T-W1-A (vs--cc1) ──┐
                    ├──→ T-W1-C (Kior-C) [需 A 的数据 + B 的映射]
T-W1-B (vs--cc2) ──┘
```

## 交付目标

Wave 1 **不涉及写新代码**（除了简单的脚本辅助干跑），核心是**验证 Spec 的可行性**并产出**第一批实证数据**。

- T-W1-A: 告诉我目前的系统能过几关？
- T-W1-B: 告诉我每关具体怎么查？
- T-W1-C: 给出一份标准的 JSON 结果长什么样？
