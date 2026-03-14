# Execution Environments - LOCAL-ANTIGRAVITY & CLOUD-ROOT

## 📋 环境划分

从 **2026-03-05** 起，所有云端执行必须遵守以下环境划分：

| 环境 | 角色 | 用途 | 位置 |
|------|------|------|------|
| **LOCAL-ANTIGRAVITY** | 治理执行与审查 | 合同生成、回执校验、门禁裁决 | 本地开发环境 |
| **CLOUD-ROOT** | 业务执行 | 实际执行命令、生成回执 | 云端服务器 |

## 🔄 执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL-ANTIGRAVITY                            │
│                    (治理执行与审查)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 生成任务合同                                                 │
│     └─> create_cloud_task_contract.py                          │
│         └─> task_contract.json                                 │
│                                                                 │
│  2. 下发给 CLOUD-ROOT                                           │
│     └─> 发送 task_contract.json 到执行体                        │
│                                                                 │
│  5. 接收回执并校验                                               │
│     └─> verify_execution_receipt.py                            │
│         └─> 验证通过/失败                                       │
│                                                                 │
│  6. 生成审查/门禁决策                                            │
│     └─> verify_and_gate.py                                     │
│         └─> review_decision.json                               │
│         └─> final_gate.json                                    │
│                                                                 │
│  7. 运行强制门禁                                                 │
│     └─> cloud_lobster_mandatory_gate.py                        │
│         └─> ALLOW/DENY                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ 合同下发 / 回执回传
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       CLOUD-ROOT                                 │
│                       (业务执行)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  3. 接收任务合同                                                 │
│     └─> 读取 task_contract.json                                │
│                                                                 │
│  4. 执行并生成回执                                               │
│     ├─> 执行 command_allowlist 中的命令                         │
│     ├─> 生成 execution_receipt.json                            │
│     ├─> 保存 stdout.log                                        │
│     ├─> 保存 stderr.log                                        │
│     └─> 生成 audit_event.json                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## ⚠️ 强制规则

### LOCAL-ANTIGRAVITY 必须做：

1. ✅ 使用 `create_cloud_task_contract.py` 生成任务合同
2. ✅ 合同必须包含：
   - `task_id`
   - `baseline_id`
   - `environment: "CLOUD-ROOT"`
   - `command_allowlist`
   - `constraints.fail_closed: true`
3. ✅ 接收完整的四件套回执
4. ✅ 运行 `verify_execution_receipt.py` 验证
5. ✅ 运行 `cloud_lobster_mandatory_gate.py` 检查
6. ✅ 记录所有违规到 `docs/compliance_reviews/`

### CLOUD-ROOT 必须做：

1. ✅ 只执行 `command_allowlist` 中的命令
2. ✅ 不允许追加合同外命令
3. ✅ 生成完整的 `execution_receipt.json`
4. ✅ 回传完整的四件套：
   - `execution_receipt.json`
   - `stdout.log`
   - `stderr.log`
   - `audit_event.json`

### 禁止行为：

❌ **LOCAL-ANTIGRAVITY**：
- 禁止跳过合同生成直接执行
- 禁止接受不完整的回执
- 禁止跳过验证步骤

❌ **CLOUD-ROOT**：
- 禁止执行 allowlist 之外的命令
- 禁止不生成回执
- 禁止回传不完整的四件套

## 🔍 强制门禁

运行强制门禁以验证合规性：

```powershell
# LOCAL-ANTIGRAVITY 环境运行
python scripts/cloud_lobster_mandatory_gate.py
```

**检查项目**：
1. ✅ 任务有有效的 `task_contract.json`
2. ✅ 任务有完整的 `execution_receipt.json`
3. ✅ 回执通过 `verify_execution_receipt` 验证
4. ✅ 四件套完整
5. ✅ 有 `review_decision` 和 `final_gate` 决策

**结果**：
- **ALLOW**：所有检查通过，任务合规
- **DENY**：有违规，记录写入 `docs/compliance_reviews/`

## 📝 完整执行示例

### 1. LOCAL-ANTIGRAVITY：生成合同

```powershell
python skills/cloud-lobster-closed-loop-skill/scripts/create_cloud_task_contract.py `
  --task-id "tg1-official-20260305-1400" `
  --baseline-id "AG2-FIXED-CALIBER-TG1-20260304" `
  --objective "Check Docker containers status" `
  --allow "docker compose ps" `
  --allow "docker compose logs --since 10m openclaw-agent | tail -n 200" `
  --allow "df -h" `
  --allow "free -m"
```

输出：
```
[ok] task_id=tg1-official-20260305-1400
[ok] contract=.tmp/openclaw-dispatch/tg1-official-20260305-1400/task_contract.json
[ok] handoff=.tmp/openclaw-dispatch/tg1-official-20260305-1400/handoff_note.md
```

### 2. LOCAL-ANTIGRAVITY：下发合同

将 `task_contract.json` 发送给 CLOUD-ROOT 的执行体（Antigravity-3）

### 3. CLOUD-ROOT：执行并生成回执

执行体按照合同执行命令，生成回执：

```json
// execution_receipt.json
{
  "receipt_version": "1.0",
  "task_id": "tg1-official-20260305-1400",
  "executor": {
    "name": "Antigravity-3",
    "type": "cloud-agent",
    "version": "1.0.0"
  },
  "execution_summary": {
    "commands_executed": ["docker compose ps", "docker compose logs ...", "df -h", "free -m"],
    "total_commands": 4,
    "exit_code": 0
  },
  "artifacts": {
    "stdout_path": "stdout.log",
    "stderr_path": "stderr.log",
    "audit_path": "audit_event.json"
  },
  "final_status": "COMPLETED"
}
```

### 4. LOCAL-ANTIGRAVITY：验证回执

```powershell
python scripts/verify_execution_receipt.py `
  --contract ".tmp/openclaw-dispatch/tg1-official-20260305-1400/task_contract.json" `
  --receipt ".tmp/openclaw-dispatch/tg1-official-20260305-1400/execution_receipt.json"
```

输出：
```
status: PASS
checked_at: 2026-03-05T14:05:00Z
```

### 5. LOCAL-ANTIGRAVITY：生成审查/门禁决策

```powershell
python skills/cloud-lobster-closed-loop-skill/scripts/verify_and_gate.py `
  --task-id "tg1-official-20260305-1400" `
  --reviewer "Kior-C" `
  --gatekeeper "Antigravity-1" `
  --verification-dir "docs/2026-03-05/verification"
```

输出：
```
[ok] decision=ALLOW
[ok] review=docs/2026-03-05/verification/tg1-official-20260305-1400_review_decision.json
[ok] final_gate=docs/2026-03-05/verification/tg1-official-20260305-1400_final_gate.json
```

### 6. LOCAL-ANTIGRAVITY：运行强制门禁

```powershell
python scripts/cloud_lobster_mandatory_gate.py --task-id "tg1-official-20260305-1400"
```

输出：
```
==============================================================
[CL-MG] Cloud Lobster Mandatory Gate
[CL-MG] Started at 2026-03-05T14:06:00Z
[CL-MG] Environment: LOCAL-ANTIGRAVITY -> CLOUD-ROOT
[CL-MG] Dispatch dir: .tmp/openclaw-dispatch
==============================================================
[CL-MG] Final Decision: ALLOW
==============================================================

[CL-MG] ALLOW - All cloud tasks comply with mandatory gate
[CL-MG] ✓ Task contract present and valid
[CL-MG] ✓ Four artifacts complete
[CL-MG] ✓ Receipt verification passed
```

## 🚨 违规处理

如果强制门禁返回 **DENY**：

1. 查看 `docs/compliance_reviews/cloud_lobster_violation_*.json`
2. 根据错误代码修复问题
3. 重新运行门禁验证

---

**生效日期**：2026-03-05

**相关文档**：
- [cloud-lobster-closed-loop-skill](../../skills/cloud-lobster-closed-loop-skill/SKILL.md)
- [强制门禁脚本](../../scripts/cloud_lobster_mandatory_gate.py)
- [合规审查目录](../compliance_reviews/README.md)
