# Connector Contract - Frozen 主线承接点

## 概述

本文档定义 Connector Contract 子面与 Frozen 主线的承接点规则。

## Frozen 对象承接原则

### 1. 只读承接
- 所有 frozen 对象只能以只读方式访问
- 不允许任何形式的回写
- 不允许通过反射修改私有属性

### 2. 显式声明
- 所有 frozen 依赖必须在 contract 中显式声明
- 隐式依赖视为违规

### 3. 公开接口
- 只能访问 frozen 对象的公开接口
- 不访问内部实现细节

## Frozen 承接点清单

### Governance 对象承接点

| Frozen 对象 | 承接方式 | 用途 | 是否只读 |
|------------|---------|------|---------|
| `normalized_skill_spec` | 引用 skill_id | 获取技能规范用于外部注册 | ✅ 是 |
| `GateDecision` | 引用 decision_id | 验证裁决前置条件 | ✅ 是 |
| `EvidenceRef` | 引用 evidence_path | 读取证据用于外部通知 | ✅ 是 |
| `AuditPack` | 引用 pack_id | 读取审计包用于外部归档 | ✅ 是 |
| `ReleaseDecision` | 引用 release_id | 验证发布许可 | ✅ 是 |

### Contract 对象承接点

| Frozen 对象 | 承接方式 | 用途 | 是否只读 |
|------------|---------|------|---------|
| `intake_request` | 引用 request_id | 获取原始请求上下文 | ✅ 是 |
| `validation_report` | 引用 report_id | 获取验证结果 | ✅ 是 |
| `adjudication_report` | 引用 report_id | 获取裁决结果 | ✅ 是 |
| `coverage_statement` | 引用 statement_id | 获取覆盖声明 | ✅ 是 |

## Frozen 承接关系详解

### 1. 承接时序

**静态声明阶段（Contract 定义时）：**
- frozen_dependencies 在 Contract 定义时静态声明
- 声明使用 FrozenDependencyDeclaration 结构
- 声明包含 module 字符串路径（如 "skillforge.src.contracts.normalized_skill_spec"）

**动态读取阶段（system_execution 查询时）：**
- system_execution 调用 get_connection_contract() 获取契约
- Integration Gateway 在执行时动态读取 frozen 对象
- Connector Contract 不负责读取，只负责声明

```python
# 静态声明（Contract 定义时）
CONTRACT = ExternalConnectionContract(
    frozen_dependencies=[
        FrozenDependencyDeclaration(
            frozen_module="skillforge.src.contracts.normalized_skill_spec",
            frozen_object_type="NormalizedSkillSpec",
            access_pattern="read",
            purpose="获取技能规范用于外部注册"
        ),
    ],
)

# 动态读取（Integration Gateway 执行时）
# system_execution/handler/gateway 负责读取，不在 Connector Contract 层
```

### 2. 引用方式

**Contract 定义层（静态声明）：**
- 使用 module 字符串路径（如 "skillforge.src.contracts.normalized_skill_spec"）
- 不直接导入 frozen 模块
- 不存储 frozen 对象实例

**Integration Gateway 层（动态读取）：**
- 根据 module 字符串动态导入
- 读取时验证对象完整性
- 读取后不缓存可变引用

```python
# ✅ 正确：Contract 定义层使用字符串声明
FrozenDependencyDeclaration(
    frozen_module="skillforge.src.contracts.normalized_skill_spec",  # 字符串
    frozen_object_type="NormalizedSkillSpec",
)

# ❌ 错误：Contract 定义层直接导入
import skillforge.src.contracts.normalized_skill_spec as spec  # 禁止！
```

### 3. 生命周期

**Contract 生命周期：**
- Contract 对象在系统启动时创建（单例）
- Contract 对象不可变 (frozen=True)
- Contract 对象不缓存 frozen 对象实例

**Frozen 对象读取生命周期：**
- 每次执行时动态读取 frozen 对象
- 读取后验证完整性（digest 校验）
- 执行完成后不保留引用

**Frozen 对象更新处理：**
- 如果 frozen 对象被更新，Contract 定义不受影响
- 下次执行时读取新的 frozen 对象版本
- Contract 不需要重新加载

```python
# Contract 定义（系统启动时，单例，不可变）
GIT_CONTRACT = ExternalConnectionContract(...)  # frozen=True

# Integration Gateway 执行时（每次动态读取）
def execute_with_contract(contract: ExternalConnectionContract):
    for dep in contract.frozen_dependencies:
        # 每次动态读取，不缓存
        frozen_obj = import_and_read(dep.module)
        # 验证完整性
        verify_integrity(frozen_obj)
        # 使用后丢弃引用
```

## 承接点使用规范

### 1. normalized_skill_spec 承接
```python
# ✅ 正确：只读引用
from skillforge.src.contracts import normalized_skill_spec

def get_skill_for_registration(skill_id: str) -> Optional[Dict]:
    """获取技能规范用于外部注册"""
    spec = normalized_skill_spec.get_spec(skill_id)
    return {
        "skill_id": spec.skill_id,
        "name": spec.name,
        "version": spec.version,
        # 不包含内部实现细节
    }

# ❌ 错误：修改 spec
def modify_skill_spec(skill_id: str, changes: Dict):
    spec = normalized_skill_spec.get_spec(skill_id)
    spec.update(changes)  # 禁止！
```

### 2. GateDecision 承接
```python
# ✅ 正确：只读验证
from skillforge.src.contracts.governance import gate_decision_envelope

def verify_gate_precondition(gate_id: str) -> bool:
    """验证 gate 前置条件"""
    decision = gate_decision_envelope.load_decision(gate_id)
    return decision.decision == "PASS"

# ❌ 错误：修改 decision
def override_gate_decision(gate_id: str, new_decision: str):
    decision = gate_decision_envelope.load_decision(gate_id)
    decision.decision = new_decision  # 禁止！
```

### 3. EvidenceRef 承接
```python
# ✅ 正确：只读搬运
from skillforge.src.contracts.governance import evidence_ref

def prepare_evidence_for_notification(evidence_id: str) -> Dict:
    """准备证据用于外部通知"""
    evidence = evidence_ref.load(evidence_id)
    return {
        "evidence_id": evidence.evidence_id,
        "content": evidence.content,
        "timestamp": evidence.timestamp,
    }

# ❌ 错误：修改 evidence
def alter_evidence(evidence_id: str, alterations: Dict):
    evidence = evidence_ref.load(evidence_id)
    evidence.content.update(alterations)  # 禁止！
```

### 4. AuditPack 承接
```python
# ✅ 正确：只读归档
from skillforge.src.contracts import audit_pack

def prepare_audit_for_archive(pack_id: str) -> Dict:
    """准备审计包用于外部归档"""
    pack = audit_pack.load_pack(pack_id)
    return {
        "pack_id": pack.pack_id,
        "manifest": pack.manifest,
        "digest": pack.digest,
    }

# ❌ 错误：重新生成 pack
def regenerate_audit_pack(pack_id: str, new_data: Dict):
    pack = audit_pack.load_pack(pack_id)
    pack.manifest = new_data  # 禁止！
```

## 依赖声明格式

### Contract 中的依赖声明
```python
@dataclass(frozen=True)
class FrozenDependencyDeclaration:
    """Frozen 依赖声明"""

    frozen_module: str
    frozen_object_type: str
    access_pattern: str  # "read" | "reference" | "query"
    purpose: str

# 示例
DEPENDENCIES = [
    FrozenDependencyDeclaration(
        frozen_module="skillforge.src.contracts.normalized_skill_spec",
        frozen_object_type="NormalizedSkillSpec",
        access_pattern="read",
        purpose="获取技能规范用于外部注册"
    ),
    FrozenDependencyDeclaration(
        frozen_module="skillforge.src.contracts.governance.gate_decision_envelope",
        frozen_object_type="GateDecision",
        access_pattern="read",
        purpose="验证裁决前置条件"
    ),
]
```

## 违规检测规则

### 1. 隐式依赖检测
- 如果 contract 使用了未声明的 frozen 对象 → 违规
- 如果 contract 访问了私有属性 → 违规

### 2. 写操作检测
- 如果 contract 调用了 frozen 对象的写方法 → 违规
- 如果 contract 修改了 frozen 对象的属性 → 违规

### 3. 生命周期检测
- 如果 contract 缓存了 frozen 对象的可变引用 → 违规
- 如果 contract 在 frozen 对象变更后未刷新缓存 → 违规

## 硬约束

1. **所有 frozen 依赖必须显式声明**
2. **所有访问必须是只读的**
3. **不得缓存 frozen 对象的可变引用**
4. **不得修改 frozen 对象的任何属性**
5. **不得调用 frozen 对象的写方法**
