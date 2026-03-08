# Task Skill Spec: T-W1-B

```yaml
# 元信息
task_id: "T-W1-B"
executor: "vs--cc2"
wave: "Wave 1"
depends_on: []
estimated_minutes: 30

# 输入合同 (Input Contract)
input:
  description: "建立 G1-G5 的【检查命令 + 结果字段】精确映射表"
  context_files:
    - path: "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/skill_acceptance_L5_hard_gate_v3.md"
      purpose: "验收标准"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "docs/2026-02-17/l5_gate_mapping.md"
      type: "新建"
      description: |
        Markdown 表格，包含:
        | Gate | 检查命令 (CLI) | 证据文件 (JSON) | 关键字段 (JSONPath) | 期望值 |
        |---|---|---|---|---|
        | G1 | python -m ... | runtime_report.json | $.exit_code | 0 |
        | ... | ... | ... | ... | ... |
        
        如果某个命令当前不存在，标注 "TODO: Implement"
  constraints:
    - "命令必须是可复制粘贴执行的完整命令"
    - "JSONPath 必须精确"

# 红线 (Deny List)
deny:
  - "不得发明不存在的 Spec"
  - "必须严格对应 v3 版本的定义"
```
