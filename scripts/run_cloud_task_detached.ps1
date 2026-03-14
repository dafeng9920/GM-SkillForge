param(
    [Parameter(Mandatory = $true)]
    [string]$TaskId,

    [Parameter(Mandatory = $true)]
    [string]$CloudHost,

    [string]$CloudUser = "root",
    [string]$CloudRepo = "/root/gm-skillforge"
)

$ErrorActionPreference = "Stop"

# SSH/SCP options for non-interactive automation and quicker failure on stuck links
$sshOpts = @(
    "-o", "StrictHostKeyChecking=no",
    "-o", "ConnectTimeout=10",
    "-o", "ConnectionAttempts=1",
    "-o", "ServerAliveInterval=5",
    "-o", "ServerAliveCountMax=2",
    "-o", "BatchMode=yes"
)

$localTaskDir = Join-Path ".tmp/openclaw-dispatch" $TaskId
$localContract = Join-Path $localTaskDir "task_contract.json"
$localHandoff = Join-Path $localTaskDir "handoff_note.md"
$localExecutor = "scripts/execute_antigravity_task.py"

if (-not (Test-Path $localContract)) {
    throw "task_contract.json not found: $localContract"
}
if (-not (Test-Path $localExecutor)) {
    throw "executor script not found: $localExecutor"
}

Write-Host "[1/4] Ensuring remote task directory..."
$remoteDirs = "$CloudRepo/.tmp/openclaw-dispatch/$TaskId /var/log/gm-skillforge /var/run"
& ssh $sshOpts "$CloudUser@$CloudHost" "mkdir -p $remoteDirs"
if ($LASTEXITCODE -ne 0) { throw "SSH failed to ensure directory (Code $LASTEXITCODE)" }

Write-Host "[2/4] Uploading contract artifacts..."
& scp $sshOpts "$localContract" "$CloudUser@$CloudHost`:$CloudRepo/.tmp/openclaw-dispatch/$TaskId/task_contract.json"
if ($LASTEXITCODE -ne 0) { throw "SCP failed to upload contract (Code $LASTEXITCODE)" }

if (Test-Path $localHandoff) {
    & scp $sshOpts "$localHandoff" "$CloudUser@$CloudHost`:$CloudRepo/.tmp/openclaw-dispatch/$TaskId/handoff_note.md"
    if ($LASTEXITCODE -ne 0) { throw "SCP failed to upload handoff note (Code $LASTEXITCODE)" }
}

Write-Host "[2.5/4] Uploading cloud executor script..."
& scp $sshOpts "$localExecutor" "$CloudUser@$CloudHost`:$CloudRepo/scripts/execute_antigravity_task.py"
if ($LASTEXITCODE -ne 0) { throw "SCP failed to upload executor script (Code $LASTEXITCODE)" }

Write-Host "[3/4] Starting detached execution on CLOUD-ROOT..."
$remoteCmd = @"
mkdir -p /var/log/gm-skillforge /var/run
cd $CloudRepo
if command -v python3 >/dev/null 2>&1; then
  PY_BIN=python3
elif command -v python >/dev/null 2>&1; then
  PY_BIN=python
else
  echo "ERROR: neither python3 nor python found in PATH" > /var/log/gm-skillforge/$TaskId.nohup.log
  exit 127
fi
# IMPORTANT: Use PowerShell escaping (`$) so remote shell receives $PY_BIN and $! literally.
nohup `$PY_BIN scripts/execute_antigravity_task.py --task-id $TaskId --no-verify > /var/log/gm-skillforge/$TaskId.nohup.log 2>&1 &
echo `$! > /var/run/$TaskId.pid
echo STARTED
"@

& ssh $sshOpts "$CloudUser@$CloudHost" $remoteCmd
if ($LASTEXITCODE -ne 0) {
    throw "Failed to start remote task on $CloudHost (Code $LASTEXITCODE)"
}

Write-Host "[4/4] Done."
Write-Host "Remote PID file: /var/run/$TaskId.pid"
Write-Host "Remote log:      /var/log/gm-skillforge/$TaskId.nohup.log"
Write-Host "After 2h, run:   powershell -File scripts/fetch_cloud_task_artifacts.ps1 -TaskId $TaskId -CloudHost $CloudHost -CloudUser $CloudUser -CloudRepo $CloudRepo"
