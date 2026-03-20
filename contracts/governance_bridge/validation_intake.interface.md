# validation_intake.interface

- Interface role:
  - Draft intake interface only
  - Not a governance validation implementation
  - Not a decision interface
  - Not an executable service

- Upstream object:
  - `BuildValidationReport`

- Allowed callers:
  - `build-validation adapter`
  - `governance intake adapter`

- Forbidden callers:
  - `release-manager`
  - `audit-pack builder`
  - `workflow/orchestrator` as decision owner

- Forbidden semantics:
  - governance-pass
  - audit-pass
  - release-allowed
