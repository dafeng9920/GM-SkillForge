#!/bin/bash
#
# GOVERNANCE ASSET PUSH (Local to Cloud)
#
# Usage:
#   chmod +x push_governance_assets.sh
#   ./push_governance_assets.sh <CLOUD_HOST>
#

HOST="${1:-152.136.25.101}"
USER="root"
# 物理宿主机根 (脚本与 Docs 落点)
CLOUD_BOX="/root/openclaw-box"
# 项目工作根 (Skill 源码落点)
CLOUD_REPO="/root/gm-skillforge"

echo "--- [1/2] Pushing Scripts to BOX ---"
ssh ${USER}@${HOST} "mkdir -p ${CLOUD_BOX}/scripts"
scp scripts/verify_governance_env.sh scripts/pre_absorb_check.sh scripts/absorb.sh ${USER}@${HOST}:${CLOUD_BOX}/scripts/

echo "--- [2/2] Pushing Skills to REPO ---"
ssh ${USER}@${HOST} "mkdir -p ${CLOUD_REPO}/skills"

# Syncing individual skills
for skill in \
    "gm-multi-agent-orchestrator-skill" \
    "lobster-task-package-skill" \
    "lobster-absorb-gate-skill" \
    "lobster-cloud-execution-governor-skill"; do
    echo "Syncing $skill..."
    ssh ${USER}@${HOST} "mkdir -p ${CLOUD_REPO}/skills/$skill"
    scp -r skills/$skill/* ${USER}@${HOST}:${CLOUD_REPO}/skills/$skill/
done

echo "--- Final Verification ---"
ssh ${USER}@${HOST} "ls -la ${CLOUD_BOX}/scripts/absorb.sh && ls -la ${CLOUD_REPO}/skills/gm-multi-agent-orchestrator-skill/SKILL.md"

echo "DONE."
