# E4 Execution Report (返修后)

**Task ID**: E4
**Executor**: Kior-B
**Date**: 2026-03-19
**Status**: COMPLETED - 等待最终审查
**返修**: 已修复 P1/P2 风险

## 任务目标

完成 external action policy 子面的最小准备骨架。

## 交付物清单

### 1. 文件结构

```
skillforge/src/contracts/external_action_policy/
├── __init__.py                    # 模块入口
├── README.md                       # 策略定义文档
├── external_action_policy.py       # 主策略实现
├── classification.py               # 动作分类
├── permit_check.py                 # Permit 校验
└── evidence_transport.py           # Evidence 搬运规则
```

### 2. 职责定义

| 职责 | 负责模块 | 说明 |
|------|----------|------|
| 动作分类 | `classification.py` | 区分关键/非关键动作 |
| Permit 校验 | `permit_check.py` | 委托给 `gate_permit.py` |
| Evidence 搬运 | `evidence_transport.py` | 只读搬运，不可改写 |
| 策略决策 | `external_action_policy.py` | 综合决策是否允许执行 |

### 3. 不负责项

- **不负责** permit 生成（Governance 层负责）
- **不负责** Evidence 生成（Gate 层负责）
- **不负责** AuditPack 生成（T14 负责）
- **不负责** 外部动作真实执行（External Connector 负责）
- **不负责** 外部系统状态管理

## 核心约束实现

### 1. 关键动作必须持 Permit

```python
# 不可变关键动作集合 - 禁止运行时修改
CRITICAL_ACTIONS: frozenset[str] = frozenset({
    "PUBLISH_LISTING",
    "EXECUTE_VIA_N8N",
    "EXPORT_WHITELIST",
    "UPGRADE_REPLACE_ACTIVE",
    "TRIGGER_EXTERNAL_CONNECTOR",
    "WRITE_EXTERNAL_STATE",
    "MODIFY_EXTERNAL_RESOURCE",
    "DELETE_EXTERNAL_RESOURCE",
})
```

**安全约束**：
- 使用 `frozenset` 确保不可变
- 模块级常量，禁止运行时修改
- 已删除 `add_critical_action()` / `remove_critical_action()` 方法

### 2. 集成层只读搬运

```python
# Evidence 搬运规则
def transport_evidence_ref(ref: EvidenceRef) -> EvidenceRef:
    # 只传递引用，不修改内容
    return EvidenceRef(
        evidence_id=ref.evidence_id,
        source_locator=ref.source_locator,  # 保持原始 locator
        content_hash=ref.content_hash,      # 保持原始 hash
        kind=ref.kind,
        note=ref.note,
        created_at=ref.created_at,
    )
```

### 3. 不得越权触发真实外部动作

```python
# trigger.py 中已有骨架，未实现真实触发
class Trigger(TriggerInterface):
    def trigger(self, request: TriggerRequest) -> TriggerResult:
        raise NotImplementedError("Trigger 触发功能待实现")
```

## Permit 使用条件

### 错误码映射

遵循 `gate_permit.py` 的 7 项错误码：

| 错误码 | 含义 | 映射到 |
|--------|------|--------|
| E001 | permit 缺失 | PERMIT_REQUIRED |
| E002 | permit 格式无效 | PERMIT_INVALID |
| E003 | 签名无效 | PERMIT_INVALID |
| E004 | permit 过期 | PERMIT_EXPIRED |
| E005 | scope 不匹配 | PERMIT_SCOPE_MISMATCH |
| E006 | subject 不匹配 | PERMIT_SUBJECT_MISMATCH |
| E007 | permit 已撤销 | PERMIT_REVOKED |

## Evidence / AuditPack 引用规则

### 引用完整性

```
Gate -> Evidence -> AuditPack -> Integration Gateway -> External
     (生成)     (聚合)          (搬运)             (传递)
```

- **source_locator**: 必须保持原始值
- **content_hash**: 必须保持原始值
- **集成层**: 只添加 transport_timestamp 元数据

### 搬运日志

所有搬运操作都会被记录：

```python
{
    "timestamp": "2026-03-19T12:00:00Z",
    "kind": "evidence",
    "payload": {...},
}
```

## 接口契约

### ExternalActionPolicy

```python
class ExternalActionPolicy:
    def is_critical_action(self, action: str) -> bool
    def requires_permit(self, action: str) -> bool
    def classify(self, action: str) -> ActionCategory
    def evaluate_action(
        self,
        action: str,
        permit_token: str | dict | None,
        execution_context: dict | None,
    ) -> ActionPolicyDecision
```

### ActionPolicyDecision

```python
@dataclass
class ActionPolicyDecision:
    action: str
    allowed: bool
    category: ActionCategory
    permit_required: bool
    block_reason: ExecutionBlockReason | None
    permit_check_result: PermitCheckResult | None
```

### ExecutionBlockReason (返修新增)

```python
class ExecutionBlockReason(Enum):
    PERMIT_REQUIRED = "PERMIT_REQUIRED"
    PERMIT_INVALID = "PERMIT_INVALID"
    PERMIT_EXPIRED = "PERMIT_EXPIRED"
    PERMIT_SCOPE_MISMATCH = "PERMIT_SCOPE_MISMATCH"
    PERMIT_SUBJECT_MISMATCH = "PERMIT_SUBJECT_MISMATCH"
    PERMIT_REVOKED = "PERMIT_REVOKED"
    UNKNOWN_ACTION_BLOCKED = "UNKNOWN_ACTION_BLOCKED"  # P2 修复
```

## 合规性检查

### Antigravity-1 闭链要求

- [x] contract -> receipt -> dual-gate 结构定义
- [x] Evidence 引用不可篡改
- [x] Permit 校验不可绕过

### "稳定" 宣称证据标准

- [x] 不做 "稳定" 宣称（仅框架，未执行）
- [x] 所有决策必须附带 Evidence 引用（设计完成）

## 待实现项目

### Phase 2（需要 Governor）

1. Permit 真实校验（当前委托给 gate_permit.py）
2. Evidence 搬运日志持久化
3. 真实外部动作触发（当前骨架）
4. 与 Integration Gateway 的实际集成

## 依赖关系

```
external_action_policy
├── gate_permit.py (Permit 校验)
├── audit_pack.py (AuditPack 结构)
├── integration_gateway/ (搬运目标)
└── system_execution/ (编排层)
```

## 使用示例

```python
from skillforge.src.contracts.external_action_policy import (
    evaluate_action,
    is_critical_action,
)

# 1. 检查动作是否关键
if is_critical_action("PUBLISH_LISTING"):
    # 2. 评估是否允许执行
    decision = evaluate_action(
        action="PUBLISH_LISTING",
        permit_token=permit_token,
        execution_context={
            "repo_url": "https://github.com/...",
            "commit_sha": "abc123",
            "run_id": "20260319_120000",
        },
    )

    if decision.allowed:
        # 执行动作
        pass
    else:
        # 处理阻断
        print(f"Blocked: {decision.block_reason}")
```

## 验证清单

- [x] 关键动作列表定义（使用不可变 frozenset）
- [x] 非关键动作豁免规则
- [x] Permit 校验接口
- [x] Evidence 搬运规则
- [x] 不改写 Evidence/AuditPack 语义
- [x] 不触发真实外部动作
- [x] 错误码映射完整
- [x] **P1 修复**: 删除运行时修改方法，使用不可变常量
- [x] **P2 修复**: UNKNOWN 类别默认阻断

## 返修记录

### P1 - 运行时修改关键动作列表风险

**问题**: `add_critical_action()` / `remove_critical_action()` 方法可能被滥用绕过 permit

**修复**:
- 删除这两个方法
- 使用模块级 `frozenset` 常量
- `get_critical_actions()` 返回不可变集合

### P2 - UNKNOWN 类别处理不明确

**问题**: UNKNOWN 类别没有明确处理逻辑

**修复**:
- 添加 `UNKNOWN_ACTION_BLOCKED` 阻断原因
- UNKNOWN 类别默认返回 `allowed=False`
- 未知动作视为需要 permit（安全优先）

## 签名

**执行者**: Kior-B
**日期**: 2026-03-19
**状态**: E4 返修完成，等待合规官 Kior-C 最终审查

**返修确认**:
- P1 风险已修复（删除运行时修改方法）
- P2 风险已修复（UNKNOWN 默认阻断）
- 无新增发现
