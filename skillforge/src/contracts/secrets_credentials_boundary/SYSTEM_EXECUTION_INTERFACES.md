# System Execution 接口关系 - Secrets/Credentials Boundary

## 接口调用方向

```
system_execution → Secrets Boundary: ✅ 允许
Secrets Boundary → system_execution: ❌ 禁止
```

## 提供的接口

### 1. 查询凭据需求

```python
def get_credential_requirement(credential_type: str) -> CredentialRequirement:
    """
    查询指定类型的凭据需求规范

    返回凭据的类型定义、敏感级别、掩码规则等信息
    不返回真实凭据值
    """
```

**返回结构：**
```python
{
    "credential_type": "api_token",
    "sensitivity_level": "L3",  # 敏感级别
    "masking_pattern": "sk-****",  # 掩码模式
    "format_requirements": {
        "min_length": 20,
        "prefix": "sk-"
    },
    "allowed_contexts": ["external_api_call"],  # 允许使用的上下文
    "prohibited_contexts": ["logging", "frozen_object"]  # 禁止使用的上下文
}
```

### 2. 查询掩码规则

```python
def get_masking_rule(credential_type: str) -> MaskingRule:
    """
    查询凭据掩码规则

    用于日志、报告、调试信息中的凭据掩码
    """
```

**返回结构：**
```python
{
    "credential_type": "api_token",
    "mask_pattern": "sk-****",
    "show_first_n": 3,  # 显示前3个字符
    "show_last_n": 0,   # 不显示最后字符
    "mask_char": "*",   # 掩码字符
    "exception_contexts": ["audit_trace"]  # 特殊情况下允许完整记录的上下文
}
```

### 3. 验证边界合规性

```python
def validate_boundary_compliance(context: dict) -> ComplianceReport:
    """
    验证凭据使用是否符合边界规则

    检查凭据是否流入禁止的上下文（如 frozen 对象、日志）
    """
```

**返回结构：**
```python
{
    "is_compliant": True,
    "violations": [],
    "warnings": [
        {
            "type": "credential_near_frozen",
            "message": "凭据在距离 frozen 对象1层的作用域中被引用",
            "severity": "WARNING"
        }
    ]
}
```

## 不提供的接口

### ❌ 禁止接口

| 禁止接口 | 原因 |
|---------|------|
| `get_credential_value(type)` | Secrets Boundary 不存储凭据 |
| `store_credential(type, value)` | Secrets Boundary 不持久化凭据 |
| `refresh_credential(type)` | Secrets Boundary 不管理凭据生命周期 |
| `decrypt_credential(encrypted_value)` | Secrets Boundary 不处理加密 |
| `cache_credential(type, value)` | Secrets Boundary 不实现缓存 |
| `list_all_credentials()` | Secrets Boundary 不维护凭据清单 |

## 接口使用流程

### 典型流程：外部 API 调用

```
1. system_execution 读取 normalized_skill_spec
   └─ spec.external_actions.required_credentials = ["api_token"]

2. system_execution 调用 get_credential_requirement("api_token")
   └─ 获取凭据规范：需要 sk- 前缀，L3 敏感级别

3. system_execution 在边界外获取凭据值
   └─ 从环境变量/临时存储/用户输入获取
   └─ Secrets Boundary 不参与此步骤

4. system_execution 执行外部调用
   └─ 使用凭据值调用 Integration Gateway

5. 调用完成后，凭据值立即清理
   └─ 内存清理，不写入日志

6. 如需记录，调用 get_masking_rule()
   └─ 记录掩码后的凭据：sk-****
```

## Service 层扩展

### system_execution/service 层新增方法

```python
# 在 system_execution/service 中添加
class CredentialBoundaryService:
    def check_credential_requirement(self, credential_type: str) -> CredentialRequirement:
        """检查凭据需求规范"""
        return self.boundary.get_credential_requirement(credential_type)

    def mask_credential_for_logging(self, credential_type: str, value: str) -> str:
        """为日志掩码凭据"""
        rule = self.boundary.get_masking_rule(credential_type)
        return apply_masking(value, rule)

    def validate_usage_context(self, credential_type: str, context: str) -> bool:
        """验证凭据使用上下文是否合法"""
        requirement = self.boundary.get_credential_requirement(credential_type)
        return context in requirement["allowed_contexts"]
```

## 边界规则

### 凭据与 frozen 的距离规则

**规则：凭据值与 frozen 对象之间至少隔离 2 层作用域**

```
✅ 合法：
frozen_object → system_execution → external_context(credential)

❌ 非法：
frozen_object → credential_reference
frozen_object.handler → credential_reference
```

### 凭据生命周期规则

| 阶段 | 位置 | 时长 |
|------|------|------|
| 需求声明 | frozen 对象 | 永久 |
| 获取凭据 | system_execution 边界外 | 临时 |
| 使用凭据 | Integration Gateway | 即时 |
| 清理凭据 | 内存清理 | 立即 |
| 记录凭据 | 日志（掩码） | 永久 |

### 凭据传递规则

```
✅ 允许：
- 环境变量 → system_execution（一次性读取）
- 临时输入 → Integration Gateway（直接传递）
- 掩码凭据 → 日志/报告

❌ 禁止：
- 凭据 → frozen 对象
- 凭据 → 数据库
- 凭据 → 配置文件
- 凭据 → 版本控制
- 凭据 → 未经掩码的日志
```
