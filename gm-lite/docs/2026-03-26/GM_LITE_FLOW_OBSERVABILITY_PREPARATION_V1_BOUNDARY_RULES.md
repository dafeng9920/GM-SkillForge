# GM LITE Flow Observability Preparation v1 Boundary Rules

## 允许项
- 定义 run metrics / run summary / dashboard 字段
- 定义插件侧最小可见性项
- 定义统计口径与排除项

## 禁止项
- 不直接实现复杂可视化 UI
- 不重构插件壳
- 不改动 `.gm_bus` 现有 contract
- 不把 observability 变成完整监控平台

## 权威口径
- 权威树：`D:\gm-lite`
- 镜像树：`D:\GM-SkillForge\gm-lite`
- 时间默认口径：系统运行过程时间
