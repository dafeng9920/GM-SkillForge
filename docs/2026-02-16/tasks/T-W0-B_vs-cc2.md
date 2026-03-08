# Task Skill Spec: T-W0-B

```yaml
# 元信息
task_id: "T-W0-B"
executor: "vs--cc2"
wave: "Wave 0"
depends_on: ["T-W0-A"]  # 需要 A 先创建 utils/constitution.py
estimated_minutes: 30

# 输入合同 (Input Contract)
input:
  description: "升级 constitution_gate.py，从真实宪法文件读取版本和 hash，去除硬编码 '0.1.0'，宪法缺失即 DENY"
  context_files:
    - path: "docs/2026-02-16/constitution_v1.md"
      purpose: "理解宪法内容"
    - path: "docs/2026-02-16/不可回退架构约束_v1.md"
      purpose: "理解 §1.1 宪法覆盖点要求"
    - path: "skillforge-spec-pack/skillforge/src/nodes/constitution_gate.py"
      purpose: "当前 Gate 逻辑（重点看 L133, L151, L183 硬编码 constitution_version）"
    - path: "skillforge-spec-pack/skillforge/src/utils/constitution.py"
      purpose: "T-W0-A 创建的共享模块（复用 load_constitution 函数）"
  constants:
    constitution_filename: "constitution_v1.md"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge-spec-pack/skillforge/src/nodes/constitution_gate.py"
      type: "修改"
      description: |
        1. 导入 load_constitution（从 T-W0-A 的 utils/constitution.py）
        2. execute() 开头调用 load_constitution()
        3. 宪法缺失 → 立即返回 DENY，reason 引用 §2.2 Fail-Closed
        4. 将所有 "constitution_version": "0.1.0" 替换为真实 constitution_ref
        5. details 中新增 "constitution_hash" 字段
  constraints:
    - "Gate 输出的 constitution_version 来自真实文件，不是硬编码"
    - "Gate 输出新增 constitution_hash 字段"
    - "宪法文件缺失时 decision == 'DENY'"
    - "DENY 的 reason 必须明确引用宪法条款"
    - "现有测试不得被破坏"

# 红线 (Deny List)
deny:
  - "不得修改 pack_publish.py（属于 T-W0-A）"
  - "不得修改 validate.py（属于 T-W0-C）"
  - "不得修改测试文件（属于 T-W0-D）"
  - "不得重新实现 load_constitution()，必须从 utils/constitution.py 导入"
  - "不得引入新的第三方依赖"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "python -m pytest skillforge/tests/ contract_tests/ test_skill_threshold.py -v"
      expect: "全部 passed，0 failed"
  manual_checks:
    - "constitution_version 不再是硬编码 '0.1.0'"
    - "Gate 输出包含 constitution_hash"
    - "宪法文件删除后，execute() 返回 DENY"
```
