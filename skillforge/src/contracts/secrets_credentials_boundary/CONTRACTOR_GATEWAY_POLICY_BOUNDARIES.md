# Secrets/Credentials Boundary 与其他子面的边界说明

## 与 Connector Contract 的边界

### 职责划分

| Secrets/Credentials Boundary | Connector Contract |
|----------------------------|-------------------|
| 定义凭据敏感级别和分层规则 | 定义外部连接合同的输入/输出/约束 |
| 声明凭据不得进入 frozen | 声明连接契约不承载裁决 |
| 提供凭据掩码规则 | 提供连接接口规范 |

### 数据流向

```
Connector Contract ───只读──→ Secrets Boundary
     │                        │
     │                        └── 查询凭据类型规范
     │
     └── 外部连接合同定义中声明需要哪些凭据类型
         └── 示例: requires_credentials: ["api_token"]
```

### 禁止项

| 行为 | 说明 |
|------|------|
| ❌ Connector Contract 存储凭据值 | 凭据值不得进入连接契约 |
| ❌ Secrets Boundary 定义连接逻辑 | 连接逻辑由 Connector Contract 负责 |
| ❌ 互相调用对方内部接口 | 只通过规范文档进行边界约束 |

### 接口契约

**Connector Contract 可以引用：**
- `CredentialRequirement` - 凭据需求规范（类型、格式）
- `MaskingRule` - 掩码规则（用于日志记录）

**Connector Contract 不能获取：**
- 凭据实际值
- 加密后的凭据
- 凭据的存储位置

---

## 与 Integration Gateway 的边界

### 职责划分

| Secrets/Credentials Boundary | Integration Gateway |
|----------------------------|---------------------|
| 定义凭据分层规则 | 实现外部连接承接与转发 |
| 提供凭据查询接口（规范） | 使用凭据调用外部系统 |
| 不存储、不提供凭据值 | 临时使用凭据，立即清理 |
| 不实现缓存 | 可实现凭据缓存（运行时） |

### 数据流向

```
Integration Gateway ───查询──→ Secrets Boundary
     │                          │
     │                          └── get_credential_requirement()
     │                              get_masking_rule()
     │
     └── 从边界外获取凭据值
         └── 调用外部系统
         └── 立即清理凭据
         └── 记录掩码版本
```

### 凭据使用时机

| 阶段 | Secrets Boundary | Integration Gateway |
|------|-----------------|---------------------|
| 准备 | 定义凭据类型规范 | 读取规范，识别需求 |
| 获取 | 不参与 | 从边界外获取凭据值 |
| 使用 | 不参与 | 使用凭据调用外部系统 |
| 清理 | 不参与 | 立即清理内存中的凭据 |
| 记录 | 提供掩码规则 | 记录掩码后的凭据 |

### 禁止项

| 行为 | 说明 |
|------|------|
| ❌ Secrets Boundary 提供凭据值 | 只提供规范，不提供值 |
| ❌ Integration Gateway 存储凭据到 frozen | 凭据不得下沉 frozen |
| ❌ Integration Gateway 明文记录凭据 | 必须使用掩码 |

### 接口契约

**Integration Gateway 调用 Secrets Boundary：**
```python
# 查询凭据规范
requirement = secrets_boundary.get_credential_requirement("api_token")

# 查询掩码规则
masking_rule = secrets_boundary.get_masking_rule("api_token")

# 验证合规性
compliance = secrets_boundary.validate_boundary_compliance(context)
```

**Secrets Boundary 不提供：**
```python
# ❌ 禁止接口
value = secrets_boundary.get_credential_value("api_token")
secrets_boundary.store_credential("api_token", "sk-xxxx")
```

---

## 与 External Action Policy 的边界

### 职责划分

| Secrets/Credentials Boundary | External Action Policy |
|----------------------------|------------------------|
| 定义凭据敏感级别和边界 | 定义哪些外部动作必须持 permit |
| 声明凭据使用约束 | 声明动作执行策略 |
| 提供凭据掩码规则 | 定义 permit 校验规则 |
| 不参与动作执行判断 | 不参与凭据管理 |

### 独立性

**Secrets/Credentials Boundary 和 External Action Policy 是两个独立的维度：**

| 维度 | Secrets/Credentials Boundary | External Action Policy |
|------|----------------------------|------------------------|
| 关注点 | 凭据本身的敏感级别和使用边界 | 动作是否需要治理许可 |
| 判断依据 | 凭据类型（L0-L4） | 动作类型（关键/非关键）|
| 约束对象 | 凭据数据流 | 执行流程 |
| 示例 | L3 凭据不得进入 frozen | 发布动作必须持 permit |

### 双重要求

```
外部动作执行 = Permit 校验（Policy） + 凭据使用规则（Secrets Boundary）
```

| 场景 | Permit | 凭据规则 | 结果 |
|------|--------|---------|------|
| L3 凭据调用外部 API | ✅ 需要 | ❌ 不得进入 frozen | 双重约束 |
| L0 凭据查询操作 | ❌ 可豁免 | ✅ 无边界限制 | 只遵守凭据规则 |
| 发布动作（L3 凭据）| ✅ 需要 | ❌ 不得明文记录 | 双重约束 |

### 禁止项

| 行为 | 说明 |
|------|------|
| ❌ Policy 判断凭据敏感度 | 凭据敏感度由 Secrets Boundary 定义 |
| ❌ Secrets Boundary 判断动作是否需要 permit | Permit 需求由 Policy 定义 |
| ❌ 混淆两个边界 | 凭据规则 ≠ Permit 规则 |

---

## 与 System Execution 的边界

### 职责划分

| Secrets/Credentials Boundary | System Execution |
|----------------------------|------------------|
| 定义凭据规范和边界规则 | 使用凭据规范指导执行 |
| 提供查询接口（不提供值） | 从边界外获取凭据值 |
| 不参与实际执行 | 执行外部动作 |

### 接口调用方向

```
System Execution → Secrets Boundary: ✅ 查询
Secrets Boundary → System Execution: ❌ 禁止主动推送
```

### 接口清单

**System Execution 可以调用：**
- `get_credential_requirement(credential_type) -> CredentialRequirement`
- `get_masking_rule(credential_type) -> MaskingRule`
- `validate_boundary_compliance(context) -> ComplianceReport`

**Secrets Boundary 不提供：**
- `get_credential_value()` - 不提供凭据值
- `store_credential()` - 不存储凭据
- `refresh_credential()` - 不轮换凭据

---

## 跨子面协同场景

### 场景 1：外部 API 调用

```
1. System Execution 读取 normalized_skill_spec
   └─ spec 声明需要 api_token 凭据

2. System Execution 查询 Secrets Boundary
   └─ get_credential_requirement("api_token")
   └─ 返回: L3 敏感级别，sk-**** 掩码规则

3. System Execution 检查 External Action Policy
   └─ is_critical_action("call_external_api")
   └─ 返回: 需要 permit

4. System Execution 验证 permit 存在
   └─ ✅ permit 有效

5. System Execution 从边界外获取凭据值
   └─ 从环境变量/临时存储
   └─ Secrets Boundary 不参与

6. System Execution 调用 Integration Gateway
   └─ 传递凭据值（临时使用）
   └─ Integration Gateway 调用 Connector Contract 接口

7. 调用完成，清理凭据
   └─ Integration Gateway 立即清理内存

8. 记录日志
   └─ 使用掩码规则: sk-****
```

### 场景 2：发布技能

```
1. External Action Policy 判断
   └─ PUBLISH_LISTING 是关键动作
   └─ 需要 permit

2. System Execution 验证 permit
   └─ ✅ permit 有效

3. System Execution 查询 Secrets Boundary
   └─ 发布需要哪些凭据？
   └─ 返回: 可能需要 deployment_key（L3）

4. 获取凭据值
   └─ 从边界外获取
   └─ 立即使用

5. 调用发布接口
   └─ 通过 Integration Gateway
   └─ 使用 Connector Contract 定义的接口

6. 清理和记录
   └─ 清理凭据
   └─ 记录掩码版本
```

---

## 违规检测

### 自动检测规则

| 检测项 | 规则 | 违规级别 |
|--------|------|---------|
| Connector Contract 包含凭据值 | 不得包含 `token`、`secret` 等字段值 | P0 |
| Integration Gateway 存储凭据到 frozen | 凭据不得进入 frozen 对象 | P0 |
| Integration Gateway 明文记录凭据 | 日志中必须使用掩码 | P0 |
| Policy 判断凭据敏感度 | 凭据敏感度由 Secrets Boundary 定义 | P1 |
| Secrets Boundary 提供 permit 判断 | Permit 判断由 Policy 负责 | P1 |

### 边界交叉检查

```python
def check_boundary_crossing(context: dict) -> BoundaryReport:
    """
    检查是否有子面之间的边界交叉
    """
    violations = []

    # 检查 Connector Contract 是否包含凭据值
    if "connector_contract" in context and "credential_value" in context["connector_contract"]:
        violations.append("Connector Contract cannot contain credential values")

    # 检查 Integration Gateway 是否试图存储凭据
    if "integration_gateway" in context and "store_credential" in context["integration_gateway"]:
        violations.append("Integration Gateway cannot store credentials")

    # 检查 Policy 是否试图定义凭据规则
    if "action_policy" in context and "credential_level" in context["action_policy"]:
        violations.append("Policy should not define credential levels")

    return BoundaryReport(
        is_compliant=len(violations) == 0,
        violations=violations
    )
```

---

## 总结

### Secrets/Credentials Boundary 的定位

| 维度 | 定位 |
|------|------|
| 与 Connector Contract | 规范提供者 |
| 与 Integration Gateway | 规范提供者，不参与执行 |
| 与 External Action Policy | 独立维度，不交叉 |
| 与 System Execution | 规范查询接口 |

### 核心原则

1. **只提供规范，不提供值**
2. **只定义边界，不实现功能**
3. **只读承接，不修改 frozen**
4. **独立于 Policy，各司其职**
