# Task Skill Spec

```yaml
task_id: "T28"
executor: "vs--cc3"
wave: "Wave 1"
depends_on: []
estimated_minutes: 85

input:
  description: "CI 强制门：将 P0/P1 seed 校验接入 pre-merge 与 nightly"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "P0/P1 DoD 规则"
    - path: "docs/2026-02-20/task_dispatch_T28-T34.md"
      purpose: "读取批次目标"
  constants:
    job_id: "L45-D6-SEEDS-P2-20260220-006"
    skill_id: "l45_seeds_p2_operationalization"

output:
  deliverables:
    - path: ".github/workflows/seeds-governance.yml"
      type: "新建"
      schema_ref: "CI workflow"
    - path: "scripts/validate_seeds_p0_p1.py"
      type: "新建"
      schema_ref: "strict seed validator"
    - path: "docs/2026-02-20/L45_P2_CI_GOVERNANCE_REPORT_v1.md"
      type: "新建"
      schema_ref: "CI 接入报告"
  constraints:
    - "strict 模式失败即阻断"
    - "pre-merge 与 nightly 都可执行"
    - "校验结果可审计"

deny:
  - "不得跳过 strict 失败"

gate:
  auto_checks:
    - command: "python scripts/validate_seeds_p0_p1.py --strict"
      expect: "passed"
```

