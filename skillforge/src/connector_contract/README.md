# Connector Contract

## 定位
Connector Contract 是 SkillForge 外部连接接口契约定义层，负责**定义外部连接接口**，**不实现连接**。

## 核心原则
1. **只定义，不实现** - 只定义接口契约，不实现真实连接
2. **只声明，不生成** - 只声明 permit 需求，不生成 permit
3. **只引用，不改写** - 只引用 Evidence/AuditPack，不修改
4. **只读，不写** - 对 frozen 主线只读，不回写

## 目录结构
```
connector_contract/
├── README.md                    # 本文件
├── RESPONSIBILITIES.md          # 职责定义
├── EXCLUSIONS.md                # 不负责项
├── CONNECTIONS.md               # 接口关系
├── PERMIT_RULES.md              # Permit 使用规则
├── RUNTIME_BOUNDARY.md          # Runtime 排除边界
├── __init__.py                  # 模块导出
└── types.py                     # 契约类型定义
```

## 与 Frozen 主线的关系
- **只读承接** - 只读取 frozen 主线的公开承接结果
- **不回写** - 不回写 GateDecision / EvidenceRef / AuditPack / permit 语义
- **不修改** - 不修改 frozen 对象边界

## 与 Integration Gateway 的关系
- **上游定义** - 为 Integration Gateway 提供连接接口契约
- **不依赖实现** - 不依赖 Integration Gateway 的具体实现
- **协议无关** - 定义通用、协议无关的接口结构

## 与 External System 的关系
- **不接入** - 不接入真实外部系统
- **不联调** - 不进行真实外部系统联调
- **只定义接口** - 只定义连接接口契约

## 状态
- **阶段**: 准备阶段
- **范围**: 最小接口契约定义
- **禁令**: 不得进入 runtime
