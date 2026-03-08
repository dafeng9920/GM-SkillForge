# Task Skill Spec: T-W4B1-03
# Executor: Kior-C

# 元信息
task_id: "T-W4B1-03"
executor: "Kior-C"
wave: "Wave 4 Batch 1"
depends_on: ["T-W4B1-01", "T-W4B1-02"] # Waits for Entrance & Logic layers
estimated_minutes: 45

# 输入合同 (Input Contract)
input:
  description: "Implement the Delivery Layer: Scaffold, Test, and Audit Pack Publishing."
  context_files:
    - path: "skillforge/src/contracts/gates/gate_interface_v1.yaml"
      purpose: "Strictly follow Input/Output schema"
  constants:
    gate_group: "delivery"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge/src/contracts/gates/scaffold.yaml"
      type: "新建"
    - path: "skillforge/src/contracts/gates/sandbox.yaml"
      type: "新建"
    - path: "skillforge/src/contracts/gates/publish.yaml"
      type: "新建"
    - path: "skillforge/src/skills/gates/gate_scaffold.py"
      type: "新建"
    - path: "skillforge/src/skills/gates/gate_sandbox.py"
      type: "新建"
    - path: "skillforge/src/skills/gates/gate_publish.py"
      type: "新建"
    - path: "tests/gates/test_delivery.py"
      type: "新建"
  constraints:
    - "Must chain evidence from G1-G6"
    - "L3 AuditPack must include 'content_hash' of all prior artifacts"
    - "Fail-Closed: Sandbox Fail MUST trigger REJECTED"

# 红线 (Deny List)
deny:
  - "不得伪造 Evidence"
  - "不得在测试失败时发布 AuditPack"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "pytest tests/gates/test_delivery.py"
      expect: "passed"
  manual_checks:
    - "Verify L3 AuditPack Manifest integrity"
    - "Verify TraceLog exists"

# 实现模式 (Implementation Pattern)
# Must follow 'experience_capture.py' pattern:
# class GateScaffoldSkill:
#     def validate_input(self, input_data) -> list[str]: ...
#     def execute(self, input_data) -> dict: ...
#     def validate_output(self, output) -> list[str]: ...
#     if __name__ == "__main__": main()
