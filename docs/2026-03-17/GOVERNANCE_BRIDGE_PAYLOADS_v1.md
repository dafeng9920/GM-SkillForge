# GOVERNANCE_BRIDGE_PAYLOADS_v1

## 1. Governance Candidate Intake Payload

- Source:
  - `CandidateSkill`
- Draft file:
  - `contracts/governance_bridge/candidate_intake.payload.json`
- Role:
  - governance-consumable input only
  - not governance-approved candidate

## 2. Governance Validation Intake Payload

- Source:
  - `BuildValidationReport`
- Draft file:
  - `contracts/governance_bridge/validation_intake.payload.json`
- Role:
  - governance-consumable input only
  - not governance validation result

## 3. Pre-Packaging Review Intake Payload

- Source:
  - `DeliveryManifest`
- Draft file:
  - `contracts/governance_bridge/pre_packaging_review.payload.json`
- Role:
  - pre-packaging review input only
  - not release permit
