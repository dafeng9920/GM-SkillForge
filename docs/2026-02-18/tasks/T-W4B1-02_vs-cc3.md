# Task Skill Spec: T-W4B1-02
# Executor: vs--cc3

# 元信息
task_id: "T-W4B1-02"
executor: "vs--cc3"
wave: "Wave 4 Batch 1"
depends_on: [] # Parallel Development with T-W4B1-01
estimated_minutes: 45

# 输入合同 (Input Contract)
input:
  description: "Implement the Logic Layer gates: Spec Drafting and Constitution Risk Check."
  context_files:
    - path: "skillforge/src/contracts/gates/gate_interface_v1.yaml"
      purpose: "Strictly follow Input/Output schema"
  constants:
    gate_group: "logic"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge/src/contracts/gates/draft_spec.yaml"
      type: "新建"
    - path: "skillforge/src/contracts/gates/risk_check.yaml"
      type: "新建"
    - path: "skillforge/src/skills/gates/gate_draft_spec.py"
      type: "新建"
    - path: "skillforge/src/skills/gates/gate_risk.py"
      type: "新建"
    - path: "tests/gates/test_logic.py"
      type: "新建"
  constraints:
    - "Must Input: ScanReport (from G2)"
    - "Must Output: SkillSpec (YAML)"
    - "Fail-Closed: Risk Detected MUST trigger REJECTED"

# 红线 (Deny List)
deny:
  - "不得放行带有 'override_governance' 标记的 Spec"
  - "不得修改 Constitution 定义"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "pytest tests/gates/test_logic.py"
      expect: "passed"
  manual_checks:
    - "Verify skill_spec.yaml is valid YAML"
    - "Verify risk_assessment.json captures simulated threats"

# 实现模式 (Implementation Pattern)
# Must follow 'experience_capture.py' pattern:
# class GateDraftSpec:
#     def validate_input(self, input_data) -> list[str]: ...
#     def execute(self, input_data) -> dict: ...
#     def validate_output(self, output) -> list[str]: ...
#     if __name__ == "__main__": main()
