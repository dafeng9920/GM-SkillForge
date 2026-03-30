# GM LITE Shell Seed Implementation v1 Boundary Rules

## 权威路径
- 权威项目树：`D:\gm-lite`
- 镜像 / 主控文档树：`D:\GM-SkillForge\gm-lite`
- 权威 verification 路径以 `D:\gm-lite\docs\2026-03-24\verification\gm_lite_shell_seed_implementation\` 为准

## 允许接线对象
- `.controller_console`
- `.gm_bus`
- `src\gm_bus`
- `src\blueprint_orchestrator`
- dispatch assist 输出
- read-model / view-model / examples

## 外壳边界
- 外壳必须服务“作战运行级 1”
- 外壳优先解决统一入口与最小操作面
- 外壳必须让主控官看到：当前状态、当前卡点、下一动作
- 外壳必须为后续自动转递预留挂点

## 禁止越界
- 不做重型可视化 UI
- 不做真实自动发单
- 不做插件 API 深度接线
- 不改写现有 bus / blueprint contract
- 不绕过 authority path 规则

## 默认交互纪律
- 所有状态真相仍以权威树文件为准
- shell 只做读取、汇总、最小动作触发
- 真实打勾、红线、恢复链仍归 runtime / blueprint 层

## 主控官关切
- 本轮必须减少“翻文档/找脚本/记路径”摩擦
- 本轮不要求彻底消灭手动转递，但必须把它收缩成一个明确的操作面
