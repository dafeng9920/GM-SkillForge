# check_skill_structure.ps1
# Skill 结构校验脚本
# 检查目录与必备文件是否存在
# 退出码: 0=PASS, 1=FAIL

param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
$ExitCode = 0

Write-Host "=== Skill Structure Check ===" -ForegroundColor Cyan
Write-Host "RepoRoot: $RepoRoot"
Write-Host ""

# 定义三个 skill 目录
$Skills = @(
    "skills/permit-governance-skill",
    "skills/release-gate-skill",
    "skills/rollback-tombstone-skill"
)

$Results = @()

foreach ($Skill in $Skills) {
    $SkillPath = Join-Path $RepoRoot $Skill
    $SkillName = Split-Path $Skill -Leaf
    $SkillResults = @{
        skill = $SkillName
        checks = @()
        passed = $true
    }

    Write-Host "Checking: $SkillName" -ForegroundColor Yellow

    # Check 1: 目录存在
    $DirExists = Test-Path $SkillPath
    $SkillResults.checks += @{
        name = "directory_exists"
        passed = $DirExists
        path = $SkillPath
    }
    if ($DirExists) {
        Write-Host "  [PASS] Directory exists: $SkillPath" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Directory missing: $SkillPath" -ForegroundColor Red
        $SkillResults.passed = $false
        $ExitCode = 1
    }

    # Check 2: SKILL.md 存在
    $SkillMdPath = Join-Path $SkillPath "SKILL.md"
    $SkillMdExists = Test-Path $SkillMdPath
    $SkillResults.checks += @{
        name = "skill_md_exists"
        passed = $SkillMdExists
        path = $SkillMdPath
    }
    if ($SkillMdExists) {
        Write-Host "  [PASS] SKILL.md exists" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] SKILL.md missing" -ForegroundColor Red
        $SkillResults.passed = $false
        $ExitCode = 1
    }

    # Check 3: agents/openai.yaml 存在
    $OpenaiYamlPath = Join-Path $SkillPath "agents/openai.yaml"
    $OpenaiYamlExists = Test-Path $OpenaiYamlPath
    $SkillResults.checks += @{
        name = "openai_yaml_exists"
        passed = $OpenaiYamlExists
        path = $OpenaiYamlPath
    }
    if ($OpenaiYamlExists) {
        Write-Host "  [PASS] agents/openai.yaml exists" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] agents/openai.yaml missing" -ForegroundColor Red
        $SkillResults.passed = $false
        $ExitCode = 1
    }

    # Check 4: references/ 目录存在（可选但检查）
    $ReferencesPath = Join-Path $SkillPath "references"
    $ReferencesExists = Test-Path $ReferencesPath
    $SkillResults.checks += @{
        name = "references_dir_exists"
        passed = $ReferencesExists
        path = $ReferencesPath
        optional = $true
    }
    if ($ReferencesExists) {
        Write-Host "  [PASS] references/ directory exists" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] references/ directory missing (optional)" -ForegroundColor Yellow
    }

    # 如果 SKILL.md 引用了 references，则必须存在
    if ($SkillMdExists) {
        $SkillMdContent = Get-Content $SkillMdPath -Raw
        if ($SkillMdContent -match "references/") {
            $RefFiles = [regex]::Matches($SkillMdContent, "references/[a-zA-Z0-9_-]+\.md")
            foreach ($RefFile in $RefFiles) {
                $RefPath = Join-Path $SkillPath $RefFile.Value
                $RefExists = Test-Path $RefPath
                if (-not $RefExists) {
                    Write-Host "  [FAIL] Referenced file missing: $($RefFile.Value)" -ForegroundColor Red
                    $SkillResults.passed = $false
                    $ExitCode = 1
                } else {
                    Write-Host "  [PASS] Referenced file exists: $($RefFile.Value)" -ForegroundColor Green
                }
            }
        }
    }

    $Results += $SkillResults
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
    check_name = "skill_structure"
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    passed = ($ExitCode -eq 0)
    skills = $Results
}

$ReportPath = Join-Path $RepoRoot "ci/out/structure_check.json"
$Report | ConvertTo-Json -Depth 5 | Out-File $ReportPath -Encoding UTF8
Write-Host "Report saved: $ReportPath"

exit $ExitCode
