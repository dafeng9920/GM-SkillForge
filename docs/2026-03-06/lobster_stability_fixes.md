# Lobster Console + lobsterctl Stability Fixes

## Overview
This document outlines the specific fixes needed to stabilize the Lobster Console + lobsterctl cloud execution paths from "usable" to "repeatable, low-maintenance" operation.

## Fix Specifications

### Fix 1: Status Output Sanitization
**File**: `scripts/lobsterctl.py`
**Lines**: 143-196
**Issue**: SSH remote command output mixes JSON with shell noise
**Fix**: Already implemented via `--noprofile --norc` bash flags

```python
# Current implementation (already fixed):
cmd = [
    "ssh",
    "-T",  # Disable pseudo-terminal allocation
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=10",
    f"{args.cloud_user}@{args.cloud_host}",
    "bash",
    "--noprofile",  # Prevent shell init noise
    "--norc",
    "-lc",
    remote,  # JSON output command
]
```

**Status**: ✅ Already implemented, working as designed

---

### Fix 2: Fetch Artifact Precheck
**File**: `scripts/fetch_cloud_task_artifacts.ps1`
**Lines**: 22-40
**Issue**: Verification runs even when artifacts are missing

**Current Code**:
```powershell
Write-Host "[2/3] Listing local artifacts..."
Get-ChildItem $localTaskDir | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize

Write-Host "[3/3] Running local gate verification..."
& python scripts/enforce_cloud_lobster_closed_loop.py --task-id $TaskId --action verify
```

**Proposed Fix**:
```powershell
Write-Host "[2/3] Validating artifacts..."
$requiredFiles = @("execution_receipt.json", "stdout.log", "stderr.log", "audit_event.json")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (-not (Test-Path (Join-Path $localTaskDir $file))) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "[ERROR] Missing required artifacts: $($missingFiles -join ', ')"
    Write-Host "[ACTION] Please ensure CLOUD-ROOT execution completed successfully"
    exit 1
}

Write-Host "[OK] All required artifacts present"

Write-Host "[3/3] Running local gate verification..."
& python scripts/enforce_cloud_lobster_closed_loop.py --task-id $TaskId --action verify
```

**Status**: ⏳ Designed, ready for implementation

---

### Fix 3: Executor Resilience
**File**: `scripts/execute_antigravity_task.py`
**Lines**: 98-103
**Issue**: Silent failures on Python environment issues

**Current Code** (already has fallback):
```python
# Cloud Linux fallback: if `python` is missing, transparently use python3.
if command.startswith("python "):
    python_ok = subprocess.run("command -v python", shell=True, capture_output=True, text=True).returncode == 0
    python3_ok = subprocess.run("command -v python3", shell=True, capture_output=True, text=True).returncode == 0
    if not python_ok and python3_ok:
        normalized_command = "python3 " + command[len("python "):]
        self.log_audit("COMMAND_REWRITE", f"Rewrote command for compatibility: {command} -> {normalized_command}")
```

**Additional Enhancement Needed**:
```python
def check_python_environment(self) -> dict:
    """Check Python environment and return status."""
    checks = {
        "python_available": False,
        "python3_available": False,
        "python_version": None,
        "python3_version": None,
    }

    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            checks["python_available"] = True
            checks["python_version"] = result.stdout.strip()
    except FileNotFoundError:
        pass

    try:
        result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            checks["python3_available"] = True
            checks["python3_version"] = result.stdout.strip()
    except FileNotFoundError:
        pass

    return checks

# Add to execute() method, before allowlist execution:
env_check = self.check_python_environment()
if not any([env_check["python_available"], env_check["python3_available"]]):
    self.log_audit("FATAL", "No Python interpreter available")
    raise RuntimeError("Python not available in CLOUD-ROOT environment")
```

**Status**: ⏳ Enhancement designed, ready for implementation

---

### Fix 4: Verification Gate Clarity
**File**: `scripts/verify_and_gate.py`
**Lines**: 86-121
**Issue**: Overlapping checks between enforcement scripts

**Current Code Structure**:
```python
def run_cloud_lobster_mandatory_gate(task_id: str) -> dict:
    enforce_script = pathlib.Path("scripts/enforce_cloud_lobster_closed_loop.py")
    legacy_gate_script = pathlib.Path("scripts/cloud_lobster_mandatory_gate.py")

    # Tries enforce_script first, falls back to legacy_gate_script
```

**Proposed Enhancement**:
```python
def run_cloud_lobster_mandatory_gate(task_id: str) -> dict:
    """Run mandatory gate with clear responsibility separation."""
    enforce_script = pathlib.Path("scripts/enforce_cloud_lobster_closed_loop.py")

    result = {
        "task_id": task_id,
        "timestamp": utc_now(),
        "gate_name": "cloud_lobster_mandatory_gate",
        "responsibility": "Enforce FAIL-CLOSED policy for CLOUD-ROOT tasks",
        "checks": {
            "contract_exists": "UNKNOWN",
            "receipt_exists": "UNKNOWN",
            "four_artifacts_complete": "UNKNOWN",
            "receipt_verified": "UNKNOWN",
        },
        "status": "DENY",
        "exit_code": -1,
    }

    if not enforce_script.exists():
        result["error"] = f"Gate script not found: {enforce_script}"
        return result

    try:
        cmd = [sys.executable, str(enforce_script), "--task-id", task_id, "--action", "verify", "--quiet"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        result["exit_code"] = proc.returncode
        result["stdout"] = proc.stdout.strip()
        result["stderr"] = proc.stderr.strip()
        result["status"] = "ALLOW" if proc.returncode == 0 else "DENY"

        # Parse check results from output if available
        # This makes each check's status explicit

    except subprocess.TimeoutExpired:
        result["error"] = "Gate check timed out"
    except Exception as e:
        result["error"] = str(e)

    return result
```

**Status**: ⏳ Enhancement designed, ready for implementation

---

### Fix 5: Connection Pooling (Lower Priority)
**File**: `scripts/lobsterctl.py`
**Issue**: No SSH connection pooling

**Proposed Enhancement**:
```python
# Add connection reuse for status polling
class SSHConnectionManager:
    def __init__(self, host, user):
        self.host = host
        self.user = user
        self.control_path = f"/tmp/ssh-control-{user}@{host}"

    def connect(self):
        """Establish persistent SSH connection."""
        subprocess.run([
            "ssh", "-o", "ControlMaster=yes",
            "-o", f"ControlPath={self.control_path}",
            "-o", "ControlPersist=300",
            f"{self.user}@{self.host}", "echo", "connected"
        ], check=True)

    def disconnect(self):
        """Close persistent SSH connection."""
        subprocess.run([
            "ssh", "-o", f"ControlPath={self.control_path}",
            "-O", "exit", f"{self.user}@{self.host}"
        ])
```

**Status**: 📋 Designed, lower priority

---

### Fix 6: Log Tail Limits (Lower Priority)
**File**: `scripts/lobsterctl.py`
**Lines**: 178-195
**Issue**: No limit on tail output size

**Current Code** (already has limit):
```python
if getattr(args, "tail_lines", 0) > 0:
    tail_cmd = [
        "ssh",
        # ... SSH options ...
        f"{args.cloud_user}@{args.cloud_host}",
        "bash", "--noprofile", "--norc", "-lc",
        f'tail -n {args.tail_lines} "{log_file}" 2>/dev/null || true',
    ]
```

**Status**: ✅ Already implemented with `--tail-lines` parameter

---

## Implementation Priority

### Priority 1 (Before Next Smoke Test)
1. ✅ Status output sanitization - Already done
2. ⏳ Fetch artifact precheck - Ready to implement
3. ✅ Log tail limits - Already done

### Priority 2 (This Week)
4. ⏳ Executor resilience enhancement - Ready to implement
5. ⏳ Verification gate clarity - Ready to implement

### Priority 3 (Next Sprint)
6. 📋 Connection pooling - Designed, lower priority

---

## Testing Checklist

After implementing fixes, verify:

- [ ] Status command returns clean JSON output
- [ ] Fetch command fails clearly when artifacts missing
- [ ] Executor logs Python environment check
- [ ] Verification gate shows each check's status
- [ ] Smoke task completes end-to-end
- [ ] Dual gate verification produces PASS

---

*Document Version: 1.0.0*
*Last Updated: 2026-03-06*
*Author: Kior-B (T3-A Execution)*
