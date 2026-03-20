---
name: agent-browser-skill
description: OpenClaw 自动化操作的“核心手脚”。提供高阶语义化的网页交互能力，实现跨平台的复杂流程自动化。
---

# agent-browser-skill

## 触发条件

- 需要从非 API 来源获取深度实时数据
- 需要执行模拟人工的网页表单填写或操作流程
- 需要对目标网站进行视觉或 DOM 结构的深度探测

## 原子层指令 (Atomic Actions)

- `semantic_nav`: 语义化导航（如：“去 GitHub 搜最新的 OpenClaw 仓库”）。
- `element_interact`: 低级 DOM 交互（点击、输入、滚动）。
- `visual_assertion`: 视觉验证，确保操作后的页面状态符合预期。

## 协同逻辑 (MvP Integration)

- **World Vision Link**: 将抓取的网页关键信息自动流失给 `world-vision-skill` 进行二次建模。
- **Memory Feed**: 操作成功的关键路径会自动输入 `capability-evolver-skill` 作为后续自动化的模板。

## DoD

- [ ] 与本地 `browser_subagent` 驱动器成功配对
- [ ] 支持无头 (Headless) 与有头 (Headed) 模式切换
- [ ] 具备完善的自动反爬和验证码处理（本地辅助）逻辑
