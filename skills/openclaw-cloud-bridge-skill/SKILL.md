---
name: openclaw-cloud-bridge-skill
description: 本地 Skill 指挥云端 OpenClaw 的闭环执行协议。用于生成任务合同、通过 Gemini 中继下发、校验云端回执并在本地完成审查。
---

# openclaw-cloud-bridge-skill

## 目标

建立稳定闭环:

1. 本地生成可审计任务合同（Task Contract）
2. Gemini 作为中继将合同传到云服务器
3. 云端 OpenClaw 严格按合同执行
4. 本地校验回执（Execution Receipt）并给出 PASS/FAIL

## 触发条件

- 用户要求“本地 Skill -> 云端 OpenClaw”执行闭环
- 需要将运行任务交给 Gemini 中继后远程执行
- 需要 fail-closed、命令白名单、可审计回放

## 关键约束（必须）

- `fail_closed`: 任一合同字段缺失则拒绝执行
- `command_allowlist`: 仅允许白名单命令
- `no_free_shell`: 禁止自由拼接任意命令
- `artifact_required`: 必须回传 `execution_receipt.json`
- `local_review_gate`: 本地未通过回执审查不得宣称完成
- `human_permit`: 任何破坏性命令必须人工放行（默认不允许）

## Preflight Checklist（执行前必须输出）

1. `IsolationCheck`: 执行端是否在受控环境（cloud host + contract mode）
2. `ScopeCheck`: 目标路径是否限定为 `/root/openclaw-box`（或合同指定路径）
3. `ImpactCheck`: 是否包含不可逆操作（删除、覆盖、系统级改动）

若任一项无法证明，立即 `FAIL_CLOSED`。

## 输入

```yaml
input:
  objective: "对云端 openclaw 做健康巡检"
  cloud_project_dir: "/root/openclaw-box"
  channel: "BlueLobster-Cloud"
  relay_agent: "Antigravity-Gemini"
  allowed_commands:
    - "docker compose ps"
    - "docker compose logs --since 10m openclaw-agent | tail -n 200"
    - "ss -lntp | grep 18789 || true"
    - "df -h"
    - "free -m"
  acceptance:
    - "openclaw_core is Up"
    - "no EACCES in last 10m logs"
    - "no Unknown model in last 10m logs"
```

## 输出

```yaml
output:
  task_contract: ".tmp/openclaw-dispatch/<task_id>/task_contract.json"
  handoff_note: ".tmp/openclaw-dispatch/<task_id>/handoff_note.md"
  receipt_expected: ".tmp/openclaw-dispatch/<task_id>/execution_receipt.json"
  local_review:
    decision: "PASS|FAIL"
    reasons: []
```

## 操作流程

### Step 1: 本地生成任务合同

运行:

```bash
python skills/openclaw-cloud-bridge-skill/scripts/create_task_contract.py ^
  --objective "OpenClaw 云端健康巡检" ^
  --project-dir "/root/openclaw-box" ^
  --allow "docker compose ps" ^
  --allow "docker compose logs --since 10m openclaw-agent | tail -n 200" ^
  --allow "ss -lntp | grep 18789 || true" ^
  --allow "df -h" ^
  --allow "free -m" ^
  --accept "openclaw_core is Up" ^
  --accept "no EACCES in last 10m logs" ^
  --accept "no Unknown model in last 10m logs"
```

### Step 2: Gemini 中继下发

将 `task_contract.json` 与 `handoff_note.md` 发送给 Gemini。
Gemini 在云端按合同顺序执行，禁止附加合同外命令。

### Step 3: 云端执行回传

云端必须回传:

- `execution_receipt.json`
- `stdout.log`
- `stderr.log`（可为空）
- `audit_event.json`（记录 permit/deny 与时间线）

### Step 4: 本地回执校验

```bash
python skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py ^
  --contract ".tmp/openclaw-dispatch/<task_id>/task_contract.json" ^
  --receipt ".tmp/openclaw-dispatch/<task_id>/execution_receipt.json"
```

若输出 `PASS`，闭环成立；否则 `FAIL` 并返回修复建议。

## DoD

- [ ] 任务合同已生成且包含 allowlist
- [ ] Gemini 执行命令与合同一致
- [ ] execution_receipt 校验通过
- [ ] 本地审查给出明确 PASS/FAIL
- [ ] 全流程可复盘（task_id 关联）
- [ ] 审计事件写入 `AuditPack/evidence/openclaw_cloud_bridge_<task_id>.json`

## 参考

- 合同 schema: `schemas/openclaw_cloud_task_contract.schema.json`
- 回执 schema: `schemas/openclaw_execution_receipt.schema.json`
- 示例: `skills/openclaw-cloud-bridge-skill/references/contract_examples.md`
