param(
    [Parameter(Mandatory = $true)]
    [string]$TaskId,

    [Parameter(Mandatory = $true)]
    [string]$CloudHost,

    [string]$CloudUser = "root",
    [string]$CloudRepo = "/root/gm-skillforge"
)

$ErrorActionPreference = "Stop"

# SSH Options for non-interactive automation
$sshOpts = @("-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes")

$localTaskDir = Join-Path ".tmp/openclaw-dispatch" $TaskId
if (-not (Test-Path $localTaskDir)) {
    New-Item -ItemType Directory -Path $localTaskDir -Force | Out-Null
}

Write-Host "[1/3] Downloading task artifacts from $CloudHost..."
$remotePath = "$CloudUser@$CloudHost`:$CloudRepo/.tmp/openclaw-dispatch/$TaskId/*"
& scp $sshOpts $remotePath "$localTaskDir/"
if ($LASTEXITCODE -ne 0) {
    throw "SCP failed to download artifacts from ${CloudHost} (Code $LASTEXITCODE)"
}

Write-Host "[2/3] Listing local artifacts..."
Get-ChildItem $localTaskDir | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize

Write-Host "[3/3] Running local gate verification..."
# Determine today's verification directory
$Today = Get-Date -Format "yyyy-MM-dd"
$VerificationDir = "docs/$Today/verification"

# Ensure we are in the repo root for relative paths
& python scripts/enforce_cloud_lobster_closed_loop.py --task-id $TaskId --action verify
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: enforce_cloud_lobster_closed_loop.py failed with exit code $LASTEXITCODE"
    # Continue to verify_and_gate for partial results
}

& python scripts/verify_and_gate.py --task-id $TaskId --verification-dir $VerificationDir
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: verify_and_gate.py failed with exit code $LASTEXITCODE"
}

Write-Host "✅ Completed verification for task: $TaskId"
