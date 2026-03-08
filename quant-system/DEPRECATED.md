# ⚠️ 此目录已废弃

**迁移日期**: 2026-02-23
**原因**: 架构重构，回归核心

## 迁移映射

| 原位置 | 新位置 |
|--------|--------|
| `skills/base.py` | `skillforge/src/skills/quant/` (已合并到 Core) |
| `skills/data/` | `adapters/quant/data/` |
| `skills/research/` | `adapters/quant/strategies/` |
| `docker/` | 🗑️ 已删除 (废弃独立部署) |
| `scripts/` | 🗑️ 已删除 |

## 新架构

参见: [QUANT_ARCHITECTURE_DECISION.md](../docs/2026-02-22/量化/QUANT_ARCHITECTURE_DECISION.md)

```
Quant = Adapter (翻译层)
SkillForge = Core (执行层)
```

## 保留文件

以下文件暂时保留供参考：
- `CONSTITUTION_ALIGNMENT.md` - 待合并到主宪法
- `contracts/INTERFACE_CONTRACTS.md` - 待简化
- `tests/` - 待迁移
