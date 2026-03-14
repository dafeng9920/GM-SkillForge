# Quant System 基础设施启动脚本 (PowerShell版本)
# Phase 0: 基础设施准备

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$DockerDir = Join-Path $ProjectRoot "docker"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Quant System 基础设施启动" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "项目根目录: $ProjectRoot"
Write-Host "Docker配置:  $DockerDir"
Write-Host ""

# 检查Docker是否运行
try {
    $null = docker info 2>&1
    Write-Host "✓ Docker运行正常" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker未运行，请先启动Docker Desktop" -ForegroundColor Red
    exit 1
}

# 切换到Docker目录
Set-Location $DockerDir

# 创建必要的目录
Write-Host ""
Write-Host "创建数据目录..." -ForegroundColor Yellow
$directories = @(
    "sql",
    "redis",
    "prometheus",
    "grafana/provisioning/datasources",
    "grafana/provisioning/dashboards",
    "data/tdengine",
    "data/postgres",
    "data/redis",
    "data/minio"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path $DockerDir $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  创建: $dir"
    }
}

Write-Host "✓ 数据目录创建完成" -ForegroundColor Green

# 停止并删除旧容器（如果存在）
Write-Host ""
Write-Host "清理旧容器..." -ForegroundColor Yellow
docker-compose -f quant-stack.yml down -v 2>$null

# 启动基础设施
Write-Host ""
Write-Host "启动基础设施容器..." -ForegroundColor Yellow
docker-compose -f quant-stack.yml up -d

# 等待容器启动
Write-Host ""
Write-Host "等待容器启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查容器状态
Write-Host ""
Write-Host "检查容器状态..." -ForegroundColor Yellow
docker-compose -f quant-stack.yml ps

# 等待服务就绪
Write-Host ""
Write-Host "等待服务就绪..." -ForegroundColor Yellow

Write-Host "  PostgreSQL..." -NoNewline
$maxWait = 30
$waited = 0
while ($waited -lt $maxWait) {
    try {
        $null = docker exec quant-postgres pg_isready -U quant_admin 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓" -ForegroundColor Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
    $waited += 2
    Write-Host "." -NoNewline
}

Write-Host "  Redis..." -NoNewline
$maxWait = 30
$waited = 0
while ($waited -lt $maxWait) {
    try {
        $null = docker exec quant-redis redis-cli ping 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓" -ForegroundColor Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
    $waited += 2
    Write-Host "." -NoNewline
}

Write-Host "  MinIO..." -NoNewline
$maxWait = 30
$waited = 0
while ($waited -lt $maxWait) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9000/minio/health/live" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Write-Host " ✓" -ForegroundColor Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
    $waited += 2
    Write-Host "." -NoNewline
}

Write-Host "  TDengine..." -NoNewline
$maxWait = 30
$waited = 0
while ($waited -lt $maxWait) {
    try {
        $null = docker exec quant-tdengine taos -s tdengine 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓" -ForegroundColor Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
    $waited += 2
    Write-Host "." -NoNewline
}

# 显示访问信息
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✓ 基础设施启动完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务访问地址：" -ForegroundColor Yellow
Write-Host "  PostgreSQL:     localhost:5432"
Write-Host "  Redis:          localhost:6379"
Write-Host "  TDengine:       localhost:6030"
Write-Host "  MinIO Console:  http://localhost:9000"
Write-Host "  MinIO API:       http://localhost:9001"
Write-Host "  PGAdmin:        http://localhost:5050"
Write-Host "  Redis Commander: http://localhost:8081"
Write-Host "  Grafana:        http://localhost:3000"
Write-Host "  Prometheus:     http://localhost:9090"
Write-Host ""
Write-Host "默认凭据：" -ForegroundColor Yellow
Write-Host "  PostgreSQL:     quant_admin / quant_secure_change_me"
Write-Host "  MinIO:          minioadmin / minioadmin_change_me"
Write-Host "  PGAdmin:        admin@quant.local / admin_change_me"
Write-Host "  Grafana:        admin / admin_change_me"
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "  1. 运行健康检查: python scripts/check_quant_stack.py"
Write-Host "  2. 开始Phase 1: 数据层实现"
Write-Host ""

# 返回项目根目录
Set-Location $ProjectRoot
