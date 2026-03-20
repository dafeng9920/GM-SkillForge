# GM-LITE Controller Console - Control Action Placeholders

> **版本**: v1
> **状态**: 占位定义，未进入 runtime
> **所属模块**: gm_lite_controller_console_minimal_implementation

## 说明

本文档定义 GM-LITE 控制台主控官动作占位。这些动作仅为接口定义，不包含实际运行时实现。

## 动作占位列表

### AC001 - 查看任务状态
- **动作**: `view_task_status`
- **描述**: 查看指定任务的状态信息
- **输入**: `task_id`
- **输出**: 任务状态视图对象
- **状态**: PLACEHOLDER
- **Runtime**: 未实现

### AC002 - 查看缺件列表
- **动作**: `view_missing_items`
- **描述**: 查看当前缺件清单
- **输入**: `module_id`
- **输出**: 缺件视图对象
- **状态**: PLACEHOLDER
- **Runtime**: 未实现

### AC003 - 查看告警信息
- **动作**: `view_alerts`
- **描述**: 查看当前告警列表
- **输入**: `severity_level` (可选)
- **输出**: 告警视图对象
- **状态**: PLACEHOLDER
- **Runtime**: 未实现

### AC004 - 查看 Gate Ready 状态
- **动作**: `view_gate_ready`
- **描述**: 查看任务是否达到 Gate Ready 状态
- **输入**: `task_id`
- **输出**: Gate Ready 状态对象
- **状态**: PLACEHOLDER
- **Runtime**: 未实现

### AC005 - 查看 Next Hop
- **动作**: `view_next_hop`
- **描述**: 查看任务的下一跳节点
- **输入**: `task_id`
- **输出**: Next Hop 信息对象
- **状态**: PLACEHOLDER
- **Runtime**: 未实现

### AC006 - 查看阻断项
- **动作**: `view_blockers`
- **描述**: 查看当前阻断任务推进的项
- **输入**: `task_id` (可选)
- **输出**: 阻断项视图对象
- **状态**: PLACEHOLDER
- **Runtime**: 未实现

## 未包含动作

以下动作**不在**当前 Light 版范围内：
- 任务分配/派遣
- 自动状态同步
- 外部服务调用
- 权限验证
- 实时通知

## Runtime 说明

当前所有动作占位**不包含**：
- 函数实现
- API 调用
- 状态修改
- 副作用操作

这些占位仅用于定义控制台未来支持的交互类型。
