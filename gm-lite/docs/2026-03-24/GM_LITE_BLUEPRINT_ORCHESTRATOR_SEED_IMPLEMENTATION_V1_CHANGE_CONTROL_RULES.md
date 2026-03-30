# GM LITE Blueprint Orchestrator Seed Implementation v1 Change Control Rules

## Frozen 输入
- `GM_LITE_SAMPLE_FLOW_VALIDATION_V1_REPORT.md`
- `GM_BUS_MANAGER_SEED_IMPLEMENTATION_V1_REPORT.md`
- 已有 `.gm_bus` contract 与 metadata guardrail 文档组

## 允许变更
- 补充 active 初始化样板
- 补充 `manifest.json` / `blueprint.md` 模板
- 补充 M6 样板逻辑
- 补充 `.frozen_seal` 说明与样板

## 禁止变更
- 不重写 `.gm_bus` contract
- 不扩展到完整 gate runtime
- 不扩展到完整镜像同步系统
- 不在此轮接入 qwen local gate
- 不把 seed 实现升级成 release judgment

## 主控规则
- 出现 authority path 冲突，立即暂停
- 出现 scope expansion，立即暂停
- 出现 frozen contract 被改写，立即暂停
