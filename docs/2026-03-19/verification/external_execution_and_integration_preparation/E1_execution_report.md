# E1 Connector Contract 执行报告

## 任务信息
- **Task ID**: E1
- **任务名称**: connector contract 子面最小准备骨架
- **执行者**: vs--cc1
- **审查者**: Kior-A
- **合规官**: Kior-C
- **执行日期**: 2026-03-19
- **执行模式**: parallel

## 交付物清单

### 1. 目录/文件骨架
```
skillforge/src/connector_contract/
├── README.md                    # 模块定位和核心原则
├── RESPONSIBILITIES.md          # 职责定义
├── EXCLUSIONS.md                # 不负责项
├── CONNECTIONS.md               # 接口关系
├── PERMIT_RULES.md              # Permit 使用规则
├── RUNTIME_BOUNDARY.md          # Runtime 排除边界
├── __init__.py                  # 模块导出
└── types.py                     # 契约类型定义
```

### 2. 职责定义
详见 [RESPONSIBILITIES.md](../../skillforge/src/connector_contract/RESPONSIBILITIES.md)

**核心职责**:
- 契约定义：定义外部连接接口的数据结构、schema 规范、错误分类
- 依赖声明：声明对 frozen 主线的只读依赖
- Permit 需求声明：声明连接所需的 permit 类型（不生成）
- Evidence 引用声明：声明 Evidence 引用类型（不修改）
- 接口分类：按连接类型分类（git/webhook/api/registry/storage/notification）

### 3. 不负责项
详见 [EXCLUSIONS.md](../../skillforge/src/connector_contract/EXCLUSIONS.md)

**明确不负责**:
- 不实现连接（真实连接由 Integration Gateway 执行）
- 不生成 Permit（Permit 由 Governor 生成）
- 不修改 Evidence/AuditPack（由内核生成）
- 不裁决（裁决是 Governor/Gate/Release 的职责）
- 不进入 Runtime（Runtime 执行是 Integration Gateway 的职责）
- 不改写 Frozen 主线（Frozen 主线不可倒灌）

### 4. 与 Frozen 主线的承接点
详见 [CONNECTIONS.md](../../skillforge/src/connector_contract/CONNECTIONS.md)

**只读承接**:
- GateDecision: 只读引用，用于 permit 需求声明
- EvidenceRef: 只读引用，用于 evidence 引用声明
- AuditPack: 只读引用，用于 audit_pack 引用声明
- NormalizedSkillSpec: 只读引用，用于技能规范获取

**不回写**: 不回写 GateDecision / EvidenceRef / AuditPack / permit 语义

### 5. 与 system_execution 的接口关系
详见 [CONNECTIONS.md](../../skillforge/src/connector_contract/CONNECTIONS.md)

**关系定位**:
- system_execution → integration_gateway → connector_contract（契约提供）
- Connector Contract 为 Integration Gateway 提供接口契约
- Connector Contract 不依赖 Integration Gateway 的具体实现

### 6. Permit 规则说明
详见 [PERMIT_RULES.md](../../skillforge/src/connector_contract/PERMIT_RULES.md)

**核心原则**: 只声明 permit 需求，不生成 permit

**Permit 声明方式**:
- 通过 `PermitRequirementDeclaration` 声明 permit 需求
- 在 `ExternalConnectionContract` 的 `required_permits` 字段中声明
- 引用 Governor 定义的 permit 类型

**禁止事项**:
- 不生成 permit 实例
- 不验证 permit 有效性
- 不存储 permit 实例

### 7. Evidence 引用规则说明
详见 [CONNECTIONS.md](../../skillforge/src/connector_contract/CONNECTIONS.md)

**核心原则**: 只引用，不修改

**引用声明方式**:
- 通过 `EvidenceReferenceDeclaration` 声明引用类型
- 声明访问模式（read/upload/notify）
- 声明引用用途

**禁止事项**:
- 不生成 Evidence/AuditPack
- 不修改 Evidence/AuditPack
- 不删除 Evidence/AuditPack

### 8. 后续 Runtime 的排除边界
详见 [RUNTIME_BOUNDARY.md](../../skillforge/src/connector_contract/RUNTIME_BOUNDARY.md)

**不进入的范围**:
- 连接执行（不建立真实连接）
- 数据传输（不发送/接收真实数据）
- 协议处理（不解析协议报文）
- 状态管理（不维护连接状态）
- 错误处理（不处理网络错误）

**边界声明**:
- 所有 dataclass 都是 frozen=True
- 文档明确标注"不实现连接"
- 清晰区分接口定义与实现

## Python 类型定义

### 核心类型
详见 [types.py](../../skillforge/src/connector_contract/types.py)

1. **FrozenDependencyDeclaration**: Frozen 依赖声明
2. **PermitRequirementDeclaration**: Permit 需求声明
3. **EvidenceReferenceDeclaration**: Evidence 引用声明
4. **ExternalConnectionContract**: 外部连接接口契约定义
5. **ConnectorRequest**: Connector 请求定义
6. **ConnectorResult**: Connector 结果定义

### 预定义契约
- **GENERIC_CONNECTION_CONTRACT**: 通用、协议无关的连接契约示例

## 硬约束验证

| 硬约束 | 检查结果 |
|--------|---------|
| 不接入真实外部系统 | ✅ 只定义接口契约 |
| 不进入 runtime | ✅ 没有执行逻辑 |
| 不改写 frozen 主线 | ✅ 只读依赖声明 |
| 不生成真实外部协议实现 | ✅ 只有 schema |
| 有 permit/evidence/auditpack 规则说明 | ✅ 专门文档 |

## 合规自检

| 检查项 | 状态 | 说明 |
|-------|------|------|
| 不接入真实外部系统 | ✅ | 只定义接口契约 |
| 不进入 runtime | ✅ | 没有执行逻辑 |
| 不绕过 permit | ✅ | 只声明需求，不生成 |
| 不改写 Evidence/AuditPack | ✅ | 只引用，不修改 |
| 不改写 frozen 对象 | ✅ | 只读依赖声明 |
| 有 permit 规则说明 | ✅ | PERMIT_RULES.md |
| 有 evidence 规则说明 | ✅ | CONNECTIONS.md |
| 有职责定义 | ✅ | RESPONSIBILITIES.md |
| 有不负责项 | ✅ | EXCLUSIONS.md |
| 有接口关系说明 | ✅ | CONNECTIONS.md |

## 文件清单

### 新增文件
1. `skillforge/src/connector_contract/README.md`
2. `skillforge/src/connector_contract/RESPONSIBILITIES.md`
3. `skillforge/src/connector_contract/EXCLUSIONS.md`
4. `skillforge/src/connector_contract/CONNECTIONS.md`
5. `skillforge/src/connector_contract/PERMIT_RULES.md`
6. `skillforge/src/connector_contract/RUNTIME_BOUNDARY.md`
7. `skillforge/src/connector_contract/__init__.py`
8. `skillforge/src/connector_contract/types.py`
9. `skillforge/src/contracts/connector_contract/__init__.py` (向后兼容)
10. `docs/2026-03-19/verification/external_execution_and_integration_preparation/E1_execution_report.md` (本文件)

### 修改文件
无（未修改任何现有文件）

## 审查路径

1. **Kior-A (Review)**:
   - 检查职责定义是否清晰
   - 检查不负责项是否完整
   - 检查接口关系是否清楚
   - 检查 permit/evidence 规则是否自洽
   - 检查是否偷带真实外部接入语义

2. **Kior-C (Compliance)**:
   - 检查是否接入真实外部系统
   - 检查是否进入 runtime
   - 检查是否绕过 permit
   - 检查是否允许改写 Evidence/AuditPack
   - 检查是否要求改 frozen 主线

## 执行者声明

我，vs--cc1，作为任务 E1 的执行者，声明：

1. 本交付物仅包含 connector contract 子面的最小准备骨架
2. 未实现任何真实外部连接
3. 未进入 runtime 执行层
4. 未改写 frozen 主线任何对象
5. 未生成任何 permit 实例
6. 未修改任何 Evidence/AuditPack
7. 所有 permit/evidence/auditpack 规则均已明确说明
8. 所有职责边界均已清晰定义

---

**执行者**: vs--cc1
**日期**: 2026-03-19
**状态**: 待审查
