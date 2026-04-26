# GM_LITE_HUMAN_FIRST_CONVERSATIONAL_USABILITY_V1_SCOPE

## Objective

将 `GM-Lite` 从“已具备基础链路能力的工作台”推进为“人类优先的对话式启动与执行面”。

## Core Judgment Standard

后续实现只按以下 4 条判断是否成立：

1. 对话框优先
2. 默认说人话
3. 机器结构下沉
4. 点击即用

## What Is Already Considered Complete

- Codex / Console → `.gm_bus` 中转链已基本具备
- AI 军团读取 / 认领 / 回写主链已基本具备
- context continuity / state transition 基础能力已具备
- operator relief 与 continuous collaboration 已达到第一阶段可用

## What This Line Solves

本线不再重点解决“链路是否存在”，而重点解决：

- 用户是否能在单一对话面里启动任务
- 用户是否能看懂默认反馈
- 用户是否不必直接面对原始 `.gm_bus` / protocol / trace
- 用户是否能用更少点击、更少解释完成常用动作

## Not In Scope

- 不扩展上游知识库/SkillForge 架构
- 不重做 `.gm_bus` 协议层
- 不新增重型调度中心
- 不把插件做成纯技术调试面板

## Expected Outcome

`GM-Lite` 默认呈现为一个对话驱动的工作台：

- 用户一句话即可启动或继续任务
- 系统默认返回人类可读状态
- 原始结构仅在调试层显示
- 高频动作可直接点击完成
