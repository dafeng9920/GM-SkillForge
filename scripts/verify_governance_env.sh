#!/bin/bash
#
# Governance environment verifier
#
# Purpose:
# - Validate APP_ROOT / DROPZONE_ROOT / DOCS_ROOT before absorb flow
# - Fail closed when required paths are missing, unreadable, unwritable, or unsafe
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

is_safe_path() {
    local path="$1"
    [[ "$path" == /* ]] || return 1
    [[ "$path" != *".."* ]] || return 1
    [[ "$path" != *"//"* ]] || return 1
    return 0
}

check_dir_readable() {
    local label="$1"
    local path="$2"
    if [[ ! -d "$path" ]]; then
        log_fail "$label 不存在: $path"
        return 1
    fi
    if [[ ! -r "$path" ]]; then
        log_fail "$label 不可读: $path"
        return 1
    fi
    log_ok "$label 可读: $path"
}

check_dir_writable() {
    local label="$1"
    local path="$2"
    if [[ ! -d "$path" ]]; then
        log_fail "$label 不存在: $path"
        return 1
    fi
    if [[ ! -w "$path" ]]; then
        log_fail "$label 不可写: $path"
        return 1
    fi
    log_ok "$label 可写: $path"
}

main() {
    log_info "验证治理环境变量..."
    log_info "APP_ROOT=$APP_ROOT"
    log_info "DROPZONE_ROOT=$DROPZONE_ROOT"
    log_info "DOCS_ROOT=$DOCS_ROOT"

    for pair in \
        "APP_ROOT:$APP_ROOT" \
        "DROPZONE_ROOT:$DROPZONE_ROOT" \
        "DOCS_ROOT:$DOCS_ROOT"; do
        name="${pair%%:*}"
        value="${pair#*:}"
        if ! is_safe_path "$value"; then
            log_fail "$name 路径不安全: $value"
            exit 1
        fi
    done

    check_dir_readable "APP_ROOT" "$APP_ROOT"
    check_dir_writable "DROPZONE_ROOT" "$DROPZONE_ROOT"
    check_dir_writable "DOCS_ROOT" "$DOCS_ROOT"

    if [[ "$APP_ROOT" == "$DROPZONE_ROOT" || "$APP_ROOT" == "$DOCS_ROOT" || "$DROPZONE_ROOT" == "$DOCS_ROOT" ]]; then
        log_fail "治理根目录不能重叠"
        exit 1
    fi

    log_ok "治理环境验证通过"
}

main "$@"
