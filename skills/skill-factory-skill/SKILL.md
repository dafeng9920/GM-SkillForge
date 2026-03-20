---
name: skill-factory-skill
description: OpenClaw 技能铸造炉。根据 Commander 的意图或智能体的自演化需求，自动化生成、测试并注入新的 SKILL.md 技能模块。
---

# skill-factory-skill

## 触发条件

- `CapabilityEvolver` 识别出新的重复逻辑模式，建议提取为 Skill 时。
- Commander 发出“开发新功能/新 Skill”指令时。
- 需要修复或重构现有低质量（Bloated）的外部 Skill 时。

## 铸造流程 (The Forge)

1. **Intent Extraction**: 接收原始意图（如：“我需要一个能自动监控 GitHub 报错并提炼解决方案的技能”）。
2. **Drafting**: 基于 `.pen` 规范或 `SKILL.md` 模板生成初稿。
3. **Logic Hardening**: 注入输入输出 Schema、DoD 以及必要的安全拦截逻辑。
4. **Validation**: 生成 3-5 个测试用例，在本地模拟运行。
5. **Auditing**: 强制通过 `Aegis Audit` 进行敏感信息和冗余信息检测。

## 输出 (Output)

- `new-skill/SKILL.md`: 标准化技能定义文件。
- `test_report.json`: 该技能的模拟运行报告。

## DoD

- [ ] 生成的技能文件遵循“10:1 脱水原则”，无冗余描述
- [ ] 必须包含明确的触发条件和 DoD 清单
- [ ] 必须通过 `aegis-audit-skill` 的 STRICT 级别扫描
