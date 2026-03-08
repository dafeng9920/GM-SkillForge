# check_skill_contract_markers.ps1
# Skill 契约标记校验脚本
# 检查关键治理语义是否出现在 SKILL.md
# 退出码: 0=PASS, 1=FAIL

param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
$ExitCode = 0

Write-Host "=== Skill Contract Markers Check ===" -ForegroundColor Cyan
Write-Host "RepoRoot: $RepoRoot"
Write-Host ""

# 定义每个 skill 必须包含的标记
$SkillMarkers = @{
    "skills/permit-governance-skill" = @{
        required = @(
            @{ pattern = "no-permit-no-release"; desc = "核心约束标记" },
            @{ pattern = "fail_closed|Fail-Closed"; desc = "Fail-Closed 标记" },
            @{ pattern = "E001"; desc = "E001 错误码" },
            @{ pattern = "E003"; desc = "E003 错误码" }
        )
    }
    "skills/release-gate-skill" = @{
        required = @(
            @{ pattern = "release_allowed"; desc = "release_allowed 字段" },
            @{ pattern = "all-or-nothing|ALL_OR_NOTHING"; desc = "all-or-nothing 策略" },
            @{ pattern = "E001"; desc = "E001 错误码" },
            @{ pattern = "E003"; desc = "E003 错误码" }
        )
    }
    "skills/rollback-tombstone-skill" = @{
        required = @(
            @{ pattern = "tombstone_schema|tombstone_id|Tombstone"; desc = "Tombstone 定义" },
            @{ pattern = "immutable|不可篡改|IMMUTABLE"; desc = "不可变标记" },
            @{ pattern = "replay_consistency|replay_pointer"; desc = "Replay 一致性检查" }
        )
    }
}

$Results = @()

foreach ($SkillPath in $SkillMarkers.Keys) {
    $FullSkillPath = Join-Path $RepoRoot $SkillPath
    $SkillMdPath = Join-Path $FullSkillPath "SKILL.md"
    $SkillName = Split-Path $SkillPath -Leaf

    $SkillResult = @{
        skill = $SkillName
        checks = @()
        passed = $true
    }

    Write-Host "Checking: $SkillName" -ForegroundColor Yellow

    if (-not (Test-Path $SkillMdPath)) {
        Write-Host "  [FAIL] SKILL.md not found: $SkillMdPath" -ForegroundColor Red
        $SkillResult.passed = $false
        $ExitCode = 1
        $Results += $SkillResult
        continue
    }

    $Content = Get-Content $SkillMdPath -Raw

    foreach ($Marker in $SkillMarkers[$SkillPath].required) {
        $Pattern = $Marker.pattern
        $Desc = $Marker.desc

        if ($Content -match $Pattern) {
            Write-Host "  [PASS] Found: $Desc ($Pattern)" -ForegroundColor Green
            $SkillResult.checks += @{
                pattern = $Pattern
                description = $Desc
                found = $true
            }
        } else {
            Write-Host "  [FAIL] Missing: $Desc ($Pattern)" -ForegroundColor Red
            $SkillResult.checks += @{
                pattern = $Pattern
                description = $Desc
                found = $false
            }
            $SkillResult.passed = $false
            $ExitCode = 1
        }
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
    check_name = "skill_contract_markers"
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    passed = ($ExitCode -eq 0)
    skills = $Results
}

$ReportPath = Join-Path $RepoRoot "ci/out/contract_markers_check.json"
$Report | ConvertTo-Json -Depth 5 | Out-File $ReportPath -Encoding UTF8
Write-Host "Report saved: $ReportPath"

exit $ExitCode
