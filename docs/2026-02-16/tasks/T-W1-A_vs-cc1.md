# Task Skill Spec: T-W1-A

```yaml
# 元信息
task_id: "T-W1-A"
executor: "vs--cc1"
wave: "Wave 1"
depends_on: []
estimated_minutes: 40

# 输入合同 (Input Contract)
input:
  description: "对现有系统执行 L5 Gate 干跑 (Dry Run)，分析 G1-G5 现状"
  context_files:
    - path: "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/skill_acceptance_L5_hard_gate_v3.md"
      purpose: "验收标准"
    - path: "skillforge-spec-pack/skillforge/src/nodes/"
      purpose: "现有代码库"
  constants:
    gates: ["G1", "G2", "G3", "G4", "G5"]

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "docs/2026-02-17/l5_dry_run_report.md"
      type: "新建"
      description: |
        一份详细的干跑报告，回答以下问题:
        
        ### G1 能力可运行
        - 4个 python 命令是否存在？能否运行？
        - 现状: PASS / FAIL
        
        ### G2 治理可阻断
        - audit_report_boundary.json 是否存在？
        - 违反边界是否会 exit 1？
        - 现状: PASS / FAIL
        
        ### G3 证据可追溯
        - 现有输出是否包含 run_id / trace_id？
        - 现状: PASS / FAIL
        
        ### G4 回放可复核
        - 现有系统支持确定性重放吗？
        - 现状: PASS / FAIL
        
        ### G5 变更可控
        - audit_report_consistency.json 是否存在？
        - 现状: PASS / FAIL
  constraints:
    - "必须真实执行命令尝试，不能只看代码"
    - "如命令不存在，记录下来"
    - "如文件不存在，记录下来"

# 红线 (Deny List)
deny:
  - "不得修改任何代码（观察模式）"
  - "不得伪造结果"
```
