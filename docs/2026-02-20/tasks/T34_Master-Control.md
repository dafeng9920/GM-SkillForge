# Task Skill Spec

```yaml
task_id: "T34"
executor: "Master-Control"
wave: "Wave 3"
depends_on: ["T33"]
estimated_minutes: 45

input:
  description: "P2 主控签核：基于 T33 输出 READY_FOR_P2_AUTORUN 终判"
  context_files:
    - path: "docs/2026-02-20/verification/T33_gate_decision.json"
      purpose: "技术验收判定"
    - path: "docs/2026-02-20/verification/T33_execution_report.yaml"
      purpose: "执行细节与阻塞项"
    - path: "docs/2026-02-20/tasks/各小队任务完成汇总_T28-T34.md"
      purpose: "汇总看板回填"
  constants:
    job_id: "L45-D6-SEEDS-P2-20260220-006"
    skill_id: "l45_seeds_p2_operationalization"

output:
  deliverables:
    - path: "docs/2026-02-20/L45_P2_MASTER_SIGNOFF_v1.md"
      type: "新建"
      schema_ref: "Master Signoff"
    - path: "docs/2026-02-20/tasks/各小队任务完成汇总_T28-T34.md"
      type: "修改"
      schema_ref: "主控最终判定"
  constraints:
    - "仅在 T33=ALLOW 时可签 READY_FOR_P2_AUTORUN=YES"
    - "若非 ALLOW，必须输出阻塞与下一步"

deny:
  - "不得越过 T33 直接签核"
```

