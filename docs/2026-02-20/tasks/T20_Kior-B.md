# Task Skill Spec

```yaml
task_id: "T20"
executor: "Kior-B"
wave: "Wave 1"
depends_on: []
estimated_minutes: 80

input:
  description: "SEEDS-P0-5 Usage/Quota：落盘 usage.jsonl，并在入队时记账"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "usage 计量要求"
    - path: "skillforge/src/contracts/policy/membership_middleware.py"
      purpose: "quota 判断接入点"
  constants:
    job_id: "L45-D4-SEEDS-P0-20260220-004"
    skill_id: "l45_seeds_p0_foundation"

output:
  deliverables:
    - path: "logs/usage.jsonl"
      type: "新建"
      schema_ref: "usage ledger jsonl"
    - path: "skillforge/src/contracts/policy/usage_meter.py"
      type: "新建"
      schema_ref: "enqueue-time metering"
    - path: "skillforge/tests/test_usage_meter.py"
      type: "新建"
      schema_ref: "计量入账与读取测试"
  constraints:
    - "入队/接受时扣减（非完成时）"
    - "append-only"
    - "读取点可用于 quota 判断"

deny:
  - "不得在任务完成后才记账"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_usage_meter.py"
      expect: "passed"
```

