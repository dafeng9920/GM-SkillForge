# Task Skill Spec

```yaml
task_id: "T24"
executor: "vs--cc1"
wave: "Wave 1"
depends_on: []
estimated_minutes: 70

input:
  description: "SEEDS-P1-7 UI 文案映射合同（i18n_key）：建立最小合同并接入读取校验"
  context_files:
    - path: "docs/SEEDS_v0.md"
      purpose: "i18n_key 占位模板"
    - path: "docs/2026-02-20/L45_N8N_BOUNDARY_CONTRACT_v1.md"
      purpose: "文档层键值映射参考"
  constants:
    job_id: "L45-D5-SEEDS-P1-20260220-005"
    skill_id: "l45_seeds_p1_guardrails"

output:
  deliverables:
    - path: "ui/contracts/i18n_keys.yml"
      type: "新建"
      schema_ref: "i18n key contract"
    - path: "skillforge/src/contracts/ui/i18n_contract_loader.py"
      type: "新建"
      schema_ref: "读取与键存在性检查"
    - path: "skillforge/tests/test_i18n_contract_loader.py"
      type: "新建"
      schema_ref: "键完整性测试"
  constraints:
    - "合同必须覆盖 8 Gate title key + fallback key"
    - "读取器缺 key 时 fail-closed 报错"
    - "keys 文件必须是可机器解析 YAML"

deny:
  - "不得在代码中硬编码回退文案绕过合同"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_i18n_contract_loader.py"
      expect: "passed"
```

