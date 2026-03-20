# BRIDGE_COMPAT_AND_RISK_CONTROLS_v1

## 1. ContractBundle.status.validated

- Current status:
  - compat / legacy-style only
- Minimal implementation handling:
  - does not enter bridge recommended primary fields
  - if ever referenced, may only appear as production-background context
- Explicitly forbidden reinterpretation:
  - governance validated
  - gate pass
  - release ready

## 2. CandidateSkill.status -> production_status

- Enters minimal implementation:
  - yes
- Protection rule:
  - must remain a production-side status label
  - must not be interpreted as review result

## 3. BuildValidationReport.status -> build_validation_status

- Enters minimal implementation:
  - yes
- Protection rule:
  - must remain build-side validation status
  - must not be interpreted as governance validation result

## 4. DeliveryManifest.status -> delivery_status

- Enters minimal implementation:
  - yes
- Protection rule:
  - must remain delivery-prep status
  - must not be interpreted as release permit or publish state

## 5. Shared control rule

- All bridge status-like fields must carry source-layer prefixes in meaning:
  - `production_`
  - `build_validation_`
  - `delivery_`
- No bridge minimal implementation may emit:
  - governance decision
  - review decision
  - release decision
