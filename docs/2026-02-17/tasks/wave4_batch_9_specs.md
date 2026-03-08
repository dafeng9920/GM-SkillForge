# Wave 4 Batch 1: The "Legion 9" Dispatch Specs

> **Status**: READY FOR DISPATCH
> **Objective**: Migrate 9 Core/Strategy Assets from `NEW-GM` to `SkillForge`.
> **Constraint**: NO Code Copying. Intent Migration Only.

---

## 🟢 Group A: Core Tooling (Agents 1-4)

### Task T-W4-01: Audit Repo Skill
**Executor**: Agent-1
**Source**: `NEW-GM/scripts/audit_tools_v0_5.ps1` (Logic Reference)
**Target**: `skillforge/src/skills/audit_repo.py`
**Instructions**:
1. Define Contract: `contracts/intents/audit_repo.yml`
2. Implement Logic: Scan a target repo path against `contracts/constitution_v1.md`.
3. Output: `ScanReport` (Pass/Fail + FailReason).
4. Evidence: Must generate `audit_scan_receipt`.

### Task T-W4-02: Generate Skill
**Executor**: Agent-2
**Source**: `NEW-GM/scripts/scaffold_skill.py` (Logic Reference)
**Target**: `skillforge/src/skills/generate_skill.py`
**Instructions**:
1. Define Contract: `contracts/intents/generate_skill.yml`
2. Implement Logic: Take `ScanReport` + `RepoPath` -> Generate `SkillSpec`.
3. Output: `SkillSpec` (YAML string).
4. Gate: Must verify license compatibility.

### Task T-W4-03: Upgrade Skill
**Executor**: Agent-3
**Source**: `NEW-GM/scripts/update_revision.py` (Logic Reference)
**Target**: `skillforge/src/skills/upgrade_skill.py`
**Instructions**:
1. Define Contract: `contracts/intents/upgrade_skill.yml`
2. Implement Logic: Increment revision, append to `evolution.json`.
3. Output: `UpgradeManifest`.
4. Constraint: Atomic update only.

### Task T-W4-04: Tombstone Skill
**Executor**: Agent-4
**Source**: `NEW-GM/AUDIT/CONSTITUTION.md` (Section 3: Default Deny)
**Target**: `skillforge/src/skills/tombstone.py`
**Instructions**:
1. Define Contract: `contracts/intents/tombstone.yml`
2. Implement Logic: Write a `REVOKED` record to `tombstones.json`.
3. Constraint: Once revoked, never valid again (Fail-Closed).

---

## 🔵 Group B: Strategy Assets (Agents 5-7)

### Task T-W4-05: Trend Following Strategy
**Executor**: Agent-5
**Source**: `NEW-GM/strategies/template_trend_following.py`
**Target**: `skillforge/src/skills/strategies/trend_following.py`
**Instructions**:
1. Extract Intent: MA Crossover + ATR Trailing Stop.
2. Implement as `Skill`: Input `MarketData` -> Output `Signal`.
3. Evidence: `BacktestRef` (Simulated).

### Task T-W4-06: Mean Reversion Strategy
**Executor**: Agent-6
**Source**: `NEW-GM/strategies/template_mean_reversion.py`
**Target**: `skillforge/src/skills/strategies/mean_reversion.py`
**Instructions**:
1. Extract Intent: RSI + Bollinger Bands.
2. Implement as `Skill`: Input `MarketData` -> Output `Signal`.
3. Constraint: Must handle `volume_threshold`.

### Task T-W4-07: Multi-Factor Strategy
**Executor**: Agent-7
**Source**: `NEW-GM/strategies/template_multi_factor.py`
**Target**: `skillforge/src/skills/strategies/multi_factor.py`
**Instructions**:
1. Extract Intent: Composite Score of (Momentum, Value, Quality).
2. Implement as `Skill`: Input `FactorData` -> Output `PortfolioWeights`.
3. Note: This is an advanced migration, ensure clean scoring logic.

---

## 🟡 Group C: Foundation & Kernel (Agents 8-9)

### Task T-W4-08: Evidence Schema
**Executor**: Agent-8
**Source**: `NEW-GM/AUDIT/EVIDENCE_SCHEMA.md`
**Target**: `skillforge/src/contracts/evidence_schema.yaml`
**Instructions**:
1. Formalize the markdown schema into a strict YAML contract.
2. Define `StandardEvidence` types (ScanReport, TestResult, Tombstone).
3. Objective: This becomes the validation rules for all other skills.

### Task T-W4-09: Time Semantics (Kernel)
**Executor**: Agent-9
**Source**: `NEW-GM/AUDIT/CONSTITUTION.md` (Section 4: Time Semantics)
**Target**: `skillforge/src/kernel/time_manager.py`
**Instructions**:
1. Implement `EventTime` vs `AvailableTime` logic.
2. Logic: `assert available_time <= decision_time`.
3. This is a Kernel-level utility used by all RAG/Backtest skills.
