# Task Skill Spec

```yaml
task_id: "T30"
executor: "vs--cc2"
wave: "Wave 1"
depends_on: []
estimated_minutes: 80

input:
  description: "Feature Flags 环境化：enable_n8n_execution 改为按环境 profile 生效"
  context_files:
    - path: "orchestration/feature_flags.yml"
      purpose: "现有 flags"
    - path: "skillforge/src/contracts/governance/feature_flag_loader.py"
      purpose: "读取逻辑接入点"
  constants:
    job_id: "L45-D6-SEEDS-P2-20260220-006"
    skill_id: "l45_seeds_p2_operationalization"

output:
  deliverables:
    - path: "orchestration/feature_flags.yml"
      type: "修改"
      schema_ref: "dev/staging/prod profiles"
    - path: "skillforge/src/contracts/governance/feature_flag_loader.py"
      type: "修改"
      schema_ref: "env-aware loader"
    - path: "docs/2026-02-20/L45_P2_FLAGS_ENV_REPORT_v1.md"
      type: "新建"
      schema_ref: "环境化报告"
  constraints:
    - "必须区分 dev/staging/prod"
    - "prod 默认安全策略不得放宽"
    - "缺 profile 必须 fail-closed"

deny:
  - "不得硬编码单环境常量覆盖配置"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_feature_flag_loader.py"
      expect: "passed"
```

