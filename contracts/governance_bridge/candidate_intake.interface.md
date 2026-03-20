# candidate_intake.interface

- Interface role:
  - Draft intake interface only
  - Not a governance object implementation
  - Not a decision interface
  - Not an executable service

- Upstream object:
  - `CandidateSkill`

- Allowed callers:
  - `production-chain assembler`
  - `candidate intake adapter`

- Forbidden callers:
  - `skill-creator`
  - `release-manager`
  - `workflow/orchestrator` as decision owner

- Forbidden semantics:
  - approved
  - gate-pass
  - release-ready
