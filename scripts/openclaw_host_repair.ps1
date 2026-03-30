# openclaw_host_repair.ps1 - OpenClaw 宿主机-容器自动对齐修复脚本
# -------------------------------------------------------------------
# 功能：自动提取 Docker Key -> 适配宿主机 V1 格式 -> 对齐 18793 端口 -> 强制重启网关
# 执行：.\scripts\openclaw_host_repair.ps1
# -------------------------------------------------------------------

$ErrorActionPreference = "SilentlyContinue"
$HOST_CONFIG_PATH = "$HOME\.openclaw"
$AGENT_AUTH_PATH = "$HOST_CONFIG_PATH\agents\main\agent\auth-profiles.json"
$LOCAL_ENV_PATH = "D:\GM-SkillForge\openclaw-box\.env"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   OpenClaw Host-Container 对齐修复工具" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. 寻找 Zai API Key
Write-Host "[1/4] 🔍 正在检索 Zai API Key..." -ForegroundColor Yellow
$zaiKey = ""
if (Test-Path $LOCAL_ENV_PATH) {
    $envContent = Get-Content $LOCAL_ENV_PATH
    foreach ($line in $envContent) {
        if ($line -match "OPENAI_API_KEY=(.+)") {
            $zaiKey = $Matches[1].Trim()
            break
        }
    }
}

if (-not $zaiKey) {
    Write-Host "❌ 未能在 .env 中找到 API Key，尝试从 Docker 提取..." -ForegroundColor Red
    $zaiKey = docker inspect openclaw_core --format="{{range .Config.Env}}{{if (and (contains . \"OPENAI_API_KEY=\") (not (contains . \"url\"))) }}{{print .}}{{end}}{{end}}"
    if ($zaiKey -match "OPENAI_API_KEY=(.+)") { $zaiKey = $Matches[1].Trim() }
}

if (-not $zaiKey) {
    Write-Host "❌ 无法定位 API Key，请手动检查 .env 或 Docker。" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 已锁定 Key: $($zaiKey.Substring(0,8))..." -ForegroundColor Green

# 2. 注入宿主机授权 (V1 格式)
Write-Host "`n[2/4] 💉 正在注入宿主机授权 (Profile V1)..." -ForegroundColor Yellow
$authJson = @{
    version = 1
    profiles = @{
        "zai:default" = @{
            type = "api_key"
            provider = "zai"
            key = $zaiKey
        }
    }
} | ConvertTo-Json -Depth 10

if (-not (Test-Path (Split-Path $AGENT_AUTH_PATH))) { New-Item -ItemType Directory -Path (Split-Path $AGENT_AUTH_PATH) -Force }
$authJson | Out-File -FilePath $AGENT_AUTH_PATH -Encoding UTF8
$authJson | Out-File -FilePath "$HOST_CONFIG_PATH\agents\main\agent\auth.json" -Encoding UTF8 # 备份旧格式
Write-Host "✅ 授权文件已同步至 $AGENT_AUTH_PATH" -ForegroundColor Green

# 3. 强行对齐 18793 端口
Write-Host "`n[3/4] 📐 正在对齐 host 端口至 18793..." -ForegroundColor Yellow
$openClawJsonPath = "$HOST_CONFIG_PATH\openclaw.json"
if (Test-Path $openClawJsonPath) {
    $config = Get-Content $openClawJsonPath | ConvertFrom-Json
    $config.gateway.port = 18793
    $config | ConvertTo-Json -Depth 10 | Out-File $openClawJsonPath -Encoding UTF8
    Write-Host "✅ 宿主机 openclaw.json 已对齐至 18793。" -ForegroundColor Green
}

# 4. 强制重启服务
Write-Host "`n[4/4] 🚀 正在强制刷新网关服务..." -ForegroundColor Yellow
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
openclaw gateway install --force
openclaw gateway start

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "   ✅ 修复完成！请访问 http://127.0.0.1:18793" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
