# Task Skill Spec: T-W4B1-01
# Executor: vs--cc2

# 元信息
task_id: "T-W4B1-01"
executor: "vs--cc2"
wave: "Wave 4 Batch 1"
depends_on: []
estimated_minutes: 30

# 输入合同 (Input Contract)
input:
  description: "Implement the first 2 gates of the migration pipeline: Intake and Scan."
  context_files:
    - path: "skillforge/src/contracts/gates/gate_interface_v1.yaml"
      purpose: "Strictly follow Input/Output schema"
  constants:
    gate_group: "entrance"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge/src/contracts/gates/intake_repo.yaml"
      type: "新建"
    - path: "skillforge/src/contracts/gates/repo_scan.yaml"
      type: "新建"
    - path: "skillforge/src/skills/gates/gate_intake.py"
      type: "新建"
    - path: "skillforge/src/skills/gates/gate_scan.py"
      type: "新建"
    - path: "tests/gates/test_intake_scan.py"
      type: "新建"
  constraints:
    - "Must produce EvidenceRef for both gates"
    - "Fail-Closed: Missing commit_sha MUST trigger REJECTED"
    - "Fail-Closed: Low fit score MUST trigger REJECTED"

# 红线 (Deny List)
deny:
  - "不得修改 gate_interface_v1.yaml"
  - "不得引入 heavy dependencies (like pandas) just for JSON scanning"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "pytest tests/gates/test_intake_scan.py"
      expect: "passed"
  manual_checks:
    - "Verify intake_manifest.json is generated"
    - "Verify scan_report.json is generated"

# 实现模式 (Implementation Pattern)
# Must follow 'experience_capture.py' pattern:
# class GateIntakeRepo:
#     def validate_input(self, input_data) -> list[str]: ...
#     def execute(self, input_data) -> dict: ...
#     def validate_output(self, output) -> list[str]: ...
#     if __name__ == "__main__": main()
