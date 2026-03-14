---
name: protocol-gate-ci-checker-skill
description: 校验协议测试门禁（T1-T5）是否接入 CI 且 fail-closed，确保未通过时禁止合并。
---

# protocol-gate-ci-checker-skill

## 触发条件

- 修改了协议测试或 CI workflow
- 需要验证 ISSUE-09 门禁持续生效
- 发布前需要确认 CI 阻断链路

## 输入

```yaml
input:
  ci_file: ".github/workflows/ci.yml"
  protocol_tests:
    - "skillforge/tests/test_l6_protocol.py"
  gate_script: "scripts/run_l6_protocol_gate.py"
  required_gates:
    - "l6-protocol-gate"
    - "final-gate"
```

## 输出

```yaml
output:
  ci_gate_report: "verification/T10_pipeline_gate_report.md"
  check_result:
    - gate_present
    - fail_closed
    - merge_blocking
```

## DoD

- [ ] CI 中存在协议门禁 job
- [ ] 协议测试失败时 pipeline 失败
- [ ] 最终 gate 依赖协议门禁结果

