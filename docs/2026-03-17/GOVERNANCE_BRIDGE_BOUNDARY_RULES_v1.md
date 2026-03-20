# GOVERNANCE_BRIDGE_BOUNDARY_RULES_v1

## 1. Production / Governance separation

- Production outputs are not governance decisions.
- Production objects may be consumed by governance intake, but may not become
  governance objects without an explicit bridge payload layer.

## 2. Object identity rules

- `CandidateSkill` is not `Governance Approved Candidate`
- `BuildValidationReport` is not `GovernanceValidation`
- `DeliveryManifest` is not `Release Permit`

## 3. skill-creator boundary

- `skill-creator` stays in packaging/delivery layer.
- It must not become governance intake, governance reviewer, or release
  decision authority.

## 4. workflow / orchestrator boundary

- `workflow/orchestrator` may later call bridge interfaces.
- It may not own decision semantics.
- It may not write governance conclusions.

## 5. Compat control rules

- `ContractBundle.status.validated` remains compatibility-only.
- Bridge layers must not reinterpret it as:
  - governance validated
  - gate pass
  - release ready

## 6. Allowed bridge preparation outputs

- payload mapping docs
- payload/schema drafts
- interface maps
- boundary rule docs

## 7. Forbidden bridge preparation outputs

- governance implementation code
- release implementation code
- handoff execution code
- workflow binding code
