# Node Registry 与身份校验实现报告 (ISSUE-06 / T07)

> **版本**: v1.0
> **状态**: P0 完成
> **创建**: 2026-02-26
> **Executor**: vs--cc2
> **关联 Issue**: ISSUE-06 (P0-10-issue-任务清单.md)

---

## 1. 概述

本文档记录 GM-SkillForge 系统的 **Node Registry（节点注册表）** 实现，确保：

1. 建立 `node_id -> pubkey/cert/status` 的中央注册表
2. 未知节点或失效节点全部**拒绝（NODE_UNTRUSTED）**
3. 与 T05 Ed25519 签名模块集成，支持公钥存储与验签
4. Fail-closed 默认行为：未注册节点一律不信任

---

## 2. ISSUE-06 验收标准映射

| 验收标准 | 实现状态 | 证据 |
|---------|---------|------|
| 建立 `node_id -> pubkey/cert/status` 注册表 | ✅ 完成 | `NodeRegistry` 类 |
| registry 读取层 | ✅ 完成 | `get_node()`, `get_public_key()`, `list_nodes()` |
| NODE_UNTRUSTED 裁决 | ✅ 完成 | `verify_node_trust()` 返回错误码 |
| 未知节点全部拒绝 | ✅ 完成 | Fail-closed 模式下默认拒绝 |
| 失效节点全部拒绝 | ✅ 完成 | DISABLED/REVOKED 状态拒绝 |

---

## 3. 实现详情

### 3.1 核心模块：`node_registry.py`

**文件位置**: `skillforge-spec-pack/skillforge/src/utils/node_registry.py`

#### 主要类和函数

| 类型 | 名称 | 用途 |
|-----|------|------|
| `class` | `NodeRegistry` | 中央节点注册表 |
| `class` | `NodeInfo` | 节点信息数据类 |
| `class` | `TrustDecision` | 信任验证结果 |
| `enum` | `NodeStatus` | 节点状态 (ACTIVE/DISABLED/REVOKED/PENDING) |
| `enum` | `NodeRegistryError` | 错误码枚举 |

### 3.2 数据结构

#### NodeInfo（节点信息）

```python
@dataclass
class NodeInfo:
    node_id: str                    # 节点唯一标识
    public_key_hex: str             # Ed25519 公钥（64 hex 字符）
    status: NodeStatus              # 节点状态
    registered_at: str              # 注册时间戳
    last_seen_at: str               # 最后活跃时间戳
    cert_fingerprint: Optional[str] # 证书指纹（可选）
    metadata: Dict                  # 元数据字典
```

#### NodeStatus（节点状态）

| 状态 | 含义 | 是否信任 |
|-----|------|---------|
| `ACTIVE` | 激活状态 | ✅ 信任 |
| `DISABLED` | 已禁用 | ❌ 拒绝 (NODE_DISABLED) |
| `REVOKED` | 已撤销 | ❌ 拒绝 (NODE_UNTRUSTED) |
| `PENDING` | 待审核 | ❌ 拒绝 (除非 allow_pending=True) |

---

## 4. NODE_UNTRUSTED 拒绝策略

### 4.1 错误码定义

```python
class NodeRegistryError(str, Enum):
    NODE_UNTRUSTED = "NODE_UNTRUSTED"      # 节点不受信任（通用）
    NODE_NOT_FOUND = "NODE_NOT_FOUND"      # 节点未找到
    NODE_DISABLED = "NODE_DISABLED"        # 节点已禁用
    NODE_EXPIRED = "NODE_EXPIRED"          # 节点已过期
    INVALID_PUBLIC_KEY = "INVALID_PUBLIC_KEY"
    INVALID_NODE_ID = "INVALID_NODE_ID"
    REGISTRY_LOAD_ERROR = "REGISTRY_LOAD_ERROR"
    REGISTRY_SAVE_ERROR = "REGISTRY_SAVE_ERROR"
```

### 4.2 拒绝场景

| 场景 | 错误码 | HTTP 状态 | 示例 |
|-----|-------|----------|------|
| 未注册节点 | `NODE_UNTRUSTED` | 403 | `"node-999" not in registry` |
| 已禁用节点 | `NODE_DISABLED` | 403 | `"node-001" status=DISABLED` |
| 已撤销节点 | `NODE_UNTRUSTED` | 403 | `"node-002" status=REVOKED` |
| 待审核节点 | `NODE_UNTRUSTED` | 403 | `"node-003" status=PENDING` |

### 4.3 Fail-Closed 默认行为

```python
# 默认：Fail-Closed 模式（推荐）
registry = NodeRegistry(fail_closed=True)
decision = registry.verify_node_trust("unknown-node")
# 结果: is_trusted=False, error_code="NODE_UNTRUSTED"

# Fail-Open 模式（不推荐，仅用于测试）
registry = NodeRegistry(fail_closed=False)
decision = registry.verify_node_trust("unknown-node")
# 结果: is_trusted=True（危险！）
```

---

## 5. API 使用指南

### 5.1 基础用法

#### 注册节点

```python
from skillforge.src.utils.node_registry import NodeRegistry, NodeStatus

registry = NodeRegistry()

# 注册一个激活节点
node_info = registry.register_node(
    node_id="node-001",
    public_key_hex="a" * 64,  # Ed25519 公钥
    status=NodeStatus.ACTIVE,
    cert_fingerprint="abc123",
    metadata={"env": "production"}
)
```

#### 验证节点信任

```python
# 验证节点是否受信任
decision = registry.verify_node_trust("node-001")

if decision.is_trusted:
    # 继续处理请求（如验签）
    public_key = registry.get_public_key("node-001")
    # ... 使用公钥验签
else:
    # 拒绝请求
    return {
        "error": decision.error_code,
        "message": decision.error_message,
        "trace_id": trace_id
    }
```

#### 查询节点信息

```python
# 获取节点信息
node_info = registry.get_node("node-001")
print(node_info.node_id, node_info.status)

# 列出所有激活节点
active_nodes = registry.list_nodes(NodeStatus.ACTIVE)

# 获取公钥
public_key = registry.get_public_key("node-001")
```

### 5.2 状态管理

```python
# 禁用节点
registry.disable_node("node-001")

# 启用节点
registry.enable_node("node-001")

# 撤销节点（不可逆）
registry.revoke_node("node-001")

# 更新最后活跃时间
registry.update_last_seen("node-001")
```

### 5.3 持久化

```python
# 保存到磁盘
registry.save()

# 从磁盘重新加载
registry.reload()

# 指定自定义路径
registry = NodeRegistry(registry_path="db/my_registry.json")
```

### 5.4 与 T05 Ed25519 集成

```python
from skillforge.src.utils.ed25519_signature import (
    generate_keypair,
    verify_node_signature
)
from skillforge.src.utils.node_registry import NodeRegistry

# 1. 生成密钥对
keypair = generate_keypair()

# 2. 注册节点（存储公钥）
registry = NodeRegistry()
registry.register_node("node-001", keypair.public_key_hex)

# 3. 验证节点信任
decision = registry.verify_node_trust("node-001")
if not decision.is_trusted:
    raise Exception(f"NODE_UNTRUSTED: {decision.error_message}")

# 4. 获取公钥并验签
public_key_hex = registry.get_public_key("node-001")
# ... 使用 public_key_hex 验证签名
```

---

## 6. 与 T01 policy_check 集成

### 6.1 在 policy_check 中调用

```python
# skillforge/src/policy/checks.py

from skillforge.src.utils.node_registry import NodeRegistry, NodeRegistryError

# 全局单例
_registry = None

def get_registry() -> NodeRegistry:
    global _registry
    if _registry is None:
        _registry = NodeRegistry()
    return _registry

def check_node_registry(node_id: str) -> tuple[bool, str]:
    """
    Node Registry 校验（T07 实现）

    Returns:
        (is_valid, error_message)
    """
    registry = get_registry()
    decision = registry.verify_node_trust(node_id)

    if decision.is_trusted:
        return True, ""

    # Fail-Closed: 任何未信任节点均拒绝
    error_code = decision.error_code or NodeRegistryError.NODE_UNTRUSTED
    return False, f"{error_code}: {decision.error_message}"
```

### 6.2 在 policy_check 流程中的位置

```
┌─────────────────────────────────────────────────────────────┐
│                    policy_check() 流程                       │
├─────────────────────────────────────────────────────────────┤
│  1. Schema Validation                                        │
│  2. Signature Validation                                     │
│  3. Nonce/Challenge Validation                               │
│  4. Node Registry Validation  ← T07 实现                    │
│     └─ check_node_registry(node_id)                         │
│        └─ verify_node_trust()                               │
│           └─ NODE_UNTRUSTED → DENY (403)                    │
│  5. Constitution Rule Validation                            │
│  6. All Pass → ALLOW (200)                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. 测试覆盖

### 7.1 测试文件

**位置**: `skillforge-spec-pack/skillforge/tests/test_node_registry.py`

### 7.2 测试类统计

| 测试类 | 测试用例数 | 覆盖范围 |
|-------|----------|---------|
| `TestNodeInfo` | 3 | NodeInfo 数据类 |
| `TestNodeRegistryCreation` | 5 | 注册表创建 |
| `TestNodeRegistration` | 8 | 节点注册 |
| `TestNodeQuery` | 6 | 节点查询 |
| `TestTrustVerification` | 11 | 信任验证（核心） |
| `TestStatusManagement` | 8 | 状态管理 |
| `TestRegistryPersistence` | 5 | 持久化 |
| `TestUtilityMethods` | 5 | 工具方法 |
| `TestConvenienceFunctions` | 2 | 便捷函数 |
| `TestIntegrationWithEd25519` | 2 | 与 T05 集成 |
| `TestConstants` | 2 | 常量 |
| `TestErrorCodes` | 1 | 错误码 |

**总计**: **58 个测试用例**

### 7.3 关键测试场景

| 场景 | 测试函数 | 验证点 |
|-----|---------|--------|
| 未知节点拒绝 | `test_unknown_node_rejected_fail_closed` | `error_code == NODE_UNTRUSTED` |
| 已禁用节点拒绝 | `test_disabled_node_rejected` | `error_code == NODE_DISABLED` |
| 已撤销节点拒绝 | `test_revoked_node_rejected` | `error_code == NODE_UNTRUSTED` |
| 激活节点信任 | `test_trusted_active_node` | `is_trusted == True` |
| 公钥存储 | `test_store_ed25519_public_key` | Ed25519 公钥正确存储 |
| 持久化 | `test_save_and_load_registry` | 保存/加载正确 |

---

## 8. 与其他任务的集成

### 8.1 依赖关系

| 任务 | 依赖类型 | 集成点 |
|-----|---------|--------|
| **T01** | 依赖 | `check_node_registry()` 在 `policy_check()` 中调用 |
| **T05** | 依赖 | 存储 `public_key_hex` 用于验签 |
| **T02** | 依赖 | 无直接依赖，registry 使用 JSON 存储 |
| **T03** | 依赖 | 无直接依赖，registry 独立于 envelope 结构 |

### 8.2 下游任务解锁

| 任务 | 解锁内容 |
|-----|---------|
| **T08** | 可对回执进行节点签名验证 |
| **T09** | 协议测试可验证节点身份 |

---

## 9. 安全考虑

### 9.1 Fail-Closed 原则

- **默认行为**: 未注册节点一律拒绝
- **不可配置的 fail-open**: 仅用于测试，明确标记风险

### 9.2 公钥验证

- Ed25519 公钥必须是 64 字符的十六进制字符串
- 验证十六进制有效性，防止注入攻击

### 9.3 状态管理

- 撤销状态不可逆（REVOKED）
- 禁用状态可恢复（DISABLED <-> ACTIVE）
- 待审核状态需显式允许（PENDING + allow_pending=True）

---

## 10. 运行证据

### 10.1 自动化验收命令

```bash
# 检查文件存在
test -f skillforge-spec-pack/skillforge/src/utils/node_registry.py

# 检查测试文件存在
test -f skillforge-spec-pack/skillforge/tests/test_node_registry.py

# 检查 __init__.py 导出
rg "NodeRegistry" skillforge-spec-pack/skillforge/src/utils/__init__.py

# 运行测试（需要 pytest）
cd skillforge-spec-pack && python -m pytest tests/test_node_registry.py -v
```

### 10.2 关键证据

| 证据类型 | 文件路径 |
|---------|---------|
| 实现代码 | `skillforge-spec-pack/skillforge/src/utils/node_registry.py` |
| 测试代码 | `skillforge-spec-pack/skillforge/tests/test_node_registry.py` |
| 模块导出 | `skillforge-spec-pack/skillforge/src/utils/__init__.py` |
| 本报告 | `docs/2026-02-26/p0-governed-execution/verification/T07_registry_report.md` |

---

## 11. 附录

### 11.1 相关文档

- [EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md](../../2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md)
- [EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md](../../../EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md)
- [multi-ai-collaboration.md](../../../multi-ai-collaboration.md)
- [T01_policy_baseline.md](./T01_policy_baseline.md)
- [T05_signature_report.md](./T05_signature_report.md)

### 11.2 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|-----|------|---------|------|
| v1.0 | 2026-02-26 | 初始版本：Node Registry 实现完成 | vs--cc2 |

---

*Document created under T07 governance process: Review → Compliance → Execution*
*EvidenceRef: EV-T07-DELIVERABLE-001*
