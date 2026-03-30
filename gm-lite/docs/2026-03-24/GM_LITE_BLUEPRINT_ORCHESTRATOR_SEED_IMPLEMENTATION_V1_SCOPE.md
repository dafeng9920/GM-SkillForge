# GM LITE Blueprint Orchestrator Seed Implementation v1 Scope

## 当前模块
- `gm_lite_blueprint_orchestrator_seed_implementation_v1`

## 当前唯一目标
- 为 `GM-LITE` 落下打勾蓝图 runtime 的最小种子实现，使权威树中的任务包可以在物理路径、manifest 状态、blueprint 打勾与最小 M6 门禁之间形成第一轮可追踪骨架。

## 本模块允许项
- 落 `BaseGate` 基类
- 落 `BlueprintOrchestrator` 最小骨架
- 落 `TaskRunner` / Python executor 最小骨架
- 落 `.gm_bus/inbox -> active/<intent_trace_id>` 物理初始化逻辑
- 落 `manifest.json + blueprint.md` 双路输出
- 落 `M6` 最小意图捕获 / noun anchors locked 逻辑
- 落 `MirrorSealer` 最小封印骨架与 `.frozen_seal` 生成规则
- 落最小 sample intent / README / usage

## 本模块禁止项
- 不实现完整 M7 / M8 / M9 自动化
- 不实现真实外部 LLM 调度
- 不实现 watcher 全量常驻运行
- 不实现 timeout / retry runtime
- 不实现跨插件 direct-connect
- 不扩展到完整 release judgment

## 本模块最小推进范围
- 骨架 1：物理路径与状态感知
- 骨架 2：双向打勾协议
- 骨架 3：镜像封印种子规则
- `Python Executor / LLM Inspector` 协作模式
- `Python -> 7B -> Controller` 成本优先级分工
- M6 最小打勾样板
- 控制台最小进度输出

## 固定输出
- `GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_SCOPE.md`
- `GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
- `GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_TASK_BOARD.md`
- `GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_ACCEPTANCE.md`
- `GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_REPORT.md`
- `GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_CHANGE_CONTROL_RULES.md`
- `GM_LITE_BLUEPRINT_ORCHESTRATOR_SEED_IMPLEMENTATION_V1_PROMPTS.md`

## 自动暂停条件
- 开始实现完整 M7-M9
- 开始接入真实云端编排
- 开始做复杂 watcher 常驻系统
- 开始做完整镜像同步编排
- 开始扩展到 release judgment

## 本模块未触碰项
- qwen local gate integration
- architecture heartbeat
- full runtime automation
