# Task Skill Spec: T-W1.5-A

```yaml
# 元信息
task_id: "T-W1.5-A"
executor: "vs--cc1"
wave: "Wave 1.5"
depends_on: []
estimated_minutes: 45

# 输入合同 (Input Contract)
input:
  description: "实现 skillforge.skills 模块下的 4 个核心 CLI 工具，使 G1/G2/G5 检查通过"
  context_files:
    - path: "docs/2026-02-17/l5_gate_mapping.md"
      purpose: "明确每个 CLI 命令的参数和预期输出"
  constants:
    pkg_name: "skillforge.skills"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge-spec-pack/skillforge/src/skills/__init__.py"
      type: "新建"
    - path: "skillforge-spec-pack/skillforge/src/skills/contract_common_builder.py"
      type: "新建"
      description: "MVP: 接收 --help, exit(0)。实现简单的 JSON 报告生成。"
    - path: "skillforge-spec-pack/skillforge/src/skills/contract_module_builder.py"
      type: "新建"
      description: "MVP: 接收 --help, exit(0)。"
    - path: "skillforge-spec-pack/skillforge/src/skills/contract_consistency_auditor.py"
      type: "新建"
      description: "实现 G5 检查。输入 file, 输出 audit_report_consistency.json。检查字段可先 mock 为 0 violations 以通过验收。"
    - path: "skillforge-spec-pack/skillforge/src/skills/governance_boundary_auditor.py"
      type: "新建"
      description: "实现 G2 检查。输入 file, 输出 audit_report_boundary.json。检查字段可先 mock 为 0 violations。"
  constraints:
    - "所有 4 个模块必须能通过 python -m skillforge.skills.xxx 调用"
    - "必须支持 --input-file 和 --output 参数（参考 l5_gate_mapping.md）"
    - "生成的 JSON 必须符合 l5_gate_mapping.md 中的结构"

# 红线 (Deny List)
deny:
  - "不得修改 core engine (留给 Task B)"
  - "不得引入重型依赖 (pandas 等)"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "python -m skillforge.skills.contract_common_builder --help"
      expect: "exit code 0"
    - command: "python -m skillforge.skills.governance_boundary_auditor --output test_report.json && grep 'total_violations' test_report.json"
      expect: "found"
```
