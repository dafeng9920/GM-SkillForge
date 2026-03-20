# GM Shared Task Bus Preparation v1 Boundary Rules

## 模块边界
- 本模块只定义共享任务总线准备边界，不实现总线
- 本模块只定义协议对象、目录结构、状态边界、投影视图
- 本模块不做插件 UI，不做插件互调，不做云端接力

## 与 GM-SkillForge 的边界
- 仅复用已验证的方法、协议思想、helper 设计意图
- 不直接搬运 `GM-SkillForge` 的历史模块实现
- 不回改 `GM-SkillForge` 已完成结论

## 与 D:/NEW-GM 的边界
- 仅吸收宪法、治理、节点化、skills 的设计意图
- 不直接复制旧服务实现
- 不让历史目录结构反向主导 `gm-lite`

## 权威状态层边界
- `manifest / task_board` 在 Light 准备阶段只作为全局视图候选
- `task board` 是投影视图，不是最终权威写源
- 后续 SQLite 状态层是下一阶段问题，不在本轮实现

## 协议对象边界
- `TaskEnvelope` 是任务真身
- `DispatchPacket` 是一次投递动作
- `Receipt` 是接单确认
- `Writeback` 是结果回写
- `EscalationPack` 是升级对象
- `StateLog` 是事件追加对象

## 目录结构边界
- `.gm_bus/` 只定义目录职责
- 目录结构必须支持：
  - `manifest`
  - `outbox`
  - `inbox`
  - `writeback`
  - `escalation`
  - `archive`

## 插件互操作边界
- 不做插件直连
- 不做共享聊天上下文
- 插件之间未来只通过共享任务现实层互通

## change control 规则
- 允许：命名收紧、对象字段补充、目录职责澄清、任务拆分补强
- 受控：增加最小协议对象字段、增加视图与状态边界说明
- 禁止：提前做实现、提前做插件直连、提前做 runtime
