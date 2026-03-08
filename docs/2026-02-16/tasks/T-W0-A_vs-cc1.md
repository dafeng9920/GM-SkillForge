# Task Skill Spec: T-W0-A

```yaml
# 元信息
task_id: "T-W0-A"
executor: "vs--cc1"
wave: "Wave 0"
depends_on: []
estimated_minutes: 40

# 输入合同 (Input Contract)
input:
  description: "将宪法引用 (constitution_ref + constitution_hash) 嵌入 AuditPack manifest，缺失即 rejected"
  context_files:
    - path: "docs/2026-02-16/constitution_v1.md"
      purpose: "理解宪法内容 + 用于 SHA256 hash 计算"
    - path: "docs/2026-02-16/不可回退架构约束_v1.md"
      purpose: "理解 §1.1 宪法版本化要求"
    - path: "skillforge-spec-pack/skillforge/src/nodes/pack_publish.py"
      purpose: "当前 manifest 构建逻辑（重点看 L391-403 provenance 块）"
  constants:
    constitution_filename: "constitution_v1.md"
    constitution_path: "docs/2026-02-16/constitution_v1.md"

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge-spec-pack/skillforge/src/utils/__init__.py"
      type: "新建"
    - path: "skillforge-spec-pack/skillforge/src/utils/constitution.py"
      type: "新建"
      description: |
        共享模块，包含 load_constitution() 函数:
        - 返回 (constitution_ref: str, constitution_hash: str)
        - 文件缺失返回 ("MISSING", "")
        - hash 使用 SHA256 hex digest
    - path: "skillforge-spec-pack/skillforge/src/nodes/pack_publish.py"
      type: "修改"
      description: |
        1. 在 execute() 中调用 load_constitution()
        2. manifest.provenance 新增 constitution_ref + constitution_hash
        3. constitution_ref == "MISSING" 时, publish_status 强制为 "rejected"
  constraints:
    - "manifest.json.provenance.constitution_ref 必须非空"
    - "manifest.json.provenance.constitution_hash 为 64 字符 hex（或空字符串如果 MISSING）"
    - "宪法缺失时 publish_result.status == 'rejected'"
    - "现有测试不得被破坏: pytest skillforge/tests/ contract_tests/ 全绿"

# 红线 (Deny List)
deny:
  - "不得修改 constitution_gate.py（属于 T-W0-B）"
  - "不得修改 validate.py（属于 T-W0-C）"
  - "不得修改测试文件（属于 T-W0-D）"
  - "不得引入新的第三方依赖"
  - "不得硬编码宪法内容，必须从文件实时读取"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "python -m pytest skillforge/tests/ contract_tests/ test_skill_threshold.py -v"
      expect: "全部 passed，0 failed"
    - command: "python -c \"from skillforge.src.utils.constitution import load_constitution; ref, h = load_constitution(); assert ref != 'MISSING'; assert len(h) == 64; print(f'OK: {ref} {h[:16]}...')\""
      expect: "OK: constitution_v1.md xxxxxxxx..."
  manual_checks:
    - "manifest.provenance 包含 constitution_ref 和 constitution_hash"
    - "宪法文件删除后，execute() 返回 rejected"
```
