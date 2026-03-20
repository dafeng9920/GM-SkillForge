# T10: Judgment Override / Residual Risk / Release Decision / Escalation Gate

## Task Summary

**Task ID**: T10
**Deliverables**:
- `judgment_overrides.schema.json` - Schema for judgment override records
- `residual_risks.schema.json` - Schema for residual risk records
- `release_decision.schema.json` - Schema for final release decisions
- Sample scenarios demonstrating the full system

## Hard Constraints Enforced

1. **CRITICAL findings without evidence CANNOT be overridden**
2. **Findings without evidence_refs CANNOT be whitewashed**
3. **Judgment override CANNOT use free-form text** - structured enums only
4. **Contract failures REQUIRE rejection** - no exceptions

---

## Schema Overview

### 1. Judgment Overrides (`judgment_overrides.schema.json`)

**Purpose**: Defines when and how human judgment can override automated gate decisions.

**Key Features**:
- Structured justification codes (NO free-form text)
- Mandatory approver identity with role-based authority
- Evidence binding for audit trail
- Conditions attached to overrides
- Links to residual risk records

**Allowed Override Scenarios** (enum):
```json
[
  "FALSE_POSITIVE_DETECTED",
  "COMPENSATING_CONTROL_EXISTS",
  "ACCEPTANCE_WINDOW_ACTIVE",
  "BUSINESS_JUSTIFICATION",
  "TECHNICAL_DEBT_ACCEPTED",
  "TRANSIENT_CONDITION",
  "DEPENDENCY_VALIDATED",
  "DOCUMENTATION_ACCEPTED",
  "TEST_COVERAGE_VERIFIED",
  "RISK_ACCEPTED_PENDING_FIX"
]
```

**Cannot Override**:
- CRITICAL severity findings (hard block)
- Findings without evidence_refs
- Contract validation failures (E3xx)

**Override ID Format**: `O-{run_id}-{seq}`
Example: `O-20260316_120000-1`

---

### 2. Residual Risks (`residual_risks.schema.json`)

**Purpose**: Documents risks that remain after mitigation or override, with tracking and remediation requirements.

**Key Features**:
- Risk level assessment (CRITICAL/HIGH/MEDIUM/LOW)
- Likelihood and Impact scoring
- Mitigation strategy (avoid/transfer/mitigate/accept/monitor)
- Status tracking (open/mitigating/monitoring/accepted/closed)
- Links to source finding and override

**Risk ID Format**: `R-{run_id}-{seq}`
Example: `R-20260316_120000-1`

**Risk Categories**:
- `security` - Security vulnerabilities
- `correctness` - Functional correctness issues
- `performance` - Performance concerns
- `reliability` - Reliability and availability
- `compliance` - Regulatory/compliance issues
- `data_quality` - Data integrity concerns
- `access_control` - Authorization/authentication
- `supply_chain` - Dependency risks

---

### 3. Release Decision (`release_decision.schema.json`)

**Purpose**: Defines the final gate decision with structured evidence binding and escalation paths.

**Decision Outcomes**:
| Outcome | Description | Conditions |
|---------|-------------|------------|
| `RELEASE` | Full release | No blocking findings, no residual risks |
| `CONDITIONAL_RELEASE` | Release with conditions | Overrides approved, residual risks mitigating |
| `LIMITED_RELEASE` | Limited scope release | Scope restrictions apply |
| `ESCALATE` | Escalate to higher authority | Novel risk, exceeds delegated authority |
| `REJECT` | Reject release | Critical findings, no evidence, contract fails |

**Rationale Codes** (enum):
```json
[
  "ALL_CHECKS_PASSED",
  "CRITICAL_FINDINGS_UNRESOLVED",
  "HIGH_RISK_THRESHOLD_EXCEEDED",
  "EVIDENCE_INCOMPLETE",
  "OVERRIDE_APPROVED",
  "CONDITIONAL_ACCEPTANCE",
  "LIMITED_SCOPE_APPROVED",
  "ESCALATION_REQUIRED",
  "REMEDIATION_REQUIRED",
  "DEFERRED_DECISION"
]
```

---

## Sample Scenarios

### Sample 1: Clean Release
**File**: `sample_1_clean_release.json`

**Scenario**: All checks passed, no overrides needed.
- **Findings**: 2 total (1 LOW, 1 INFO)
- **Overrides**: 0
- **Residual Risks**: 0
- **Decision**: RELEASE
- **Rationale**: ALL_CHECKS_PASSED

### Sample 2: Conditional Release with Overrides
**File**: `sample_2_conditional_release.json`

**Scenario**: HIGH and MEDIUM findings overridden with compensating controls.
- **Findings**: 8 total (2 HIGH, 3 MEDIUM)
- **Overrides**: 2
  - subprocess usage → COMPENSATING_CONTROL_EXISTS
  - missing error handling → TEST_COVERAGE_VERIFIED
- **Residual Risks**: 2 (MEDIUM, LOW)
- **Decision**: CONDITIONAL_RELEASE
- **Conditions**: Monitoring, remediation deadline, staging-only
- **Scope**: staging environment, specific teams, usage limits

### Sample 3: Rejection
**File**: `sample_3_rejection.json`

**Scenario**: CRITICAL finding (eval on user input) cannot be overridden.
- **Findings**: 5 total (1 CRITICAL, 2 HIGH)
- **Overrides**: 0 (blocked by hard constraint)
- **Residual Risks**: 0
- **Decision**: REJECT
- **Rationale**: CRITICAL_FINDINGS_UNRESOLVED
- **Reason**: eval() usage is CRITICAL severity, no evidence of mitigating controls

### Sample 4: Escalation
**File**: `sample_4_escalation.json`

**Scenario**: Novel LLM prompt injection pattern exceeds delegated authority.
- **Findings**: 4 total (1 HIGH - novel pattern)
- **Overrides**: 1 (escalation recommended)
- **Residual Risks**: 1 HIGH
- **Decision**: ESCALATE
- **Escalated To**: SECURITY_COUNCIL
- **Reason**: NOVEL_ATTACK_VECTOR

---

## Decision Matrix

| Finding Severity | Evidence Present | Override Possible | Decision |
|------------------|------------------|-------------------|----------|
| CRITICAL | No | NO | REJECT |
| CRITICAL | Yes + Compensating Control | MAYBE* | ESCALATE |
| HIGH | Yes | YES (Security Architect) | Conditional |
| MEDIUM | Yes | YES (Tech Lead) | Conditional |
| LOW | Yes | YES (Tech Lead) | Release |
| INFO | Any | N/A | Release |

*CRITICAL with evidence requires escalation to Security Council or CTO office.

---

## Audit Trail

Every decision must include:
1. **Decision Chain**: Chronological record of all decisions
2. **Evidence Refs**: Links to all supporting evidence
3. **Approver Identity**: Who made the decision and their role
4. **Timestamps**: When each decision was made

---

## File Structure

```
skillforge/src/contracts/
├── judgment_overrides.schema.json
├── residual_risks.schema.json
├── release_decision.schema.json
└── T10_samples/
    ├── sample_1_clean_release.json
    ├── sample_2_conditional_release.json
    ├── sample_3_rejection.json
    └── sample_4_escalation.json
```

---

## Integration Points

**Input from**:
- T3: `validation_report.json` (ValidationFailure)
- T4: `rule_scan_report.json` (RuleHit)
- T5: `pattern_detection_report.json` (PatternMatch)
- T6: `findings.json` (Unified Finding)

**Output to**:
- Gate decision process
- AuditPack/evidence/
- Release orchestration

---

## Compliance Notes

**Antigravity-1 Compliance**:
- All override decisions are recorded in judgment_overrides.json
- Residual risks are tracked with mitigation plans
- Evidence refs bind to all supporting documents
- Decision chain provides complete traceability

**Closed-Loop Contract Standards**:
- Receipt references: task_id, contract_hash, artifact_digest
- Dual-gate: entry + exit decisions both recorded
- Override decisions include gate_decision references

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0-t10 | 2026-03-16 | Initial T10 deliverable |

---

## References

- T3: Skill Contract Validator
- T4: Rule Scanner
- T5: Pattern Matcher
- T6: Finding Builder
- Gate Interface: `gate_interface_v1.yaml`
