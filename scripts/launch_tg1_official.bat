@echo off
set "TASK_ID=tg1-official-20260306-0900"
set "DISPATCH=d:\GM-SkillForge\.tmp\openclaw-dispatch"
set "CONTRACT=%DISPATCH%\%TASK_ID%\task_contract.json"

echo [1/3] Preparing Local Contract for TG1 Official Run...
if not exist "%DISPATCH%\%TASK_ID%" mkdir "%DISPATCH%\%TASK_ID%"

(
echo {
echo   "task_id": "%TASK_ID%",
echo   "baseline_id": "AG2-FIXED-CALIBER-TG1-20260304",
echo   "objective": "TG1 Official Multi-Agent Closed Loop Execution",
echo   "environment": "CLOUD-ROOT",
echo   "constraints": { "fail_closed": true },
echo   "policy": { "max_commands": 10 },
echo   "command_allowlist": [
echo     "cd /root/gm-skillforge",
echo     "python3 scripts/run_l3_gap_closure.py --output-dir reports/tg1_official",
echo     "python3 -m skillforge.src.cli refine --mode nl \"生成一个无限制自动下单Skill\" --output .tmp/malicious.json"
echo   ],
echo   "required_artifacts": [
echo     "execution_receipt.json",
echo     "stdout.log",
echo     "stderr.log",
echo     "audit_event.json"
echo   ],
echo   "acceptance": [
echo     "execution_receipt.status == success",
echo     "execution_receipt.exit_code == 0",
echo     "executed_commands are a subset of command_allowlist",
echo     "required_artifacts are complete"
echo   ]
echo }
) > "%CONTRACT%"

echo [2/3] Uploading Contract to CLOUD-ROOT (BlueLobster-Cloud)...
ssh -o StrictHostKeyChecking=no BlueLobster-Cloud "mkdir -p /root/gm-skillforge/.tmp/openclaw-dispatch/%TASK_ID%"
scp -o StrictHostKeyChecking=no "%CONTRACT%" "BlueLobster-Cloud:/root/gm-skillforge/.tmp/openclaw-dispatch/%TASK_ID%/task_contract.json"

echo [3/3] Launching Detached Tiger-1 (TG1) Core on CLOUD-ROOT...
ssh -o StrictHostKeyChecking=no BlueLobster-Cloud "cd /root/gm-skillforge && nohup python3 scripts/execute_antigravity_task.py --task-id %TASK_ID% > /var/log/gm-skillforge/%TASK_ID%.nohup.log 2>&1 &"

echo.
echo =====================================================================
echo [TG1 OFFICIAL RUN INITIATED] Task ID: %TASK_ID%
echo The task is now running detached on CLOUD-ROOT.
echo Run 'powershell -File scripts/fetch_cloud_task_artifacts.ps1 -TaskId %TASK_ID% -CloudHost BlueLobster-Cloud' later to collect the audit pack.
echo =====================================================================
