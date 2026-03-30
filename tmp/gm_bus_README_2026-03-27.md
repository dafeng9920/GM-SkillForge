# .gm_bus

GM Shared Task Bus - 共享任务总线目录。

## 版本

- **当前版本**: Light (定义阶段)
- **版本范围**: 准备阶段 (Preparation Phase)

## 三层定位

`GM-LITE` 当前处于三层体系中的前置上游位置：

- **GM-LITE** = 前置任务现实层 + 轻量接入/适配入口 + 执行桥接层
- **superpowers 类层** = 执行方法论增强层
- **SkillForge** = 治理裁决层 + L3 标准 Skill 固化层

其中 `.gm_bus` 的职责只限于：

- 让不同插件 / agent / 执行器看到同一个任务现实
- 统一任务发现、投递、接收、回写、升级、归档的协议边界

`.gm_bus` **不是**：

- 重运行时内核
- 完整插件运行时平台
- 最终治理裁决层
- 重型执行方法论本身

## 目录结构

```text
.gm_bus/
├── manifest/      # 任务清单投影视图
├── outbox/        # 待投递任务
├── inbox/         # 已接收待确认任务
├── writeback/     # 执行结果回写
├── escalation/    # 升级处理请求
└── archive/       # 已完结任务归档
```

## 目录职责

| 目录 | 职责 |
|------|------|
| `manifest/` | 当前态快照 / 发现入口 / 检索视图，不应单独视为最终权威真源 |
| `outbox/` | 存放待投递的 `DispatchPacket` |
| `inbox/` | 存放已接收待确认的 `DispatchPacket` |
| `writeback/` | 存放执行返回的 `Receipt` / `Writeback` 对象 |
| `escalation/` | 存放升级处理的 `EscalationPack` |
| `archive/` | 存放已完结任务的 `StateLog` 与归档记录 |

## 权威关系说明

当前建议明确：

- `manifest/` 更适合作为任务当前态的投影视图与检索入口
- 最终权威不应仅依赖覆盖式当前态文件
- 更可靠的权威应来自：
  - append-only 的 `StateLog`
  - 或 `TaskEnvelope + 状态迁移记录` 的组合

因此：

> `manifest/` 是便于发现和查看的当前态入口，  
> 不是唯一最终真源。

## 协议对象映射

| 协议对象 | 目标目录 | 语义 |
|----------|----------|------|
| `TaskEnvelope` | `manifest/` | 任务当前态投影 / 发现入口 |
| `DispatchPacket` | `outbox/` → `inbox/` | 投递动作的静态传递 |
| `Receipt` | `writeback/` | 接单确认回写 |
| `Writeback` | `writeback/` | 执行结果回写 |
| `EscalationPack` | `escalation/` | 阻塞、依赖缺失、路径不明等升级处理请求 |
| `StateLog` | `archive/` | 事件追加记录与归档基础 |

## 与执行层的边界

执行器不应直接把 `.gm_bus` 当成自由操作目录。

推荐路径是：

`TaskEnvelope / DispatchPacket`
→ `GM Execution Bridge`
→ `ExecutionLaunchContract`
→ `.gm_exec/runs/<run_id>/...`
→ `Receipt / Writeback / EscalationPack`
→ 回写 `.gm_bus`

这意味着：

- 执行期脏数据应待在 `.gm_exec`
- `.gm_bus` 只承接标准化回写对象
- 执行器不应直接修改全局状态或直接归档

## 最小状态链

当前建议只保留最小状态链：

`DISCOVERED -> DISPATCHED -> ACKED -> IN_EXECUTION -> WRITEBACK_SUBMITTED -> CLOSED`

异常分支仅保留：

- `ESCALATED`
- `FAILED`

原因：

- Light 版本优先冻结协议和目录边界
- 暂不膨胀成复杂状态机系统

## 运行时排除 (Light 版本)

当前版本**不包含**以下运行时功能：

- 文件系统运行时（文件监听、自动扫描、增量更新）
- 任务调度运行时（自动投递、自动确认、超时检测、重试）
- 状态管理运行时（重状态机引擎、复杂状态同步、冲突检测）
- 持久化运行时（SQLite 层、迁移系统、数据库驱动）
- 插件系统运行时（插件发现、复杂互操作、生命周期管理）
- UI/可视化运行时（Kanban UI、列表视图、实时更新）
- 重型执行方法论运行时
- 最终治理裁决运行时

以上功能预留至后续实现阶段，不在当前 Light 版本内。

## 版本边界

| 版本 | 范围 |
|------|------|
| **Light** (当前) | 协议对象边界、目录结构规范、投影视图定义、桥接前置准备 |
| **Execution Bridge Prep** | 执行契约、`.gm_exec` 工作区、标准回写对象 |
| **Core** (预留) | 未来若确有必要，再讨论更重运行时能力 |
| **UI Layer** (预留) | 可视化层、轻量观察面、操作入口 |

## 硬约束遵守

- 未实现重运行时代码
- 未引入数据库（SQLite 等不在 Light 范围）
- 未将 `.gm_bus` 变成完整插件运行时中心
- 未将治理职责塞入 `GM-LITE`
- 当前以目录结构、协议边界、桥接前置定义为主

## 相关文档

- `docs/2026-03-27/verification/三层定位.md`
- `docs/2026-03-27/GM_LITE_THREE_LAYER_BOUNDARY_WITH_SUPERPOWERS_V1.md`
- `docs/2026-03-27/GM_LITE_EXECUTION_BRIDGE_AND_CONTRACT_PREPARATION_V1_SCOPE.md`

