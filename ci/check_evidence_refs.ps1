# check_evidence_refs.ps1
# 证据引用校验脚本
# 检查每个 skill 是否引用至少一个已有证据文档路径
# 退出码: 0=PASS, 1=FAIL

param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
$ExitCode = 0

Write-Host "=== Evidence Refs Check ===" -ForegroundColor Cyan
Write-Host "RepoRoot: $RepoRoot"
Write-Host ""

# 定义三个 skill
$Skills = @(
    "skills/permit-governance-skill",
    "skills/release-gate-skill",
    "skills/rollback-tombstone-skill"
)

# 证据路径匹配模式
$EvidencePatterns = @(
    "docs/2026-02-18/[\w_-]+\.md",
    "docs/2026-02-16/[\w_-]+\.md",
    "skillforge/src/[\w/]+\.py"
)

$Results = @()

foreach ($Skill in $Skills) {
    $SkillMdPath = Join-Path $RepoRoot "$Skill/SKILL.md"
    $ReferencesPath = Join-Path $RepoRoot "$Skill/references"
    $SkillName = Split-Path $Skill -Leaf

    $SkillResult = @{
        skill = $SkillName
        checks = @()
        evidence_refs = @()
        passed = $true
    }

    Write-Host "Checking: $SkillName" -ForegroundColor Yellow

    # Check 1: SKILL.md 中的证据引用
    if (Test-Path $SkillMdPath) {
        $Content = Get-Content $SkillMdPath -Raw

        foreach ($Pattern in $EvidencePatterns) {
            $Matches = [regex]::Matches($Content, $Pattern)
            foreach ($Match in $Matches) {
                $RefPath = $Match.Value
                $FullRefPath = Join-Path $RepoRoot $RefPath

                $CheckResult = @{
                    ref = $RefPath
                    source = "SKILL.md"
                    exists = $false
                }

                if (Test-Path $FullRefPath) {
                    Write-Host "  [PASS] Evidence ref exists: $RefPath" -ForegroundColor Green
                    $CheckResult.exists = $true
                    $SkillResult.evidence_refs += $RefPath
                } else {
                    Write-Host "  [FAIL] Evidence ref missing: $RefPath" -ForegroundColor Red
                    $SkillResult.passed = $false
                    $ExitCode = 1
                }

                $SkillResult.checks += $CheckResult
            }
        }
    }

    # Check 2: references/ 目录中的证据文件
    if (Test-Path $ReferencesPath) {
        $RefFiles = Get-ChildItem $ReferencesPath -Filter "*.md" -ErrorAction SilentlyContinue
        foreach ($RefFile in $RefFiles) {
            $RefContent = Get-Content $RefFile.FullName -Raw

            # 检查 references 文件中是否有引用 docs/ 路径
            foreach ($Pattern in $EvidencePatterns) {
                $Matches = [regex]::Matches($RefContent, $Pattern)
                foreach ($Match in $Matches) {
                    $RefPath = $Match.Value
                    $FullRefPath = Join-Path $RepoRoot $RefPath

                    # 跳过相对路径引用（../ 格式）
                    if ($RefPath -match "^\.\./") {
                        continue
                    }

                    $CheckResult = @{
                        ref = $RefPath
                        source = "references/$($RefFile.Name)"
                        exists = $false
                    }

                    if (Test-Path $FullRefPath) {
                        Write-Host "  [PASS] Evidence ref exists (via references): $RefPath" -ForegroundColor Green
                        $CheckResult.exists = $true
                    } else {
                        Write-Host "  [WARN] Evidence ref not found: $RefPath" -ForegroundColor Yellow
                    }

                    $SkillResult.checks += $CheckResult
                }
            }
        }
    }

    # Check 3: 至少有一个有效证据引用
    $ValidRefsCount = ($SkillResult.checks | Where-Object { $_.exists }).Count
    if ($ValidRefsCount -gt 0) {
        Write-Host "  [PASS] Has $ValidRefsCount valid evidence reference(s)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] No valid evidence references found" -ForegroundColor Red
        $SkillResult.passed = $false
        $ExitCode = 1
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
    check_name = "evidence_refs"
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    passed = ($ExitCode -eq 0)
    skills = $Results
}

$ReportPath = Join-Path $RepoRoot "ci/out/evidence_refs_check.json"
$Report | ConvertTo-Json -Depth 5 | Out-File $ReportPath -Encoding UTF8
Write-Host "Report saved: $ReportPath"

exit $ExitCode
