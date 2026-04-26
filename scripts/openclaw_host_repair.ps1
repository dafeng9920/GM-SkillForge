# openclaw_host_repair.ps1 - OpenClaw Host-Cloud Alignment & Repair Script
# -------------------------------------------------------------------
# Function: Detect Env -> (Cloud) Build SSH Tunnel -> (Local) Align Port & Auth
# Execution: .\scripts\openclaw_host_repair.ps1 -Mode Cloud (Default) or -Mode Local
# -------------------------------------------------------------------

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Local", "Cloud")]
    [string]$Mode = "Cloud"
)

$ErrorActionPreference = "Stop" # Use Stop for cleaner error catching
$CLUSTER_JSON = "D:\GM-SkillForge\openclaw-box\openclaw_cluster.json"
$HOST_CONFIG_PATH = "$HOME\.openclaw"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   OpenClaw Life Support System (Mode: $Mode)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if ($Mode -eq "Cloud") {
    # 1. Find Cluster Config
    Write-Host "[1/4] [Cluster] Retrieving cloud cluster configuration..." -ForegroundColor Yellow
    if (-not (Test-Path $CLUSTER_JSON)) {
        Write-Host "Error: Cluster config not found at $CLUSTER_JSON" -ForegroundColor Red
        return
    }
    
    $config_raw = Get-Content $CLUSTER_JSON -Raw | ConvertFrom-Json
    $cluster = $config_raw.clusters[0]
    $publicIP = $cluster.host
    $hostPort = $cluster.port
    $internalPort = $cluster.internal_port
    $sshUser = $cluster.ssh_user

    Write-Host "OK: Locked Cluster -> $($cluster.description)" -ForegroundColor Green

    # 2. Build SSH Tunnel
    Write-Host "`n[2/4] [Tunnel] Establishing SSH Bridge (Local:$hostPort -> Remote:$internalPort)..." -ForegroundColor Yellow
    
    # Check if port is already in use
    try {
        $existing = Get-NetTCPConnection -LocalPort $hostPort -ErrorAction Stop
        if ($existing) {
            Write-Host "Warning: Port $hostPort is occupied. Trying to flush connection..." -ForegroundColor Gray
            Stop-Process -Id $existing.OwningProcess -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
    } catch {
        # Port not in use, proceed
    }

    $sshArgs = "-L ${hostPort}:127.0.0.1:${internalPort} ${sshUser}@${publicIP} -N"
    Write-Host "Executing: ssh $sshArgs" -ForegroundColor Gray
    
    # Start SSH in background
    Start-Process ssh -ArgumentList $sshArgs -NoNewWindow
    
    Start-Sleep -Seconds 3
    Write-Host "OK: Tunnel started." -ForegroundColor Green

    # 3. Browser Context Guard
    Write-Host "`n[3/4] [Browser] Security Context Guidance..." -ForegroundColor Yellow
    Write-Host "Note: If you see 'Secure Context Required', follow these steps:" -ForegroundColor Red
    Write-Host "1. Open: chrome://flags/#unsafely-treat-insecure-origin-as-secure" -ForegroundColor Cyan
    Write-Host "2. Enter: http://localhost:$hostPort" -ForegroundColor Cyan
    Write-Host "3. Set to 'Enabled' and Relaunch." -ForegroundColor Cyan

    # 4. Remote Approval
    Write-Host "`n[4/4] [Approval] Requesting remote device pairing approval..." -ForegroundColor Yellow
    Write-Host "Executing Remote: docker exec openclaw_core openclaw devices approve --all" -ForegroundColor Gray
    try {
        ssh ${sshUser}@${publicIP} "docker exec openclaw_core openclaw devices approve --all"
    } catch {
        Write-Host "Note: Remote approval command failed, please run manually if needed." -ForegroundColor Gray
    }

    Write-Host "`n==========================================" -ForegroundColor Cyan
    Write-Host "   SUCCESS: Bridge established! Visit: http://localhost:$hostPort" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan

} else {
    Write-Host "[1/4] [Local] Retrieving local environment..." -ForegroundColor Yellow
    # Reserved for local logic
    Write-Host "OK: Local mode logic coming soon." -ForegroundColor Gray
}
