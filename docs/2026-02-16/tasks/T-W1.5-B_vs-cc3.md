# Task Skill Spec: T-W1.5-B

```yaml
# 元信息
task_id: "T-W1.5-B"
executor: "vs--cc3"
wave: "Wave 1.5"
depends_on: []
estimated_minutes: 40

# 输入合同 (Input Contract)
input:
  description: "改造 PipelineEngine 和 NodeRunner，实现 run_id 注入和 Trace 透传 (G3/G4)"
  context_files:
    - path: "docs/2026-02-17/l5_dry_run_report.md"
      purpose: "查看 G3/G4 失败原因"
    - path: "skillforge-spec-pack/skillforge/src/orchestration/engine.py"
      purpose: "修改点 1"
    - path: "skillforge-spec-pack/skillforge/src/orchestration/node_runner.py"
      purpose: "修改点 2"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge-spec-pack/skillforge/src/orchestration/engine.py"
      type: "修改"
      description: |
        1. execute() 方法新增可选参数 `run_id: str = None`
        2. 如果 run_id 为空，生成 UUID
        3. 将 run_id 放入 context 传递给 NodeRunner
    - path: "skillforge-spec-pack/skillforge/src/orchestration/node_runner.py"
      type: "修改"
      description: |
        1. 接收 run_id
        2. 将 run_id 写入每个 Node 的输出结果
        3. 确保 trace_id 在同一次 run 中有逻辑关联 (或简单地透传)
  constraints:
    - "G3 要求: 所有输出必须包含 run_id"
    - "G4 要求: 相同 run_id + 相同输入应产生确定性输出 (Mock UUID 或 Seeded UUID)"

# 红线 (Deny List)
deny:
  - "不得破坏现有测试 (test_protocols.py 等)"
  - "run_id 必须是字符串"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "python -m pytest skillforge/tests/"
      expect: "all passed"
  manual_checks:
    - "运行一次 pipeline，检查输出 JSON 是否含 run_id"
```
