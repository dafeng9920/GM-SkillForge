# Task Skill Spec

```yaml
task_id: "T25"
executor: "vs--cc2"
wave: "Wave 1"
depends_on: []
estimated_minutes: 70

input:
  description: "SEEDS-P1-8 Feature Flags：新增最小开关文件并接入执行时读取"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "feature_flags 模板"
    - path: "skillforge/src/api/routes/n8n_orchestration.py"
      purpose: "enable_n8n_execution 读取接入点"
  constants:
    job_id: "L45-D5-SEEDS-P1-20260220-005"
    skill_id: "l45_seeds_p1_guardrails"

output:
  deliverables:
    - path: "orchestration/feature_flags.yml"
      type: "新建"
      schema_ref: "feature flags"
    - path: "skillforge/src/contracts/governance/feature_flag_loader.py"
      type: "新建"
      schema_ref: "flags loader"
    - path: "skillforge/tests/test_feature_flag_loader.py"
      type: "新建"
      schema_ref: "开关读取与默认值测试"
  constraints:
    - "必须包含 enable_n8n_execution"
    - "默认策略必须防止半成品能力污染主流程"
    - "开关关闭时要有可审计 evidence（不静默）"

deny:
  - "不得把开关写死在代码里"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_feature_flag_loader.py"
      expect: "passed"
```

