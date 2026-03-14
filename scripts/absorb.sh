#!/bin/bash
#
# Host absorb script
#
# Purpose:
# - Absorb whitelisted artifacts/evidence from dropzone into docs root
# - Never copy files outside manifest whitelist
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

    # Use unified validation gate for pre-absorb check
    # This integrates TASK-MAIN-03: unified_validation_gate.py into mainline
    log_info "Running unified validation gate (absorb mode)..."
    if ! python "$SCRIPT_DIR/unified_validation_gate.py" --absorb --task-id "$task_id"; then
        log_fail "Unified validation gate failed - absorb denied"
        exit 1
    fi
    log_ok "Unified validation gate passed"

    local task_root="$DROPZONE_ROOT/$task_id"
    local manifest="$task_root/manifest.json"

    python - "$manifest" "$task_root" "$DOCS_ROOT" <<'PY'
import json
import shutil
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
task_root = Path(sys.argv[2]).resolve()
docs_root = Path(sys.argv[3]).resolve()

data = json.loads(manifest_path.read_text(encoding="utf-8"))
artifacts = data.get("artifacts", [])
evidence = data.get("evidence", [])
task_id = data.get("task_id", task_root.name)

dest_root = docs_root / task_id
dest_root.mkdir(parents=True, exist_ok=True)

copied = []
for rel in artifacts + evidence:
    src = (task_root / rel).resolve()
    rel_path = Path(rel)
    dest = (dest_root / rel_path).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    copied.append(str(dest))

print(json.dumps({"task_id": task_id, "dest_root": str(dest_root), "copied": copied}, ensure_ascii=False, indent=2))
PY

    log_ok "absorb 完成"
}

main "$@"
