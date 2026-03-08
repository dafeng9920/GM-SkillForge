# Task Skill Spec

```yaml
task_id: "T32"
executor: "Kior-A"
wave: "Wave 1"
depends_on: []
estimated_minutes: 80

input:
  description: "运营回归集扩展：新增 regression cases 并接入 nightly 回归入口"
  context_files:
    - path: "regression/README.md"
      purpose: "回归规范"
    - path: "regression/cases"
      purpose: "现有样例基线"
  constants:
    job_id: "L45-D6-SEEDS-P2-20260220-006"
    skill_id: "l45_seeds_p2_operationalization"

output:
  deliverables:
    - path: "regression/cases"
      type: "修改"
      schema_ref: "新增可复核 case"
    - path: "scripts/run_regression_suite.py"
      type: "新建"
      schema_ref: "回归入口"
    - path: "docs/2026-02-20/L45_P2_REGRESSION_EXPANSION_REPORT_v1.md"
      type: "新建"
      schema_ref: "回归扩展报告"
  constraints:
    - "新增 case 必须有 input + expected"
    - "回归入口支持 CI 运行"
    - "输出稳定，不依赖随机性"

deny:
  - "不得仅新增 README 不新增可运行 case"

gate:
  auto_checks:
    - command: "python scripts/run_regression_suite.py --ci"
      expect: "passed"
```

