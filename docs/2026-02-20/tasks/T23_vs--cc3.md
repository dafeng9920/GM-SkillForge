# Task Skill Spec

```yaml
task_id: "T23"
executor: "vs--cc3"
wave: "Wave 1"
depends_on: []
estimated_minutes: 75

input:
  description: "SEEDS-P1-6 Regression Set 占位：建立固定回归样例目录与最小校验入口"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "Regression Set 占位要求"
    - path: "skillforge/tests"
      purpose: "现有测试结构参考"
  constants:
    job_id: "L45-D5-SEEDS-P1-20260220-005"
    skill_id: "l45_seeds_p1_guardrails"

output:
  deliverables:
    - path: "regression/README.md"
      type: "新建"
      schema_ref: "Regression 规范与执行说明"
    - path: "regression/cases/case_001/input.json"
      type: "新建"
      schema_ref: "固定输入样例"
    - path: "regression/cases/case_001/expected.md"
      type: "新建"
      schema_ref: "固定期望摘要"
    - path: "skillforge/tests/test_regression_seed_smoke.py"
      type: "新建"
      schema_ref: "占位回归可执行检查"
  constraints:
    - "回归样例必须可执行，不得仅文档化"
    - "至少 1 个 case 固定输入与期望输出"
    - "新增用例不得依赖外部网络"

deny:
  - "不得用随机输出作为 expected"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_regression_seed_smoke.py"
      expect: "passed"
```

