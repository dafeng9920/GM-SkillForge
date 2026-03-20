# E4 合规审查认定: External Action Policy 子面最小准备骨架

> **任务**: E4 | **合规官**: Kior-C | **日期**: 2026-03-19
> **执行者**: Kior-B | **审查者**: vs--cc1
> **审查类型**: B Guard 硬审 (Zero Exception)
> **认定结论**: ✅ **PASS - RELEASE CLEARED**

---

## Zero Exception Directives 审查结果

### Directive 1: 只要接入真实外部系统，直接 FAIL ✅ PASS

| 检查项 | 方法 | 结果 | 证据 |
|--------|------|------|------|
| HTTP 客户端 | import 检查 | ✅ 无 | 无 `requests/aiohttp/http.client/urllib` 导入 |
| 外部 API 调用 | 代码检查 | ✅ 无 | `trigger.py` 中明确 `raise NotImplementedError` |
| 外部系统状态管理 | 代码检查 | ✅ 无 | 无状态管理逻辑 |
| 真实动作执行 | 代码检查 | ✅ 无 | `evaluate_action` 仅返回决策对象 |

**证据文件**:
- `skillforge/src/contracts/external_action_policy/README.md:41-42` - 明确声明"不负责外部动作真实执行"
- `skillforge/src/contracts/external_action_policy/trigger.py:18-20` - 真实触发功能待实现
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_execution_report.md:84-90` - 骨架未实现真实触发

**代码证据**:
```python
# trigger.py
class Trigger(TriggerInterface):
    def trigger(self, request: TriggerRequest) -> TriggerResult:
        raise NotImplementedError("Trigger 触发功能待实现")
```

**认定**: E4 未接入任何真实外部系统。

---

### Directive 2: 只要生成 permit，直接 FAIL ✅ PASS

| 检查项 | 方法 | 结果 | 证据 |
|--------|------|------|------|
| Permit 生成方法 | 代码检查 | ✅ 无 | 只有验证逻辑，无生成 |
| Permit 续期逻辑 | 代码检查 | ✅ 无 | 无续期实现 |
| Governor 调用 | import/调用检查 | ✅ 无 | 未导入 Governor 模块 |
| Permit 签发 | 代码检查 | ✅ 无 | 委托给 `gate_permit.py` |

**证据文件**:
- `skillforge/src/contracts/external_action_policy/README.md:38-39` - 明确声明"不负责 permit 生成"
- `skillforge/src/contracts/external_action_policy/permit_check.py:60-76` - 委托验证给 `gate_permit.py`
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_execution_report.md:192-194` - Permit 真实校验委托给 gate_permit.py

**代码证据**:
```python
# permit_check.py
def check_permit_for_action(
    permit_token: str | dict,
    action: str,
    execution_context: dict | None = None,
) -> PermitCheckResult:
    # 委托给 gate_permit.py 的 validate_permit
    from skillforge.src.contracts.gate_permit import validate_permit
    return validate_permit(permit_token, action, execution_context)
```

**认定**: E4 未实现任何 permit 生成逻辑，正确委托给治理层。

---

### Directive 3: 只要改写 Evidence/AuditPack，直接 FAIL ✅ PASS

| 检查项 | 方法 | 结果 | 证据 |
|--------|------|------|------|
| Evidence 修改 | 代码检查 | ✅ 无 | `transport_evidence_ref` 只传递引用 |
| AuditPack 修改 | 代码检查 | ✅ 无 | 只读搬运，无改写 |
| 重生成逻辑 | 代码检查 | ✅ 无 | 无重生成实现 |
| 引用方式 | 代码检查 | ✅ 只读 | 保持原始 `source_locator` 和 `content_hash` |

**证据文件**:
- `skillforge/src/contracts/external_action_policy/README.md:40-41` - 明确声明"不负责 Evidence 生成"
- `skillforge/src/contracts/external_action_policy/evidence_transport.py:15-29` - 只读搬运实现
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_execution_report.md:67-81` - 集成层只读搬运规则

**代码证据**:
```python
# evidence_transport.py
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

**认定**: E4 未实现任何 Evidence/AuditPack 修改逻辑。

---

### Directive 4: 只要进入 Runtime，直接 FAIL ✅ PASS

| 检查项 | 方法 | 结果 | 证据 |
|--------|------|------|------|
| 执行控制逻辑 | 代码检查 | ✅ 无 | `evaluate_action` 仅返回决策 |
| 真实动作触发 | 代码检查 | ✅ 无 | `trigger.py` 未实现 |
| 会话状态管理 | 代码检查 | ✅ 无 | 无状态管理 |
| 重试逻辑 | 代码检查 | ✅ 无 | 无重试实现 |
| 超时处理 | 代码检查 | ✅ 无 | 无超时处理 |

**证据文件**:
- `skillforge/src/contracts/external_action_policy/README.md:42-43` - 明确声明"不负责外部系统状态管理"
- `skillforge/src/contracts/external_action_policy/trigger.py` - 骨架未实现真实触发
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_execution_report.md:83-90` - 不得越权触发真实外部动作

**Runtime 排除边界声明**:
```markdown
**不负责项**:
- 不负责 permit 生成（Governance 层负责）
- 不负责 Evidence 生成（Gate 层负责）
- 不负责 AuditPack 生成（T14 负责）
- 不负责 外部动作真实执行（External Connector 负责）
- 不负责 外部系统状态管理
```

**认定**: E4 未进入 Runtime。

---

## 合规审查重点验证

### 1. External Action Policy 职责边界清晰度 ✅ PASS

| 检查项 | 文档位置 | 状态 |
|--------|---------|------|
| 核心职责定义 | README.md:28-35 | ✅ 清晰 |
| 不负责项声明 | README.md:36-43 | ✅ 完整 |
| 与其他子面边界 | README.md | ✅ 明确 |

**核心职责**:
1. 动作分类 - 区分关键/非关键动作
2. Permit 校验 - 委托给 `gate_permit.py`
3. Evidence 搬运 - 只读搬运，不可改写
4. 策略决策 - 综合决策是否允许执行

**不负责项**:
1. permit 生成（Governance 层负责）
2. Evidence 生成（Gate 层负责）
3. AuditPack 生成（T14 负责）
4. 外部动作真实执行（External Connector 负责）
5. 外部系统状态管理

**认定**: 职责边界清晰。

---

### 2. 关键动作 Permit 不可绕过 ✅ PASS

| 检查项 | 状态 | 证据 |
|--------|------|------|
| 不可变关键动作集合 | ✅ 已修复 | `CRITICAL_ACTIONS` 使用 `frozenset` |
| 删除运行时修改方法 | ✅ 已修复 | 无 `add/remove` 方法 |
| UNKNOWN 类别默认阻断 | ✅ 已修复 | `UNKNOWN_ACTION_BLOCKED` |
| 非 Permit 执行阻断 | ✅ 通过 | `PERMIT_REQUIRED` 阻断原因 |

**证据文件**:
- `skillforge/src/contracts/external_action_policy/external_action_policy.py:24-33` - 不可变关键动作集合
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_execution_report.md:246-267` - 返修修复记录
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_review_report.md:125-134` - 返修验证结果

**返修前问题 (P1)**:
```python
# 已删除的危险代码
def add_critical_action(self, action: str) -> None:
    self._critical_actions.add(action)
```

**返修后修复**:
```python
# 现在使用不可变常量
CRITICAL_ACTIONS: frozenset[str] = frozenset({
    "PUBLISH_LISTING",
    "EXECUTE_VIA_N8N",
    # ... 其他关键动作
})
```

**认定**: Permit 不可绕过机制已通过返修修复。

---

### 3. Evidence / AuditPack 只读搬运语义 ✅ PASS

| 检查项 | 状态 | 证据 |
|--------|------|------|
| source_locator 保持 | ✅ 通过 | `transport_evidence_ref` 保持原始值 |
| content_hash 保持 | ✅ 通过 | `transport_evidence_ref` 保持原始值 |
| 无改写逻辑 | ✅ 通过 | 只有引用传递 |
| 验证函数完整 | ✅ 通过 | `verify_evidence_ref_format` |

**证据文件**:
- `skillforge/src/contracts/external_action_policy/evidence_transport.py:15-29` - 只读搬运实现
- `skillforge/src/contracts/external_action_policy/evidence_transport.py:42-62` - 验证函数
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_execution_report.md:107-120` - 引用完整性规则

**认定**: Evidence/AuditPack 只读搬运语义正确。

---

### 4. Permit 错误码映射完整性 ✅ PASS

| 错误码 | 含义 | 映射状态 |
|--------|------|---------|
| E001 | permit 缺失 | ✅ `PERMIT_REQUIRED` |
| E002 | permit 格式无效 | ✅ `PERMIT_INVALID` |
| E003 | 签名无效 | ✅ `PERMIT_INVALID` |
| E004 | permit 过期 | ✅ `PERMIT_EXPIRED` |
| E005 | scope 不匹配 | ✅ `PERMIT_SCOPE_MISMATCH` |
| E006 | subject 不匹配 | ✅ `PERMIT_SUBJECT_MISMATCH` |
| E007 | permit 已撤销 | ✅ `PERMIT_REVOKED |
| 未知动作 | (P2 新增) | ✅ `UNKNOWN_ACTION_BLOCKED` |

**证据文件**:
- `skillforge/src/contracts/external_action_policy/external_action_policy.py:36-44` - `ExecutionBlockReason` 枚举
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_execution_report.md:94-106` - 错误码映射

**认定**: Permit 错误码映射完整，包含 P2 修复的未知动作阻断。

---

### 5. 是否偷带真实动作执行语义 ✅ PASS

| 禁止语义 | 文档声明 | 代码验证 | 状态 |
|----------|---------|---------|------|
| 真实 HTTP 调用 | ✅ 禁止 | 无 `requests/aiohttp` 导入 | ✅ 无违规 |
| 真实外部触发 | ✅ 禁止 | `raise NotImplementedError` | ✅ 无违规 |
| 状态持久化 | ✅ 禁止 | 无状态管理代码 | ✅ 无违规 |
| 连接管理 | ✅ 禁止 | 无连接池实现 | ✅ 无违规 |

**证据文件**:
- `skillforge/src/contracts/external_action_policy/README.md:42-43` - 明确声明不负责真实执行
- `skillforge/src/contracts/external_action_policy/trigger.py` - 骨架未实现
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_review_report.md:79-83` - 没有偷带真实动作实现

**审查报告引用**:
> ### ✅ 没有偷带真实动作实现
> - `ExternalActionPolicy.evaluate_action` 只返回决策对象，不执行任何外部动作
> - 文档明确说明真实执行由其他模块负责
> - 没有发现任何 `requests.post()`, `subprocess.run()`, `os.system()` 等危险调用

**认定**: 无偷带真实动作执行语义。

---

## 硬约束验证总结

| 约束 | 状态 | 证据 |
|------|------|------|
| 不接入真实外部系统 | ✅ PASS | 无 HTTP 导入，`trigger.py` 未实现 |
| 不生成 permit | ✅ PASS | 委托给 `gate_permit.py` |
| 不改写 Evidence/AuditPack | ✅ PASS | 只读搬运，保持原始 hash/locator |
| 不进入 Runtime | ✅ PASS | 只返回决策，无真实执行 |
| 清晰的子面边界 | ✅ PASS | Policy ≠ Connector ≠ Integration ≠ Secrets |

---

## 审查返修记录

### 第一轮审查（vs--cc1）

| 问题 | 级别 | 修复状态 |
|------|------|---------|
| P1 - 运行时修改关键动作列表可能被滥用 | REJECT | ✅ 已修复 |
| P2 - UNKNOWN 类别的处理规则不明确 | REVIEW | ✅ 已修复 |

### 返修验证（Kior-B）

**P1 修复**:
- ✅ `CRITICAL_ACTIONS` 改为模块级 `frozenset[str]`
- ✅ 删除 `add_critical_action()` 和 `remove_critical_action()` 方法
- ✅ `get_critical_actions()` 返回不可变集合
- ✅ `__init__` 不再维护内部状态

**P2 修复**:
- ✅ `ExecutionBlockReason` 添加 `UNKNOWN_ACTION_BLOCKED`
- ✅ `evaluate_action()` 中 UNKNOWN 类别返回 `allowed=False`
- ✅ 处理顺序：UNKNOWN → NON_CRITICAL → CRITICAL（安全优先）

### 返修验证结果

| 审查重点 | 返修前 | 返修后 |
|----------|--------|--------|
| 外部动作分类是否清晰 | ✅ 清晰 | ✅ 清晰 |
| permit 规则是否清楚且不可绕过 | ⚠️ 有风险 | ✅ **已修复** |
| Evidence / AuditPack 是否保持只读语义 | ✅ 只读语义正确 | ✅ 只读语义正确 |
| 是否偷带真实动作实现 | ✅ 无真实实现 | ✅ 无真实实现 |

---

## 合规官认定

### Zero Exception 检查结论
- ✅ **未接入真实外部系统**
- ✅ **未生成 permit**
- ✅ **未改写 Evidence/AuditPack**
- ✅ **未进入 Runtime**

### 合规审查结论
- ✅ **External Action Policy 职责边界清晰**
- ✅ **关键动作 Permit 不可绕过（已通过返修修复）**
- ✅ **Evidence/AuditPack 只读搬运语义正确**
- ✅ **Permit 错误码映射完整**
- ✅ **无偷带真实动作执行语义**

### 最终认定

**状态**: ✅ **PASS - RELEASE CLEARED**

**理由**:
1. 所有 Zero Exception Directives 检查通过
2. External Action Policy 职责边界清晰（动作分类、Permit 校验、Evidence 搬运、策略决策）
3. 不负责项完整声明（不生成 permit、不生成 Evidence、不执行真实动作、不管理系统状态）
4. P1 问题已修复：关键动作列表使用不可变 `frozenset`，无法运行时修改
5. P2 问题已修复：UNKNOWN 类别默认阻断，遵循安全优先原则
6. Permit 校验正确委托给治理层 `gate_permit.py`
7. Evidence/AuditPack 只读搬运语义正确，保持原始引用完整性
8. 无偷带真实动作执行语义（`trigger.py` 明确未实现）

**批准行动**:
- ✅ E4 任务 **合规通过**
- ✅ 可进入下一阶段 (E6 Publish/Notify/Sync Boundary)

---

**合规官签名**: Kior-C
**审查日期**: 2026-03-19
**证据级别**: COMPLIANCE
**审查标准**: B Guard Hard Check (Zero Exception)
**基于审查**: vs--cc1 (审查报告: docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_review_report.md)
**基于执行**: Kior-B (执行报告: docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_execution_report.md)
**下一步**: E6 Publish/Notify/Sync Boundary 任务
