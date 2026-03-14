# cloud_bridge_sync.ps1 - GM-SkillForge Cloud-Local Bridge Automation (V3)
# -------------------------------------------------------------------
# 功能：本地抓取行情 -> Git 推送 -> 云端直连 -> 自动化验收
# 架构：Bridge of the Sea (Feeder + Sync + Adjudicator)
# -------------------------------------------------------------------

param (
    [string]$commitMessage = "Market Snapshot & Skill Sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    [switch]$OpenDashboard = $true,
    [switch]$SkipMarket = $false
)

$STABLE_URL = "https://mom-cocktail-characterization-consideration.trycloudflare.com"
$GATEWAY_TOKEN = "3a6d798bca0857a6548a8842f5295fcb41f66d92dbe7d1ee"
$AUTH_URL = "$STABLE_URL/#token=$GATEWAY_TOKEN"

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   GM-SkillForge: 跨海大桥同步程序 (V3)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 0. A 股行情抓取 (Architecture A: Local Feeder)
if (-not $SkipMarket) {
    Write-Host "`n[0/4] 🔭 正在执行本地行情侦察 (akshare)..." -ForegroundColor Yellow
    python ./scripts/fetch_ashare_data.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ 行情抓取出现异常，将继续尝试推送其余文件。" -ForegroundColor Magenta
    } else {
        Write-Host "✅ 行情快照已捕获。" -ForegroundColor Green
    }
}

# 1. 本地 Git 同步
Write-Host "`n[1/4] 📦 正在同步本地 Skill 与 Intelligence 到 Git..." -ForegroundColor Yellow
git add .
git commit -m $commitMessage --allow-empty
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git 推送失败，请检查网络或配置。" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "✅ 全量同步已完成。" -ForegroundColor Green

# 2. 自动化信号
Write-Host "`n[2/4] 🔔 请留意：云端 Adjudicator 正在监听行情更新..." -ForegroundColor Yellow
Write-Host "      !market status - 查看最新同步的情报" -ForegroundColor Gray

# 3. 开启或刷新管理后台
if ($OpenDashboard) {
    Write-Host "`n[3/4] 🌉 正在刷新云端直连大桥..." -ForegroundColor Yellow
    Write-Host "      正在跳转至：$STABLE_URL" -ForegroundColor Gray
    Start-Process $AUTH_URL
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "   ✅ V3 同步完成，行情已跨海，大桥运行中！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host "`n[💡 重要提醒] 别忘了让云端“收货”：" -ForegroundColor Magenta
Write-Host "请在 Discord 频道（或云端终端）发送：" -ForegroundColor Gray
Write-Host ">>> !shell git pull" -ForegroundColor Cyan
Write-Host "然后小龙虾就能读取到最新的行情快照了！" -ForegroundColor Gray
