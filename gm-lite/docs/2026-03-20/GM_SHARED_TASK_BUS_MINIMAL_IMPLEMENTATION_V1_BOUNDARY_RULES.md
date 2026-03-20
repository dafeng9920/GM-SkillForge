# GM Shared Task Bus Minimal Implementation v1 Boundary Rules

## 模块边界
- 本模块只做 `.gm_bus` 最小实现，不做完整总线系统
- 本模块只落文件骨架、协议骨架、校验与投影雏形
- 本模块不解决真实插件互通

## 权威状态边界
- 当前实现阶段允许 `manifest` 作为共享任务现实的权威文件骨架
- `task_board` 仍然是投影视图，不是权威写源
- `StateLog` 只做追加事件骨架，不做完整运行时状态机

## 协议对象边界
- `TaskEnvelope` 表达任务真身
- `DispatchPacket` 表达一次投递
- `Receipt` 表达接单确认对象骨架
- `Writeback` 表达标准回写骨架
- `EscalationPack` 表达升级对象骨架
- `StateLog` 表达事件追加骨架

## 目录结构边界
- `.gm_bus/manifest/`：权威索引与全局清单
- `.gm_bus/outbox/`：待投递动作
- `.gm_bus/inbox/`：待处理任务入口
- `.gm_bus/writeback/`：标准回写件
- `.gm_bus/escalation/`：升级包
- `.gm_bus/archive/`：归档结果

## 实现边界
- 允许：目录、文件、schema、example、stub、README
- 受控：最小 validator / projector 雏形
- 禁止：自动 watcher、自动 relay、自动 retry、跨插件直接调用

## 搜索与上下文边界
- 默认只在 `gm-lite/` 当前模块相关目录内搜索
- 不跨 `D:/NEW-GM` 或 `GM-SkillForge` 旧主线大范围扫描
- 大型全局规则应通过最小事实源投影提供

## change control
- 允许：字段补充、命名收紧、目录职责澄清、示例完善
- 受控：调整 manifest 字段、补充 projector / validator 雏形
- 禁止：提前做运行时、提前做 UI、提前做跨插件互通
