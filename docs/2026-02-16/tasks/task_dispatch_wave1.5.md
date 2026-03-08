# Wave 1.5: L5 基础设施补全 — 任务分派总表

> **主控官**: Claude (Antigravity)
> **宪法依据**: `constitution_v1.md` §2.5「宪法先于能力」
> **前置依赖**: Wave 1 Mapping (已完成)

## 进度看板

| 波次 | 任务 | 执行者 | 状态 | Gate Decision |
|------|------|--------|------|---------------|
| W1.5 | T-W1.5-A: 核心 Skills 实现 | vs--cc1 | ⏳ 待启动 | — |
| W1.5 | T-W1.5-B: Engine Trace 改造 | vs--cc3 | ⏳ 待启动 | — |
| W1.5 | T-W1.5-C: 再次验收 (Re-Verification) | Kior-C | ⏳ 待启动 | — |

## 依赖关系

```
T-W1.5-A (vs--cc1) ──┐
                      ├──→ T-W1.5-C (Kior-C) [全系统联调验收]
T-W1.5-B (vs--cc3) ──┘
```

## 交付目标

变红为绿：
- G1, G2, G5 依赖 T-W1.5-A
- G3, G4 依赖 T-W1.5-B
- 最终由 T-W1.5-C 确认 "All 5 Gates Passed"
