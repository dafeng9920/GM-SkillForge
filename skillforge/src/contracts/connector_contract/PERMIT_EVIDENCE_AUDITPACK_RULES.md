# Connector Contract - Permit/Evidence/AuditPack 引用规则

## 概述

本文档定义 Connector Contract 子面对 Permit、Evidence、AuditPack 的引用规则。

## 核心原则

1. **Permit 只声明不生成**
2. **Evidence 只读不修改**
3. **AuditPack 只读不重生成**
4. **所有引用必须显式声明**

## Permit 引用规则

### 1. Permit 声明（不生成）

```python
# ✅ 正确：声明需要的 permit 类型
@dataclass(frozen=True)
class ExternalConnectionContract:
    """外部连接接口契约"""
    required_permits: List[str]  # 声明需要的 permit

# 示例：Git 推送需要 permit
GIT_PUSH_CONTRACT = ExternalConnectionContract(
    connection_type="git",
    target="repository",
    required_permits=["external.git.push"],  # 只声明
)

# ❌ 错误：生成 permit
def create_permit(permit_type: str) -> Permit:
    return Permit(type=permit_type, status="allowed")  # 禁止！
```

### 2. Permit 前置检查规则

```python
# system_execution 层的 permit 检查
def verify_permit_precondition(contract: ExternalConnectionContract) -> bool:
    """
    验证 permit 前置条件

    注意：此函数在 system_execution 层实现，
    Connector Contract 只声明需要什么 permit。
    """
    for permit_type in contract.required_permits:
        if not permit_store.has_valid_permit(permit_type):
            return False
    return True
```

### 3. Permit 分类

| Permit 类型 | 用途 | 示例 |
|------------|------|------|
| `external.git.push` | Git 推送操作 | 推送代码到远程仓库 |
| `external.git.pull` | Git 拉取操作 | 从远程仓库拉取代码 |
| `external.webhook.notify` | Webhook 通知 | 发送构建结果通知 |
| `external.api.call` | 外部 API 调用 | 调用第三方服务 API |
| `external.registry.publish` | 发布到注册表 | 发布技能包到注册表 |
| `external.storage.upload` | 上传到存储 | 上传证据到外部存储 |

### 4. Permit 过期处理

```python
# ✅ 正确：检查过期后拒绝连接
def execute_with_permit_check(contract: ExternalConnectionContract):
    if not verify_permit_precondition(contract):
        raise PermitExpiredError("Permit 已过期或不存在")
    # 拒绝连接

# ❌ 错误：自动续期
def auto_renew_permit(permit_type: str):
    permit_store.renew(permit_type)  # 禁止自动续期！
```

## Evidence 引用规则

### 1. Evidence 只读引用

```python
# ✅ 正确：只读引用 Evidence
from skillforge.src.contracts.governance import evidence_ref

def prepare_evidence_for_external(evidence_id: str) -> Dict:
    """
    准备证据用于外部通知

    只读：不修改原始证据
    """
    evidence = evidence_ref.load(evidence_id)
    return {
        "evidence_id": evidence.evidence_id,
        "content": evidence.content,
        "timestamp": evidence.timestamp,
        "digest": evidence.digest,  # 用于验证完整性
    }

# ❌ 错误：修改 Evidence
def modify_evidence(evidence_id: str, changes: Dict):
    evidence = evidence_ref.load(evidence_id)
    evidence.content.update(changes)  # 禁止！
```

### 2. Evidence 搬运规则

```python
# ✅ 正确：搬运 Evidence 到外部系统
def upload_evidence_to_external(evidence_id: str, target: str):
    """
    搬运证据到外部系统

    规则：
    1. 只读加载
    2. 不修改
    3. 上传副本
    """
    evidence = evidence_ref.load(evidence_id)

    # 验证完整性
    if not verify_digest(evidence):
        raise EvidenceCorruptedError("证据已被篡改")

    # 上传到外部（搬运，不移动）
    external_system.upload(target, evidence.content)

    # 原始证据保持不变
```

### 3. Evidence 引用声明

```python
@dataclass(frozen=True)
class EvidenceReferenceDeclaration:
    """Evidence 引用声明"""
    evidence_type: str  # "gate_decision" | "validation_report" | "audit_pack"
    access_pattern: str  # "read" | "upload" | "notify"
    purpose: str

# Contract 中的声明
class WebhookNotifyContract:
    evidence_references = [
        EvidenceReferenceDeclaration(
            evidence_type="validation_report",
            access_pattern="read",
            purpose="读取验证结果用于通知"
        ),
    ]
```

## AuditPack 引用规则

### 1. AuditPack 只读引用

```python
# ✅ 正确：只读引用 AuditPack
from skillforge.src.contracts import audit_pack

def prepare_audit_for_external_archive(pack_id: str) -> Dict:
    """
    准备审计包用于外部归档

    只读：不修改原始审计包
    """
    pack = audit_pack.load_pack(pack_id)
    return {
        "pack_id": pack.pack_id,
        "manifest": pack.manifest,
        "digest": pack.digest,
        "items": pack.items,  # 只读引用
    }

# ❌ 错误：修改 AuditPack
def modify_audit_pack(pack_id: str, new_items: List):
    pack = audit_pack.load_pack(pack_id)
    pack.items = new_items  # 禁止！
```

### 2. AuditPack 归档规则

```python
# ✅ 正确：归档 AuditPack 到外部系统
def archive_audit_pack(pack_id: str, archive_target: str):
    """
    归档审计包到外部系统

    规则：
    1. 只读加载
    2. 验证完整性
    3. 归档副本
    """
    pack = audit_pack.load_pack(pack_id)

    # 验证完整性
    if not audit_pack.verify_digest(pack):
        raise AuditPackCorruptedError("审计包已被篡改")

    # 归档到外部（归档副本）
    archive_system.store(archive_target, pack)

    # 原始审计包保持不变
```

### 3. AuditPack 重新生成禁止

```python
# ❌ 错误：重新生成 AuditPack
def regenerate_audit_pack(pack_id: str, new_data: Dict):
    """
    禁止重新生成审计包
    """
    pack = audit_pack.load_pack(pack_id)
    pack.manifest = new_data  # 禁止！
    pack.digest = calculate_new_digest(new_data)  # 禁止！
```

## 综合引用示例

### 场景：Webhook 通知带证据

```python
# ✅ 正确：只读引用 Evidence 进行通知
def send_webhook_with_evidence(
    webhook_url: str,
    evidence_id: str,
    permit: Permit
):
    """
    发送 Webhook 通知（带证据）

    流程：
    1. 检查 permit
    2. 只读加载 Evidence
    3. 发送通知
    """
    # 1. 检查 permit
    if not permit.is_valid("external.webhook.notify"):
        raise PermitMissingError("缺少 Webhook 通知许可")

    # 2. 只读加载 Evidence
    evidence = evidence_ref.load(evidence_id)

    # 3. 准备通知负载
    payload = {
        "event": "validation_completed",
        "evidence": {
            "id": evidence.evidence_id,
            "content": evidence.content,
            "timestamp": evidence.timestamp,
        },
    }

    # 4. 发送通知（由 Integration Gateway 执行）
    # webhook_gateway.send(webhook_url, payload)
```

### 场景：外部归档审计包

```python
# ✅ 正确：只读引用 AuditPack 进行归档
def archive_audit_pack_to_external(
    pack_id: str,
    archive_target: str,
    permit: Permit
):
    """
    归档审计包到外部系统

    流程：
    1. 检查 permit
    2. 只读加载 AuditPack
    3. 归档到外部
    """
    # 1. 检查 permit
    if not permit.is_valid("external.storage.archive"):
        raise PermitMissingError("缺少归档许可")

    # 2. 只读加载 AuditPack
    pack = audit_pack.load_pack(pack_id)

    # 3. 验证完整性
    if not audit_pack.verify_digest(pack):
        raise AuditPackCorruptedError("审计包已被篡改")

    # 4. 归档到外部（由 Integration Gateway 执行）
    # archive_gateway.store(archive_target, pack)
```

## 禁止行为清单

| 行为 | 是否允许 | 理由 |
|------|---------|------|
| 声明需要的 permit 类型 | ✅ 允许 | 前置条件声明 |
| 检查 permit 是否存在 | ✅ 允许 | 前置条件验证 |
| 生成 permit | ❌ 禁止 | Governor 职责 |
| 续期 permit | ❌ 禁止 | Governor 职责 |
| 只读加载 Evidence | ✅ 允许 | 引用证据 |
| 上传 Evidence 副本 | ✅ 允许 | 搬运证据 |
| 修改 Evidence | ❌ 禁止 | 破坏证据完整性 |
| 重新生成 Evidence | ❌ 禁止 | 内核生成，外部不可改 |
| 只读加载 AuditPack | ✅ 允许 | 引用审计包 |
| 归档 AuditPack 副本 | ✅ 允许 | 归档审计 |
| 修改 AuditPack | ❌ 禁止 | 破坏审计完整性 |
| 重新生成 AuditPack | ❌ 禁止 | 内核生成，外部不可改 |

## 硬约束总结

1. **Permit 只声明不生成**
2. **Evidence 只读不修改**
3. **AuditPack 只读不重生成**
4. **所有引用必须显式声明**
5. **完整性验证强制执行**
6. **任何修改原始治理对象的行为直接 FAIL**
