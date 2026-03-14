param(
    [string]$HostIp = "152.136.25.101",
    [string]$User = "root",
    [string]$CloudBox = "/root/openclaw-box",
    [string]$CloudRepo = "/root/gm-skillforge"
)

$ErrorActionPreference = "Stop"

Write-Host "--- [1/2] Pushing Scripts to BOX ---" -ForegroundColor Cyan
ssh "$User@$HostIp" "mkdir -p $CloudBox/scripts"
if ($LASTEXITCODE -ne 0) { throw "SSH failed to create scripts dir" }

# Upload individual scripts
$scriptsToPush = @("verify_governance_env.sh", "pre_absorb_check.sh", "absorb.sh")
foreach ($s in $scriptsToPush) {
    Write-Host "Pushing $s..."
    scp "scripts/$s" "$User@$HostIp`:$CloudBox/scripts/"
    if ($LASTEXITCODE -ne 0) { throw "SCP failed for $s" }
}

Write-Host "--- [2/2] Pushing Skills to REPO ---" -ForegroundColor Cyan
ssh "$User@$HostIp" "mkdir -p $CloudRepo/skills"

$skills = @(
    "gm-multi-agent-orchestrator-skill",
    "lobster-task-package-skill",
    "lobster-absorb-gate-skill",
    "lobster-cloud-execution-governor-skill"
)

foreach ($skill in $skills) {
    Write-Host "Syncing $skill..."
    ssh "$User@$HostIp" "mkdir -p $CloudRepo/skills/$skill"
    # Copy directory content
    scp -r "skills/$skill/." "$User@$HostIp`:$CloudRepo/skills/$skill/"
    if ($LASTEXITCODE -ne 0) { Write-Warning "SCP issues for $skill (continuing...)" }
}

Write-Host "--- Final Verification ---" -ForegroundColor Yellow
ssh "$User@$HostIp" "ls -la $CloudBox/scripts/absorb.sh && ls -la $CloudRepo/skills/gm-multi-agent-orchestrator-skill/SKILL.md"

Write-Host "DONE." -ForegroundColor Green
