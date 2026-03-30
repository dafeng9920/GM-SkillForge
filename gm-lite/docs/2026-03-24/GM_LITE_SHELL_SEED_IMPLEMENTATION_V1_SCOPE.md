# GM LITE Shell Seed Implementation v1 Scope

## 当前模块
- `gm_lite_shell_seed_implementation_v1`

## 当前唯一目标
- 为 `GM-LITE` 建立最小可作战外壳，使系统不再只是分散代码与文档集合，而是开始具备统一入口、最小操作面、蓝图可见性与任务送入能力。

## 本模块允许项
- 落 shell 统一入口骨架
- 落最小 read model / view model 绑定
- 落 blueprint / bus / dispatch 状态展示入口
- 落最小 action surface（如：ingest / inspect / dispatch / suspend / resume）
- 落最小 shell README / usage / examples
- 落为后续打掉手动转递预留的 action hook

## 本模块禁止项
- 不实现重型 VSCode WebView UI
- 不实现完整插件市场打包
- 不实现真实 auto-send
- 不实现完整 direct-connect
- 不实现完整 runtime orchestration
- 不扩展到 light release judgment

## 本模块最小推进范围
- 统一入口
- 最小操作面
- 状态可见性
- 蓝图 / bus / assist / gate 的最小接线
- 为“消灭手动转递”预留挂点

## 固定输出
- `GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_SCOPE.md`
- `GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_BOUNDARY_RULES.md`
- `GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_TASK_BOARD.md`
- `GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_ACCEPTANCE.md`
- `GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_REPORT.md`
- `GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_CHANGE_CONTROL_RULES.md`
- `GM_LITE_SHELL_SEED_IMPLEMENTATION_V1_PROMPTS.md`

## 自动暂停条件
- 开始做重型 UI 视觉工程
- 开始做真实 auto-send
- 开始做复杂插件通道注入
- 开始做完整 runtime 编排
- 开始扩展到 release judgment

## 本模块未触碰项
- qwen local gate integration
- full auto-dispatch bridge
- complete plugin packaging
