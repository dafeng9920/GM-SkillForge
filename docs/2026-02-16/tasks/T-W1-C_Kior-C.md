# Task Skill Spec: T-W1-C

```yaml
# 元信息
task_id: "T-W1-C"
executor: "Kior-C"
wave: "Wave 1"
depends_on: ["T-W1-A", "T-W1-B"]
estimated_minutes: 20

# 输入合同 (Input Contract)
input:
  description: "基于 v3 Spec 和 映射表，'手搓' 标准的 JSON 证据样例 (PASSED/REJECTED)"
  context_files:
    - path: "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/skill_acceptance_L5_hard_gate_v3.md"
      purpose: "Schema 定义 (Section 4.1)"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "docs/2026-02-17/samples/l5_result_passed.json"
      type: "新建"
      description: "符合 v3 Schema 的全通过样本"
    - path: "docs/2026-02-17/samples/l5_result_rejected.json"
      type: "新建"
      description: "符合 v3 Schema 的 G2 失败样本"
  constraints:
    - "必须通过 schema 校验 (可用在线校验工具或脚本自测)"
    - "REJECTED 样本必须包含 error_code"

# 红线 (Deny List)
deny:
  - "JSON 格式必须严格合法"
  - "Schema 校验不通过视为任务失败"
```
