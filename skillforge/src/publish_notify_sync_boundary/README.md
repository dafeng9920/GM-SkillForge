# Publish / Notify / Sync Boundary

## 定位
Publish / Notify / Sync Boundary 是 SkillForge 与外部系统之间的**动作边界层**，负责定义发布、通知、同步三类关键动作的边界规则。

## 核心原则
1. **必须持 permit** - 所有 publish/notify/sync 动作必须持有有效 permit
2. **只定义边界，不执行** - 只定义动作边界，不实现真实动作
3. **只建议，不裁决** - 只提供建议，不做最终 PASS/FAIL 判定
4. **只引用，不生成** - 只引用 Evidence/AuditPack，不生成新的

## 目录结构
```
publish_notify_sync_boundary/
├── README.md                    # 本文件
├── RESPONSIBILITIES.md          # 职责定义
├── EXCLUSIONS.md                # 不负责项
├── CONNECTIONS.md               # 接口关系
├── PERMIT_RULES.md              # Permit 使用规则
├── RUNTIME_BOUNDARY.md          # Runtime 排除边界
├── __init__.py                  # 模块入口
├── boundary_interface.py        # 边界接口定义
├── publish_boundary.py          # 发布边界（仅骨架）
├── notify_boundary.py           # 通知边界（仅骨架）
└── sync_boundary.py             # 同步边界（仅骨架）
```

## 三类关键动作

### 1. Publish (发布)
- **定义**: 将技能或资源发布到外部系统
- **示例**: PUBLISH_LISTING, UPGRADE_REPLACE_ACTIVE
- **Permit 要求**: 必须持有 PublishPermit

### 2. Notify (通知)
- **定义**: 向外部系统发送通知消息
- **示例**: 发送 slack 消息、发送 email 通知
- **Permit 要求**: 必须持有 NotifyPermit

### 3. Sync (同步)
- **定义**: 同步状态到外部系统
- **示例**: 同步技能状态、同步配置
- **Permit 要求**: 必须持有 SyncPermit

## 与 E4 (External Action Policy) 的关系
- **E4** 定义关键动作列表和 permit 校验规则
- **E6** 定义 publish/notify/sync 三类动作的具体边界规则
- **E4 的 CRITICAL_ACTIONS** 包含 E6 的动作类型

## 与 E5 (Retry / Compensation Boundary) 的关系
- **E5** 定义失败后的重试/补偿建议
- **E6** 定义动作执行前的边界规则
- **E5 的 CompensationPermit** 可能触发 **E6 的重新动作**

## 状态
- **阶段**: 准备阶段
- **范围**: 最小骨架定义
- **禁令**: 不得进入 runtime
