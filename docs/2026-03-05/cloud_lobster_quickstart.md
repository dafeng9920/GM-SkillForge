# Cloud Lobster Closed Loop - 快速开始指南

> **⚠️ 重要**：从 2026-03-05 起，所有 CLOUD-ROOT 执行必须使用此流程。

## 🎯 一句话说明

**所有云端执行必须走闭环**：合同 → 执行 → 回执 → 验证 → 门禁 → 入库

## 🚀 5分钟快速开始

### 1. 生成任务合同

```powershell
python skills/cloud-lobster-closed-loop-skill/scripts/create_cloud_task_contract.py `
  --task-id "my-task-20260305" `
  --baseline-id "AG2-FIXED-CALIBER-TG1-20260304" `
  --objective "任务描述" `
  --allow "命令1" `
  --allow "命令2" `
  --allow "命令3"
```

**参数说明**：
- `--task-id`: 任务唯一标识（建议格式：`<name>-YYYYMMDD`）
- `--baseline-id`: 基线 ID（固定使用 `AG2-FIXED-CALIBER-TG1-20260304`）
- `--objective`: 任务目标描述
- `--allow`: 允许执行的命令（可多次使用）

### 2. 下发给执行体

将生成的合同发送给 CLOUD-ROOT 执行体：

```powershell
# 合同位置
.tmp/openclaw-dispatch/<task-id>/task_contract.json

# 发送给执行体（Antigravity-3）
```

### 3. 执行体执行并回传

执行体（CLOUD-ROOT）会：
1. 只执行 `command_allowlist` 中的命令
2. 生成四件套回执：
   - `execution_receipt.json`
   - `stdout.log`
   - `stderr.log`
   - `audit_event.json`

### 4. 验证回执

```powershell
python scripts/verify_execution_receipt.py `
  --contract ".tmp/openclaw-dispatch/<task-id>/task_contract.json" `
  --receipt ".tmp/openclaw-dispatch/<task-id>/execution_receipt.json"
```

**期望输出**：`status: PASS`

### 5. 生成审查决策

```powershell
python skills/cloud-lobster-closed-loop-skill/scripts/verify_and_gate.py `
  --task-id "<task-id>" `
  --reviewer "Kior-C" `
  --gatekeeper "Antigravity-1" `
  --verification-dir "docs/2026-03-05/verification"
```

**期望输出**：`decision=ALLOW`

### 6. 运行强制门禁

```powershell
python scripts/cloud_lobster_mandatory_gate.py --task-id "<task-id>"
```

**期望输出**：`Final Decision: ALLOW`

## ❌ 常见错误

### 错误 1：没有合同

```
[SF_CLOUD_LOBSTER_NO_CONTRACT] No task_contract.json found
```

**解决**：运行步骤 1 生成合同

### 错误 2：四件套缺失

```
[SF_CLOUD_LOBSTER_ARTIFACTS_MISSING] Missing artifacts: stdout.log, audit_event.json
```

**解决**：确保执行体回传所有四个文件

### 错误 3：验证失败

```
[SF_CLOUD_LOBSTER_VERIFICATION_FAILED] Verification failed
```

**解决**：
1. 查看详细错误信息
2. 检查回执是否与合同一致
3. 确保所有命令都在 allowlist 中

### 错误 4：绕过尝试

```
[SF_CLOUD_LOBSTER_BYPASS_ATTEMPT] Detected bypass attempt
```

**解决**：
**立即停止**，按照完整流程重新执行

## 📋 检查清单

使用以下清单确保合规：

- [ ] 使用 `create_cloud_task_contract.py` 生成了合同
- [ ] 合同包含所有必需字段
- [ ] 执行体只执行 allowlist 中的命令
- [ ] 执行体生成了完整的四件套
- [ ] 运行了 `verify_execution_receipt.py` 并通过
- [ ] 运行了 `verify_and_gate.py` 并得到 ALLOW
- [ ] 运行了 `cloud_lobster_mandatory_gate.py` 并得到 ALLOW

## 🔍 故障排查

### 查看任务状态

```powershell
# 查看任务目录
ls .tmp/openclaw-dispatch/<task-id>/

# 应该看到：
# - task_contract.json
# - handoff_note.md
# - execution_receipt.json
# - stdout.log
# - stderr.log
# - audit_event.json
```

### 查看验证结果

```powershell
# 详细验证输出
python scripts/verify_execution_receipt.py `
  --contract ".tmp/openclaw-dispatch/<task-id>/task_contract.json" `
  --receipt ".tmp/openclaw-dispatch/<task-id>/execution_receipt.json"
```

### 查看违规记录

```powershell
# 查看最新的违规记录
ls docs/compliance_reviews/cloud_lobster_violation_*.json | Select-Object -Last 1 | Get-Content
```

## 📚 更多信息

- [完整文档](../../skills/cloud-lobster-closed-loop-skill/SKILL.md)
- [环境划分](./execution_environments.md)
- [合规审查](../compliance_reviews/README.md)
- [强制门禁](../../scripts/cloud_lobster_mandatory_gate.py)

---

**生效日期**：2026-03-05
**执行环境**：LOCAL-ANTIGRAVITY → CLOUD-ROOT
**强制策略**：FAIL-CLOSED
