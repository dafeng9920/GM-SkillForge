# T-W0-E: v3 引用替换清单 — 主控官直接产出

> 执行者: 主控官 (Claude/Antigravity)
> 状态: ✅ 完成

## 扫描结果

扫描范围: `D:\GM-SkillForge\docs\` + `D:\GM-SkillForge\skillforge-spec-pack\`

### 引用 `skill_acceptance_L5_hard_gate` 的文件

| 文件 | 引用版本 | 需要动作 |
|---|---|---|
| `docs/2026-02-16/specs/skill_acceptance_L5_hard_gate.md` | v1 (无版本后缀) | ⚠️ 需在文件头标注"已被 v3 替代" |
| `docs/2026-02-16/完整版模块清单+全量接口契约目录/skill_acceptance_L5_hard_gate_v3.md` | v3 ✅ | 当前有效版本，无需变更 |
| `docs/2026-02-16/TODO.MD` L4 | v3 ✅ | 已正确引用 v3 |
| `docs/2026-02-16/TODO.MD` L15 | v3 ✅ | 已正确引用 v3 |

### 代码层

`skillforge-spec-pack/` 中 **无任何代码引用** `skill_acceptance_L5_hard_gate` — 无需代码修改。

## 需执行的唯一操作

在 `docs/2026-02-16/specs/skill_acceptance_L5_hard_gate.md` 文件头插入废弃声明:

```markdown
> ⚠️ **DEPRECATED**: 本文档已被 `skill_acceptance_L5_hard_gate_v3.md` 替代。
> 参考: `docs/2026-02-16/完整版模块清单 + 全量接口契约目录/skill_acceptance_L5_hard_gate_v3.md`
> 依据: `constitution_v1.md` §8.3 — 未引用宪法依据的规则变更视为无效
```

## 结论

影响面极小 — 只有 1 个旧文件需要标注废弃，0 处代码需要修改。v3 已经是事实上的唯一有效版本。
