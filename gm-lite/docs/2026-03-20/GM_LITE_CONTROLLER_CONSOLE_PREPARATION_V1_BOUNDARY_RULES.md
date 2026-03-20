# GM LITE Controller Console Preparation v1 Boundary Rules

## 模块边界
- 本模块只定义 controller console 准备边界，不实现控制台
- 本模块只定义主控官视图、输入源、交互动作与禁止项
- 本模块不做任何 UI / 面板代码

## 与 `.gm_bus` 的边界
- controller console 读取 `.gm_bus` 共享任务现实
- controller console 不直接改写 `.gm_bus` 权威状态
- controller console 可读取 manifest / writeback / escalation / archive

## 与 task board 的边界
- task board 是控制台投影视图来源之一
- task board 不是控制台的唯一事实源
- verification 与 `.gm_bus` 共同构成主控判断基础

## 主控官边界
- 主控官通过控制台看状态、缺件、next hop、gate ready、阻断项
- 主控官不通过控制台直接“替执行者完成任务”
- 主控官只做裁决、放行、退回、终验

## change control
- 允许：视图项补充、命名收紧、交互动作澄清
- 受控：新增只读视图类别、补充主控动作说明
- 禁止：提前做 UI、提前做自动化 runtime、提前做插件互通
