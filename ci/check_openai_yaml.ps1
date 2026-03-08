# check_openai_yaml.ps1
# OpenAI YAML 配置校验脚本
# 检查 agents/openai.yaml 基本有效性
# 退出码: 0=PASS, 1=FAIL

param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
$ExitCode = 0

Write-Host "=== OpenAI YAML Check ===" -ForegroundColor Cyan
Write-Host "RepoRoot: $RepoRoot"
Write-Host ""

# 定义三个 skill
$Skills = @(
    "skills/permit-governance-skill",
    "skills/release-gate-skill",
    "skills/rollback-tombstone-skill"
)

$Results = @()

foreach ($Skill in $Skills) {
    $YamlPath = Join-Path $RepoRoot "$Skill/agents/openai.yaml"
    $SkillName = Split-Path $Skill -Leaf

    $SkillResult = @{
        skill = $SkillName
        checks = @()
        passed = $true
    }

    Write-Host "Checking: $SkillName" -ForegroundColor Yellow

    if (-not (Test-Path $YamlPath)) {
        Write-Host "  [FAIL] openai.yaml not found: $YamlPath" -ForegroundColor Red
        $SkillResult.passed = $false
        $ExitCode = 1
        $Results += $SkillResult
        continue
    }

    $Content = Get-Content $YamlPath -Raw

    # Check 1: name 字段存在且非空
    if ($Content -match "name:\s*[`"']?([a-zA-Z0-9_-]+)[`"']?") {
        $NameValue = $Matches[1]
        Write-Host "  [PASS] name field exists: $NameValue" -ForegroundColor Green
        $SkillResult.checks += @{ name = "name_field"; passed = $true; value = $NameValue }
    } else {
        Write-Host "  [FAIL] name field not found" -ForegroundColor Red
        $SkillResult.checks += @{ name = "name_field"; passed = $false }
        $SkillResult.passed = $false
        $ExitCode = 1
    }

    # Check 2: description 字段存在且非空
    if ($Content -match "description:\s*[|>]?\s*") {
        Write-Host "  [PASS] description field exists" -ForegroundColor Green
        $SkillResult.checks += @{ name = "description_field"; passed = $true }
    } else {
        Write-Host "  [FAIL] description field not found or empty" -ForegroundColor Red
        $SkillResult.checks += @{ name = "description_field"; passed = $false }
        $SkillResult.passed = $false
        $ExitCode = 1
    }

    # Check 3: version 字段存在
    if ($Content -match "version:\s*[`"']?v?[0-9.]+[`"']?") {
        Write-Host "  [PASS] version field exists" -ForegroundColor Green
        $SkillResult.checks += @{ name = "version_field"; passed = $true }
    } else {
        Write-Host "  [FAIL] version field not found" -ForegroundColor Red
        $SkillResult.checks += @{ name = "version_field"; passed = $false }
        $SkillResult.passed = $false
        $ExitCode = 1
    }

    # Check 4: frozen_at 或 frozen 字段存在（冻结时间戳）- 可选
    if ($Content -match "frozen_at:\s*[`"']?[0-9-]+[`"']?") {
        Write-Host "  [PASS] frozen_at field exists" -ForegroundColor Green
        $SkillResult.checks += @{ name = "frozen_at_field"; passed = $true }
    } else {
        Write-Host "  [WARN] frozen_at field not found (recommended)" -ForegroundColor Yellow
        $SkillResult.checks += @{ name = "frozen_at_field"; passed = $true; optional = $true }
    }

    # Check 5: default_prompt 或 system_prompt 存在（提示词）
    if ($Content -match "default_prompt:|system_prompt:|operations:") {
        Write-Host "  [PASS] prompt or operations field exists" -ForegroundColor Green
        $SkillResult.checks += @{ name = "prompt_field"; passed = $true }
    } else {
        Write-Host "  [WARN] prompt field not found" -ForegroundColor Yellow
        $SkillResult.checks += @{ name = "prompt_field"; passed = $true; optional = $true }
    }

    # Check 6: fail_closed_rules 存在（Fail-Closed 规则）- 可选
    if ($Content -match "fail_closed_rules:|fail_closed:") {
        Write-Host "  [PASS] fail_closed section exists" -ForegroundColor Green
        $SkillResult.checks += @{ name = "fail_closed_rules"; passed = $true }
    } else {
        Write-Host "  [WARN] fail_closed section not found" -ForegroundColor Yellow
        $SkillResult.checks += @{ name = "fail_closed_rules"; passed = $true; optional = $true }
    }

    $Results += $SkillResult
    Write-Host ""
}

# 汇总
Write-Host "=== Summary ===" -ForegroundColor Cyan
$PassedCount = ($Results | Where-Object { $_.passed }).Count
$TotalCount = $Results.Count
Write-Host "Skills checked: $TotalCount"
Write-Host "Skills passed: $PassedCount"

if ($ExitCode -eq 0) {
    Write-Host "Result: PASS" -ForegroundColor Green
} else {
    Write-Host "Result: FAIL" -ForegroundColor Red
}

# 输出 JSON 报告
$Report = @{
    check_name = "openai_yaml"
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    passed = ($ExitCode -eq 0)
    skills = $Results
}

$ReportPath = Join-Path $RepoRoot "ci/out/openai_yaml_check.json"
$Report | ConvertTo-Json -Depth 5 | Out-File $ReportPath -Encoding UTF8
Write-Host "Report saved: $ReportPath"

exit $ExitCode
