---
name: three-hash-permit-guard-skill
description: Enforce three-hash permit binding and delivery completeness as a single fail-closed gate. Use before final gate adjudication or any side-effect release.
---

# three-hash-permit-guard-skill

## 触发条件

- 最终门控裁决前验证
- 任何副作用释放前验证
- 需要验证 Permit 绑定字段与交付项完整性

## 输入

```yaml
input:
  permit: "path/to/permit.json"
  base_path: "."  # repo root for delivery completeness check
  out: "docs/2026-03-04/verification/three_hash_permit_guard.json"
```

## 输出

```yaml
output:
  guard_status: "PASS|FAIL"
  permit_check:
    demand_hash_present: true
    contract_hash_present: true
    decision_hash_present: true
    audit_pack_hash_present: true
    revision_present: true
    permit_valid: true
  delivery_check:
    required_items_present: true
    missing_items: []
    delivery_complete: true
  blocking_reasons: []
  fail_closed: true
```

## 检查项

1. `scripts/validate_permit_binding.py`
   - 验证 permit 包含完整绑定字段：
     `demand_hash + contract_hash + decision_hash + audit_pack_hash + revision`
   - 验证哈希格式正确

2. `scripts/validate_delivery_completeness.py`
   - 验证所有必需交付项存在
   - 验证交付项完整性

## 决策规则

- Permit PASS + Delivery PASS => `PASS`
- Otherwise => `FAIL` (fail-closed)

## 脚本模式

```powershell
python skills/three-hash-permit-guard-skill/scripts/run_guard.py --permit permits/example/permit.json --base-path . --out docs/2026-03-04/verification/three_hash_permit_guard.json
```

## Non-goals

- Do not issue permits
- Do not modify contracts
- Do not execute cloud tasks

## DoD

- [ ] Permit 包含 demand_hash
- [ ] Permit 包含 contract_hash
- [ ] Permit 包含 decision_hash
- [ ] Permit 包含 audit_pack_hash
- [ ] Permit 包含 revision
- [ ] 所有必需交付项已验证
- [ ] 验证报告已生成
- [ ] Fail-closed 规则已应用
