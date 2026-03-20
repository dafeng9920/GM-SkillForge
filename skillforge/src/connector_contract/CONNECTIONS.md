# Connector Contract 接口关系

## 上游: Frozen 主线

### 只读承接
```
frozen 主线 → connector_contract
```

### 承接内容
- **GateDecision**: 只读引用，用于 permit 需求声明
- **EvidenceRef**: 只读引用，用于 evidence 引用声明
- **AuditPack**: 只读引用，用于 audit_pack 引用声明
- **NormalizedSkillSpec**: 只读引用，用于技能规范获取

### 接口契约
- **输入**: Frozen 对象的公开接口
- **输出**: FrozenDependencyDeclaration（只读依赖声明）
- **约束**: 所有访问必须是只读的

### 只读承接规则
- Connector Contract **只读** Frozen 对象
- 不修改 Frozen 对象的内容
- 不生成新的治理对象

## 下游: Integration Gateway

### 契约提供
```
connector_contract → integration_gateway
```

### 提供内容
- **ExternalConnectionContract**: 外部连接契约定义
- **请求 schema**: 请求数据结构规范
- **响应 schema**: 响应数据结构规范
- **错误分类**: 错误代码和分类

### 接口契约
- **输出**: 外部连接接口契约（frozen dataclass）
- **用途**: 为 Integration Gateway 提供路由和转换依据
- **约束**: 契约对象不可变

### 依赖方向
- Integration Gateway **依赖** Connector Contract
- Connector Contract **不依赖** Integration Gateway 实现
- 接口定义与实现解耦

## 旁路: Governor

### Permit 声明
```
connector_contract ← governor
```

### 声明内容
- **PermitRequirementDeclaration**: permit 需求声明
- **Permit 类型列表**: 声明需要的 permit 类型
- **用途说明**: 声明 permit 使用场景

### 接口契约
- **输入**: Governor 定义的 permit 类型
- **输出**: PermitRequirementDeclaration（声明，不生成）
- **约束**: 不生成 permit，只声明需求

### 引用规则
- Connector Contract **引用** Governor 定义的 permit 类型
- **不定义** 新的 permit 类型
- **不生成** permit 实例

## 引用: Evidence/AuditPack

### 引用声明
```
connector_contract → evidence/audit_pack
```

### 声明内容
- **EvidenceReferenceDeclaration**: evidence 引用声明
- **访问模式**: read/upload/notify
- **用途说明**: 引用用途声明

### 接口契约
- **输入**: 内核生成的 Evidence/AuditPack 类型
- **输出**: EvidenceReferenceDeclaration（引用声明）
- **约束**: 只引用，不修改

### 只引用规则
- Connector Contract **只引用** Evidence/AuditPack 类型
- **不生成** 新的 Evidence/AuditPack
- **不修改** 引用的 Evidence/AuditPack

## 类型定义文件
- [types.py](./types.py) - 契约类型定义（从 contracts/connector_contract/ 导出）

## 导出规则
- 所有契约类型从 `skillforge.src.contracts.connector_contract` 导出
- `skillforge.src.connector_contract` 重新导出这些类型
- 保持向后兼容性
