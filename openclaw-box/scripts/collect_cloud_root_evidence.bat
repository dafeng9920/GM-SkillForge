@echo off
REM CLOUD-ROOT Live Status Collection (Windows)
REM
REM This script connects to CLOUD-ROOT via SSH, transfers the collection script,
REM executes it, and copies the evidence back to LOCAL-ANTIGRAVITY.
REM
REM Usage:
REM   collect_cloud_root_evidence.bat
REM
REM Environment Variables (optional):
REM   CLOUD_HOST - CLOUD-ROOT hostname (default: CLOUD-HOST)
REM   CLOUD_USER - CLOUD-ROOT username (default: cloud-root)

setlocal enabledelayedexpansion

echo ========================================
echo CLOUD-ROOT Live Status Collection
echo ========================================
echo.

REM Configuration
set CLOUD_HOST=%CLOUD_HOST%
set CLOUD_USER=%CLOUD_USER%
if "%CLOUD_HOST%"=="" (
    set CLOUD_HOST=CLOUD-HOST
)
if "%CLOUD_USER%"=="" (
    set CLOUD_USER=cloud-root
)

echo Target Host: %CLOUD_HOST%
echo Target User: %CLOUD_USER%
echo.

REM Check if SSH client is available
set SSH_CMD=
where plink.exe >nul 2>&1
if %errorlevel% equ 0 (
    set SSH_CMD=plink
    echo Using PuTTY plink.exe
) else (
    where ssh.exe >nul 2>&1
    if %errorlevel% equ 0 (
        set SSH_CMD=ssh
        echo Using OpenSSH ssh.exe
    ) else (
        echo ERROR: SSH client not found.
        echo Please install one of:
        echo   - PuTTY (includes plink.exe): https://www.putty.org/
        echo   - OpenSSH (includes ssh.exe): https://github.com/PowerShell/Win32-OpenSSH
        pause
        exit /b 1
    )
)

echo Using SSH client: %SSH_CMD%
echo.

REM Define script paths (use absolute paths)
set REPO_ROOT=%~dp0..\..
set LOCAL_SCRIPT=%~dp0collect_cloud_root_live_status.sh
set REMOTE_SCRIPT=/tmp/collect_cloud_root_live_status.sh
set REMOTE_DIR=/tmp/cloud-root-evidence

echo ========================================
echo Step 1: Transfer Collection Script
echo ========================================

REM Create remote directory
echo Creating remote directory...
%SSH_CMD% %CLOUD_USER%@%CLOUD_HOST% "mkdir -p %REMOTE_DIR%"
if errorlevel 1 (
    echo Failed to create remote directory
    pause
    exit /b 1
)
echo Done.
echo.

REM Transfer script using SCP (if available) or type | ssh
echo Transferring collection script to CLOUD-ROOT...
where scp.exe >nul 2>&1
if %errorlevel equ 0 (
    echo Using SCP for transfer...
    scp.exe "%LOCAL_SCRIPT%" %CLOUD_USER%@%CLOUD_HOST%:%REMOTE_SCRIPT%
) else (
    echo Using type ^| ssh for transfer...
    type "%LOCAL_SCRIPT%" | %SSH_CMD% %CLOUD_USER%@%CLOUD_HOST% "cat > %REMOTE_SCRIPT%"
)

if errorlevel 1 (
    echo Failed to transfer collection script
    pause
    exit /b 1
)
echo Done.
echo.

echo ========================================
echo Step 2: Execute Collection Script
echo ========================================

echo Executing collection script on CLOUD-ROOT...
%SSH_CMD% %CLOUD_USER%@%CLOUD_HOST% "chmod +x %REMOTE_SCRIPT% && bash %REMOTE_SCRIPT%"
if errorlevel 1 (
    echo Failed to execute collection script
    pause
    exit /b 1
)
echo Done.
echo.

echo ========================================
echo Step 3: Retrieve Evidence Files
echo ========================================

REM Create local directory if not exists
if not exist "docs\2026-03-05\verification" (
    mkdir "docs\2026-03-05\verification"
)

echo Retrieving evidence files from CLOUD-ROOT...

REM Get list of evidence files
echo Listing evidence files on CLOUD-ROOT...
%SSH_CMD% %CLOUD_USER%@%CLOUD_HOST% "ls -1 %REMOTE_DIR%/cloud_root_live_status_*.txt %REMOTE_DIR%/cloud_root_live_status_*.json 2>nul"
echo.

REM Copy each evidence file using type | ssh
for %%f in (txt json) do (
    echo Retrieving .%%f files...
    %SSH_CMD% %CLOUD_USER%@%CLOUD_HOST% "cat %REMOTE_DIR%/cloud_root_live_status_*.%%f 2>nul" > "docs\2026-03-05\verification\cloud_root_live_status_temp.%%f"
)

echo Done.
echo.

echo ========================================
echo Step 4: Verify Evidence Transfer
echo ========================================

REM Check if files were retrieved
set EVIDENCE_TXT=
set EVIDENCE_JSON=
for /f "delims=" %%f in ('dir /b docs\2026-03-05\verification\cloud_root_live_status_temp.txt 2^>nul') do (
    set EVIDENCE_TXT=1
)
for /f "delims=" %%f in ('dir /b docs\2026-03-05\verification\cloud_root_live_status_temp.json 2^>nul') do (
    set EVIDENCE_JSON=1
)

if defined EVIDENCE_TXT (
    echo Evidence files retrieved successfully.
    echo.

    REM Rename to proper timestamp names
    for /f "tokens=*" %%f in ('dir /b docs\2026-03-05\verification\cloud_root_live_status_temp.txt 2^>nul') do (
        echo Evidence: %%f
    )
    echo.

    echo Next steps:
    echo   1. Review the evidence files
    echo   2. Verify gate criteria in CLOUD_ROOT_REVALIDATION_GUIDE.md
    echo   3. Create final gate decision based on evidence
) else (
    echo WARNING: Evidence files may not have been retrieved properly.
    echo Please check:
    echo   - Connection to CLOUD-ROOT
    echo   - Script execution on CLOUD-ROOT
    echo   - File permissions
)

echo.
echo ========================================
echo Evidence Collection Complete
echo ========================================
echo.
echo Evidence location: docs\2026-03-05\verification\
echo.
echo To view evidence:
echo   type docs\2026-03-05\verification\cloud_root_live_status_temp.txt
echo.

pause

