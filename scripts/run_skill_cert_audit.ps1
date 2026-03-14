param(
    [ValidateSet("P0", "P1", "P2", "ALL")]
    [string]$Batch = "P0",
    [string]$RepoRoot = "d:\\GM-SkillForge"
)

$ErrorActionPreference = "Stop"

$allRepoSkills = Get-ChildItem -Path (Join-Path $RepoRoot "skills") -Directory | ForEach-Object { $_.Name }

$p0 = @(
    "wave-gate-orchestrator-skill",
    "triple-record-validator-skill",
    "decision-schema-normalizer-skill",
    "wave-recheck-generator-skill",
    "dispatch-broadcast-builder-skill",
    "p0-final-adjudicator-skill",
    "evidence-freeze-board-skill",
    "protocol-gate-ci-checker-skill"
)

# 先给出保守分层：P1 为除 P0 外、且已存在 openai.yaml 的技能；P2 为剩余技能
$p1 = @()
$p2 = @()
foreach ($s in $allRepoSkills) {
    if ($p0 -contains $s) { continue }
    $openai = Join-Path $RepoRoot ("skills\" + $s + "\agents\openai.yaml")
    if (Test-Path $openai) { $p1 += $s } else { $p2 += $s }
}

switch ($Batch) {
    "P0" { $targetSkills = $p0 }
    "P1" { $targetSkills = $p1 }
    "P2" { $targetSkills = $p2 }
    "ALL" { $targetSkills = $allRepoSkills }
}

$ts = Get-Date -Format "yyyy-MM-dd_HHmmss"
$outDir = Join-Path $RepoRoot ("reports\skill_cert_audit\" + (Get-Date -Format "yyyy-MM-dd"))
if (-not (Test-Path $outDir)) {
    New-Item -Path $outDir -ItemType Directory -Force | Out-Null
}
$outFile = Join-Path $outDir ("batch_" + $Batch + "_" + $ts + ".json")

$results = @()
foreach ($skill in $targetSkills) {
    $skillDir = Join-Path $RepoRoot ("skills\" + $skill)
    $skillMd = Join-Path $skillDir "SKILL.md"
    $openai = Join-Path $skillDir "agents\openai.yaml"

    $hasSkill = Test-Path $skillMd
    $hasOpenai = Test-Path $openai

    $decision = "PASS"
    $requiredChanges = @()

    if (-not $hasSkill) {
        $decision = "DENY"
        $requiredChanges += "Missing SKILL.md"
    } elseif (-not $hasOpenai) {
        $decision = "REQUIRES_CHANGES"
        $requiredChanges += "Missing agents/openai.yaml"
    }

    $results += @{
        skill = $skill
        skill_md = $hasSkill
        openai_yaml = $hasOpenai
        decision = $decision
        required_changes = $requiredChanges
    }
}

$summary = @{
    batch = $Batch
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    total = $results.Count
    pass = ($results | Where-Object { $_.decision -eq "PASS" }).Count
    requires_changes = ($results | Where-Object { $_.decision -eq "REQUIRES_CHANGES" }).Count
    deny = ($results | Where-Object { $_.decision -eq "DENY" }).Count
    overall_decision = if (($results | Where-Object { $_.decision -eq "DENY" }).Count -gt 0) { "DENY" } elseif (($results | Where-Object { $_.decision -eq "REQUIRES_CHANGES" }).Count -gt 0) { "REQUIRES_CHANGES" } else { "ALLOW" }
}

$report = @{
    summary = $summary
    results = $results
}

$report | ConvertTo-Json -Depth 8 | Set-Content -Path $outFile -Encoding UTF8

Write-Host "[AUDIT] Batch: $Batch"
Write-Host "[AUDIT] Output: $outFile"
Write-Host "[AUDIT] overall_decision: $($summary.overall_decision)"
Write-Host "[AUDIT] pass=$($summary.pass), requires_changes=$($summary.requires_changes), deny=$($summary.deny)"

exit 0

