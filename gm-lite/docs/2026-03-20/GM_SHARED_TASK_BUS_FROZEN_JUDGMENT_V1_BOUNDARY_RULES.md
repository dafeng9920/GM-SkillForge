# GM Shared Task Bus Frozen Judgment v1 Boundary Rules

## 模块边界
- 本模块只做冻结判断，不做新实现
- 本模块只确认当前 `.gm_bus` 最小实现是否可冻结
- 本模块不推动后续主线提前进入

## 冻结边界
- Frozen 对象只包括：
  - `.gm_bus` 目录骨架
  - 6 个协议对象的最小定义
  - `manifest / task_board / projector / validator` 当前边界口径
  - 当前 verification 通过结论

## 非冻结项
- SQLite 状态层
- 插件 adapter
- 自动互通 runtime
- timeout / retry runtime
- 插件 UI
- chat-output-to-bus bridge 的正式实现

## change control
- 允许：文档澄清、命名收紧、非语义说明补强
- 受控：字段补充建议、后续模块前置说明
- 禁止：回改 frozen 前提、直接扩实现范围、提前做下一层主线
