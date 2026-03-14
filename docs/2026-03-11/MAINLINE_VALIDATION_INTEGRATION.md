# 主线验证接入规范 - unified_validation_gate.py

- 日期：`2026-03-11`
- 任务：`TASK-MAIN-03`
- 执行者：`Agent C`
- 目标：将 `scripts/unified_validation_gate.py` 接入主线日常运行

## 一、当前主线验证时机盘点

根据 `docs/2026-03-11/T-ASM_Final_Gate_裁决_2026-03-11.md`，当前主线为：

```
Permit -> pre_absorb_check -> absorb -> local_accept -> final_accept
```

### 现有验证节点分析

| 阶段 | 当前验证脚本 | 覆盖范围 | 缺口 |
|------|-------------|---------|------|
| **Permit** | `core/pack_and_permit.py` | Permit 五字段 + Delivery 六件套 | 无 Three-Hash 验证 |
| **pre_absorb_check** | `pre_absorb_check.sh` | 任务包完整性 + 环境变量 | 独立脚本，未集成 |
| **absorb** | `absorb.sh` | 调用 pre_absorb_check + 复制文件 | 依赖 pre_absorb_check |
| **local_accept** | 无统一入口 | 依赖文档口径 | 缺代码化验证 |
| **final_accept** | 无统一入口 | 依赖文档口径 | 缺代码化验证 |

### 现有验证调用链

```
core/pack_and_permit.py
├── validate_permit_binding.py (Permit 五字段)
├── validate_delivery_completeness.py (Delivery 六件套)
└── (缺失) validate_three_hashes.py

absorb.sh
└── pre_absorb_check.sh
    └── verify_governance_env.sh
```

## 二、unified_validation_gate 接入点设计

### 2.1 最小接入原则

- **不修改现有脚本逻辑**
- **不破坏现有验证能力**
- **提供统一调用方式作为推荐默认**
- **保持各验证脚本独立可调用**

### 2.2 接入点矩阵

| 主线阶段 | 推荐模式 | 调用命令 | 验证内容 | 适用场景 |
|---------|---------|---------|---------|---------|
| **Permit 签发前** | `quick` | `python scripts/unified_validation_gate.py --quick --permit <permit>` | Permit + Delivery (跳过三哈希) | 快速开发迭代 |
| **Permit 签发前（完整）** | `mainline` | `python scripts/unified_validation_gate.py --mainline --permit <permit> --demand <d> --contract <c> --decision <d> --manifest <m>` | Permit + Delivery + Three-Hash | 正式发布前 |
| **pre_absorb** | `absorb` | `python scripts/unified_validation_gate.py --absorb --task-id <task>` | Pre-absorb 检查 | 替代直接调用 pre_absorb_check.sh |
| **local_accept** | `mainline` | `python scripts/unified_validation_gate.py --mainline --permit <permit>` | 完整主线验证 | 最终本地验收 |
| **cloud task 回传** | `cloud` | `python scripts/unified_validation_gate.py --cloud --task-id <task>` | Receipt + N-Boundary | 云端任务验证 |

## 三、主线默认验证调用方式

### 3.1 Permit 阶段验证（开发迭代）

**场景**：开发过程中快速验证 Permit 和 Delivery 完整性

```bash
# Quick 模式 - 跳过三哈希，快速反馈
python scripts/unified_validation_gate.py --quick --permit permits/default/tg1_baseline_permit.json
```

**预期结果**：
- ALLOW: Permit 五字段完整 + Delivery 六件套齐全
- DENY: 缺少必需字段或交付项

### 3.2 Permit 阶段验证（正式发布）

**场景**：正式发布前完整验证，包括三哈希一致性

```bash
# Mainline 模式 - 完整验证
python scripts/unified_validation_gate.py --mainline \
  --permit permits/default/tg1_baseline_permit.json \
  --demand .tmp/pr1_smoke/demand.json \
  --contract .tmp/pr1_smoke/contract.json \
  --decision .tmp/pr1_smoke/decision.json \
  --manifest .tmp/pr1_smoke/MANIFEST.json
```

**预期结果**：
- ALLOW: 所有验证通过 (Permit + Delivery + Three-Hash + Fixed-Caliber)
- DENY: 任何验证失败

### 3.3 Absorb 阶段验证

**场景**：Absorb 前验证任务包完整性

```bash
# Absorb 模式 - 替代直接调用 pre_absorb_check.sh
python scripts/unified_validation_gate.py --absorb --task-id REAL-TASK-002
```

**预期结果**：
- ALLOW: 任务包完整性 + 环境变量验证通过
- DENY: 任务包缺失或环境不符合

### 3.4 Local Accept 阶段验证

**场景**：本地最终验收，确认所有主线要求满足

```bash
# Mainline 模式 - 作为 local_accept 的代码化验证
python scripts/unified_validation_gate.py --mainline \
  --permit permits/default/tg1_baseline_permit.json \
  --demand .tmp/pr1_smoke/demand.json \
  --contract .tmp/pr1_smoke/contract.json \
  --decision .tmp/pr1_smoke/decision.json \
  --manifest .tmp/pr1_smoke/MANIFEST.json
```

### 3.5 Cloud Task 回传验证

**场景**：云端任务执行后验证执行回执和 N-Boundary

```bash
# Cloud 模式
python scripts/unified_validation_gate.py --cloud --task-id TASK-001
```

## 四、推荐主线流程（集成 unified_validation_gate）

### 4.1 开发迭代流程（快速）

```
1. 修改代码
2. python scripts/unified_validation_gate.py --quick --permit <permit>
3. 如果 ALLOW -> 继续
4. 如果 DENY -> 修复后重试
5. 提交代码
```

### 4.2 正式发布流程（完整）

```
1. 完成开发
2. python scripts/unified_validation_gate.py --mainline --permit <permit> ... (完整参数)
3. 如果 ALLOW -> 继续
4. 如果 DENY -> 修复后重试
5. 创建/更新 Permit
6. 提交发布
```

### 4.3 Absorb 流程

```
1. 任务包到达 dropzone
2. python scripts/unified_validation_gate.py --absorb --task-id <task>
3. 如果 ALLOW -> 执行 absorb.sh
4. 如果 DENY -> 拒绝 absorb
```

### 4.4 Local Accept 流程

```
1. 完成开发 + absorb
2. python scripts/unified_validation_gate.py --mainline --permit <permit> ... (完整参数)
3. 如果 ALLOW -> 标记 local_accept = PASS
4. 如果 DENY -> 修复后重试
5. 进入 final_accept
```

## 五、Fail-Closed 保证

所有验证模式均遵循 Fail-Closed 原则：

- 任何验证失败 = DENY
- Exit code: 0 = ALLOW, 1 = DENY
- 详细错误信息输出到 stdout
- 验证结果保存为 JSON（带时间戳）

## 六、证据引用格式

统一验证门生成的验证结果文件格式：

```json
{
  "schema_version": "1.0.0",
  "mode": "mainline|quick|absorb|cloud",
  "decision": "ALLOW|DENY",
  "decision_time": "2026-03-11T...",
  "checks": {
    "antigravity_2_guard": { ... },
    "n_boundary": { ... }
  },
  "errors": [ ... ],
  "warnings": [ ... ],
  "required_changes": [ ... ],
  "evidence_refs": [
    "antigravity_2_guard:ALLOW",
    "n_boundary:TASK-001:PASS"
  ]
}
```

文件保存位置：
```
docs/{date}/verification/unified_validation_{mode}_{timestamp}.json
```

## 七、向后兼容说明

### 7.1 现有验证脚本保持独立可用

所有现有验证脚本仍可独立直接调用：

```bash
# 直接调用 AG-2
python scripts/antigravity_2_guard.py --permit <permit> ...

# 直接调用 Permit 验证
python scripts/validate_permit_binding.py --permit <permit>

# 直接调用 pre_absorb_check
bash scripts/pre_absorb_check.sh <task_id>
```

### 7.2 现有调用方式保持不变

- `core/pack_and_permit.py` 继续直接调用验证脚本
- `absorb.sh` 继续直接调用 `pre_absorb_check.sh`
- 不强制修改现有调用链

## 八、下一阶段集成路径

### 8.1 短期（立即执行）

- 推广 `unified_validation_gate.py` 作为推荐默认验证方式
- 在文档中标注主线各阶段的推荐验证命令
- 保持现有脚本独立可用

### 8.2 中期（下一轮）

- 考虑在 `core/pack_and_permit.py` 中集成 quick 模式验证
- 考虑在 `absorb.sh` 中集成 absorb 模式验证
- 创建 local_accept 和 final_accept 的统一脚本入口

### 8.3 长期（后续优化）

- 统一所有验证调用到 `unified_validation_gate.py`
- 将现有验证脚本逐步迁移为内部实现
- 保持向后兼容的独立调用接口

## 九、快速参考

### 主线验证命令速查

```bash
# Quick 开发验证
python scripts/unified_validation_gate.py --quick --permit <permit>

# 完整主线验证
python scripts/unified_validation_gate.py --mainline --permit <permit> \
  --demand <d> --contract <c> --decision <d> --manifest <m>

# Absorb 验证
python scripts/unified_validation_gate.py --absorb --task-id <task>

# Cloud 任务验证
python scripts/unified_validation_gate.py --cloud --task-id <task>

# 安静模式（仅输出 ALLOW/DENY）
python scripts/unified_validation_gate.py --mode <mode> ... --quiet

# 指定输出文件
python scripts/unified_validation_gate.py --mode <mode> ... --output validation.json
```

### 验证模式选择指南

| 场景 | 推荐模式 | 理由 |
|------|---------|------|
| 开发迭代 | `quick` | 快速反馈，跳过三哈希 |
| 正式发布 | `mainline` | 完整验证，包括三哈希 |
| Absorb 前检查 | `absorb` | 任务包完整性验证 |
| 云端任务回传 | `cloud` | Receipt + N-Boundary |
| 最终验收 | `mainline` | 完整主线验证 |

---

**文档版本**: v1.0
**最后更新**: 2026-03-11
**维护者**: Agent C / TASK-MAIN-03
