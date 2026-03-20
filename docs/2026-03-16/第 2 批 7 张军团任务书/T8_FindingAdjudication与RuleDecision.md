# T8 Finding Adjudication 与 RuleDecision 三权分发提示词

适用任务：

* `T8`

对应角色：

* Execution: `Antigravity-1`
* Review: `vs--cc3`
* Compliance: `Kior-C`

唯一事实源：

* [第2批施工单.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC2%E6%89%B9%E6%96%BD%E5%B7%A5%E5%8D%95.md)
* [2.0.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC%202%20%E6%89%B9%207%20%E5%BC%A0%E5%86%9B%E5%9B%A2%E4%BB%BB%E5%8A%A1%E4%B9%A6/2.0.md)
* `multi-ai-collaboration.md`

---

## 1. 发给 Antigravity-1（Execution）

```text
你是任务 T8 的执行者 Antigravity-1。

你只负责执行，不负责放行，不负责合规裁决。

task_id: T8
目标: 把 finding 从“发现对象”推进成“可裁决对象”，形成 RuleDecision 与 adjudication_report
交付物:
- adjudication_report.json
- adjudication schema
- rule_decisions[]
- 必要测试

你必须完成：
1. 为每条 finding 生成 truth_assessment / impact_level / evidence_strength / primary_basis / largest_uncertainty / recommended_action
2. 生成确定性的 RuleDecision
3. 保证无 evidence 的 finding 不得进入 adjudication success
4. 提供固定样例与验证命令

硬约束：
- 不得扩到 Owner Review
- 不得扩到 ReleaseDecision
- 不得使用自由文本拍板替代结构化字段
- 无 EvidenceRef 不得宣称完成
```

## 2. 发给 vs--cc3（Review）

```text
你是任务 T8 的审查者 vs--cc3。

你只做审查，不做执行，不做合规放行。

task_id: T8
执行者: Antigravity-1
目标: 形成 RuleDecision 与 adjudication_report

审查重点：
1. adjudication 字段是否稳定
2. severity/confidence/source 是否有确定来源
3. 无 evidence finding 是否被阻断
4. 是否偷带 Owner Review / ReleaseDecision 逻辑
5. EvidenceRef 是否足以支撑结论
```

## 3. 发给 Kior-C（Compliance）

```text
你是任务 T8 的合规官 Kior-C。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

task_id: T8
执行者: Antigravity-1
审查者: vs--cc3
目标: 形成 RuleDecision 与 adjudication_report

合规审查重点：
1. 是否允许无证据 finding 进入裁决结果
2. 是否把模糊判断直接写成确定结论
3. 是否缺少 EvidenceRef

Zero Exception Directives：
- 只要无证据 finding 可流转，直接 FAIL
- 只要 severity/confidence 拍脑袋生成，直接 FAIL
```

---

## 4. Compliance Attestation (Kior-C)

```yaml
task_id: T8
decision: PASS
reviewed_at: 2026-03-16
compliance_officer: Kior-C

violations: []

evidence_refs:
  - adjudicator.py:155-175 (determine_evidence_strength: evidence_count==0 → INSUFFICIENT)
  - adjudicator.py:343-346 (make_decision: INSUFFICIENT → FAIL/DEFER)
  - adjudicator.py:143-149 (SEVERITY_TO_IMPACT 映射)
  - finding_builder.py:291-323 (assign_initial_confidence 确定性分配)
  - findings.schema.json:291-298 (evidence_refs minItems: 1)
  - test_t8_adjudication.py:602-618 (test_adjudicate_finding_fail_no_evidence)
  - test_t8_adjudication.py:931-951 (test_no_pass_without_evidence)
  - Test execution: 59/59 PASSED

required_changes: []

notes:
  - [ADVISORY] adjudicator.py:553 使用 finding.get("evidence_refs", [])
    当前实现依赖输入已通过 schema 验证的前提。建议未来版本可添加显式断言，
    但当前不影响功能正确性（测试已验证空 evidence 正确被阻断）。

  - [ADVISORY] adjudicator.py:550 直接使用 finding["what"]["confidence"]
    confidence 值有确定来源：T6 assign_initial_confidence() 基于源类型和代码
    的确定性分配。T8 计算是组合值，不是"拍脑袋"。

  - Zero Exception Directives 验证：
    1. 无证据 finding → ✅ INSUFFICIENT → FAIL/DEFER
    2. severity/confidence → ✅ 有确定来源（非拍脑袋）
    3. EvidenceRef → ✅ Schema 强制 minItems: 1
```

---

## 5. 主控官终验记录（Codex）

- **task_id**: T8
- **decision**: **ALLOW**
- **reviewed_at**: 2026-03-16

### 终验依据

- `python -m pytest tests/contracts/test_t8_adjudication.py -v`
  - 结果：`59 passed`
- `python tests/contracts/verify_t8_compliance.py`
  - 结果：`All T8 compliance checks PASSED`
- `python -m skillforge.src.contracts.adjudicator --findings-report run/T6_evidence/findings.json --output run/T8_evidence/adjudication_report.json`
  - 结果：成功生成 `run/T8_evidence/adjudication_report.json`

### 主控结论

- T8 已具备稳定的 `RuleDecision` / `adjudication_report` 输出能力
- 无 evidence finding 被正确阻断
- severity / confidence / basis / uncertainty 均为结构化字段
- 当前 advisory 不构成阻断项

### required_changes

无。允许进入 `T9`。
