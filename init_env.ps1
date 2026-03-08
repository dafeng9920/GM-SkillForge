$CondaHook = "C:\tools\miniconda3\shell\condabin\conda-hook.ps1"
if (Test-Path $CondaHook) {
    # Initialize conda in the current shell
    & $CondaHook
    # Activate the environment
    conda activate genesis-final
} else {
    Write-Host "Error: Conda hook not found at $CondaHook" -ForegroundColor Red
}
