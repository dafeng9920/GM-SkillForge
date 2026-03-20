# Permit 与 Credentials 使用边界说明

## 核心原则

**Permit 与 Credentials 是两个独立的概念，不能互相替代。**

## 定义对比

### Permit（许可）

| 属性 | 值 |
|------|-----|
| 定义 | 治理层授权执行某操作的许可 |
| 来源 | Governor / Gate Decision / Release Decision |
| 作用 | 证明"允许执行" |
| 生命周期 | 与治理流程绑定 |
| 敏感级别 | L0（公开） |
| 可否进入 frozen | ✅ 是 |
| 可否进入日志 | ✅ 是 |
| 示例 | `external.action.execute` permit |

### Credentials（凭据）

| 属性 | 值 |
|------|-----|
| 定义 | 访问外部系统所需的认证信息 |
| 来源 | 外部系统颁发 / 用户配置 |
| 作用 | 证明"有权访问" |
| 生命周期 | 与外部系统绑定 |
| 敏感级别 | L2-L4（敏感到机密） |
| 可否进入 frozen | ❌ 否 |
| 可否进入日志 | ❌ 否 |
| 示例 | API Token, SSH Key, Password |

## 关系图

```
外部执行请求
    │
    ├─ 需要 Permit（治理许可）
    │   └─ "允许执行此操作"
    │   └─ 来源：GateDecision / ReleaseDecision
    │   └─ 可进入 frozen，可记录
    │
    └─ 需要 Credentials（访问凭据）
        └─ "有权访问目标系统"
        └─ 来源：外部系统 / 用户配置
        └─ 不得进入 frozen，不得记录
```

## 使用边界

### Permit 边界

**✅ Permit 可以：**
- 进入 frozen 对象
- 进入日志
- 公开引用（如 `permit_id: "external.action.execute"`）
- 跨环境传递
- 存储在配置中
- 版本控制

**❌ Permit 不能：**
- 替代 Credentials（凭据是外部系统要求，不是治理许可）
- 被绕过（无 permit 不得执行外部动作）

### Credentials 边界

**✅ Credentials 可以：**
- 在临时上下文中使用（调用外部 API）
- 通过掩码出现在日志中
- 存储在专用密钥管理系统中

**❌ Credentials 不能：**
- 进入 frozen 对象
- 进入日志（未掩码）
- 进入配置文件（除非是加密的专用配置）
- 进入版本控制
- 替代 Permit（有凭据不代表有治理许可）

## 双重要求

### 外部执行必须同时满足

```
执行外部动作 = Permit（治理许可） + Credentials（访问凭据）
```

| 情况 | Permit | Credentials | 结果 |
|------|--------|-------------|------|
| 1 | ✅ | ✅ | ✅ 允许执行 |
| 2 | ✅ | ❌ | ❌ 拒绝（无凭据） |
| 3 | ❌ | ✅ | ❌ 拒绝（无许可） |
| 4 | ❌ | ❌ | ❌ 拒绝（两者皆无） |

### 错误理解

| 错误理解 | 正确理解 |
|---------|---------|
| "有凭据就能执行" | 凭据只解决"能访问"，不解决"允许执行" |
| "有许可就能执行" | 许可只解决"允许执行"，不解决"能访问" |
| "凭据就是许可" | 两者来源不同，作用不同，不能混同 |
| "许可存储在凭据中" | 许可来自治理层，凭据来自外部系统 |

## 审查规则

### Permit 审查

- [ ] Permit 来源是否可追溯（GateDecision / ReleaseDecision）
- [ ] Permit 类型是否匹配操作（`external.action.execute` 对应外部执行）
- [ ] Permit 是否有效（未过期、未撤销）

### Credentials 审查

- [ ] Credentials 是否未进入 frozen 对象
- [ ] Credentials 是否未进入日志（未掩码）
- [ ] Credentials 敏感级别是否正确标记
- [ ] Credentials 使用是否符合分层规则

### 两者关系审查

- [ ] 是否明确区分 Permit 和 Credentials
- [ ] 是否检查两者都存在
- [ ] 是否记录 Permit 引用，掩码 Credentials

## 示例代码

### 正确示例

```python
# 正确：明确区分 Permit 和 Credentials
def execute_external_action(action_type: str, permit: Permit, credential: Credential):
    # 1. 验证 Permit（治理许可）
    if not validate_permit(permit, action_type):
        raise PermissionDenied("Missing or invalid permit")

    # 2. 获取 Credentials（访问凭据）- 不进入 frozen
    credential_value = get_credential_from_secure_store(credential.type)

    # 3. 执行外部动作
    result = call_external_api(
        action_type=action_type,
        credential=credential_value,  # 临时使用
    )

    # 4. 清理凭据
    del credential_value

    # 5. 记录 Permit 引用，掩码凭据
    log_action(
        permit_id=permit.id,  # ✅ 可以记录
        credential_mask=mask_credential(credential.type)  # ✅ 掩码记录
    )

    return result
```

### 错误示例

```python
# 错误：凭据进入 frozen 对象
frozen_spec = {
    "external_action": {
        "permit": "external.action.execute",  # ✅ OK
        "credential": "sk-1234567890"  # ❌ 凭据下沉 frozen
    }
}

# 错误：混淆 Permit 和 Credentials
if credential:
    # 假设凭据就是许可
    execute()  # ❌ 有凭据不代表有许可

# 错误：凭据未掩码记录
log(
    permit_id=permit.id,
    credential_value=credential_value  # ❌ 凭据明文记录
)
```

## 合规检查

### 自动检查

```python
def check_permit_credential_separation(context: dict) -> ComplianceReport:
    """
    检查 Permit 和 Credentials 是否正确分离
    """
    violations = []

    # 检查凭据是否进入 frozen
    if context["has_credentials"] and "frozen" in context["targets"]:
        violations.append("Credentials cannot enter frozen objects")

    # 检查凭据是否明文记录
    if context["log_contains_credential"] and not context["credential_is_masked"]:
        violations.append("Credentials must be masked in logs")

    # 检查是否混淆 permit 和 credential
    if context["permit_used_as_credential"] or context["credential_used_as_permit"]:
        violations.append("Permit and Credentials are separate concepts")

    return ComplianceReport(
        is_compliant=len(violations) == 0,
        violations=violations
    )
```

## 违规后果

| 级别 | 行为 | 处理 |
|------|------|------|
| P0 | 凭据进入 frozen 对象 | REJECT |
| P0 | 凭据明文记录到日志 | REJECT |
| P1 | 混淆 Permit 和 Credentials | REVIEW |
| P1 | 凭据掩码不当 | REVIEW |
| P2 | Permit 未记录 | SUGGEST |
