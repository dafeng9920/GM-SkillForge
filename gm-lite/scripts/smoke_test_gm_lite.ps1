param(
    [string]$AuthorityRoot = "D:\gm-lite"
)

$ErrorActionPreference = "Stop"

function Test-PathOrThrow {
    param(
        [string]$Path,
        [string]$Label
    )

    if (-not (Test-Path $Path)) {
        throw "[FAIL] $Label missing: $Path"
    }

    Write-Host "[OK] $Label" -ForegroundColor Green
}

function Test-VerificationTriplet {
    param(
        [string]$BaseDir,
        [string[]]$Ids
    )

    foreach ($id in $Ids) {
        Test-PathOrThrow (Join-Path $BaseDir "${id}_execution_report.md") "$id execution"
        Test-PathOrThrow (Join-Path $BaseDir "${id}_review_report.md") "$id review"
        Test-PathOrThrow (Join-Path $BaseDir "${id}_compliance_attestation.md") "$id compliance"
    }
}

Write-Host "== GM-LITE Smoke Test ==" -ForegroundColor Cyan
Write-Host "Authority root: $AuthorityRoot"

# Core bus / orchestrator code
Test-PathOrThrow (Join-Path $AuthorityRoot ".gm_bus") ".gm_bus root"
Test-PathOrThrow (Join-Path $AuthorityRoot "src\gm_bus\core\BusManager.ts") "BusManager core"
Test-PathOrThrow (Join-Path $AuthorityRoot "src\blueprint_orchestrator\core\BaseGate.ts") "BaseGate core"
Test-PathOrThrow (Join-Path $AuthorityRoot "src\blueprint_orchestrator\core\BlueprintOrchestrator.ts") "BlueprintOrchestrator core"
Test-PathOrThrow (Join-Path $AuthorityRoot "src\blueprint_orchestrator\core\MirrorSealer.ts") "MirrorSealer core"
Test-PathOrThrow (Join-Path $AuthorityRoot "src\gm_bus\assist\next_hop_assist.ts") "next_hop_assist"
Test-PathOrThrow (Join-Path $AuthorityRoot "src\gm_bus\assist\missing_piece_assist.ts") "missing_piece_assist"
Test-PathOrThrow (Join-Path $AuthorityRoot "src\gm_bus\assist\dispatch_packet_assist.ts") "dispatch_packet_assist"

# Bus artifacts
Test-PathOrThrow (Join-Path $AuthorityRoot ".gm_bus\manifest\task_board.json") "task_board manifest"
Test-PathOrThrow (Join-Path $AuthorityRoot ".gm_bus\schemas\TaskEnvelope.schema.json") "TaskEnvelope schema"
Test-PathOrThrow (Join-Path $AuthorityRoot ".gm_bus\schemas\DispatchPacket.schema.json") "DispatchPacket schema"

# Verification milestones
Test-VerificationTriplet (Join-Path $AuthorityRoot "docs\2026-03-24\verification\gm_lite_dispatch_assist_minimal_implementation") @("DI1","DI2","DI3","DI4")
Test-VerificationTriplet (Join-Path $AuthorityRoot "docs\2026-03-24\verification\gm_lite_sample_flow_validation") @("SV1","SV2","SV3","SV4")
Test-VerificationTriplet (Join-Path $AuthorityRoot "docs\2026-03-24\verification\gm_lite_blueprint_orchestrator_seed_implementation") @("BO1","BO2","BO3","BO4")

Write-Host ""
Write-Host "[PASS] GM-LITE smoke test passed." -ForegroundColor Green
Write-Host "Core bus, assist, blueprint runtime, and verification triplets are present."
