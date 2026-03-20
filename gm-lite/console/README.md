# GM-LITE Controller Console - Minimal Usage Guide

> **版本**: v1
> **状态**: 最小骨架，仅供准备阶段使用
> **所属模块**: gm_lite_controller_console_minimal_implementation

## 概述

GM-LITE 控制台是主控官用于查看 `.gm_bus` 共享任务总线状态与 verification 结果的只读控制台。

**当前版本仅提供骨架定义，不包含实际功能实现。**

## 目录结构

```
gm-lite/console/
├── README.md                    # 本文件
├── actions/                     # 主控动作占位定义
│   └── CONTROL_ACTION_PLACEHOLDERS.md
└── views/                       # 视图对象骨架（待补充）
```

## 最小使用说明

### 1. 查看主控动作定义

主控官可以查看 `actions/CONTROL_ACTION_PLACEHOLDERS.md` 了解控制台支持的动作类型。

**注意**: 当前所有动作仅为占位定义，未实现 runtime。

### 2. 动作占位格式

每个动作占位包含：
- **动作名称**: 动作的唯一标识
- **描述**: 动作用的说明
- **输入**: 动作需要的参数（占位）
- **输出**: 动作返回的对象类型（占位）
- **状态**: 当前为 PLACEHOLDER
- **Runtime**: 未实现

### 3. 当前支持的动作占位

| 动作 ID | 动作名称 | 描述 |
|---------|----------|------|
| AC001 | view_task_status | 查看任务状态 |
| AC002 | view_missing_items | 查看缺件列表 |
| AC003 | view_alerts | 查看告警信息 |
| AC004 | view_gate_ready | 查看 Gate Ready 状态 |
| AC005 | view_next_hop | 查看下一跳节点 |
| AC006 | view_blockers | 查看阻断项 |

## 数据源

控制台读取以下数据源（仅占位定义）：
- `.gm_bus/` - 共享任务总线
- `docs/2026-03-20/verification/` - 验证结果

**控制台不作为权威状态源，不修改执行流转结果。**

## 当前限制

### 未实现功能
- [ ] UI 界面
- [ ] 自动刷新 watcher
- [ ] 动作 runtime 执行
- [ ] Adapter 适配器
- [ ] 自动发送机制

### 已实现功能
- [x] 控制台目录骨架
- [x] 主控动作占位定义
- [x] 最小使用说明

## 后续步骤

1. 完成状态视图、告警视图、gate-ready 视图骨架（CI3）
2. 补充视图对象定义
3. 未来版本再考虑 UI 和 runtime 实现

## 变更控制

允许：
- 视图字段补充
- 命名收紧
- 样板数据补充
- README 完善

受控：
- 最小 loader / projector 占位补充
- 主控动作占位说明补充

禁止：
- 提前做 UI
- 提前做 watcher
- 提前做 adapter
- 提前做 runtime
