---
name: cloud-lobster-closed-loop-skill
description: 固定口径下的云端小龙虾闭环执行 Skill。用于在 LOCAL-ANTIGRAVITY 生成受限任务合同、下发到 CLOUD-ROOT 执行、强制四件套回传、运行本地回执校验、产出 review/final gate 决策并入库。适用于”要上云执行但必须 fail-closed 且可审计”的任务。
---

# cloud-lobster-closed-loop-skill

## 目标

**强制**把云端执行固定为单一路径（FAIL-CLOSED）：
`合同生成 -> 小龙虾执行 -> 四件套回传 -> 本地复验 -> 门禁裁决 -> 入库`

> **⚠️ MANDATORY POLICY (2026-03-05 起)**
> 从下一单开始，**所有** CLOUD-ROOT 执行**必须**使用此 Skill。
> 任何绕过 `task_contract` 或 `verify_execution_receipt` 的行为将：
> 1. 被强制门禁 `scripts/cloud_lobster_mandatory_gate.py` 立即 BLOCK
> 2. 违规记录自动写入 `docs/compliance_reviews/`
> 3. 触发合规审查流程
>
> **执行环境划分**：
> - **治理执行与审查**：LOCAL-ANTIGRAVITY
> - **业务执行**：CLOUD-ROOT

## 硬规则（必须）

- `fail_closed=true`：任一步缺失即 DENY
- **所有 CLOUD-ROOT 任务**必须**通过此闭环流程**
- 只允许 `command_allowlist`
- 必须回传四件套：`execution_receipt.json`, `stdout.log`, `stderr.log`, `audit_event.json`
- 回执必须通过脚本校验，不接受口头 PASS
- **不允许绕过 `task_contract` 直接执行**
- **不允许跳过 `verify_execution_receipt` 验证**
- 通过后才允许入库（review + final gate 都是 ALLOW）

## Step 1：本地生成任务合同（LOCAL-ANTIGRAVITY）

运行：

```powershell
python skills/cloud-lobster-closed-loop-skill/scripts/create_cloud_task_contract.py `
  --task-id "tg1-official-YYYYMMDD-HHMM" `
  --baseline-id "AG2-FIXED-CALIBER-TG1-20260304" `
  --objective "Official CLOUD-ROOT task" `
  --allow "docker compose ps" `
  --allow "docker compose logs --since 10m openclaw-agent | tail -n 200" `
  --allow "ss -lntp | grep 18789 || true" `
  --allow "df -h" `
  --allow "free -m" `
  --allow "uptime"
```

输出目录：
- `.tmp/openclaw-dispatch/<task_id>/task_contract.json`
- `.tmp/openclaw-dispatch/<task_id>/handoff_note.md`

## Step 2：下发给小龙虾执行（CLOUD-ROOT）

把 `task_contract.json` 发给 `Antigravity-3（小龙虾）`。
只允许执行合同内命令，禁止追加合同外命令。

## Step 3：回传四件套（LOCAL-ANTIGRAVITY）

回传到 `.tmp/openclaw-dispatch/<task_id>/`：
- `execution_receipt.json`
- `stdout.log`
- `stderr.log`
- `audit_event.json`

## Step 4：本地复验并生成审查/门禁决策（LOCAL-ANTIGRAVITY）

运行：

```powershell
python skills/cloud-lobster-closed-loop-skill/scripts/verify_and_gate.py `
  --task-id "<task_id>" `
  --reviewer "Kior-C" `
  --gatekeeper "Antigravity-1" `
  --verification-dir "docs/2026-03-06/verification"
```

产出：
- `<verification-dir>/<task_id>_review_decision.json`
- `<verification-dir>/<task_id>_final_gate.json`

判定规则：
- `verify_execution_receipt.py` PASS => review/final 都 ALLOW
- 否则 DENY，失败项进入 `required_changes`

## Step 5：入库条件（LOCAL-ANTIGRAVITY）

满足全部才入库：
- `review_decision.status == ALLOW`
- `final_gate.decision == ALLOW`
- `blocking_evidence == []`
- `required_changes == []`
- 通过 `scripts/cloud_lobster_mandatory_gate.py` 检查

否则保持 `CONTINUE_GOVERNANCE`，并先完成修复再复验。

## 强制门禁（MANDATORY GATE）

运行强制门禁以验证合规性：

```powershell
# 检查特定任务
python scripts/cloud_lobster_mandatory_gate.py --task-id "<task_id>"

# 检查所有任务
python scripts/cloud_lobster_mandatory_gate.py
```

如果返回 DENY，违规记录将自动写入 `docs/compliance_reviews/cloud_lobster_violation_*.json`。

**门禁检查项目**：
1. 任务是否有有效的 `task_contract.json`
2. 任务是否有完整的 `execution_receipt.json`
3. 回执是否通过 `verify_execution_receipt` 验证
4. 是否有完整的四件套回传
5. 是否有 `review_decision` 和 `final_gate` 决策

**违规记录格式**：
```json
{
  "report_type": "cloud_lobster_violation",
  "generated_at": "2026-03-05T...",
  "task_id": "...",
  "decision": "DENY",
  "error_code": "SF_CLOUD_LOBSTER_*",
  "errors": [...],
  "required_changes": [...],
  "violation_evidence": {...},
  "governance_context": {
    "enforcement_environment": "LOCAL-ANTIGRAVITY",
    "target_environment": "CLOUD-ROOT",
    "enforced_skill": "cloud-lobster-closed-loop-skill",
    "fail_closed_policy": true
  }
}
```

## 参考

- 执行提示词包：`references/prompt-pack.md`
- 合同生成脚本：`scripts/create_cloud_task_contract.py`
- 复验/门禁脚本：`scripts/verify_and_gate.py`
- **强制门禁脚本**：`scripts/cloud_lobster_mandatory_gate.py`
- 回执校验器：`skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py`
- **合规审查目录**：`docs/compliance_reviews/`
