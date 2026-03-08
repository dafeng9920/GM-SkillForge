# Task Skill Spec: T-W1.5-C

```yaml
# 元信息
task_id: "T-W1.5-C"
executor: "Kior-C"
wave: "Wave 1.5"
depends_on: ["T-W1.5-A", "T-W1.5-B"]
estimated_minutes: 30

# 输入合同 (Input Contract)
input:
  description: "再次执行 Wave 1 定义的验收命令 (Re-Verification) 并创建 CI 配置"
  context_files:
    - path: "docs/2026-02-17/l5_dry_run_report.md"
      purpose: "使用其中的 Command List 进行回归测试"
  constants:
    expected_status: "ALL PASS"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "docs/2026-02-17/l5_final_verification_report.md"
      type: "新建"
      description: "记录 G1-G5 的最终复测结果。必须全绿。"
    - path: ".github/workflows/l5-gate.yml"
      type: "新建"
      description: "Github Actions 配置，执行 G1-G5 检查，失败 exit 1"
  constraints:
    - "G1-G5 必须实际通过"
    - "CI 配置必须有效 (yaml lint pass)"

# 红线 (Deny List)
deny:
  - "不得伪造结果"
  - "必须在真实环境运行"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "python -m skillforge.skills.contract_common_builder --help"
      expect: "exit 0"
    - command: "python -m skillforge.skills.governance_boundary_auditor --help"
      expect: "exit 0"
```
