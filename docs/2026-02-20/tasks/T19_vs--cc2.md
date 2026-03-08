# Task Skill Spec

```yaml
task_id: "T19"
executor: "vs--cc2"
wave: "Wave 1"
depends_on: []
estimated_minutes: 80

input:
  description: "SEEDS-P0-4 Append-only Audit Events：每个 gate 结束写 audit_events.jsonl"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "audit_events 模板与写入点定义"
    - path: "skillforge/src/skills/experience_capture.py"
      purpose: "append-only 参考实现"
  constants:
    job_id: "L45-D4-SEEDS-P0-20260220-004"
    skill_id: "l45_seeds_p0_foundation"

output:
  deliverables:
    - path: "logs/audit_events.jsonl"
      type: "新建"
      schema_ref: "append-only event log"
    - path: "skillforge/src/skills/audit_event_writer.py"
      type: "新建"
      schema_ref: "gate finish event writer"
    - path: "skillforge/tests/test_audit_event_writer.py"
      type: "新建"
      schema_ref: "PASS/FAIL/SKIPPED 都写入测试"
  constraints:
    - "每个 gate finish 必写一条事件"
    - "append-only，不允许修改历史行"
    - "读取点至少支持按 job_id/gate_node 查询"

deny:
  - "不得只记录失败不记录成功"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_audit_event_writer.py"
      expect: "passed"
```

