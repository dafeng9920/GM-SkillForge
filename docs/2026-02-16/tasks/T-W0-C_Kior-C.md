# Task Skill Spec: T-W0-C

```yaml
# 元信息
task_id: "T-W0-C"
executor: "Kior-C"
wave: "Wave 0"
depends_on: []  # 独立任务
estimated_minutes: 20

# 输入合同 (Input Contract)
input:
  description: "在 validate.py 中新增 CHECK 16-17，校验宪法文件和架构约束文件存在性，标题从 15-Point 升级为 17-Point"
  context_files:
    - path: "skillforge-spec-pack/tools/validate.py"
      purpose: "当前 15-point 审计逻辑（重点看 L479 之后的返回位置 + L502 标题行）"
    - path: "docs/2026-02-16/constitution_v1.md"
      purpose: "确认文件路径"
    - path: "docs/2026-02-16/不可回退架构约束_v1.md"
      purpose: "确认文件路径"
  constants:
    constitution_path: "docs/2026-02-16/constitution_v1.md"
    constraints_path: "docs/2026-02-16/不可回退架构约束_v1.md"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge-spec-pack/tools/validate.py"
      type: "修改"
      description: |
        1. validate_audit_config() 末尾（return results 之前）新增:
           - CHECK 16 (CONSTITUTION_EXISTS): constitution_v1.md 存在
           - CHECK 17 (CONSTRAINTS_EXISTS): 不可回退架构约束_v1.md 存在
        2. main() 中的 print 标题: "15-Point" → "17-Point"
        3. --audit-config 的 help text 同步更新
  constraints:
    - "python tools/validate.py --audit-config 输出 17/17 全绿"
    - "CHECK 16 使用 check_id 'CONSTITUTION_EXISTS'"
    - "CHECK 17 使用 check_id 'CONSTRAINTS_EXISTS'"
    - "现有 15 个 CHECK 不得被修改或删除"

# 红线 (Deny List)
deny:
  - "不得修改 pack_publish.py（属于 T-W0-A）"
  - "不得修改 constitution_gate.py（属于 T-W0-B）"
  - "不得修改已有的 CHECK 1-15 逻辑"
  - "不得引入新的第三方依赖"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "python tools/validate.py --audit-config"
      expect: "17 passed, 0 failed"
    - command: "python -m pytest skillforge/tests/ contract_tests/ test_skill_threshold.py -v"
      expect: "全部 passed，0 failed"
  manual_checks:
    - "输出包含 CONSTITUTION_EXISTS 和 CONSTRAINTS_EXISTS 两行"
    - "标题显示 17-Point"
```
