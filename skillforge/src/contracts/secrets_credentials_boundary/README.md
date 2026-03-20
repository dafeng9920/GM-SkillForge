# Secrets / Credentials Boundary 子面

## 职责定义

### 核心职责

**Secrets/Credentials Boundary 只负责：**

1. **定义分层规则**
   - 声明 secrets 的敏感级别分类（L0-L4）
   - 定义各层级的访问边界
   - 定义跨层传递的禁止规则

2. **定义凭据边界**
   - 声明 credentials 的生命周期阶段
   - 定义凭据不得下沉进 frozen 主线的硬约束
   - 定义凭据销毁条件

3. **定义最小泄露防护**
   - 声明哪些操作禁止凭据进入日志
   - 定义凭据掩码规则
   - 定义异常情况下的凭据清理义务

4. **定义与 system_execution 的接口**
   - 声明凭据查询接口（不存储）
   - 定义凭据验证接口（不持久化）
   - 定义凭据临时使用的边界

### 明确的不负责项

**Secrets/Credentials Boundary 绝不负责：**

1. ❌ 不接入真实 secrets provider（AWS Secrets Manager、HashiCorp Vault 等）
2. ❌ 不存储真实凭据
3. ❌ 不实现凭据加密/解密
4. ❌ 不实现凭据轮换机制
5. ❌ 不管理凭据生命周期
6. ❌ 不实现访问控制策略
7. ❌ 不实现审计日志
8. ❌ 不实现凭据注入
9. ❌ 不实现运行时凭据缓存
10. ❌ 不扩展到 runtime 执行层

### 与 Frozen 主线的承接点

**禁止承接（硬约束）：**
- ❌ 任何 credentials / secrets 不得下沉进 frozen 主线
- ❌ frozen 对象不得包含凭据引用
- ❌ frozen 对象不得依赖外部凭据

**允许承接（只读）：**
- ✅ 读取 `normalized_skill_spec` 中的凭据需求声明
- ✅ 读取 `GateDecision` 中的许可标记
- ✅ 读取 `ReleaseDecision` 中的外部执行许可

**承接原则：**
1. frozen 主线永远不知道凭据存在
2. 凭据只在 system_execution 边界外存在
3. frozen 对象只标记"需要凭据X"，不存储凭据

### 与 System Execution 的接口关系

**接口调用方向：**
```
system_execution → Secrets Boundary: ✅ 查询凭据类型和掩码规则
Secrets Boundary → system_execution: ❌ 禁止主动推送凭据
```

**接口内容：**
- `get_credential_requirement(credential_type) -> CredentialRequirement`
- `get_masking_rule(credential_type) -> MaskingRule`
- `validate_boundary_compliance(context) -> ComplianceReport`

**不提供接口：**
- ❌ `get_credential_value()` - 不提供真实凭据值
- ❌ `store_credential()` - 不存储凭据
- ❌ `refresh_credential()` - 不轮换凭据

### 位置

```
skillforge/src/contracts/secrets_credentials_boundary/
```

### 后续扩展边界

**以下内容不属于本子面，需等待后续模块：**
- Runtime 凭据注入（由 Handler 层负责）
- 凭据轮换（由独立的 Secrets Management 模块负责）
- 凭据审计（由独立的 Audit 模块负责）
- 凭据缓存（由 Integration Gateway 负责）
