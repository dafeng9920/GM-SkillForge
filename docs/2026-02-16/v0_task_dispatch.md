# 2026-02-16 V0 收尾 — AI 军团任务派遣表

## 元信息

| 字段 | 值 |
|------|-----|
| 锚定文档 | `orchestration/protocol_v0_scope.yml` |
| 协议母本 | `docs/2026-02-16/GM-SkillForge Audit Engine Protocol/GM-SkillForge Audit Engine Protocol (v1.0).md` |
| 验证基线 | `validate.py --audit-config` 10/10 ✅ · `test_acceptance.py` 12/12 ✅ |
| 工作目录 | `D:\GM-SkillForge\skillforge-spec-pack` |

## 并行派遣矩阵

| 任务 ID | 名称 | 执行者 | 依赖 | 预计时长 | Mega Prompt |
|---------|------|--------|------|---------|-------------|
| T-V0-A | 确定性 Intake | Legion-A | 无 | ~2h | `T-V0-A_deterministic_intake.md` |
| T-V0-B | Skill 识别阈值外部化 | Legion-B | 无 | ~3h | `T-V0-B_skill_threshold.md` |
| T-V0-C | 静态规则版本化 | Legion-C | 无 | ~2h | `T-V0-C_static_rule_versioning.md` |
| T-V0-D | Evidence 容器闭环 | Legion-D | 无 | ~4h | `T-V0-D_evidence_container.md` |

```
T-V0-A ──┐
T-V0-B ──┼── 全部独立，可 4 路并行执行
T-V0-C ──┤
T-V0-D ──┘
         │
         ▼
   整合验收 (主控官)
   python -m pytest skillforge/tests/test_acceptance.py -v
   python tools/validate.py --audit-config
```

## 合格标准（每个军团交付前必须通过）

1. 修改的文件必须通过 `python -m pytest skillforge/tests/test_acceptance.py -v`（12/12）
2. 不得引入 `validate.py --audit-config` 回归
3. 所有新增功能必须有对应 pytest 测试
4. 代码注释必须引用 `protocol_v0_scope.yml` 对应条目
