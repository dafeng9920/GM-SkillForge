# pre_packaging_review.interface

- Interface role:
  - Draft pre-packaging review intake only
  - Not a release permit
  - Not a publish decision interface
  - Not an executable review service

- Upstream object:
  - `DeliveryManifest`

- Allowed callers:
  - `delivery adapter`
  - `pre-packaging review adapter`

- Forbidden callers:
  - `skill-creator` as review decision maker
  - `release-manager`
  - `workflow/orchestrator` as decision owner

- Forbidden semantics:
  - release-permit
  - publish-approved
  - released
