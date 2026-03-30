# GM LITE Blockage Recovery Runtime Minimal Implementation v1 Boundary Rules

## 允许项
- 在 `D:\gm-lite` 权威树内补充 blockage / recovery runtime 最小实现
- 补充与 `.gm_bus` 现有 schema 对齐的 runtime 逻辑
- 增加最小样板命令、状态推进、写回记录

## 禁止项
- 不实现完整 auto-orchestrator
- 不实现完整 state machine 平台化重构
- 不把 tri-split 合并成单层自动化
- 不改动 `D:\GM-SkillForge` 中与当前主线无关的旧模块
- 不跳过 evidence / writeback / compliance

## 权威口径
- 权威项目树：`D:\gm-lite`
- 镜像文档树：`D:\GM-SkillForge\gm-lite`
- `.gm_bus` 为唯一总线命名

## 默认技术边界
- blockage detection 先做最小触发条件，不做复杂推理引擎
- recovery 先做人工可恢复与最小 resume，不做全自动复杂编排
- escalation / memo / remediation 必须留物证，不允许隐式恢复
