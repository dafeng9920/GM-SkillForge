# R1 下单 Skill 模板（可直接给执行体）

## 0) 目标
在 **CLOUD-ROOT** 执行一单基础链路回归任务（R1），并在 **LOCAL-ANTIGRAVITY** 完成双门禁复验。

---

## 1) 固定约束（不得改动）
- `fail_closed=true`
- 必须有 `task_contract.json`
- 必须回传四件套：
  - `execution_receipt.json`
  - `stdout.log`
  - `stderr.log`
  - `audit_event.json`
- 回执字段必须包含：
  - `task_id`
  - `status` (`success|failure`)
  - `executed_commands`
  - `exit_code`
  - `artifacts`
  - `summary`

---

## 2) 下单参数（只改变量）
- `TASK_ID`: `r1-cloud-smoke-YYYYMMDD-HHMM`
- `BASELINE_ID`: `AG2-FIXED-CALIBER-TG1-20260304`
- `OBJECTIVE`: `R1 CLOUD-ROOT 基础链路回归（目录/版本/资源）`

---

## 3) 合同模板（执行体生成并落盘）
路径：
`.tmp/openclaw-dispatch/r1-cloud-smoke-20260305-2353/task_contract.json`

```json
{
  "task_id": "r1-cloud-smoke-20260305-2353",
  "baseline_id": "AG2-FIXED-CALIBER-TG1-20260304",
  "objective": "R1 CLOUD-ROOT 基础链路回归（目录/版本/资源）",
  "environment": "CLOUD-ROOT",
  "constraints": {
    "fail_closed": true
  },
  "policy": {
    "max_commands": 6
  },
  "command_allowlist": [
    "cd /root/gm-skillforge",
    "pwd",
    "python3 --version",
    "df -h",
    "free -m",
    "uptime"
  ],
  "required_artifacts": [
    "execution_receipt.json",
    "stdout.log",
    "stderr.log",
    "audit_event.json"
  ],
  "acceptance": [
    "execution_receipt.status == success",
    "execution_receipt.exit_code == 0",
    "executed_commands are a subset of command_allowlist",
    "required_artifacts are complete"
  ]
}
```

---

## 4) 执行体操作模板（CLOUD-ROOT）
```bash
cd /root/gm-skillforge
python3 scripts/execute_antigravity_task.py --task-id r1-cloud-smoke-20260305-2353 --no-verify
```

回传目录（云端）：
`/root/gm-skillforge/.tmp/openclaw-dispatch/r1-cloud-smoke-20260305-2353/`

---

## 5) 本地回收 + 复验模板（LOCAL-ANTIGRAVITY）
```powershell
powershell -File scripts/fetch_cloud_task_artifacts.ps1 `
  -TaskId "r1-cloud-smoke-20260305-2353" `
  -CloudHost "BlueLobster-Cloud" `
  -CloudUser "root" `
  -CloudRepo "/root/gm-skillforge"

python scripts/enforce_cloud_lobster_closed_loop.py --task-id r1-cloud-smoke-20260305-2353 --action verify
python scripts/verify_and_gate.py --task-id r1-cloud-smoke-20260305-2353 --verification-dir docs/2026-03-06/verification
```

---

## 6) 判定标准
- `Gate1=PASS`
- `Gate2=ALLOW`
- `overall=PASS`

若任一不满足：
- 立即 `DENY`
- 输出 `required_changes`
- 禁止口头放行


