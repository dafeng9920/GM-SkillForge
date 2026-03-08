# Wave 4 Batch Specs: Library Migration (Phase 1)

> **Instructions**: 
> 将以下 4 个 Task 分发给 4 个独立的 Coding Agent 并行执行。
> 统一目标：Generate Contract (`contracts/intents/*.yml`) and Implementation (`skills/*.py`).

---

## Task T-W4-01: Audit Repo Skill

**Executor**: Agent-1
**Input**: 
- `skillforge/src/orchestration/intent_map.yml` (Target: `audit_repo_skill`)
- `skillforge/src/contracts/rag_3d.yaml` (Reference)
**Output**:
- `skillforge/src/contracts/intents/audit_repo.yml`
- `skillforge/src/skills/audit_repo.py`
**Constraints**:
- Must implement `repo_scan_fit_score` logic.
- Must produce `L3 AuditPack` with `scan_report`.

---

## Task T-W4-02: Generate Skill

**Executor**: Agent-2
**Input**: 
- `skillforge/src/orchestration/intent_map.yml` (Target: `generate_skill_from_repo`)
**Output**:
- `skillforge/src/contracts/intents/generate_skill.yml`
- `skillforge/src/skills/generate_skill.py`
**Constraints**:
- Must implement `draft_skill_spec` strategy (plug-in style).
- Must enforce `license_gate`.

---

## Task T-W4-03: Upgrade Skill

**Executor**: Agent-3
**Input**: 
- `skillforge/src/orchestration/intent_map.yml` (Target: `upgrade_skill_revision`)
**Output**:
- `skillforge/src/contracts/intents/upgrade_skill.yml`
- `skillforge/src/skills/upgrade_skill.py`
**Constraints**:
- Must consume `evolution.json` (Wave 3 asset).
- Must ensure regression testing pass.

---

## Task T-W4-04: Tombstone Skill

**Executor**: Agent-4
**Input**: 
- `skillforge/src/orchestration/intent_map.yml` (Target: `tombstone_skill`)
**Output**:
- `skillforge/src/contracts/intents/tombstone.yml`
- `skillforge/src/skills/tombstone.py`
**Constraints**:
- Must write to `system-of-record` index (Wave 3).
- Critical: Dead means DEAD. No bypass.
