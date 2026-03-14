<#
.SYNOPSIS
    OpenClaw 商业版一键安装脚本 (Windows)
    针对非技术客户设计的自动化部署程序。
#>

$ErrorActionPreference = "Stop"
$OC_DIR = "C:\OpenClaw-Box"
$DATA_DIR = "$OC_DIR\data"

Write-Host "🦞 欢迎使用 OpenClaw 商业部署程序..." -ForegroundColor Cyan

# 1. 检查权限
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "❌ 请右键点击‘以管理员身份运行’此脚本。"
}

# 2. 检查 Docker
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "❌ 未检测到 Docker。请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop/"
}

# 3. 创建目录结构
if (-not (Test-Path $DATA_DIR)) {
    New-Item -ItemType Directory -Path $DATA_DIR -Force
    Write-Host "✅ 已创建部署目录: $OC_DIR" -ForegroundColor Green
}

# 4. 生成默认配置文件 (如果不存在)
$configPath = "$DATA_DIR\openclaw.json"
if (-not (Test-Path $configPath)) {
    # 此处内容与 openclaw.json.template 一致，但会插入一些随机生成的 Token
    $gwToken = [Guid]::NewGuid().ToString("N")
    $configContent = @"
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "在此粘贴_DISCORD_BOT_TOKEN",
      "groupPolicy": "allowlist",
      "streaming": "partial",
      "threadBindings": { "spawnSubagentSessions": true }
    }
  },
  "gateway": {
    "mode": "local",
    "controlUi": { "dangerouslyAllowHostHeaderOriginFallback": false },
    "auth": { "mode": "token", "token": "$gwToken" },
    "bind": "loopback",
    "port": 18789
  },
  "agents": { "defaults": { "sandbox": { "mode": "all" } } }
}
"@
    $configContent | Out-File -FilePath $configPath -Encoding utf8
    Write-Host "✅ 已生成安全加固型配置文件：$configPath" -ForegroundColor Green
    Write-Host "⚠️ 请打开此文件并填入你的 Discord Token。" -ForegroundColor Yellow
}

# 5. 生成 docker-compose.yml
$dcPath = "$OC_DIR\docker-compose.yml"
$dcContent = @"
services:
  openclaw-db:
    image: postgres:15-alpine
    container_name: openclaw_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: clawuser
      POSTGRES_PASSWORD: clawpassword
      POSTGRES_DB: openclaw
    volumes:
      - openclaw_pgdata:/var/lib/postgresql/data

  openclaw-agent:
    image: openclaw-agent:latest
    container_name: openclaw_core
    restart: unless-stopped
    depends_on:
      - openclaw-db
    environment:
      DATABASE_URL: postgresql://clawuser:clawpassword@openclaw-db:5432/openclaw
      OPENCLAW_CONFIG_PATH: /home/node/.openclaw/openclaw.json
    volumes:
      - ./data:/home/node/.openclaw:rw
    ports:
      - "127.0.0.1:18789:18789"
    user: "0:0"
    command: ["openclaw", "gateway", "run", "--port", "18789", "--bind", "loopback", "--allow-unconfigured"]

volumes:
  openclaw_pgdata:
"@
$dcContent | Out-File -FilePath $dcPath -Encoding utf8
Write-Host "✅ 已生成 docker-compose 编排文件。" -ForegroundColor Green

Write-Host "`n🦞 安装完成！" -ForegroundColor Cyan
Write-Host "1. 请编辑 $configPath 填入 Token。"
Write-Host "2. 运行 'docker compose up -d' 启动服务。"
Write-Host "3. 尽情享受你的私有 AI 助理吧！"
