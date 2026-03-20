# External Action Policy (E4 Deliverable)

**Task ID**: E4
**Executor**: Kior-B
**Status**: Framework Only - No Execution
**Date**: 2026-03-19

## Purpose

定义外部动作策略子面的最小准备骨架。

**硬约束**：
- 集成层只能搬运 Evidence / AuditPack，不可改写
- 不得越权触发真实外部动作
- 关键动作必须持 permit

## Scope

### 关键动作 vs 非关键动作

| 分类 | 定义 | Permit 要求 |
|------|------|-------------|
| **关键动作** | 产生外部副作用（发布/导出/替换/执行等） | 必须持有效 permit |
| **非关键动作** | 只读操作（查询/验证/读取） | 可豁免 permit |

### 关键动作列表

```python
CRITICAL_ACTIONS = [
    "PUBLISH_LISTING",       # 发布技能列表
    "EXECUTE_VIA_N8N",       # 通过 n8n 执行
    "EXPORT_WHITELIST",      # 导出白名单
    "UPGRADE_REPLACE_ACTIVE",# 升级替换活动技能
    "TRIGGER_EXTERNAL_CONNECTOR",  # 触发外部连接器
    "WRITE_EXTERNAL_STATE",  # 写入外部状态
]
```

## Permit 使用条件

### 1. Permit 校验点

```
System Execution -> Integration Gateway -> External Connector
                     |
                     v
              Permit Checkpoint
```

### 2. 校验规则

遵循 `permit_contract_v1.yml` + `gate_permit.py`：

**安全约束**：
- 关键动作集合不可变（模块级 `frozenset`）
- 未知动作默认阻断（安全优先）
- 禁止运行时修改关键动作列表

- **E001**: permit 缺失 -> PERMIT_REQUIRED
- **E002**: permit 格式无效 -> PERMIT_INVALID
- **E003**: 签名无效 -> PERMIT_INVALID
- **E004**: permit 过期 -> PERMIT_EXPIRED
- **E005**: scope 不匹配 -> PERMIT_SCOPE_MISMATCH
- **E006**: subject 不匹配 -> PERMIT_SUBJECT_MISMATCH
- **E007**: permit 已撤销 -> PERMIT_REVOKED

### 3. 错误处理

所有关键动作在 permit 校验失败时必须：

1. 阻断执行
2. 返回 `PERMIT_REQUIRED` 错误码
3. 记录 Evidence（失败记录）

## Evidence / AuditPack 引用规则

### 1. 只读搬运

```python
# 集成层只能搬运，不可改写
class IntegrationGateway:
    def transport(self, evidence_ref: EvidenceRef) -> EvidenceRef:
        # 只传递引用，不修改内容
        return evidence_ref  # Pass-through
```

### 2. AuditPack 完整性

- AuditPack 必须来自 `audit_pack.py` 生成的标准格式
- 集成层不得修改 AuditPack 内部数据
- 只能添加传输元数据（如 transport_timestamp）

### 3. Evidence 链路保护

```
Gate -> Evidence -> AuditPack -> Integration Gateway -> External
     (生成)     (聚合)          (搬运)
```

- 集成层不得断开 Evidence 链路
- 必须保持 `source_locator` 完整

## 不负责项

1. **不负责** permit 生成（Governance 层负责）
2. **不负责** Evidence 生成（Gate 层负责）
3. **不负责** AuditPack 生成（T14 负责）
4. **不负责** 外部动作真实执行（External Connector 负责）
5. **不负责** 外部系统状态管理

## 接口契约

### ExternalActionPolicy

```python
class ExternalActionPolicy:
    def is_critical_action(self, action: str) -> bool:
        """判断是否为关键动作"""
        pass

    def check_permit_required(self, action: str) -> bool:
        """检查是否需要 permit"""
        pass

    def validate_evidence_ref(self, ref: EvidenceRef) -> bool:
        """验证 Evidence 引用格式"""
        pass

    def can_transport(self, evidence_ref: EvidenceRef) -> bool:
        """检查是否可以搬运（只读）"""
        pass
```

## 交付物

- [x] `README.md` - 策略定义
- [x] `external_action_policy.py` - 策略实现
- [x] `classification.py` - 动作分类
- [x] `permit_check.py` - Permit 校验
- [x] `evidence_transport.py` - Evidence 搬运规则
- [x] `E4_execution_report.md` - 执行报告

## 合规性

遵循 Antigravity-1 闭链要求：
- contract -> receipt -> dual-gate 完整
- Evidence 引用不可篡改
- Permit 校验不可绕过
