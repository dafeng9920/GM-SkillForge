# GOVERNANCE_BRIDGE_PAYLOAD_DRAFTS_v1

## 1. GovernanceCandidateIntakePayload

- Purpose:
  - Receive production-side candidate object as governance intake input
- Source:
  - `CandidateSkill`
- Draft fields:
  - `candidate_id`
  - `intent_id`
  - `contract_id`
  - `candidate_name`
  - `skill_root`
  - `generated_files`
  - `entrypoints`
  - `dependencies`
  - `required_changes`
  - `production_status`

## 2. GovernanceValidationIntakePayload

- Purpose:
  - Receive build-side validation result as governance intake input
- Source:
  - `BuildValidationReport`
- Draft fields:
  - `report_id`
  - `candidate_id`
  - `checks`
  - `summary`
  - `missing_artifacts`
  - `broken_references`
  - `smoke_test_result`
  - `trace_result`
  - `handoff_ready`
  - `build_validation_status`

## 3. PrePackagingReviewIntakePayload

- Purpose:
  - Receive delivery-prep object before any packaging review logic
- Source:
  - `DeliveryManifest`
- Draft fields:
  - `delivery_id`
  - `candidate_id`
  - `validation_report_id`
  - `delivery_name`
  - `package_input_root`
  - `handoff_target`
  - `package_manifest`
  - `integrity_checks`
  - `handoff_payload`
  - `delivery_status`
