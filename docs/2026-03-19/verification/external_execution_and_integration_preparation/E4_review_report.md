# E4 审查报告 - External Action Policy 子面

审查者: vs--cc1

任务: E4 - external action policy 子面最小准备骨架

执行者: Kior-B

---

## 第一轮审查

一、总体评估：REVIEW - 有条件通过

二、发现项

### P1 - 风险 - 运行时修改关键动作列表可能被滥用
位置: external_action_policy.py:202-216

问题:
```python
def add_critical_action(self, action: str) -> None:
    """添加关键动作（谨慎使用）"""
    self._critical_actions.add(action)

def remove_critical_action(self, action: str) -> None:
    """移除关键动作（谨慎使用）"""
    self._critical_actions.discard(action)
```

违规点: 允许运行时动态修改关键动作列表，理论上可能被恶意代码利用来绕过 permit 检查。例如：

```python
# 恶意代码可能这样绕过
policy = get_policy()
policy.remove_critical_action("PUBLISH_LISTING")
decision = policy.evaluate_action("PUBLISH_LISTING", None, {})  # 现在 allowed=True
```

理由: 虽然文档说明 "谨慎使用"，但没有强制约束。关键动作列表应该是配置驱动的，而不是运行时可变的。

建议:
1. 删除 `add_critical_action` 和 `remove_critical_action` 方法
2. 将关键动作列表定义为模块级常量（不可变）
3. 如果需要扩展，应通过配置文件加载，而不是运行时修改

### P2 - 不清晰 - UNKNOWN 类别的处理规则不明确
位置: classification.py:78-113, external_action_policy.py:138-145

问题: 当动作被分类为 `UNKNOWN` 时，`evaluate_action` 的处理逻辑不明确。

当前代码中，非关键动作 (NON_CRITICAL) 直接返回 `allowed=True`，但 UNKNOWN 类别没有明确处理。如果某个动作既不在关键白名单也不在非关键白名单，且不匹配任何模式，将被分类为 UNKNOWN，但 `evaluate_action` 只明确处理了 NON_CRITICAL 分支。

建议: 明确 UNKNOWN 类别的默认行为应该是：
- 选项 A: 默认阻断（安全优先）
- 选项 B: 默认允许但记录警告（兼容性优先）

建议选择选项 A（默认阻断），因为 "未知动作" 可能是安全风险。

### 信息 - Permit 检查与 gate_permit.py 的依赖关系
位置: permit_check.py:60-76

说明: `check_permit_for_action` 函数直接调用 `gate_permit.py` 的 `validate_permit`。这是正确的设计（委托给治理层），但需要确认 `gate_permit.py` 中的 `validate_permit` 函数已经实现且稳定。

建议: 在 E4 执行报告中补充对 `gate_permit.py` 依赖的说明。

三、正面发现

### ✅ 外部动作分类清晰
- `classification.py` 清晰定义了三种类别 (CRITICAL, NON_CRITICAL, UNKNOWN)
- 白名单和模式匹配规则完整
- 分类优先级明确

### ✅ Evidence / AuditPack 只读语义保持良好
- `evidence_transport.py` 的搬运函数正确实现了只读传递
- `source_locator`, `content_hash` 等关键字段保持完整
- 验证函数确保引用格式正确

### ✅ 没有偷带真实动作实现
- `ExternalActionPolicy.evaluate_action` 只返回决策对象，不执行任何外部动作
- 文档明确说明真实执行由其他模块负责
- 没有发现任何 `requests.post()`, `subprocess.run()`, `os.system()` 等危险调用

### ✅ Permit 错误码映射完整
- 7 项错误码 (E001-E007) 正确映射到 `ExecutionBlockReason`
- 阻断原因清晰明确

四、合规性检查（预审查）

| 合规项 | 状态 | 说明 |
|--------|------|------|
| Permit 不可绕过 | ⚠️ 条件通过 | 需修复 P1 问题 |
| Evidence/AuditPack 不可改写 | ✅ 通过 | 只读搬运语义正确 |
| 不进入真实外部动作 | ✅ 通过 | 无真实执行代码 |
| 不写成裁决层 | ✅ 通过 | 明确委托给 gate_permit.py |

五、建议的修复优先级

| 优先级 | 问题 | 建议 |
|--------|------|------|
| P1 | 运行时修改关键动作列表 | 删除 add/remove 方法，使用不可变常量 |
| P2 | UNKNOWN 类别处理不明确 | 明确默认阻断策略 |

六、总结

E4 交付物的整体质量良好，分类清晰，只读语义正确，没有偷带真实动作实现。主要问题是 P1 (运行时修改关键动作列表) 存在潜在的 permit 绕过风险，建议修复后再由合规官 Kior-C 进行最终审查。

如果 P1 问题得到修复，本审查建议改为 **PASS**。

---

## 第二轮审查（返修验证）

### 返修执行者：Kior-B

### 返修验证

| 问题 | 修复状态 | 验证 |
|------|---------|------|
| **P1** - 运行时修改关键动作列表 | ✅ 已修复 | `CRITICAL_ACTIONS` 现为 `frozenset`，`add/remove` 方法已删除 |
| **P2** - UNKNOWN 类别处理不明确 | ✅ 已修复 | 添加 `UNKNOWN_ACTION_BLOCKED`，默认阻断 |

### 代码验证结果

**P1 修复验证：**
- ✅ `CRITICAL_ACTIONS` 改为模块级 `frozenset[str]`（第 24-33 行）
- ✅ `add_critical_action()` 和 `remove_critical_action()` 方法已删除
- ✅ `get_critical_actions()` 返回 `frozenset[str]`
- ✅ `__init__` 不再维护内部状态

**P2 修复验证：**
- ✅ `ExecutionBlockReason` 添加 `UNKNOWN_ACTION_BLOCKED`（第 44 行）
- ✅ `evaluate_action()` 中 UNKNOWN 类别返回 `allowed=False`
- ✅ 处理顺序：UNKNOWN → NON_CRITICAL → CRITICAL（安全优先）

### 最终审查结论

| 审查重点 | 结果 |
|----------|------|
| 外部动作分类是否清晰 | ✅ 清晰 |
| permit 规则是否清楚且不可绕过 | ✅ **已修复** |
| Evidence / AuditPack 是否保持只读语义 | ✅ 只读语义正确 |
| 是否偷带真实动作实现 | ✅ 无真实实现 |

---

## 最终评估：PASS

E4 交付物已修复所有审查发现的问题：
1. 关键动作列表现在使用不可变 `frozenset`，无法运行时修改
2. UNKNOWN 类别默认阻断，遵循安全优先原则

**等待合规官 Kior-C 最终审查。**
