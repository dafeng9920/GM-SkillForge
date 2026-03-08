# Task Skill Spec: T-W0-D

```yaml
# 元信息
task_id: "T-W0-D"
executor: "Kior-A"
wave: "Wave 0"
depends_on: ["T-W0-A", "T-W0-B"]  # 需要 A+B 完成后才能测试
estimated_minutes: 35

# 输入合同 (Input Contract)
input:
  description: "编写 constitution 强制执行测试，覆盖 REJECTED 路径，满足 V1-Prove §6.4 '至少 1 个真实 REJECTED 可追溯'"
  context_files:
    - path: "docs/2026-02-16/constitution_v1.md"
      purpose: "理解宪法信条和红线"
    - path: "docs/2026-02-16/不可回退架构约束_v1.md"
      purpose: "理解 §6.4 冻结到位条件"
    - path: "skillforge-spec-pack/skillforge/src/utils/constitution.py"
      purpose: "T-W0-A 创建的共享模块"
    - path: "skillforge-spec-pack/skillforge/src/nodes/pack_publish.py"
      purpose: "T-W0-A 修改后的 manifest 逻辑"
    - path: "skillforge-spec-pack/skillforge/src/nodes/constitution_gate.py"
      purpose: "T-W0-B 修改后的 Gate 逻辑"
    - path: "skillforge-spec-pack/skillforge/tests/test_acceptance.py"
      purpose: "模仿现有测试风格和 fixture 模式"
  constants:
    constitution_filename: "constitution_v1.md"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge-spec-pack/skillforge/tests/test_constitution_enforcement.py"
      type: "新建"
      description: |
        测试类 TestConstitutionEnforcement，至少包含以下 5 个测试:

        1. test_gate_deny_when_constitution_missing
           - 模拟宪法文件缺失（用 monkeypatch 或 tmp_path）
           - 断言 constitution_gate.execute() 返回 decision == "DENY"
           - 断言 reason 包含 "missing" 或 "fail-closed"

        2. test_gate_includes_constitution_hash
           - 正常执行 gate
           - 断言输出 details 包含 constitution_hash
           - 断言 hash 长度 == 64

        3. test_manifest_includes_constitution_ref
           - 正常执行 pack_publish
           - 断言 manifest.provenance 包含 constitution_ref
           - 断言 constitution_ref 不是 "MISSING"

        4. test_pack_rejected_when_constitution_missing
           - 模拟宪法文件缺失
           - 断言 publish_result.status == "rejected"

        5. test_constitution_hash_is_deterministic
           - 调用 load_constitution() 两次
           - 断言两次 hash 完全一致
  constraints:
    - "所有测试必须 passed"
    - "至少 1 个测试覆盖 REJECTED/DENY 路径"
    - "测试不得依赖外部网络或文件系统副作用"
    - "使用 pytest fixtures (monkeypatch, tmp_path) 隔离"

# 红线 (Deny List)
deny:
  - "不得修改 pack_publish.py（属于 T-W0-A）"
  - "不得修改 constitution_gate.py（属于 T-W0-B）"
  - "不得修改 validate.py（属于 T-W0-C）"
  - "不得修改现有测试文件"
  - "不得引入新的第三方依赖"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "python -m pytest skillforge/tests/test_constitution_enforcement.py -v"
      expect: "5 passed, 0 failed"
    - command: "python -m pytest skillforge/tests/ contract_tests/ test_skill_threshold.py -v"
      expect: "全部 passed，0 failed（含新增测试）"
  manual_checks:
    - "至少 1 个测试明确验证 REJECTED/DENY 路径"
    - "测试命名清晰表达宪法约束"
```
