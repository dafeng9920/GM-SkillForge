# Task Skill Spec

```yaml
task_id: "T26"
executor: "Kior-B"
wave: "Wave 1"
depends_on: []
estimated_minutes: 80

input:
  description: "SEEDS-P1-9 Repro Env 指纹占位：落盘 provenance 模板并保证 GateDecision 引用"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "provenance.repro_env 占位要求"
    - path: "docs/2026-02-20/verification/T22_gate_decision.json"
      purpose: "GateDecision 结构参考"
  constants:
    job_id: "L45-D5-SEEDS-P1-20260220-005"
    skill_id: "l45_seeds_p1_guardrails"

output:
  deliverables:
    - path: "templates/provenance.json"
      type: "新建"
      schema_ref: "repro_env placeholder"
    - path: "skillforge/src/contracts/governance/provenance_loader.py"
      type: "新建"
      schema_ref: "provenance 读取与注入"
    - path: "skillforge/tests/test_provenance_loader.py"
      type: "新建"
      schema_ref: "repro_env 字段存在测试"
  constraints:
    - "GateDecision / 报告输出必须可包含 provenance.repro_env"
    - "可先占位，但字段结构必须稳定"
    - "读取失败必须 fail-closed"

deny:
  - "不得省略 repro_env 字段层级"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_provenance_loader.py"
      expect: "passed"
```

