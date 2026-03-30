# GM LITE Blueprint Orchestrator Seed Implementation v1 Prompts

## 放行顺序
- 第一波并行：`BO1 + BO2`
- 第二波串行：`BO3`
- 第三波串行：`BO4`

## 权威路径提醒
- 权威项目树以 `D:\gm-lite` 为准
- 标准 verification 路径以 `D:\gm-lite\docs\2026-03-24\verification\gm_lite_blueprint_orchestrator_seed_implementation\` 为准

## 当前模块固定禁止项
- 不实现完整 M7/M8/M9
- 不实现 auto-send
- 不实现 receipt / ack runtime
- 不实现 timeout / retry runtime
- 不实现跨插件 direct-connect
- 不实现完整镜像同步守护进程

## 当前模块默认执行哲学
- `Python` 是监工 / Executor
- `LLM` 是质检员 / Inspector
- 打勾动作优先由物理状态触发
- 语义审计只在关键卡口唤醒轻量模型
