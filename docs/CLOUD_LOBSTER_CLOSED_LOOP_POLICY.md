# CLOUD-LOBSTER-CLOSED-LOOP 强制执行策略

**生效日期**: 2026-03-05
**执行环境**: LOCAL-ANTIGRAVITY (治理执行) → CLOUD-ROOT (业务执行)
**策略级别**: HARD / FAIL-CLOSED

## 📋 策略声明

从 2026-03-05 起，**所有 CLOUD-ROOT 任务必须强制使用 `cloud-lobster-closed-loop-skill`**。

任何绕过 `task_contract` 或 `verify_execution_receipt` 的行为将立即被 **BLOCK** 并记录到 `docs/compliance_reviews/`。

## 🚪 执行路径 (唯一合法路径)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LOCAL-ANTIGRAVITY (治理层)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Step 1: 生成任务合同                                                 │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ python skills/cloud-lobster-closed-loop-skill/scripts/      │    │
│  │   create_cloud_task_contract.py \                           │    │
│  │   --task-id "tg1-official-YYYYMMDD-HHMM" \                  │    │
│  │   --baseline-id "AG2-SOVEREIGNTY-ROOT-YYYY-MM-DD" \         │    │
│  │   --objective "..." \                                        │    │
│  │   --allow "command1" --allow "command2"                      │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                      ↓ 输出: .tmp/openclaw-dispatch/<task_id>/       │
│                         - task_contract.json                         │
│                         - handoff_note.md                            │
│                                                                       │
│  Step 2: 执行前强制检查 (NEW)                                         │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ python scripts/enforce_cloud_lobster_closed_loop.py \       │    │
│  │   --task-id "<task_id>" --action dispatch                   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                      ↓ ALLOW/BLOCK                                   │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                                  ↓
┌───────────────────────────────────────────────────────────────────────┐
│                       CLOUD-ROOT (业务执行层)                          │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Step 3: 执行任务 (只执行 command_allowlist 中的命令)                  │
│  - Antigravity-3 (小龙虾) 作为执行体                                   │
│  - 禁止执行合同外命令                                                  │
│  - 记录所有执行日志                                                    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                                  ↓ 回传四件套
┌───────────────────────────────────────────────────────────────────────┐
│                    LOCAL-ANTIGRAVITY (治理层)                         │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Step 4: 执行后强制检查 (NEW)                                         │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ python scripts/enforce_cloud_lobster_closed_loop.py \       │    │
│  │   --task-id "<task_id>" --action verify                     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                      ↓ ALLOW/BLOCK                                   │
│                                                                       │
│  Step 5: 回执校验与门禁裁决                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ python skills/cloud-lobster-closed-loop-skill/scripts/      │    │
│  │   verify_and_gate.py \                                      │    │
│  │   --task-id "<task_id>" \                                   │    │
│  │   --verification-dir "docs/YYYY-MM-DD/verification"         │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                      ↓ 输出到 verification/                           │
│                         - <task_id>_review_decision.json             │
│                         - <task_id>_final_gate.json                  │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## 🔒 强制检查点 (Checkpoints)

### Checkpoint 1: Dispatch (执行前)

**文件**: `scripts/enforce_cloud_lobster_closed_loop.py --action dispatch`

**检查项**:
- ✅ `task_contract.json` 必须存在
- ✅ `schema_version` 必须是 `openclaw_task_contract_v1`
- ✅ `command_allowlist` 必须非空
- ✅ `required_artifacts` 必须包含 4 件套

**失败后果**: BLOCK → 写入 `docs/compliance_reviews/runs/YYYY-MM-DD/BLOCK_<task_id>_*.json`

### Checkpoint 2: Verify (执行后)

**文件**: `scripts/enforce_cloud_lobster_closed_loop.py --action verify`

**检查项**:
- ✅ `execution_receipt.json` 必须存在
- ✅ 四件套必须完整:
  - `execution_receipt.json`
  - `stdout.log`
  - `stderr.log`
  - `audit_event.json`
- ✅ `verify_execution_receipt.py` 必须返回 PASS

**失败后果**: BLOCK → 写入 `docs/compliance_reviews/runs/YYYY-MM-DD/BLOCK_<task_id>_*.json`

## 🚫 违规行为与后果

| 违规类型 | 检测方式 | 后果 |
|----------|----------|------|
| 无合同生成 | dispatch 时 task_contract.json 不存在 | BLOCK + 记录 |
| 使用非标准 schema | schema_version ≠ openclaw_task_contract_v1 | BLOCK + 记录 |
| 空白名单 | command_allowlist 为空 | BLOCK + 记录 |
| 无回执校验 | verify 时未运行 verify_execution_receipt.py | BLOCK + 记录 |
| 缺失交付物 | 四件套不完整 | BLOCK + 记录 |
| 口头 PASS | 未通过脚本校验直接 ALLOW | BLOCK + 记录 |

## 📝 合规审查记录格式

BLOCK 记录包含:
- `block_id`: 唯一标识符
- `task_id`: 被阻塞的任务 ID
- `bypass_reasons`: 违规原因列表
- `evidence`: 检测证据
- `remediation`: 修复步骤
- `blocked_at_utc`: 阻塞时间

记录位置:
- `docs/compliance_reviews/runs/YYYY-MM-DD/BLOCK_<task_id>_timestamp.json`
- `docs/compliance_reviews/runs/YYYY-MM-DD/BLOCK_<task_id>_timestamp.md`
- `docs/compliance_reviews/review_latest.json` (最新记录)

## 🔧 修复流程 (Remediation)

当任务被 BLOCK 后:

1. 查看 `docs/compliance_reviews/review_latest.json`
2. 按照其中的 `remediation` 步骤修复
3. 重新生成符合要求的 `task_contract.json`
4. 重新执行并通过 `verify_execution_receipt.py`
5. 确认 `review_decision.status = ALLOW` 且 `final_gate.decision = ALLOW`

## 📚 参考文档

- Skill 规范: `skills/cloud-lobster-closed-loop-skill/SKILL.md`
- 合同生成: `skills/cloud-lobster-closed-loop-skill/scripts/create_cloud_task_contract.py`
- 回执校验: `skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py`
- 门禁裁决: `skills/cloud-lobster-closed-loop-skill/scripts/verify_and_gate.py`
- 强制检查: `scripts/enforce_cloud_lobster_closed_loop.py`
