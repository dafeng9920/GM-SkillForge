# GOVERNANCE_BRIDGE_INTERFACE_MAP_v1

## 1. CandidateSkill -> Governance Candidate Intake

- Bridge name:
  - `production_candidate_to_governance_candidate_intake`
- Input object:
  - `CandidateSkill`
- Output placeholder:
  - `GovernanceCandidateIntakePayload`
- Allowed fields:
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
- Forbidden semantics:
  - `governance_approved`
  - `gate_passed`
  - `release_ready`

## 2. BuildValidationReport -> Governance Validation Intake

- Bridge name:
  - `production_validation_to_governance_validation_intake`
- Input object:
  - `BuildValidationReport`
- Output placeholder:
  - `GovernanceValidationIntakePayload`
- Allowed fields:
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
- Forbidden semantics:
  - `governance_validation_passed`
  - `audit_passed`
  - `review_passed`
  - `release_allowed`

## 3. DeliveryManifest -> Pre-Packaging Review Intake

- Bridge name:
  - `delivery_manifest_to_pre_packaging_review_intake`
- Input object:
  - `DeliveryManifest`
- Output placeholder:
  - `PrePackagingReviewIntakePayload`
- Allowed fields:
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
- Forbidden semantics:
  - `release_permit`
  - `publish_approved`
  - `released`

## 4. Fourth bridge point suggestion

- Suggested placeholder only:
  - `PrePackagingReviewResult -> skill-creator package intake`
- Status:
  - suggestion only
  - not part of current bridge preparation implementation
