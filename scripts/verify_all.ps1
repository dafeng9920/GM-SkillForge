param(
  [Parameter(Mandatory = $true)]
  [string]$TaskDir,
  [string]$ContractFile = "",
  [string]$ReceiptFile = "execution_receipt.json"
)

$ErrorActionPreference = "Stop"

function Resolve-ContractPath {
  param([string]$BaseDir, [string]$Override)
  if ($Override -ne "") {
    return (Join-Path $BaseDir $Override)
  }

  $candidates = @(
    "task_contract_v4.json",
    "task_contract_v3.json",
    "task_contract_v2.json",
    "task_contract.json"
  )

  foreach ($item in $candidates) {
    $p = Join-Path $BaseDir $item
    if (Test-Path $p) { return $p }
  }

  throw "No contract file found under $BaseDir"
}

if (-not (Test-Path $TaskDir)) {
  throw "TaskDir not found: $TaskDir"
}

$contractPath = Resolve-ContractPath -BaseDir $TaskDir -Override $ContractFile
$receiptPath = Join-Path $TaskDir $ReceiptFile

if (-not (Test-Path $receiptPath)) {
  throw "Receipt file not found: $receiptPath"
}

Write-Host "[INFO] TaskDir: $TaskDir"
Write-Host "[INFO] Contract: $contractPath"
Write-Host "[INFO] Receipt : $receiptPath"

Write-Host "[STEP] Verify receipt against contract..."
python skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py --contract $contractPath --receipt $receiptPath
if ($LASTEXITCODE -ne 0) {
  throw "Receipt verification failed."
}

Write-Host "[STEP] Artifact presence check..."
$required = @("execution_receipt.json", "stdout.log", "stderr.log", "audit_event.json")
$missing = @()
foreach ($f in $required) {
  if (-not (Test-Path (Join-Path $TaskDir $f))) {
    $missing += $f
  }
}
if ($missing.Count -gt 0) {
  throw ("Missing required artifacts: " + ($missing -join ", "))
}

Write-Host "[STEP] Quick summary..."
$receipt = Get-Content $receiptPath -Raw -Encoding UTF8 | ConvertFrom-Json
Write-Host ("[OK] task_id={0}" -f $receipt.task_id)
Write-Host ("[OK] status={0}" -f $receipt.status)
Write-Host ("[OK] exit_code={0}" -f $receipt.exit_code)
Write-Host ("[OK] commands={0}" -f $receipt.executed_commands.Count)

Write-Host "[DONE] verify_all PASS"
