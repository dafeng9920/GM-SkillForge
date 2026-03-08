# run_skillization_gate.ps1
# Skill 化总控门禁脚本
# 一键串行执行所有检查，作为 CI 入口
# 退出码: 0=PASS, 1=FAIL

param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$OutputDir = "ci/out"
)

$ErrorActionPreference = "Stop"
$ExitCode = 0
$StartTime = Get-Date

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Skillization Gate - CI Entry Point  " -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "RepoRoot: $RepoRoot"
Write-Host "OutputDir: $OutputDir"
Write-Host "StartTime: $StartTime"
Write-Host ""

# 确保输出目录存在
$FullOutputDir = Join-Path $RepoRoot $OutputDir
if (-not (Test-Path $FullOutputDir)) {
    New-Item -ItemType Directory -Path $FullOutputDir -Force | Out-Null
}

# 定义检查脚本顺序
$Checks = @(
    @{ name = "structure"; script = "check_skill_structure.ps1"; required = $true },
    @{ name = "openai_yaml"; script = "check_openai_yaml.ps1"; required = $true },
    @{ name = "contract_markers"; script = "check_skill_contract_markers.ps1"; required = $true },
    @{ name = "evidence_refs"; script = "check_evidence_refs.ps1"; required = $true },
    @{ name = "error_semantics"; script = "check_error_semantics_consistency.ps1"; required = $true }
)

$Results = @()

foreach ($Check in $Checks) {
    $CheckName = $Check.name
    $ScriptPath = Join-Path $PSScriptRoot $Check.script
    $IsRequired = $Check.required

    Write-Host "----------------------------------------" -ForegroundColor Cyan
    Write-Host "Running: $CheckName" -ForegroundColor Yellow
    Write-Host "Script: $($Check.script)" -ForegroundColor Gray
    Write-Host ""

    $CheckResult = @{
        name = $CheckName
        script = $Check.script
        required = $IsRequired
        passed = $false
        duration_ms = 0
        error = $null
    }

    $CheckStart = Get-Date

    try {
        # 执行检查脚本
        & $ScriptPath -RepoRoot $RepoRoot
        $CheckExitCode = $LASTEXITCODE

        $CheckEnd = Get-Date
        $CheckResult.duration_ms = [int](($CheckEnd - $CheckStart).TotalMilliseconds)

        if ($CheckExitCode -eq 0) {
            $CheckResult.passed = $true
            Write-Host "[PASS] $CheckName completed successfully" -ForegroundColor Green
        } else {
            $CheckResult.passed = $false
            $CheckResult.error = "Exit code: $CheckExitCode"
            Write-Host "[FAIL] $CheckName failed with exit code: $CheckExitCode" -ForegroundColor Red

            if ($IsRequired) {
                $ExitCode = 1
            }
        }
    } catch {
        $CheckEnd = Get-Date
        $CheckResult.duration_ms = [int](($CheckEnd - $CheckStart).TotalMilliseconds)
        $CheckResult.passed = $false
        $CheckResult.error = $_.Exception.Message

        Write-Host "[ERROR] $CheckName threw exception: $($_.Exception.Message)" -ForegroundColor Red

        if ($IsRequired) {
            $ExitCode = 1
        }
    }

    $Results += $CheckResult
    Write-Host ""
}

$EndTime = Get-Date
$TotalDurationMs = [int](($EndTime - $StartTime).TotalMilliseconds)

# 汇总
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Skillization Gate - Summary  " -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

$PassedCount = ($Results | Where-Object { $_.passed }).Count
$TotalCount = $Results.Count
$RequiredPassed = ($Results | Where-Object { $_.required -and $_.passed }).Count
$RequiredTotal = ($Results | Where-Object { $_.required }).Count

Write-Host "Checks: $PassedCount/$TotalCount passed"
Write-Host "Required: $RequiredPassed/$RequiredTotal passed"
Write-Host "Duration: ${TotalDurationMs}ms"
Write-Host ""

# 显示详细结果
Write-Host "Detailed Results:" -ForegroundColor Cyan
foreach ($Result in $Results) {
    $Status = if ($Result.passed) { "[PASS]" } else { "[FAIL]" }
    $Color = if ($Result.passed) { "Green" } else { "Red" }
    $Required = if ($Result.required) { " (required)" } else { " (optional)" }
    Write-Host "  $Status $($Result.name)$Required - $($Result.duration_ms)ms" -ForegroundColor $Color
}

Write-Host ""

# 生成最终报告
$FinalReport = @{
    gate_name = "skillization_gate"
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    passed = ($ExitCode -eq 0)
    summary = @{
        total_checks = $TotalCount
        passed_checks = $PassedCount
        required_total = $RequiredTotal
        required_passed = $RequiredPassed
    }
    duration_ms = $TotalDurationMs
    checks = $Results
}

$ReportPath = Join-Path $RepoRoot "$OutputDir/skillization_gate_report.json"
$FinalReport | ConvertTo-Json -Depth 5 | Out-File $ReportPath -Encoding UTF8

# 最终判定
if ($ExitCode -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  RESULT: PASS  " -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Report saved: $ReportPath"
    Write-Host "All skillization checks passed. Ready for merge/deploy."
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  RESULT: FAIL  " -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Report saved: $ReportPath"
    Write-Host "One or more required checks failed. Block merge/deploy."
}

exit $ExitCode
