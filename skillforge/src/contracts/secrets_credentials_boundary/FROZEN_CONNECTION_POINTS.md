# Frozen 主线承接点规则 - Secrets/Credentials Boundary

## 核心原则

**凭据永远不下沉进 frozen 主线。**

## 禁止承接（硬约束）

### ❌ 禁止项

| 禁止内容 | 原因 | 后果 |
|---------|------|------|
| 凭据下沉 frozen | frozen 对象应是纯声明，不携带敏感信息 | REJECT |
| frozen 对象引用凭据 | 破坏 frozen 的可审查性 | REJECT |
| frozen 对象包含凭据哈希 | 哈希也可被用于暴力破解 | REJECT |
| frozen 对象包含凭据元数据 | 元数据可能泄露凭据类型和用途 | REVIEW |

## 允许承接（只读）

### ✅ Frozen 对象只读访问

| Frozen 对象 | 用途 | 访问方式 |
|------------|------|---------|
| `normalized_skill_spec` | 读取凭据需求声明（如 `requires_credentials: ["api_token"]`） | 只读字符串 |
| `GateDecision` | 读取外部执行许可标记 | 只读布尔值 |
| `ReleaseDecision` | 读取发布许可 | 只读布尔值 |

### 承接原则

1. **需求声明与凭据分离**
   - frozen 对象只声明"需要凭据X"
   - 凭据值在 system_execution 边界外获取
   - 凭据永不进入 frozen 对象

2. **引用方式**
   - 使用字符串标识符引用凭据类型
   - 不存储凭据值、哈希、或加密版本
   - 示例：`credential_type: "external_api_token"` ✅
   - 反例：`credential_token: "sk-xxxx"` ❌

3. **生命周期分离**
   - frozen 对象生命周期：永久可审查
   - 凭据生命周期：临时、可轮换、可撤销
   - 两者不得绑定

## Frozen 对象中的凭据声明模式

### ✅ 正确模式

```python
# normalized_skill_spec 中的正确声明
{
    "external_actions": {
        "required_credentials": [
            {
                "type": "api_token",
                "purpose": "external_api_auth",
                "level": "L3"
            }
        ]
    }
}
```

### ❌ 错误模式

```python
# 错误：包含凭据值
{
    "external_actions": {
        "credentials": {
            "api_token": "sk-1234567890"  # ❌ 凭据下沉
        }
    }
}

# 错误：包含凭据哈希
{
    "external_actions": {
        "credentials": {
            "api_token_hash": "a1b2c3d4..."  # ❌ 哈希也可能泄露
        }
    }
}

# 错误：包含加密凭据
{
    "external_actions": {
        "credentials": {
            "api_token_encrypted": "U2FsdGVkX1..."  # ❌ 加密数据也不得下沉
        }
    }
}
```

## 承接时序

### 静态声明阶段（Frozen）

1. `normalized_skill_spec` 定义：需要哪些类型的凭据
2. 凭据类型标识符写入 spec（如 "api_token"）
3. spec 进入 frozen 主线，可被审查

### 动态使用阶段（System Execution）

1. system_execution 读取 spec，识别凭据需求
2. system_execution 在边界外获取凭据值（不进入 frozen）
3. 凭据值用于外部调用，调用后立即清理
4. frozen 对象永不接触凭据值

## 验证规则

### 自动检查

- ❌ frozen 对象中不得出现 `credential`、`token`、`secret`、`password`、`key` 等敏感字段值
- ❌ frozen 对象中不得出现 Base64 编码的凭据
- ❌ frozen 对象中不得出现加密字符串

### 人工审查

- frozen 对象的可审查性：任何人可以安全地审查 frozen 对象而不接触敏感信息
- frozen 对象的可复制性：frozen 对象可以安全地复制到任何环境

## 违规后果

| 级别 | 行为 | 处理 |
|------|------|------|
| P0 | 凭据值下沉 frozen | REJECT，必须移除 |
| P1 | 凭据哈希/加密数据下沉 | REJECT，必须移除 |
| P2 | 凭据元数据过度详细 | REVIEW，建议简化 |
