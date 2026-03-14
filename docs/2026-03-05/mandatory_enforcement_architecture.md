# Cloud Lobster Mandatory Enforcement Architecture

## 📐 架构概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        强制执行架构 (2026-03-05 起)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    cloud-lobster-closed-loop-skill                   │   │
│  │                       (强制闭环执行 Skill)                            │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  1. create_cloud_task_contract.py    ← 生成任务合同                   │   │
│  │  2. 下发到 CLOUD-ROOT                 ← 执行业务命令                   │   │
│  │  3. verify_and_gate.py               ← 验证并生成决策                  │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │ 强制门禁                                │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              cloud_lobster_mandatory_gate.py                         │   │
│  │                       (FAIL-CLOSED 门禁)                             │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ✓ 检查 task_contract.json                                           │   │
│  │  ✓ 检查 execution_receipt.json                                        │   │
│  │  ✓ 运行 verify_execution_receipt.py                                   │   │
│  │  ✓ 检查四件套完整性                                                   │   │
│  │  ✓ 检查 review/final_gate 决策                                        │   │
│  │                                                                      │   │
│  │  DENY → 写入 docs/compliance_reviews/                                │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔒 FAIL-CLOSED 策略

### 任何检查失败 → DENY + 阻断 + 记录

| 检查项 | 失败行为 | 记录位置 |
|-------|---------|---------|
| 无有效合同 | DENY | `docs/compliance_reviews/cloud_lobster_violation_*.json` |
| 无有效回执 | DENY | `docs/compliance_reviews/cloud_lobster_violation_*.json` |
| 四件套缺失 | DENY | `docs/compliance_reviews/cloud_lobster_violation_*.json` |
| 验证失败 | DENY | `docs/compliance_reviews/cloud_lobster_violation_*.json` |
| 绕过尝试 | DENY | `docs/compliance_reviews/cloud_lobster_violation_*.json` |

## 📁 文件结构

```
GM-SkillForge/
├── scripts/
│   └── cloud_lobster_mandatory_gate.py          # 强制门禁脚本
├── skills/
│   └── cloud-lobster-closed-loop-skill/
│       ├── SKILL.md                             # Skill 文档（已更新强制策略）
│       └── scripts/
│           ├── create_cloud_task_contract.py    # 合同生成
│           └── verify_and_gate.py               # 验证和门禁
├── docs/
│   ├── 2026-03-05/
│   │   ├── execution_environments.md            # 环境划分说明
│   │   └── cloud_lobster_quickstart.md          # 快速开始指南
│   └── compliance_reviews/
│       ├── README.md                            # 合规审查说明（已更新）
│       ├── review_latest.json                   # 最新审查结果
│       └── cloud_lobster_violation_*.json       # 违规记录（自动生成）
└── .tmp/
    └── openclaw-dispatch/
        └── <task-id>/
            ├── task_contract.json               # 任务合同
            ├── handoff_note.md                  # 移交说明
            ├── execution_receipt.json           # 执行回执
            ├── stdout.log                       # 标准输出
            ├── stderr.log                       # 标准错误
            └── audit_event.json                 # 审计事件
```

## 🔄 执行流程

### 正常流程（ALLOW）

```
1. LOCAL-ANTIGRAVITY: create_cloud_task_contract.py
   ↓ 生成 task_contract.json
2. 下发到 CLOUD-ROOT
   ↓ 执行命令
3. CLOUD-ROOT: 生成四件套
   ↓ 回传
4. LOCAL-ANTIGRAVITY: verify_execution_receipt.py
   ↓ PASS
5. LOCAL-ANTIGRAVITY: verify_and_gate.py
   ↓ ALLOW
6. LOCAL-ANTIGRAVITY: cloud_lobster_mandatory_gate.py
   ↓ ALLOW ✓
```

### 违规流程（DENY）

```
1. 尝试绕过或任何检查失败
   ↓
2. cloud_lobster_mandatory_gate.py
   ↓ DENY
3. 自动写入 docs/compliance_reviews/cloud_lobster_violation_*.json
   ↓
4. 阻断继续执行
   ↓
5. 需要修复并重新验证
```

## 🛡️ 安全保障

### 1. 合同约束

- 只允许执行 `command_allowlist` 中的命令
- 不允许追加合同外命令
- `fail_closed=true` 强制执行

### 2. 回执验证

- `verify_execution_receipt.py` 验证：
  - 回执结构完整性
  - 合同回执一致性
  - 命令边界检查
  - 安全审计

### 3. 四件套完整性

- 必须回传所有四个文件：
  - `execution_receipt.json`
  - `stdout.log`
  - `stderr.log`
  - `audit_event.json`

### 4. 强制门禁

- `cloud_lobster_mandatory_gate.py` 检查：
  - 合同存在且有效
  - 回执存在且有效
  - 四件套完整
  - 验证通过
  - 决策存在

### 5. 违规记录

- 所有 DENY 自动记录到 `docs/compliance_reviews/`
- 包含完整的违规证据
- 支持追溯和审计

## 📊 监控和审查

### 日常检查

```powershell
# 每日检查所有任务
python scripts/cloud_lobster_mandatory_gate.py
```

### 违规统计

```powershell
# 统计违规数量
ls docs/compliance_reviews/cloud_lobster_violation_*.json | Measure-Object

# 按类型统计
ls docs/compliance_reviews/cloud_lobster_violation_*.json | ForEach-Object {
    $content = Get-Content $_ | ConvertFrom-Json
    $content.error_code
} | Group-Object | Sort-Object Count -Descending
```

### 合规审查

```powershell
# 运行完整合规审查
python scripts/run_3day_compliance_review.py --run-tests
```

## 🎯 关键指标

| 指标 | 目标 | 监控方法 |
|-----|------|---------|
| 强制门禁通过率 | 100% | `cloud_lobster_mandatory_gate.py` |
| 违规记录数 | 0 | `docs/compliance_reviews/` |
| 四件套完整性 | 100% | 验证脚本 |
| 合同覆盖率 | 100% | 强制门禁 |

## 📝 错误代码

| 错误代码 | 描述 | 严重程度 |
|---------|------|---------|
| SF_CLOUD_LOBSTER_NO_CONTRACT | 无合同或合同无效 | CRITICAL |
| SF_CLOUD_LOBSTER_NO_RECEIPT | 无回执或回执无效 | CRITICAL |
| SF_CLOUD_LOBSTER_ARTIFACTS_MISSING | 四件套缺失 | CRITICAL |
| SF_CLOUD_LOBSTER_VERIFICATION_FAILED | 验证失败 | HIGH |
| SF_CLOUD_LOBSTER_BYPASS_ATTEMPT | 绕过尝试 | CRITICAL |

## 🔗 相关文档

- [Skill 文档](../../skills/cloud-lobster-closed-loop-skill/SKILL.md)
- [快速开始](./cloud_lobster_quickstart.md)
- [环境划分](./execution_environments.md)
- [合规审查](../compliance_reviews/README.md)

---

**生效日期**：2026-03-05
**策略**：FAIL-CLOSED
**执行环境**：LOCAL-ANTIGRAVITY → CLOUD-ROOT
