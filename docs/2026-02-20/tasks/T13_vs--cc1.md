# Task Skill Spec

```yaml
task_id: "T13"
executor: "vs--cc1"
wave: "Wave 1"
depends_on: []
estimated_minutes: 80

input:
  description: "外部 Skill 包完整性与身份绑定校验：manifest/signature/content_hash/revision 对齐"
  context_files:
    - path: "docs/2026-02-19/contracts/external_skill_governance_contract_v1.yaml"
      purpose: "字段与 fail-closed 规则"
    - path: "skillforge/src/storage/audit_pack_store.py"
      purpose: "证据与回放指针存储模式"
    - path: "docs/2026-02-20/task_dispatch_T12-T16_external_skill_governance.md"
      purpose: "读取全局常量与验收口径"
  constants:
    job_id: "L45-D3-EXT-SKILL-GOV-20260220-003"
    skill_id: "l45_external_skill_governance_batch1"

output:
  deliverables:
    - path: "skillforge/src/adapters/external_skill_package_adapter.py"
      type: "新建"
      schema_ref: "包校验适配器"
    - path: "skillforge/tests/test_external_skill_package_adapter.py"
      type: "新建"
      schema_ref: "签名/哈希/revision 测试"
    - path: "docs/2026-02-20/L45_EXTERNAL_SKILL_PACKAGE_VALIDATION_REPORT_v1.md"
      type: "新建"
      schema_ref: "包校验报告"
  constraints:
    - "manifest 缺字段必须 fail-closed"
    - "signature 验签失败必须返回结构化错误码"
    - "content_hash 不一致必须阻断"
    - "输出必须包含 package_id/revision/evidence_ref"

deny:
  - "不得放宽验签失败阻断条件"
  - "不得跳过 content_hash 校验"
  - "不得修改既有 membership 策略语义"

gate:
  auto_checks:
    - command: "python -m pytest -q skillforge/tests/test_external_skill_package_adapter.py"
      expect: "passed"
  manual_checks:
    - "确认 revision 绑定可用于 at-time 回放"
    - "确认失败分支 required_changes 可执行"
```

