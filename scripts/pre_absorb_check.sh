#!/bin/bash
#
# Pre-absorb gate
#
# Purpose:
# - Validate dropzone task package before host absorb
# - Enforce env variables and manifest whitelist
#

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; }

APP_ROOT="${APP_ROOT:-/root/openclaw-box/data/workspace}"
DROPZONE_ROOT="${DROPZONE_ROOT:-/root/openclaw-box/dropzone}"
DOCS_ROOT="${DOCS_ROOT:-/root/openclaw-box/docs}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

main() {
    local task_id="${1:-}"
    if [[ -z "$task_id" ]]; then
        log_fail "用法: $0 <TASK_ID>"
        exit 1
    fi

    "$SCRIPT_DIR/verify_governance_env.sh"

    local task_root="$DROPZONE_ROOT/$task_id"
    local manifest="$task_root/manifest.json"

    log_info "检查任务包: $task_root"

    if [[ ! -d "$task_root" ]]; then
        log_fail "任务包目录不存在: $task_root"
        exit 1
    fi

    if [[ ! -f "$manifest" ]]; then
        log_fail "manifest.json 缺失: $manifest"
        exit 1
    fi

    python - "$manifest" "$task_root" <<'PY'
import json
import os
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
task_root = Path(sys.argv[2]).resolve()

data = json.loads(manifest_path.read_text(encoding="utf-8"))
required = ["blueprint.md", "risk_statement.md", "changes.diff", "test_report.md", "completion_record.md", "manifest.json"]

missing = [name for name in required if not (task_root / name).exists()]
if missing:
    print(f"FAIL: missing required files: {missing}")
    sys.exit(1)

artifacts = data.get("artifacts", [])
evidence = data.get("evidence", [])
env = data.get("env", {})

if not isinstance(artifacts, list) or not isinstance(evidence, list):
    print("FAIL: manifest artifacts/evidence must be arrays")
    sys.exit(1)

for rel in artifacts + evidence:
    rel_path = Path(rel)
    if rel_path.is_absolute() or ".." in rel_path.parts:
        print(f"FAIL: unsafe manifest path: {rel}")
        sys.exit(1)
    real = (task_root / rel_path).resolve()
    if not str(real).startswith(str(task_root)):
        print(f"FAIL: manifest path escapes task root: {rel}")
        sys.exit(1)
    if not real.exists():
        print(f"FAIL: manifest listed file missing: {rel}")
        sys.exit(1)

for key in ("APP_ROOT", "DROPZONE_ROOT", "DOCS_ROOT"):
    if key not in env:
        print(f"FAIL: manifest env missing key: {key}")
        sys.exit(1)

print("PASS")
PY

    log_ok "pre_absorb_check 通过"
}

main "$@"
