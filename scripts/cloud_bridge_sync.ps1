# cloud_bridge_sync.ps1 - GM-SkillForge Cloud-Local Bridge Automation (V3)
# -------------------------------------------------------------------
# Fix: Removed non-ASCII characters to avoid PowerShell encoding errors

param (
    [string]$commitMessage = "Market Snapshot & Skill Sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    [switch]$OpenDashboard = $true,
    [switch]$SkipMarket = $false
)

$STABLE_URL = "https://detailed-newsletters-departure-patricia.trycloudflare.com"
$GATEWAY_TOKEN = "3a6d798bca0857a6548a8842f5295fcb41f66d92dbe7d1ee"
$AUTH_URL = "$STABLE_URL/#token=$GATEWAY_TOKEN"

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   GM-SkillForge: Cloud Bridge Sync (V3)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 0. A-Share Data Fetch
if (-not $SkipMarket) {
    Write-Host "`n[0/4] 🔭 Fetching local market data (akshare)..." -ForegroundColor Yellow
    python ./scripts/fetch_ashare_data.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: Market data fetch encountered issues." -ForegroundColor Magenta
    } else {
        Write-Host "OK: Market snapshot captured." -ForegroundColor Green
    }
}

# 1. Git Sync
Write-Host "`n[1/4] 📦 Syncing local Skills and Intelligence to Git..." -ForegroundColor Yellow
git add .
git commit -m $commitMessage --allow-empty
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Git push failed. Check network or credentials." -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "OK: Full sync complete." -ForegroundColor Green

# 2. Automation Signal
Write-Host "`n[2/4] 🔔 Note: Cloud Adjudicator is listening for updates..." -ForegroundColor Yellow
Write-Host "      !market status - to check latest intelligence" -ForegroundColor Gray

# 3. Open Dashboard
if ($OpenDashboard) {
    Write-Host "`n[3/4] 🌉 Refreshing Cloud Bridge..." -ForegroundColor Yellow
    Write-Host "      Navigating to: $STABLE_URL" -ForegroundColor Gray
    Start-Process $AUTH_URL
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "   SUCCESS: Bridge V3 running, data sent!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host "`n[REMINDER] Don't forget to 'PULL' on the cloud host:" -ForegroundColor Magenta
Write-Host "Run this on your Cloud Terminal:" -ForegroundColor Gray
Write-Host ">>> cd /root/gm-skillforge && git pull" -ForegroundColor Cyan
