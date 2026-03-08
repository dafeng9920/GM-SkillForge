# Task Skill Spec

```yaml
task_id: "T21"
executor: "Kior-A"
wave: "Wave 1"
depends_on: []
estimated_minutes: 85

input:
  description: "SEEDS-P0-3 Permit 强制钩子：统一 permit_required(action) 规则与配置"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "permit_policy 模板"
    - path: "skillforge/src/contracts/policy/membership_middleware.py"
      purpose: "中间件接入点"
    - path: "skillforge/src/skills/gates/gate_permit.py"
      purpose: "E001/E003 语义基线"
  constants:
    job_id: "L45-D4-SEEDS-P0-20260220-004"
    skill_id: "l45_seeds_p0_foundation"

output:
  deliverables:
    - path: "security/permit_policy.yml"
      type: "新建"
      schema_ref: "actions_requiring_permit policy"
    - path: "skillforge/src/contracts/policy/permit_required.py"
      type: "新建"
      schema_ref: "permit_required(action) helper"
    - path: "skillforge/tests/test_permit_required_policy.py"
      type: "新建"
      schema_ref: "无 permit 阻断语义测试"
  constraints:
    - "所有副作用动作统一走 permit_required(action)"
    - "deny_without_permit_error_code 固定为 PERMIT_REQUIRED"
    - "语义不得漂移"

deny:
  - "不得修改 E001 错误语义"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_permit_required_policy.py"
      expect: "passed"
```

