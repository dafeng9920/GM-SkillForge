# Integration Gateway

## 定位
Integration Gateway 是 SkillForge 与外部系统之间的**纯连接层**，负责触发、路由、搬运和连接，**绝不裁决**。

## 核心原则
1. **只连接，不裁决** - 不做最终 PASS/FAIL 判定
2. **只搬运，不生成** - 不自行生成 GateDecision / permit / AuditPack
3. **只引用，不改写** - Evidence/AuditPack 只能由内核生成
4. **只准备，不运行** - 停留在骨架定义，不进入 runtime

## 目录结构
```
integration_gateway/
├── README.md                    # 本文件
├── RESPONSIBILITIES.md          # 职责定义
├── EXCLUSIONS.md                # 不负责项
├── CONNECTIONS.md               # 接口关系
├── PERMIT_RULES.md              # Permit 使用规则
├── RUNTIME_BOUNDARY.md          # Runtime 排除边界
├── gateway_interface.py         # 网关接口定义
├── router.py                    # 路由器（仅骨架）
├── trigger.py                   # 触发器（仅骨架）
└── transporter.py               # 搬运器（仅骨架）
```

## 与 Frozen 主线的关系
- **只读承接** - 读取 frozen 主线的公开承接结果
- **不回写** - 不回写 GateDecision / EvidenceRef / AuditPack / permit 语义
- **不修改** - 不修改 frozen 对象边界

## 与 system_execution 的关系
- **下游承接** - 从 system_execution 接收已编排的执行意图
- **不做二次编排** - 不替代 system_execution 的编排职责
- **不做二次裁决** - 不替代 Governor 的裁决职责

## 与 External System 的关系
- **不接入** - 当前阶段不接入真实外部系统
- **不联调** - 不进行真实 webhook/queue/db/slack/email/repo 联调
- **只定义接口** - 只定义连接接口，不实现连接逻辑

## 状态
- **阶段**: 准备阶段
- **范围**: 最小骨架定义
- **禁令**: 不得进入 runtime
