# 本地主链统一入口 - T-ASM-01 交付说明

- **任务ID**: T-ASM-01
- **日期**: 2026-03-10
- **角色**: Execution Agent A
- **返工版本**: v2 (修复 T-ASM-02 接口冲突)

## 一、交付文件清单

### 1. 核心脚本（新增）

| 文件 | 用途 |
|------|------|
| `scripts/local_accept.py` | Local Accept 统一入口 |
| `scripts/final_accept.py` | Final Accept 统一入口 |

### 2. 执行报告（新增）

| 文件 | 用途 |
|------|------|
| `docs/2026-03-10/verification/T_ASM_01_execution_report.yaml` | 正式执行报告 |

### 3. 依赖文件（T-ASM-02）

| 文件 | 用途 | 关系 |
|------|------|------|
| `core/runtime_interface.py` | 统一最小运行接口 | T-ASM-02 交付，本任务依赖 |

## 二、本地主链完整路径

### 主链结构

```
Permit → pre_absorb_check → absorb → local_accept → final_accept
   ↓           ↓                ↓           ↓              ↓
 (已有)      (已有)           (已有)      (新增)         (新增)
```

### 各节点说明

1. **Permit** (已有) - 不修改
2. **pre_absorb_check** (已有) - 不修改
3. **absorb** (已有) - 不修改
4. **local_accept** (新增) - 在 absorb 后执行
5. **final_accept** (新增) - 在 local_accept 后执行

## 三、与 T-ASM-02 的关系

### 接口定义依赖

T-ASM-01 **不定义独立的接口 Schema**，而是依赖 T-ASM-02 的 `core/runtime_interface.py`：

| 接口 | T-ASM-02 定义位置 | T-ASM-01 使用方式 |
|------|------------------|------------------|
| RunRequest | `core/runtime_interface.py:RunRequest` | local_accept 不直接使用 |
| RunResult | `core/runtime_interface.py:RunResult` | local_accept 不直接使用 |
| ArtifactManifest | `core/runtime_interface.py:ArtifactManifest` | future integration |
| ArtifactKind | `core/runtime_interface.py:ArtifactKind` | 枚举: blueprint/contract/code/test/evidence/config/documentation/other |

### 删除的冲突文件（v1 交付）

以下文件已删除，因为与 T-ASM-02 冲突：
- `schemas/local_run_request.schema.json`
- `schemas/local_run_result.schema.json`
- `schemas/artifact_manifest.schema.json`

## 四、统一入口使用说明

### 4.1 Local Accept

```bash
# 基本用法
python scripts/local_accept.py --task-id T-LOCAL-01

# 指定日期
python scripts/local_accept.py --task-id T-LOCAL-01 --date 2026-03-10

# 指定验证目录
python scripts/local_accept.py --task-id T-LOCAL-01 --verification-dir docs/2026-03-10/verification
```

**功能**：
- 检查 Execution Report 是否存在且完整
- 检查 Deliverables 是否齐全
- 检查 Evidence Refs 是否有效
- 检查 Gate Decision（非阻塞）
- 检查 Compliance Attestation（非阻塞）

**输出**：`docs/{date}/verification/{task_id}_local_accept_decision.json`

### 4.2 Final Accept

```bash
# 基本用法
python scripts/final_accept.py --task-id T-LOCAL-01

# 指定日期
python scripts/final_accept.py --task-id T-LOCAL-01 --date 2026-03-10

# 指定验证目录
python scripts/final_accept.py --task-id T-LOCAL-01 --verification-dir docs/2026-03-10/verification
```

**功能**：
- 聚合 Execution / Gate Decision / Compliance Attestation
- 验证三权分立记录完整性
- 检查 Compliance 先于 Execution（precedence 硬规则）
- 执行最终裁决：ALLOW / REQUIRES_CHANGES / DENY

**输出**：`docs/{date}/verification/{task_id}_final_accept_decision.json`

## 五、兼容性说明

### 5.1 与前半段的兼容性

| 现有组件 | 兼容性 | 说明 |
|---------|-------|------|
| `permits/default/tg1_baseline_permit.json` | ✅ 不修改 | 新脚本不干预 Permit 机制 |
| `scripts/validate_permit_binding.py` | ✅ 不调用 | 新脚本在 absorb 后执行 |
| `scripts/pre_absorb_check.sh` | ✅ 不干预 | 新脚本只读取后续产物 |
| `scripts/absorb.sh` | ✅ 不修改 | 新脚本只读取 execution_report |

### 5.2 与现有 gate 脚本的兼容性

| 现有脚本 | 兼容性 | 说明 |
|---------|-------|------|
| `scripts/antigravity_final_gate.py` | ✅ 并存 | 针对云端任务（Antigravity-Gemini） |
| `scripts/gate_final_decision.py` | ✅ 并存 | L4P5 专用 |
| `scripts/verify_and_gate.py` | ✅ 并存 | 针对云端任务的 dual gate |
| `scripts/local_accept.py` | 新增 | 本地主链通用版本 |
| `scripts/final_accept.py` | 新增 | 本地主链通用版本 |

## 六、风险点与未完成项

### 6.1 风险点

1. **YAML 依赖**: `local_accept.py` 依赖 PyYAML，如未安装会降级为 JSON
2. **路径假设**: 默认使用 `docs/{date}/verification/` 路径
3. **时间戳解析**: Compliance precedence 检查可能因格式问题失败
4. **尚未集成**: 新入口尚未被具体 Agent 调用

### 6.2 未完成项（需后续任务）

1. 最小运行接口的实际 Agent 集成使用
2. 本地多Agent并行调度逻辑实现
3. pyyaml 添加到 requirements.txt
4. 与 T-ASM-02 的自动同步机制

## 七、证据引用

### 实际修改的文件

1. `scripts/local_accept.py` - 新建
2. `scripts/final_accept.py` - 新建
3. `docs/2026-03-10/verification/T_ASM_01_execution_report.yaml` - 新建

### 删除的冲突文件

1. `schemas/local_run_request.schema.json` - 已删除（与 T-ASM-02 冲突）
2. `schemas/local_run_result.schema.json` - 已删除（与 T-ASM-02 冲突）
3. `schemas/artifact_manifest.schema.json` - 已删除（与 T-ASM-02 冲突）

### 依赖的 T-ASM-02 文件

1. `core/runtime_interface.py` - T-ASM-02 交付，定义 RunRequest/RunResult/ArtifactManifest

## 八、结论

T-ASM-01 任务已完成本地主链后半段统一入口补齐：

1. ✅ 新增 `local_accept.py` - Local Accept 统一入口
2. ✅ 新增 `final_accept.py` - Final Accept 统一入口
3. ✅ 创建正式的 `execution_report.yaml`
4. ✅ 修复与 T-ASM-02 的接口冲突
5. ✅ 保持与 Permit/pre_absorb_check/absorb 完全兼容

主链现在已完整：
**Permit → pre_absorb_check → absorb → local_accept → final_accept**
