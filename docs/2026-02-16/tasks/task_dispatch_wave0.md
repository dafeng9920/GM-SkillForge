# Wave 0: 宪法层固化 — 任务分派总表

> **主控官**: Claude (Antigravity)
> **宪法依据**: `constitution_v1.md` §2.5「宪法先于能力」
> **V1-Prove 窗口**: 2026-02-17 ~ 2026-03-03

## 进度看板

| 波次 | 任务 | 执行者 | 状态 | Gate Decision |
|------|------|--------|------|---------------|
| Wave 0 | T-W0-A: constitution_ref 嵌入 manifest | vs--cc1 | ⏳ 待启动 | — |
| Wave 0 | T-W0-B: constitution_gate 版本对齐 | vs--cc2 | ⏳ 待启动 | — |
| Wave 0 | T-W0-C: validate.py CHECK 16-17 | Kior-C | ⏳ 待启动 | — |
| Wave 0 | T-W0-D: 宪法强制测试 | Kior-A | ⏳ 待启动 | — |
| Wave 0 | T-W0-E: v3 引用替换清单 | 主控官 | ⏳ 待启动 | — |

## 依赖关系

```
T-W0-A (vs--cc1) ──┐
                    ├──→ T-W0-D (Kior-A) [需 A+B 完成后才能写测试]
T-W0-B (vs--cc2) ──┘
T-W0-C (Kior-C)  ────→ 独立
T-W0-E (主控官)   ────→ 独立
```

## 共享模块约定

T-W0-A 负责创建 `skillforge/src/utils/constitution.py`，包含 `_load_constitution()` 函数。
T-W0-B 从该模块导入，**不重复实现**。

## 全局红线 (Section C 禁止项)

1. 禁止引入多 Agent 对抗
2. 禁止引入 n8n 深度编排
3. 禁止先写功能后补治理
4. 禁止任何 NEW-GM 代码复制

## 全局验收命令

```bash
# 全套测试（含新增测试）
python -m pytest skillforge/tests/ contract_tests/ test_skill_threshold.py -v

# 17-Point 审计
python tools/validate.py --audit-config

# 宪法加载验证
python -c "from skillforge.src.utils.constitution import load_constitution; print(load_constitution())"
```
