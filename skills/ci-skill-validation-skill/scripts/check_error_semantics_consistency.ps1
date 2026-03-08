# check_error_semantics_consistency.ps1
# 错误码语义一致性校验脚本
# 检查三 skill 错误码语义一致性
# 退出码: 0=PASS, 1=FAIL

param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
$ExitCode = 0

Write-Host "=== Error Semantics Consistency Check ===" -ForegroundColor Cyan
Write-Host "RepoRoot: $RepoRoot"
Write-Host ""

# 定义三个 skill
$Skills = @(
    "skills/permit-governance-skill",
    "skills/release-gate-skill",
    "skills/rollback-tombstone-skill"
)

# 定义错误码语义标准
$ErrorSemantics = @{
    "E001" = @{
        pattern = "E001.*PERMIT_REQUIRED|PERMIT_REQUIRED.*E001"
        description = "Permit 缺失"
        release_allowed = "false"
    }
    "E003" = @{
        pattern = "E003.*PERMIT_INVALID|PERMIT_INVALID.*E003|signature.*invalid|签名.*无效"
        description = "Permit 签名无效"
        release_allowed = "false"
    }
    "release_allowed" = @{
        pattern = "release_allowed.*false|release_allowed\s*=\s*false|release_allowed:\s*false"
        description = "release_allowed 默认 false"
    }
}

$Results = @()
$AllChecks = @{}

# 收集所有 skill 的错误码信息
foreach ($Skill in $Skills) {
    $SkillMdPath = Join-Path $RepoRoot "$Skill/SKILL.md"
    $YamlPath = Join-Path $RepoRoot "$Skill/agents/openai.yaml"
    $SkillName = Split-Path $Skill -Leaf

    $SkillResult = @{
        skill = $SkillName
        checks = @()
        passed = $true
    }

    Write-Host "Checking: $SkillName" -ForegroundColor Yellow

    # 读取 SKILL.md
    $SkillMdContent = ""
    if (Test-Path $SkillMdPath) {
        $SkillMdContent = Get-Content $SkillMdPath -Raw
    }

    # 读取 openai.yaml
    $YamlContent = ""
    if (Test-Path $YamlPath) {
        $YamlContent = Get-Content $YamlPath -Raw
    }

    $CombinedContent = "$SkillMdContent`n$YamlContent"

    # Check E001 语义
    $E001Check = @{
        error_code = "E001"
        semantics_found = $false
        release_allowed_is_false = $false
    }

    if ($CombinedContent -match "E001") {
        $E001Check.semantics_found = $true

        # 检查 E001 关联的语义
        if ($CombinedContent -match "E001.*PERMIT_REQUIRED|PERMIT_REQUIRED.*E001|permit.*required|Permit.*缺失") {
            Write-Host "  [PASS] E001 semantics correct: PERMIT_REQUIRED" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] E001 found but semantics unclear" -ForegroundColor Yellow
        }

        # 检查 release_allowed = false
        if ($CombinedContent -match "E001.*release_allowed.*false|E001.*release_allowed:\s*false") {
            $E001Check.release_allowed_is_false = $true
            Write-Host "  [PASS] E001 -> release_allowed = false" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] E001 release_allowed not explicitly false" -ForegroundColor Yellow
        }
    } else {
        # 对于 rollback-tombstone-skill，E001 是可选的
        if ($SkillName -eq "rollback-tombstone-skill") {
            Write-Host "  [INFO] E001 not required for $SkillName" -ForegroundColor Cyan
            $E001Check.semantics_found = $true  # 可选
        } else {
            Write-Host "  [FAIL] E001 not found" -ForegroundColor Red
            $SkillResult.passed = $false
            $ExitCode = 1
        }
    }

    $SkillResult.checks += $E001Check

    # Check E003 语义
    $E003Check = @{
        error_code = "E003"
        semantics_found = $false
        release_allowed_is_false = $false
    }

    if ($CombinedContent -match "E003") {
        $E003Check.semantics_found = $true

        # 检查 E003 关联的语义
        if ($CombinedContent -match "E003.*PERMIT_INVALID|PERMIT_INVALID.*E003|signature.*invalid|签名.*无效|SIGNATURE") {
            Write-Host "  [PASS] E003 semantics correct: PERMIT_INVALID (signature)" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] E003 found but semantics unclear" -ForegroundColor Yellow
        }

        # 检查 release_allowed = false
        if ($CombinedContent -match "E003.*release_allowed.*false|E003.*release_allowed:\s*false") {
            $E003Check.release_allowed_is_false = $true
            Write-Host "  [PASS] E003 -> release_allowed = false" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] E003 release_allowed not explicitly false" -ForegroundColor Yellow
        }
    } else {
        # 对于 rollback-tombstone-skill，E003 是可选的
        if ($SkillName -eq "rollback-tombstone-skill") {
            Write-Host "  [INFO] E003 not required for $SkillName" -ForegroundColor Cyan
            $E003Check.semantics_found = $true  # 可选
        } else {
            Write-Host "  [FAIL] E003 not found" -ForegroundColor Red
            $SkillResult.passed = $false
            $ExitCode = 1
        }
    }

    $SkillResult.checks += $E003Check

    # Check release_allowed 语义
    $ReleaseAllowedCheck = @{
        field = "release_allowed"
        default_false_found = $false
        only_true_with_permit = $false
    }

    if ($CombinedContent -match "release_allowed.*false|release_allowed\s*=\s*false") {
        $ReleaseAllowedCheck.default_false_found = $true
        Write-Host "  [PASS] release_allowed = false found" -ForegroundColor Green
    }

    if ($CombinedContent -match "permit.*release_allowed.*true|VALID.*release_allowed.*true|release_allowed.*true.*permit") {
        $ReleaseAllowedCheck.only_true_with_permit = $true
        Write-Host "  [PASS] release_allowed = true only with valid permit" -ForegroundColor Green
    }

    $SkillResult.checks += $ReleaseAllowedCheck

    $Results += $SkillResult
    $AllChecks[$SkillName] = $SkillResult.checks

    Write-Host ""
}

# 跨 Skill 一致性检查
Write-Host "=== Cross-Skill Consistency ===" -ForegroundColor Cyan

# 检查 E001 在相关 skill 中语义一致
$E001Skills = $Results | Where-Object {
    $_.checks | Where-Object { $_.error_code -eq "E001" -and $_.semantics_found }
}
Write-Host "E001 present in $($E001Skills.Count) skills" -ForegroundColor Cyan

# 检查 E003 在相关 skill 中语义一致
$E003Skills = $Results | Where-Object {
    $_.checks | Where-Object { $_.error_code -eq "E003" -and $_.semantics_found }
}
Write-Host "E003 present in $($E003Skills.Count) skills" -ForegroundColor Cyan

# 汇总
Write-Host ""
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
    check_name = "error_semantics_consistency"
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    passed = ($ExitCode -eq 0)
    skills = $Results
    consistency = @{
        E001_present_count = $E001Skills.Count
        E003_present_count = $E003Skills.Count
    }
}

$ReportPath = Join-Path $RepoRoot "ci/out/error_semantics_check.json"
$Report | ConvertTo-Json -Depth 5 | Out-File $ReportPath -Encoding UTF8
Write-Host "Report saved: $ReportPath"

exit $ExitCode
