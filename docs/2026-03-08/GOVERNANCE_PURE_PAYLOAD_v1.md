# Governance Full Install Payload (v1.1)

> [!IMPORTANT]
> **安装说明**: 由于之前使用 `$(cat ...)` 导致了内容丢失，请直接使用以下 **物理硬编码内容**。
> 请在云端终端分段粘贴执行。

### 1. 核心桥接脚本安装

```bash
mkdir -p /root/openclaw-box/scripts

# verify_governance_env.sh
cat << 'SHELL_EOF' > /root/openclaw-box/scripts/verify_governance_env.sh
#!/bin/bash
set -euo pipefail
APP_ROOT="${APP_ROOT:-/root/openclaw-box/skillforge}"
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
    local label="$1"; local path="$2"
    if [[ ! -d "$path" || ! -r "$path" ]]; then return 1; fi
    return 0
}
main() {
    for pair in "APP_ROOT:$APP_ROOT" "DROPZONE_ROOT:$DROPZONE_ROOT" "DOCS_ROOT:$DOCS_ROOT"; do
        name="${pair%%:*}"; value="${pair#*:}"
        if ! is_safe_path "$value"; then exit 1; fi
    done
    exit 0
}
main "$@"
SHELL_EOF
chmod +x /root/openclaw-box/scripts/verify_governance_env.sh

# pre_absorb_check.sh
cat << 'SHELL_EOF' > /root/openclaw-box/scripts/pre_absorb_check.sh
#!/bin/bash
set -euo pipefail
DROPZONE_ROOT="${DROPZONE_ROOT:-/root/openclaw-box/dropzone}"
main() {
    local task_id="${1:-}"
    if [[ -z "$task_id" ]]; then exit 1; fi
    local task_root="$DROPZONE_ROOT/$task_id"
    if [[ ! -d "$task_root" || ! -f "$task_root/manifest.json" ]]; then exit 1; fi
    echo "PRECHECK PASS"
}
main "$@"
SHELL_EOF
chmod +x /root/openclaw-box/scripts/pre_absorb_check.sh

# absorb.sh
cat << 'SHELL_EOF' > /root/openclaw-box/scripts/absorb.sh
#!/bin/bash
set -euo pipefail
DOCS_ROOT="${DOCS_ROOT:-/root/openclaw-box/docs}"
DROPZONE_ROOT="${DROPZONE_ROOT:-/root/openclaw-box/dropzone}"
main() {
    local task_id="${1:-}"
    if [[ -z "$task_id" ]]; then exit 1; fi
    mkdir -p "$DOCS_ROOT/$task_id"
    cp -r "$DROPZONE_ROOT/$task_id/"* "$DOCS_ROOT/$task_id/"
    echo "ABSORB DONE: $task_id"
}
main "$@"
SHELL_EOF
chmod +x /root/openclaw-box/scripts/absorb.sh
```

### 2. 核心治理 Skill 安装

```bash
mkdir -p /root/gm-skillforge/skills/gm-multi-agent-orchestrator-skill
cat << 'SKILL_EOF' > /root/gm-skillforge/skills/gm-multi-agent-orchestrator-skill/SKILL.md
---
name: gm-multi-agent-orchestrator-skill
description: 云端多 Agent 协作状态机与角色分权
---
# gm-multi-agent-orchestrator-skill
## 角色: executor, reviewer, compliance, controller
## 状态: READY_FOR_EXECUTION, WAITING_REVIEW, WAITING_COMPLIANCE, ABSORBED
SKILL_EOF

mkdir -p /root/gm-skillforge/skills/lobster-task-package-skill
cat << 'SKILL_EOF' > /root/gm-skillforge/skills/lobster-task-package-skill/SKILL.md
---
name: lobster-task-package-skill
description: 强制产出待验收任务包 (manifest.json / evidence)
---
# lobster-task-package-skill
## 产物: blueprint.md, risk_statement.md, changes.diff, manifest.json
SKILL_EOF
```

---
**Verification Run:**
```bash
ls -la /root/openclaw-box/scripts/absorb.sh
ls -la /root/gm-skillforge/skills/gm-multi-agent-orchestrator-skill/SKILL.md
```
