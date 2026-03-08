# 治理承诺内核硬化 - 任务分派表

> 目标：在不牺牲交付节奏的前提下，完成三件 P0 事项：Permit 真验签闭环（M1）、生产语义去污染（M2/M0）、Registry 从线性文件读升级为可回滚的事务化读写（M3）。

## 执行波次 (Waves)

| 波次 | 任务编号 | 任务描述 | 执行者 | 状态 | Gate Decision |
|------|----------|----------|--------|------|---------------|
| Wave 1 | [T1](tasks/T1_vs--cc1.md) | M0 基线与护栏 + M2 去污染 | vs--cc1 | ✅ ALLOW | M0/M2 Baseline Active |
| Wave 1 | [T2](tasks/T2_vs--cc3.md) | M1 Permit 真验签强制闭环 | vs--cc3 | ✅ ALLOW | M1 Permit Hardened
| Wave 2 | [T3](tasks/T3_vs--cc1.md) | M3 Registry SQLite 双轨迁移 | vs--cc1 | ✅ ALLOW | M3 Dual-Write Active |
