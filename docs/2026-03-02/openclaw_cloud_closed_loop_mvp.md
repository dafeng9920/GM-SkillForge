# OpenClaw 上云闭环 MVP（本地 Skill -> Gemini -> 云端 -> 本地审查）

## 1. 范围

本 MVP 仅覆盖“只读巡检任务”，不允许高风险写操作。

- 允许: `docker compose ps`, `logs`, `ss`, `df`, `free`
- 禁止: 安装软件、删文件、修改系统配置、任意 shell

## 2. 目录与文件

- Skill: `skills/openclaw-cloud-bridge-skill/SKILL.md`
- 任务合同脚本: `skills/openclaw-cloud-bridge-skill/scripts/create_task_contract.py`
- 回执校验脚本: `skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py`
- 合同 schema: `schemas/openclaw_cloud_task_contract.schema.json`
- 回执 schema: `schemas/openclaw_execution_receipt.schema.json`

## 3. 操作步骤

### Step A: 本地生成任务合同

```bash
python skills/openclaw-cloud-bridge-skill/scripts/create_task_contract.py \
  --objective "OpenClaw 云端健康巡检" \
  --project-dir "/root/openclaw-box" \
  --allow "docker compose ps" \
  --allow "docker compose logs --since 10m openclaw-agent | tail -n 200" \
  --allow "ss -lntp | grep 18789 || true" \
  --allow "df -h" \
  --allow "free -m" \
  --accept "openclaw_core is Up" \
  --accept "no EACCES in last 10m logs" \
  --accept "no Unknown model in last 10m logs"
```

脚本会生成：

- `.tmp/openclaw-dispatch/<task_id>/task_contract.json`
- `.tmp/openclaw-dispatch/<task_id>/handoff_note.md`

### Step B: Gemini 中继到云端

将上面两个文件交给 Gemini，要求:

- 仅执行 `task_contract.json.command_allowlist` 内命令
- 回传 `execution_receipt.json + stdout.log + stderr.log + audit_event.json`

### Step C: 本地审查回执

```bash
python skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py \
  --contract ".tmp/openclaw-dispatch/<task_id>/task_contract.json" \
  --receipt ".tmp/openclaw-dispatch/<task_id>/execution_receipt.json"
```

输出 `PASS` 才允许进入下一任务。

## 4. 验收标准

- 任务包生成成功，且 `contract_sha256` 存在
- 云端执行命令均在 allowlist 内
- `execution_receipt.status=success` 且 `exit_code=0`
- 必需 artifacts 完整回传
- 本地校验输出 `PASS`

## 5. 扩展顺序（后续）

1. 增加 `risk_level` 与审批人字段
2. 增加回执签名（Ed25519）
3. 引入预算熔断与超时 kill
4. 从“只读巡检”扩展到“受控修复”
