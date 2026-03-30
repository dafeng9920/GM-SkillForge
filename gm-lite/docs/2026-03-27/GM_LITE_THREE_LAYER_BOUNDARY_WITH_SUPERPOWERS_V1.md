# GM_LITE_THREE_LAYER_BOUNDARY_WITH_SUPERPOWERS_V1

## Purpose

Freeze the current system boundary for the three-layer structure so later `GM-LITE` enhancement work does not drift.

---

## Core Positioning

### 1. GM-Lite

`GM-LITE` is the **upstream task-reality layer + lightweight access/adaptation entry + execution bridge layer**.

It is responsible for:

- shared task reality
- task discovery and dispatch boundary
- receipt / writeback / escalation protocol path
- lightweight plugin/access entry
- executor/plugin adaptation entry
- operator-visible control surface
- execution-bridge preparation

It is **not** responsible for:

- final governance judgment
- public release trust decisions
- heavy runtime orchestration
- heavy scheduling
- complex lifecycle management
- database/watcher/plugin-host expansion by default
- heavy execution methodology itself
- becoming a full plugin runtime platform

---

### 2. Superpowers-Class Layer

`superpowers` is the **execution methodology layer**.

It is responsible for:

- spec-first execution
- plan-first execution
- review / verification methodology
- structured implementation flow
- subagent-style execution discipline

It is **not** responsible for:

- owning `.gm_bus` as the task source of truth
- directly mutating global `GM-LITE` state
- final permit / archive / publish decisions
- replacing governance

Short definition:

> Superpowers is an execution methodology layer, not a task-reality layer and not a governance layer.

---

### 3. SkillForge

`SkillForge` is the **governance and trust-decision layer + L3 standard skill solidification layer**.

It is responsible for:

- audit
- evidence
- gate / permit
- archive
- publish judgment
- trusted asset intake
- candidate-result convergence
- standard metadata completion
- L3 skill packaging / solidification
- turning candidate capability into governed, reusable standard skill

It should consume:

- standardized `Writeback`
- `EvidenceRef`
- `ArtifactRef`
- `ExecutionSummary`
- `StateLog`

It should **not** depend on raw free-form executor text as its main trust input.

Short definition:

> SkillForge first judges, then solidifies.
> It is both the governance layer and the standard skill foundry.

---

## Bridge Principle

`GM-LITE` should not expose full `.gm_bus` semantics directly to execution engines.

The correct middle layer is a thin:

- `GM Execution Bridge`

Its job is only to:

- read dispatch objects
- compress them into `ExecutionLaunchContract`
- create `.gm_exec` run workspace
- receive standardized result objects
- translate them back into `GM-LITE` return flow

It must **not** become a second orchestration kernel.

---

## Working Model

### Current Development Order

1. Build `D:\gm-lite` and its plugin into a stable upstream working layer.
2. Use that layer to support development of the broader `GM-SkillForge` system.
3. Later merge `GM-LITE` into `GM-SkillForge` as the upstream/front section of the main chain.

This means:

> `D:\gm-lite` is currently an independent authority tree for stable development,
> but its long-term role is as the upstream/front and output section of `GM-SkillForge`.

---

## Practical Boundary For Future Enhancement

### GM-Lite can be strengthened in three directions

1. **Task-reality strengthening**
   - stronger task context
   - clearer state chain
   - better writeback / escalation visibility

2. **Execution-bridge strengthening**
   - `ExecutionLaunchContract`
   - `.gm_exec` workspace
   - standardized return objects

3. **Plugin entry strengthening**
   - less manual forwarding
   - less manual status checking
   - better quick actions
   - stronger visible operator feedback

### GM-Lite should not drift into

- final governance
- full heavy runtime by default
- executor-owned bus mutation
- free-form black-box task execution
- full plugin runtime center
- heavy lifecycle/scheduler kernel

---

## Canonical Summary

> `GM-LITE` = upstream task-reality layer + lightweight access/adaptation entry + execution-bridge layer  
> `superpowers` = execution methodology enhancement layer  
> `SkillForge` = governance and trust-decision layer + L3 standard skill solidification layer

This is the boundary that later work should preserve.

---

## Simplified Working Definitions

### GM-Lite

Responsible for:

> letting different plugins/agents see the same task, and be uniformly dispatched and written back

### superpowers

Responsible for:

> producing higher-quality candidate outputs from the task

These candidate outputs may include:

- spec
- code
- tests
- docs
- patches
- workflows
- intermediate artifacts

They are not yet final L3 skills.

### SkillForge

Responsible for:

> deciding whether the produced result is trustworthy, releasable, archivable, and then solidifying it into a governed L3 standard skill

---

## Risk Notes

### 1. GM-LITE overgrowth risk

If scheduling, lifecycle, governance, and heavy execution logic are all pushed into `GM-LITE`, it will bloat into a monolithic upstream kernel and lose its lightweight role.

### 2. Lightweight entry misread as runtime center

If "lightweight plugin/access entry" is misread as "full plugin runtime platform", `GM-LITE` will begin overlapping with `superpowers` and `SkillForge`.

### 3. Bridge-governance coupling risk

If the execution bridge starts owning audit, permit, or trust judgment, the three-layer boundary collapses quickly.

### 4. SkillForge narrowed to only a judge

If `SkillForge` is treated only as an acceptance gate, its L3 solidification/factory role will be underestimated and split elsewhere, breaking responsibility and evidence continuity.

---

## End-to-End Chain

`GM-LITE` discovers and dispatches the task  
→ `superpowers` produces candidate outputs  
→ `SkillForge` audits, converges, repairs, and solidifies  
→ L3 standard skill is archived / published / reused
