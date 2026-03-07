# AI Legion Task Dispatch (2026-03-07)

## Purpose

This document is the active dispatch baseline for the next engineering phase.

Three active tracks:

1. `T1` Architecture remediation backlog
2. `T2` High-value NEW-GM intent migration
3. `T3` Cloud execution stabilization

Governance model:

- `Execution`: implement only within contract scope
- `Review`: inspect quality and boundary correctness
- `Compliance`: enforce fail-closed and archive rules

Hard rule:

- No task closes without `execution evidence + review record + compliance decision`

---

## Global Assignment Rules

### Command Model

- `Orchestrator`: Codex / Antigravity-1
- `Execution Pool`: `vs--cc1`, `vs--cc2`, `vs--cc3`, `Kior-A`, `Kior-B`
- `Review Pool`: `Kior-C`
- `Compliance Pool`: `Antigravity-2`, `Antigravity-1`

### Constraints

- Review and Execution cannot be the same actor.
- Compliance does not implement code.
- Any cloud task must stay inside closed-loop contract + receipt + dual-gate flow.
- Any task with missing evidence is `REQUIRES_CHANGES`.

### Archive Rule

Each completed shard must produce:

- `execution_report`
- `review_decision`
- `compliance_attestation` or final compliance note
- final trace entry in `docs/VERIFICATION_MAP.md`

---

## T1. Architecture Remediation Backlog

### Goal

Close the unresolved architecture risks from `docs/2026-03-06/arch_review_gm_skillforge.md`, focusing on reliability and enforceability before more feature growth.

Dispatch pack:

- `docs/2026-03-07/T1_PROMPT_PACK_2026-03-07.md`

### Shards

#### T1-A. SQLite concurrency hardening

- Scope:
  - add WAL mode / busy timeout where registry DB writes occur
  - verify no obvious lock-prone code path remains in current single-host flow
- Suggested Execution: `vs--cc1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- all registry write paths use explicit sqlite timeout strategy
- WAL/busy timeout behavior is documented in code or ops note
- no regression in current local verification flow

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `SQLite concurrency fail-closed hardening completed`

#### T1-B. Delivery validation crash observability

- Scope:
  - add structured logging for delivery completeness validator failures
  - ensure fail-closed remains unchanged
- Suggested Execution: `vs--cc2`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- validator exceptions are logged with error context
- return semantics remain deny/fail-closed
- one reproducible error sample exists in test or doc note

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `Delivery validation failure logging added without relaxing guard`

#### T1-C. Skill registry discoverability and registration baseline

- Scope:
  - scan current `skills/` tree
  - identify registered vs unregistered skill directories
  - produce canonical registration baseline
- Suggested Execution: `Antigravity-1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: no, depends on current repo-wide truth

Acceptance:

- a machine-readable registry baseline exists
- duplicate / unregistered / legacy skill groups are identified
- next-step consolidation list is explicit

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `Skill registry baseline established for consolidation`

#### T1-D. API perimeter hardening backlog pack

- Scope:
  - requirements completeness
  - API auth gap registration
  - root-level one-shot scripts cleanup plan
- Suggested Execution: `vs--cc3`
- Review: `Kior-C`
- Compliance: `Antigravity-1`
- Parallel: yes

Acceptance:

- backlog pack separates immediate fix vs later cleanup
- each item has owner, risk, and migration path
- no fake closure language

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `API perimeter hardening backlog normalized into executable worklist`

### T1 Parallelization

- Can run in parallel: `T1-A`, `T1-B`, `T1-D`
- Must run after or separately: `T1-C`

### T1 Exit Condition

- all four shards have review + compliance records
- no unresolved `RED` item remains without explicit defer note

---

## T2. High-Value NEW-GM Intent Migration

### Goal

Migrate only the high-value intent set from `D:\\NEW-GM` into GM-SkillForge, based on the scoring model instead of full-copy migration.

### Migration Policy

- migrate `Score >= 80` first
- selectively migrate `65-79` only if they directly strengthen current contracts/gates/evidence
- do not migrate `< 65` in this wave

### Shards

#### T2-A. Constitutional intent parity pack

- Target intents:
  - `constitution_principle_survival`
  - `constitution_principle_default_deny`
  - `constitution_principle_evidence`
- Suggested Execution: `Antigravity-1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: no, these define top-level semantics

Acceptance:

- each principle has mapped implementation locus in current repo
- missing semantics are explicitly identified as code gap or doc gap
- parity result is one of: `already_present / partially_present / missing`

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `Constitutional intent parity pack established`

#### T2-B. Skill lifecycle intent migration

- Target intents:
  - `generate_skill_from_repo`
  - `upgrade_skill_revision`
  - `tombstone_skill`
- Suggested Execution: `vs--cc2`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- lifecycle intents are mapped to current scripts/docs/components
- any missing lifecycle step becomes explicit backlog item
- migration result includes recommended owner path

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `Skill lifecycle intent migration baseline completed`

#### T2-C. Audit and time semantics migration

- Target intents:
  - `audit_repo_skill`
  - `time_semantics`
- Suggested Execution: `vs--cc1`
- Review: `Kior-C`
- Compliance: `Antigravity-1`
- Parallel: yes

Acceptance:

- repository audit semantics are mapped to current evidence chain
- time semantics are aligned with current date-directory and verification flow
- mismatches are documented as exact migration gaps

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `Audit and time semantics migrated into parity baseline`

#### T2-D. Selective spiral intent evaluation

- Target intents:
  - `outer_intent_ingest`
  - `outer_contract_freeze`
  - `outer_artifact_build`
  - `inner_health_audit_intent`
  - `beidou_observability_intent`
- Suggested Execution: `Kior-A`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- each selective intent is labeled `migrate now / abstract only / defer`
- rationale is tied to fit + contribution + value
- no full-copy language is used without proof

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `Selective spiral intent migration decisions recorded`

### T2 Parallelization

- Can run in parallel: `T2-B`, `T2-C`, `T2-D`
- Must lead the wave: `T2-A`

### T2 Exit Condition

- all priority intents in score band `>= 80` have explicit parity status
- selective intents have documented go/no-go decisions

---

## T3. Cloud Execution Stabilization

### Goal

Move the cloud lobster lane from "verified workable" to "stable repeatable operating lane" for repeated overnight or batch execution.

### Shards

#### T3-A. Submit/status/fetch/verify operational stability

- Scope:
  - verify current console + lobsterctl path is deterministic
  - remove known friction around stuck submit/status behavior
- Suggested Execution: `Kior-B`
- Review: `Kior-C`
- Compliance: `Antigravity-1`
- Parallel: yes

Acceptance:

- one-click path works for at least one smoke task without manual shell repair
- status call returns bounded output and exits cleanly
- operator instructions are reduced to minimal reproducible sequence

Verification Map entry:

- category: `CLOUD-ROOT / High-Assurance Env`
- summary: `Cloud lobster control loop stabilized for routine smoke execution`

#### T3-B. Overnight unattended operating checklist

- Scope:
  - define pre-shutdown checklist
  - define morning fetch/verify checklist
  - define failure branch checklist
- Suggested Execution: `Kior-C`
- Review: `Antigravity-1`
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- checklist is executable by non-debug flow
- every step maps to real button/command in current console
- failure branch includes block/remediation language

Verification Map entry:

- category: `CLOUD-ROOT / High-Assurance Env`
- summary: `Overnight unattended runbook approved`

#### T3-C. Parallel cloud batch template

- Scope:
  - produce stable template for `M2/M3/M4` concurrent dispatch
  - keep local review/compliance centralized
- Suggested Execution: `Antigravity-1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: no, depends on current stable lane

Acceptance:

- one batch template defines task ids, wave order, and archive targets
- no executor self-approval path exists
- final aggregation path is explicit

Verification Map entry:

- category: `CLOUD-ROOT / High-Assurance Env`
- summary: `Parallel cloud batch dispatch template approved`

#### T3-D. Cloud operator registry update

- Scope:
  - remove Gemini from active cloud operator assumption
  - align docs with Antigravity-1 + Lobster Console path
- Suggested Execution: `vs--cc3`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- no current-runbook doc instructs Gemini as active dependency
- active cloud chain reflects actual operational path
- history vs current-state distinction remains preserved

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `Cloud operator registry updated to post-Gemini reality`

### T3 Parallelization

- Can run in parallel: `T3-A`, `T3-B`, `T3-D`
- Must follow stable base: `T3-C`

### T3 Exit Condition

- one unattended overnight pattern exists
- one parallel batch template exists
- no current operator doc depends on suspended executor

---

## Recommended Execution Order

### Wave 1

- `T1-A`
- `T1-B`
- `T1-D`
- `T2-A`
- `T3-A`

### Wave 2

- `T1-C`
- `T2-B`
- `T2-C`
- `T2-D`
- `T3-B`
- `T3-D`

### Wave 3

- `T3-C`

---

## Final Gate for This Dispatch

This dispatch is considered complete only when:

1. each shard has a named execution / review / compliance owner
2. each shard has at least one evidence-bearing output
3. completed shards are indexed into `docs/VERIFICATION_MAP.md`
4. deferred shards are explicitly marked with reason, not silently dropped

---

## Archive Targets

- dispatch baseline: `docs/2026-03-07/AI_LEGION_TASK_DISPATCH_2026-03-07.md`
- global registry: `docs/VERIFICATION_MAP.md`
- daily archive: `docs/2026-03-07/verification/ARCHIVE_INDEX_2026-03-07.json`
- daily progress: `docs/2026-03-07/verification/PROGRESS_REPORT_2026-03-07.md`
