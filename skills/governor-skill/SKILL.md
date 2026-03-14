---
name: governor-skill
description: 废弃入口。请勿继续使用；authoritative governor skill 已迁移到 lobster-cloud-execution-governor-skill。
---

# governor-skill

## 状态

`DEPRECATED / DO NOT USE`

本目录不是当前主仓的 authoritative governor skill。

## authoritative 路径

请统一使用：

- [lobster-cloud-execution-governor-skill](/d:/GM-SkillForge/skills/lobster-cloud-execution-governor-skill/SKILL.md)
- [resume_handoff_template.md](/d:/GM-SkillForge/skills/lobster-cloud-execution-governor-skill/references/resume_handoff_template.md)

## 原因

此前执行过程中曾临时生成过 `skills/governor-skill/`，容易导致：

- 文档引用漂移
- 执行者误以为需要新建第二个 governor skill
- authoritative path 与运行时路径混淆

为避免后续误用，本目录保留为 **废弃占位入口**，不再承载真实治理规则。

## 禁止事项

- 不要在本目录新增或维护治理规则
- 不要在文档中继续引用本目录作为 governor skill
- 不要把本目录复制到运行时环境作为正式 skill

## 后续动作

若未来确认无引用依赖，可在单独清理批次中删除本目录。
