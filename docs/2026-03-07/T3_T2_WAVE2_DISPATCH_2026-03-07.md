# T3 + T2 Wave 2 Dispatch (2026-03-07)

## Start Fact

As of `2026-03-07`, the first wave of high-value NEW-GM intent migration from `D:\NEW-GM` to `D:\GM-SkillForge` has been completed and remediated to archive-ready state.

Unified external statement reference:

- `docs/2026-03-07/T2_EXTERNAL_ALIGNMENT_STATEMENT_2026-03-07.md`

Operational interpretation:

- `T2 Wave 1` is no longer the bottleneck
- the next bottleneck is cloud lobster lane stability and unattended repeatability
- only after the cloud lane is stable should `T2 Wave 2` selective migration expand

Required completion-record template for this dispatch:

- `docs/2026-03-07/T3_T2_WAVE2_任务回传模板_COMPLIANT_v1.md`

Rule:

- execution return files for this dispatch must follow the compliant template above
- the earlier non-compliant/base template must not be used as the authoritative return format for this wave

---

## Why This Dispatch Exists

Human version:

1. First, make the cloud lobster lane real and stable.
2. Then, use that stable lane to carry the next selective migration wave.
3. Record this as a new starting fact so the team stops acting like T2 Wave 1 is still unresolved.

Engineering version:

- `T3` is now priority one because operating friction will otherwise keep slowing every later migration batch.
- `T2 Wave 2` should begin only after the cloud submit/status/fetch/overnight path is stable enough to support repeated batch execution.

Mode: `strict`

---

## Track A. T3 Cloud Execution Stabilization

### Goal

Move the lobster cloud lane from "works with operator effort" to "stable repeatable unattended lane".

### T3-A. Submit/status/fetch/verify stability closure

- Scope:
  - verify current Lobster Console + lobsterctl path is deterministic
  - remove stuck submit/status/fetch friction in current practical lane
  - document the minimal reproducible operator path
- Execution: `Kior-B`
- Review: `Kior-C`
- Compliance: `Antigravity-1`
- Parallel: yes

Acceptance:

- one smoke task can run without manual shell repair
- `status` output is bounded and exits cleanly
- `fetch/verify` path is reproducible by documented sequence

Verification Map entry:

- category: `CLOUD-ROOT / High-Assurance Env`
- summary: `Cloud lobster submit-status-fetch loop stabilized`

### T3-B. Overnight unattended runbook

- Scope:
  - define pre-shutdown checklist
  - define morning fetch/verify checklist
  - define failure branch checklist
  - keep it executable by non-debug operator flow
- Execution: `Kior-C`
- Review: `Antigravity-1`
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- one unattended overnight runbook exists
- every step maps to current real console/button/command
- failure branch includes block/remediation wording

Verification Map entry:

- category: `CLOUD-ROOT / High-Assurance Env`
- summary: `Overnight unattended lobster runbook approved`

### T3-C. Parallel cloud batch template

- Scope:
  - produce stable template for concurrent cloud dispatch batches
  - keep local review/compliance centralized
  - define archive targets and aggregation path
- Execution: `Antigravity-1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: no, depends on stable lane from T3-A

Acceptance:

- one batch template defines task ids, wave order, archive targets, and aggregation rules
- no executor self-approval path exists
- final aggregation path is explicit

Verification Map entry:

- category: `CLOUD-ROOT / High-Assurance Env`
- summary: `Parallel lobster cloud batch template approved`

### T3-D. Cloud operator documentation normalization

- Scope:
  - align current docs with Lobster Console + Antigravity-1 cloud path
  - remove stale operator assumptions from current runbooks
  - preserve history vs current-state distinction
- Execution: `vs--cc3`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: yes

Acceptance:

- no current runbook treats suspended executors as active dependency
- current cloud chain matches actual operator path
- historical records remain untouched as history

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `Cloud operator documentation normalized to current lobster lane`

---

## Track B. T2 Wave 2 Selective Migration

### Goal

Migrate the next selective set of NEW-GM intents that are still valuable enough to move, but were outside Wave 1 closure.

### Wave 2 Policy

- only handle intents that are still worth migrating after Wave 1
- prefer intents that strengthen contracts/gates/evidence or future batch execution
- do not reopen already-closed Wave 1 items unless a new defect is found

### T2W2-A. Non-F1 migration-doc path normalization pack

- Scope:
  - identify remaining non-F1 `intent_map.yml` entries still pointing to migration-doc paths
  - classify them into `promote now / keep docs-backed with reason / defer`
- Execution: `vs--cc2`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: yes, but closure depends on T3-A signal

Acceptance:

- each remaining docs-backed non-F1 entry has explicit disposition
- no ambiguous active path remains without owner reason
- output separates production-ready vs docs-backed-by-design

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `Wave 2 migration-doc path normalization baseline established`

### T2W2-B. Selective intent contract promotion shortlist

- Scope:
  - choose next selective intents worth mainline promotion after Wave 1
  - tie selection to fit + contribution + operational value
  - produce shortlist, not full migration
- Execution: `Kior-A`
- Review: `Kior-C`
- Compliance: `Antigravity-1`
- Parallel: yes

Acceptance:

- shortlist is explicit and ordered
- each shortlisted intent has rationale and expected owner path
- low-fit intents are explicitly deferred

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `Wave 2 selective intent shortlist established`

### T2W2-C. Wave 2 migration execution preconditions

- Scope:
  - define the preconditions required before Wave 2 selective intent execution starts
  - bind them to T3 stabilization outputs
- Execution: `Antigravity-1`
- Review: `Kior-C`
- Compliance: `Antigravity-2`
- Parallel: no, depends on T3-A/T3-B findings

Acceptance:

- execution preconditions are explicit
- cloud-lane dependency is stated, not implied
- no Wave 2 execution starts under undefined operating conditions

Verification Map entry:

- category: `LOCAL-ANTIGRAVITY / Architect Core`
- summary: `Wave 2 execution preconditions formalized`

---

## Execution Order

### Wave 1

- `T3-A`
- `T3-B`
- `T3-D`

### Wave 2

- `T3-C`
- `T2W2-A`
- `T2W2-B`

### Wave 3

- `T2W2-C`

---

## Exit Condition

This dispatch is complete only when:

1. `T3-A/T3-B/T3-C/T3-D` have execution, review, and compliance records
2. one unattended lobster pattern exists
3. one stable parallel cloud batch template exists
4. `T2W2-A/T2W2-B/T2W2-C` define Wave 2 migration scope and preconditions
5. `docs/VERIFICATION_MAP.md` reflects both cloud stabilization and Wave 2 baseline

---

## Archive Targets

- dispatch baseline: `docs/2026-03-07/T3_T2_WAVE2_DISPATCH_2026-03-07.md`
- external alignment statement: `docs/2026-03-07/T2_EXTERNAL_ALIGNMENT_STATEMENT_2026-03-07.md`
- global registry: `docs/VERIFICATION_MAP.md`
