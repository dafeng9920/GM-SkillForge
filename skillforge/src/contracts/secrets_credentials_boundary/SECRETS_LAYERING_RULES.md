# Secrets 分层规则

## 分层定义

### 敏感级别 L0-L4

| 级别 | 名称 | 定义 | 示例 | 边界要求 |
|------|------|------|------|---------|
| L0 | 公开 | 无敏感信息 | 用户名、应用名称 | 无边界要求 |
| L1 | 内部公开 | 组织内部可见 | 内部 API 端点 | 不得泄露到外部 |
| L2 | 敏感 | 需要访问控制 | 内部服务账号密钥 | 不得进入日志 |
| L3 | 高敏感 | 需要严格访问控制 | 第三方 API Token | 不得进入 frozen，不得进入普通日志 |
| L4 | 机密 | 最高保护级别 | 生产根密钥、证书私钥 | 不得进入 frozen，不得进入任何日志，仅限专用通道 |

## 分层规则

### L0 - 公开信息

**特征：**
- 可以安全地写入任何位置
- 可以出现在 frozen 对象中
- 可以出现在日志中
- 可以对外分享

**示例：**
- `api_endpoint: "https://api.example.com"`
- `app_name: "my-app"`
- `environment: "production"`

**边界要求：** 无

### L1 - 内部公开信息

**特征：**
- 可以出现在 frozen 对象中
- 可以出现在内部日志中
- 不得对外泄露
- 不得写入公开文档

**示例：**
- `internal_api: "https://internal.company.com/api"`
- `service_account_name: "my-service@company.com"`

**边界要求：**
- ✅ 可进入 frozen 对象
- ✅ 可进入内部日志
- ❌ 不得对外泄露

### L2 - 敏感信息

**特征：**
- 不得进入 frozen 对象
- 不得进入普通日志
- 仅可进入审计日志（带访问控制）
- 仅限授权上下文使用

**示例：**
- 内部服务账号密钥
- 数据库连接凭证（非生产）
- 内部 API 密钥

**边界要求：**
- ❌ 不得进入 frozen 对象
- ❌ 不得进入普通日志
- ✅ 可进入审计日志（掩码或加密）
- ✅ 可在授权上下文中使用

### L3 - 高敏感信息

**特征：**
- 严格禁止进入 frozen 对象
- 严格禁止进入任何日志（包括审计日志）
- 仅限临时使用，立即清理
- 必须使用掩码记录

**示例：**
- 第三方服务 API Token（OpenAI, GitHub, etc.）
- 生产环境数据库凭证
- Webhook 签名密钥

**边界要求：**
- ❌ 严格禁止进入 frozen 对象
- ❌ 严格禁止进入任何日志
- ✅ 仅在临时上下文中使用
- ✅ 必须使用掩码：`sk-****`

### L4 - 机密信息

**特征：**
- 最高级别保护
- 仅限专用通道传递
- 禁止出现在任何代码中
- 禁止出现在任何配置中
- 仅限 HSM 或专用密钥管理服务

**示例：**
- 生产根 CA 私钥
- 证书签名密钥
- 加密主密钥

**边界要求：**
- ❌ 禁止进入 frozen 对象
- ❌ 禁止进入任何日志
- ❌ 禁止进入代码
- ❌ 禁止进入配置文件
- ✅ 仅限 HSM/专用 KMS

## 跨层传递规则

### 禁止跨层传递

```
❌ L3 → frozen 对象（任何形式）
❌ L4 → 代码/配置
❌ L3 → 日志（即使掩码也不行，除非是掩码规则定义的）
❌ L4 → 任何非专用通道
```

### 允许跨层传递（有条件）

```
✅ L3 → Integration Gateway（直接传递，不存储）
✅ L3 → 临时环境变量（立即读取后清理）
✅ L2 → 审计日志（加密或哈希）
```

## 降级规则

### 凭据可能降级的情况

| 原始级别 | 降级后 | 条件 |
|---------|-------|------|
| L3 | L0 | 凭据已过期/撤销，且不再敏感 |
| L3 | L1 | 凭据已轮换，旧凭据仅用于追溯 |
| L4 | L3 | 凭据用途从根密钥降级为普通密钥 |

**注意：** 降级只能由凭据所有者显式触发，不得自动降级。

## 升级规则

### 凭据可能升级的情况

| 原始级别 | 升级后 | 条件 |
|---------|-------|------|
| L2 | L3 | 凭据开始访问生产资源 |
| L1 | L2 | 凭据开始访问敏感资源 |
| L0 | L1 | 内部信息被标记为受控 |

**注意：** 升级需要重新评估边界要求。

## 分层验证

### 自动验证规则

```python
def validate_secrets_layering(context: dict) -> LayeringReport:
    """
    验证凭据使用是否符合分层规则
    """
    violations = []

    # L3 不得进入 frozen
    if context["credential_level"] >= 3 and "frozen" in context["targets"]:
        violations.append("L3+ credentials cannot enter frozen objects")

    # L4 不得进入任何日志
    if context["credential_level"] == 4 and "logging" in context["targets"]:
        violations.append("L4 credentials cannot enter any logs")

    # L3 不得进入普通日志
    if context["credential_level"] >= 3 and "logging" in context["targets"] and context["log_type"] != "audit":
        violations.append("L3+ credentials cannot enter regular logs")

    return LayeringReport(
        is_compliant=len(violations) == 0,
        violations=violations
    )
```

## 审查清单

### L3 凭据使用清单

- [ ] 凭据未进入 frozen 对象
- [ ] 凭据未进入日志
- [ ] 凭据使用后立即清理
- [ ] 凭据仅在授权上下文中使用
- [ ] 凭据使用时已记录掩码版本

### L4 凭据使用清单

- [ ] 凭据未进入代码
- [ ] 凭据未进入配置
- [ ] 凭据未进入 frozen 对象
- [ ] 凭据未进入任何日志
- [ ] 凭据仅通过专用通道（HSM/KMS）访问
- [ ] 凭据访问已记录到独立审计系统
