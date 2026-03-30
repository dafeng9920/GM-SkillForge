# GM LITE Blueprint Orchestrator Seed Implementation v1 Boundary Rules

## 权威路径
- 权威项目树：`D:\gm-lite`
- 镜像 / 主控文档树：`D:\GM-SkillForge\gm-lite`
- 权威 verification 路径以 `D:\gm-lite\docs\2026-03-24\verification\gm_lite_blueprint_orchestrator_seed_implementation\` 为准

## 允许实现对象
- `.gm_bus/inbox`
- `.gm_bus/active/<intent_trace_id>`
- `manifest.json`
- `blueprint.md`
- `BaseGate`
- `BlueprintOrchestrator`
- `MirrorSealer` 最小封印规则
- `M6` 最小 noun anchor / checkpoint 样板

## 禁止越界
- 不实现完整 M7/M8/M9 自动执行
- 不实现 auto-send
- 不实现 receipt / ack runtime
- 不实现 timeout / retry
- 不实现跨插件 direct-connect
- 不改写已有 frozen contract
- 触发红线时必须熔断，不得带病推进

## 打勾蓝图纪律
- 打勾必须基于物理状态
- 默认由 `Python` 执行体负责打勾，`LLM` 只在语义审计节点担任质检员
- `manifest.json` 为系统真相
- `blueprint.md` 为人眼真相
- 已打勾环节必须可断点续传
- `FROZEN` 物件不可被执行体回写污染
- 门禁与蓝图必须共生：`过一关，打一勾`
- 红线高于打勾：先过红线，再允许置位 `DONE`

## 执行与审计分工
- `Python Executor` 负责路径创建、文件存在性检查、状态写入、控制台增量推送
- `7B Inspector` 默认负责 Python 无法确定的高频低成本语义质量节点
- `Controller Arbiter` 只负责高价值歧义、补完裁决与恢复裁决
- 未经物理状态确认，不允许由 LLM 直接打勾
- M6-M9 子门禁完成后，必须回调蓝图控制器更新 `manifest.json` 与 `blueprint.md`
- 任何 Gate 如命中 authority path / frozen contract / false checkmark / semantic drift 红线，必须回调熔断事件

## 路径与镜像纪律
- 权威树下完成 active 初始化
- 镜像树只接收封印后资产
- 镜像动作未满足条件时只允许生成规则和样板，不允许提前复制
