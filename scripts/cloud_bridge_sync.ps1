# cloud_bridge_sync.ps1 - GM-SkillForge Cloud-Local Bridge Automation
# -------------------------------------------------------------------
# 功能：本地编写 Skill -> Git 推送 -> 自动连通云端管理后台
# 架构：Bridge of the Sea (Cloudflare Tunnel + Git Sync)
# -------------------------------------------------------------------

param (
    [string]$commitMessage = "Auto-sync for cloud execution: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    [switch]$OpenDashboard = $true
)

$STABLE_URL = "https://mom-cocktail-characterization-consideration.trycloudflare.com"
$GATEWAY_TOKEN = "3a6d798bca0857a6548a8842f5295fcb41f66d92dbe7d1ee"
$AUTH_URL = "$STABLE_URL/#token=$GATEWAY_TOKEN"

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   GM-SkillForge: 跨海大桥同步程序 (V2)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. 本地 Git 同步
Write-Host "`n[1/3] 📦 正在同步本地 Skill 代码到 Git..." -ForegroundColor Yellow
git add .
git commit -m $commitMessage --allow-empty
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git 推送失败，请检查网络或 SSH Key。" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "✅ Git 同步已完成。" -ForegroundColor Green

# 2. 云端重载提示
Write-Host "`n[2/3] 🔔 请向 Discord/飞书 的“小龙虾”发送重载指令：" -ForegroundColor Yellow
Write-Host "      !system reload-skills" -ForegroundColor White
Write-Host "      (注意：云端已配置持续监听，通常会自动 pick up)" -ForegroundColor Gray

# 3. 开启云端直连后台
if ($OpenDashboard) {
    Write-Host "`n[3/3] 🌉 正在通过免 VPN 隧道开启云端直连后台..." -ForegroundColor Yellow
    Write-Host "      正在跳转至：$STABLE_URL" -ForegroundColor Gray
    Start-Process $AUTH_URL
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "   ✅ 全链路同步任务已提交，大桥通航中！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
