# GM LITE Shell Seed Implementation v1 Change Control Rules

## Frozen 输入
- `GM_LITE_SAMPLE_FLOW_VALIDATION_V1_REPORT.md`
- `GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_REPORT.md`
- `GM_LITE_EXECUTOR_INSPECTOR_ARBITER_ALLOCATION_V1.md`
- `GM_LITE_BLUEPRINT_GATE_COEVOLUTION_MODEL_V1.md`

## 允许变更
- 补充 shell 入口
- 补充 read model / view model 绑定
- 补充最小 action surface
- 补充 README / example / usage

## 禁止变更
- 不重写 bus contract
- 不重写 blueprint runtime contract
- 不做重 UI 大改
- 不提前实现 auto-send / direct-connect
- 不将 shell 误做成完整发布版插件

## 主控规则
- 出现 authority path 冲突，立即暂停
- 出现 scope expansion，立即暂停
- 出现壳层绕过蓝图/runtime 真相，立即暂停
