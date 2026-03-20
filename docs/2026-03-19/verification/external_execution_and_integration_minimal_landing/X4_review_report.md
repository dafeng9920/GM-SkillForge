# X4 审查报告：External Action Policy 子面最小落地骨架

**审查者**: vs--cc1
**审查日期**: 2026-03-20
**任务编号**: X4
**执行者**: Kior-B
**审查范围**: External Action Policy 子面职责与边界合规性

---

## 一、审查结论

**状态**: ✅ **PASS**

**总体评价**: X4 执行报告完整，E4 交付物复用关系明确，新增 BOUNDARIES.md 文档完整定义了与其他子面的边界。所有验收标准已满足，硬约束全部遵守。

---

## 二、审查发现

### 2.1 执行报告状态 ✅

**状态**: X4_execution_report.md 已存在

**路径**: `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X4_execution_report.md`

**内容验证**:
- ✅ 元信息完整（task_id, executor, timestamp, status）
- ✅ 与 E4 的关系说明清晰
- ✅ 复用 E4 交付物清单明确
- ✅ 新增 BOUNDARIES.md 说明
- ✅ 验收标准检查完整
- ✅ 与 X1/X2/X3 集成关系验证
- ✅ 硬约束合规性验证

### 2.2 E4 交付物复用关系 ✅

**复用声明**: X4 明确复用 E4 的所有代码交付物

| 交付物 | E4 路径 | X4 复用 | 状态 |
|--------|---------|--------|------|
| README.md | `external_action_policy/README.md` | ✅ | 清晰 |
| external_action_policy.py | `external_action_policy/external_action_policy.py` | ✅ | 清晰 |
| classification.py | `external_action_policy/classification.py` | ✅ | 清晰 |
| permit_check.py | `external_action_policy/permit_check.py` | ✅ | 清晰 |
| evidence_transport.py | `external_action_policy/evidence_transport.py` | ✅ | 清晰 |
| __init__.py | `external_action_policy/__init__.py` | ✅ | 清晰 |

### 2.3 X4 新增交付物 ✅

**新增文件**: BOUNDARIES.md

**路径**: `skillforge/src/contracts/external_action_policy/BOUNDARIES.md`

**内容验证**:
- ✅ 与 Connector Contract 的边界定义
- ✅ 与 Integration Gateway 的边界定义
- ✅ 与 Secrets/Credentials Boundary 的边界定义
- ✅ 与 System Execution 的边界定义
- ✅ 跨子面协同场景说明
- ✅ 违规检测规则
- ✅ 边界违规后果

---

## 三、External Action Policy 职责清晰度 ✅

### 3.1 核心职责定义

**职责声明位置**: [`README.md`](skillforge/src/contracts/external_action_policy/README.md)

| 核心职责 | 证据 | 状态 |
|----------|------|------|
| 动作分类 | `classification.py` | ✅ 清晰 |
| Permit 要求判定 | `external_action_policy.py` | ✅ 清晰 |
| 策略决策 | `external_action_policy.py:evaluate_action()` | ✅ 清晰 |
| Evidence 搬运规则 | `evidence_transport.py` | ✅ 清晰 |

### 3.2 不负责项声明 ✅

| 不负责项 | 声明位置 | 状态 |
|----------|---------|------|
| 不负责 permit 生成 | README.md | ✅ 清晰 |
| 不负责 Evidence 生成 | README.md | ✅ 清晰 |
| 不负责 AuditPack 生成 | README.md | ✅ 清晰 |
| 不负责外部动作真实执行 | README.md | ✅ 清晰 |
| 不负责外部系统状态管理 | README.md | ✅ 清晰 |

---

## 四、关键动作/非关键动作分类 ✅

### 4.1 分类实现

**文件**: [`classification.py`](skillforge/src/contracts/external_action_policy/classification.py)

**关键动作列表** (使用不可变 frozenset):
```python
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

### 4.2 安全约束验证

| 约束 | 实现 | 状态 |
|------|------|------|
| 使用 frozenset 确保不可变 | `CRITICAL_ACTIONS: frozenset` | ✅ 遵守 |
| 模块级常量 | 模块级定义 | ✅ 遵守 |
| 已删除运行时修改方法 | 无 add/remove 方法 | ✅ 遵守 |
| UNKNOWN 类别默认阻断 | `UNKNOWN_ACTION_BLOCKED` | ✅ 遵守 |

---

## 五、Permit 规则审查 ✅

### 5.1 Permit 使用条件

**文件**: [`README.md`](skillforge/src/contracts/external_action_policy/README.md)

**规则验证**:
- ✅ 关键动作必须持 permit
- ✅ 非关键动作可豁免 permit
- ✅ 未知动作默认阻断（安全优先）

### 5.2 错误码映射

**文件**: [`external_action_policy.py`](skillforge/src/contracts/external_action_policy/external_action_policy.py)

| 错误码 | 含义 | 映射到 | 状态 |
|--------|------|--------|------|
| E001 | permit 缺失 | PERMIT_REQUIRED | ✅ 完整 |
| E002 | permit 格式无效 | PERMIT_INVALID | ✅ 完整 |
| E003 | 签名无效 | PERMIT_INVALID | ✅ 完整 |
| E004 | permit 过期 | PERMIT_EXPIRED | ✅ 完整 |
| E005 | scope 不匹配 | PERMIT_SCOPE_MISMATCH | ✅ 完整 |
| E006 | subject 不匹配 | PERMIT_SUBJECT_MISMATCH | ✅ 完整 |
| E007 | permit 已撤销 | PERMIT_REVOKED | ✅ 完整 |

### 5.3 Permit 校验实现

**文件**: [`permit_check.py`](skillforge/src/contracts/external_action_policy/permit_check.py)

**委托实现**:
- ✅ 委托给 `gate_permit.py` 执行真实校验
- ✅ 不自行实现校验逻辑
- ✅ 保持与 frozen 主线的一致性

---

## 六、Evidence / AuditPack 只读边界 ✅

### 6.1 Evidence 搬运规则

**文件**: [`evidence_transport.py`](skillforge/src/contracts/external_action_policy/evidence_transport.py)

**搬运方法验证**:
```python
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

**约束验证**:
| 约束 | 实现 | 状态 |
|------|------|------|
| 只读搬运，不可改写 | 返回新对象，保持原值 | ✅ 遵守 |
| 保持引用完整性 | source_locator, content_hash 不变 | ✅ 遵守 |
| 记录搬运日志 | `_log_transport()` 方法 | ✅ 遵守 |

---

## 七、与 X1/X2/X3 的边界验证 ✅

### 7.1 与 Connector Contract 的边界

**文件**: [`BOUNDARIES.md`](skillforge/src/contracts/external_action_policy/BOUNDARIES.md)

| 子面 | 职责 | 接口 | 状态 |
|------|------|------|------|
| Connector Contract | 定义外部连接契约 | `ExternalConnectionContract` | ✅ 清晰 |
| External Action Policy | 定义动作分类和 permit 要求 | `ActionPolicyDecision` | ✅ 清晰 |

**数据流向**:
```
Connector Contract --> External Action Policy
                         (查询是否需要 permit)
                         <-- 返回决策
```

**禁止项验证**:
- ✅ Connector Contract 不得实现动作分类逻辑
- ✅ External Action Policy 不得定义外部连接接口

### 7.2 与 Integration Gateway 的边界

**文件**: [`BOUNDARIES.md`](skillforge/src/contracts/external_action_policy/BOUNDARIES.md)

| 子面 | 职责 | 接口 | 状态 |
|------|------|------|------|
| Integration Gateway | 搬运 ExecutionIntent 和 Evidence | `GatewayInterface` | ✅ 清晰 |
| External Action Policy | 评估动作是否允许执行 | `ExternalActionPolicy` | ✅ 清晰 |

**Permit 使用时机**:
1. Integration Gateway 接收 `ExecutionIntent`
2. 提取 `action_type`
3. 咨询 `ExternalActionPolicy.evaluate_action()`
4. 如果 `allowed=False`，阻断执行
5. 如果 `allowed=True`，继续搬运

**禁止项验证**:
- ✅ Integration Gateway 不得自行判断动作是否关键
- ✅ Integration Gateway 不得绕过 permit 检查
- ✅ External Action Policy 不得实现搬运逻辑

### 7.3 与 Secrets/Credentials Boundary 的边界

**文件**: [`BOUNDARIES.md`](skillforge/src/contracts/external_action_policy/BOUNDARIES.md)

| 子面 | 职责 | 接口 | 状态 |
|------|------|------|------|
| Secrets/Credentials Boundary | 定义凭据分层规则 | `CredentialBoundary` | ✅ 清晰 |
| External Action Policy | 定义动作 permit 要求 | `ActionPolicyDecision` | ✅ 清晰 |

**独立性验证**:
- ✅ Permit ≠ Credentials（两者分离）
- ✅ 职责不重叠（无交叉依赖）
- ✅ External Action Policy 不定义凭据分层规则

### 7.4 与 System Execution 的边界

**文件**: [`BOUNDARIES.md`](skillforge/src/contracts/external_action_policy/BOUNDARIES.md)

| 子面 | 职责 | 接口 | 状态 |
|------|------|------|------|
| System Execution | 承接内核执行控制 | `OrchestratorInterface` | ✅ 清晰 |
| External Action Policy | 提供策略决策 | `ExternalActionPolicy` | ✅ 清晰 |

**接口调用方向**:
```
System Execution --> External Action Policy
                    (查询动作是否允许)
                    <-- 返回决策
```

**禁止项验证**:
- ✅ System Execution 不得自行实现动作分类
- ✅ System Execution 不得绕过 permit 检查
- ✅ External Action Policy 不得实现执行控制逻辑

---

## 八、跨子面协同场景验证 ✅

### 8.1 场景覆盖

**文件**: [`BOUNDARIES.md`](skillforge/src/contracts/external_action_policy/BOUNDARIES.md)

| 场景 | 涉及子面 | 流程完整性 | 状态 |
|------|----------|-----------|------|
| 发布技能到外部系统 | X1, X2, X3, X4 | ✅ 完整 | ✅ 验证通过 |
| 外部 API 调用 | X1, X2, X3, X4 | ✅ 完整 | ✅ 验证通过 |
| 归档 AuditPack | X1, X2, X4 | ✅ 完整 | ✅ 验证通过 |

### 8.2 违规检测规则

**文件**: [`BOUNDARIES.md`](skillforge/src/contracts/external_action_policy/BOUNDARIES.md)

| 检测点 | 定义 | 状态 |
|--------|------|------|
| Permit 绕过检测 | ✅ 定义 | ✅ 完整 |
| Evidence 篡改检测 | ✅ 定义 | ✅ 完整 |
| 越界行为检测 | ✅ 定义 | ✅ 完整 |

---

## 九、硬约束遵守验证 ✅

| 硬约束 | 验证方法 | 证据 | 状态 |
|--------|---------|------|------|
| no runtime | 检查实现 | 接口抽象定义，无真实执行 | ✅ 遵守 |
| no real external integration | 检查导入 | 无外部系统连接 | ✅ 遵守 |
| no permit bypass | 检查逻辑 | 不可变 CRITICAL_ACTIONS，UNKNOWN 默认阻断 | ✅ 遵守 |
| no mutable evidence or audit pack | 检查搬运 | 只读搬运，保持引用完整性 | ✅ 遵守 |
| no frozen mainline mutation | 检查依赖 | 只读承接 | ✅ 遵守 |

---

## 十、验收标准完成度 ✅

| 验收标准 | 完成度 | 证据 |
|----------|--------|------|
| 子面目录/文件骨架存在 | 100% | 复用 E4 + 新增 BOUNDARIES.md |
| permit 使用规则文档存在 | 100% | README.md, classification.py |
| external action policy 边界说明存在 | 100% | BOUNDARIES.md (X4 新增) |
| 与 X1/X2/X3 集成关系验证 | 100% | BOUNDARIES.md 定义边界 |
| 未进入 runtime | 100% | 接口抽象定义 |
| 未接入真实外部系统 | 100% | 无外部系统连接 |

---

## 十一、审查决定

**状态**: ✅ **PASS**

**理由**:
1. X4 执行报告完整，与 E4 的复用关系明确
2. 新增 BOUNDARIES.md 文档完整定义了与其他子面的边界
3. 所有验收标准已满足
4. 所有硬约束全部遵守
5. 与 X1/X2/X3 的集成关系已验证
6. 未进入 runtime
7. 未接入真实外部系统
8. Permit 规则清晰且不可绕过
9. Evidence/AuditPack 只读边界清晰

**批准行动**:
- ✅ X4 任务 **审查通过**
- ✅ 可进入下一阶段

---

## 十二、EvidenceRef 最小集合

| 类型 | 路径 | 用途 |
|------|------|------|
| 执行报告 | `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/X4_execution_report.md` | X4 执行报告 |
| 策略定义 | `skillforge/src/contracts/external_action_policy/README.md` | 策略定义 |
| 主策略实现 | `skillforge/src/contracts/external_action_policy/external_action_policy.py` | 主策略实现 |
| 动作分类 | `skillforge/src/contracts/external_action_policy/classification.py` | 动作分类 |
| Permit 校验 | `skillforge/src/contracts/external_action_policy/permit_check.py` | Permit 校验 |
| Evidence 搬运 | `skillforge/src/contracts/external_action_policy/evidence_transport.py` | Evidence 搬运 |
| 边界说明 | `skillforge/src/contracts/external_action_policy/BOUNDARIES.md` | X4 新增边界文档 |
| E4 执行报告 | `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_execution_report.md` | E4 执行报告 |

---

**审查签名**: vs--cc1
**审查时间**: 2026-03-20
**证据级别**: REVIEW
**下一步**: 合规审查（Kior-C）
