# Wave 2: 10阶认知输出 — 任务分派总表

> **主控官**: Claude (Antigravity)
> **Spec**: `docs/2026-02-17/GM-SkillForge · cognition_10d 四件套.md`

## 进度看板

| 任务 | 执行者 | 目标 | 状态 | Gate |
|---|---|---|---|---|
| **T-W2-A** | vs--cc1 | **Contract Freeze** (Yaml) | ⏳ 待分发 | — |
| **T-W2-B** | vs--cc2 | **Audit Samples** (JSON) | ⏳ 待分发 | — |
| **T-W2-C** | vs--cc3 | **Skill Impl** (Code) | ⏳ 等待 A+B | — |
| **T-W2-D** | Kior-C | **Verification** (Report) | ⏳ 等待 C | — |

## 任务包列表

请将以下 Task Spec 文件分发给对应的 Agent：

1. **vs--cc1**: [T-W2-A_vs-cc1.md](file:///D:/GM-SkillForge/docs/2026-02-16/tasks/T-W2-A_vs-cc1.md)
2. **vs--cc2**: [T-W2-B_vs-cc2.md](file:///D:/GM-SkillForge/docs/2026-02-16/tasks/T-W2-B_vs-cc2.md)
3. **vs--cc3**: [T-W2-C_vs-cc3.md](file:///D:/GM-SkillForge/docs/2026-02-16/tasks/T-W2-C_vs-cc3.md)
4. **Kior-C**: [T-W2-D_Kior-C.md](file:///D:/GM-SkillForge/docs/2026-02-16/tasks/T-W2-D_Kior-C.md)

## 执行策略

- **Phase 1**: 同时启动 **T-W2-A** 和 **T-W2-B**。
- **Phase 2**: 等 A 和 B 完成后，启动 **T-W2-C**（基于确定的契约和样例写代码）。
- **Phase 3**: 代码完成后，启动 **T-W2-D**（验收）。
