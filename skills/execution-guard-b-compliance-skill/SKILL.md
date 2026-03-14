---
name: execution-guard-b-compliance-skill
description: 强制执行前必须达到合规要求 (Compliance PASS)，副作用操作需 permit 放行
---

# execution-guard-b-compliance-skill

## 触发条件

- 代码更改需要执行前审计
- 需要验证 Fail-Closed 原则
- 需要检查合规状态

## 输入

```yaml
input:
  code_diffs: "path/to/diff"
  test_outputs: "path/to/test/results"
  compliance_target: "PASS"
  protocol_reference: "D:/GM-SkillForge/docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
```

## 输出

```yaml
output:
  decision: "PASS|REQUIRES_CHANGES|DENY"
  violations: []
  evidence_refs:
    - "screenshot_log_001.png"
    - "line_42_45"
  compliance_score: 100
  audit_timestamp: "2026-03-04T12:00:00Z"
```

## 核心法则

"这条改动是否可能在任何条件下绕过 Fail-Closed？只要答案不是绝对的'否'，就不通过。"

## 唯一权限参考集

确保执行以下文件中的精确零例外指令：
`D:/GM-SkillForge/docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`

## 审计执行流程

1. 扫描代码差异中的 dummy 注入、返回 PASS 的 mock 密钥、隐式回退陷阱
2. 读取测试输出以确保没有错误被吞掉
3. 验证负面用例干净地阻止执行流
4. 严格使用以下格式输出结论：
   - **Decision**: `PASS`, `REQUIRES_CHANGES`, 或 `DENY`
   - **Violations**: （如有）
   - **Evidence Ref**: 截图日志或行号

## DoD

- [ ] 代码差异已扫描
- [ ] 测试输出已检查
- [ ] 负面用例已验证
- [ ] 决策已输出
- [ ] 违规记录已生成（如有）
