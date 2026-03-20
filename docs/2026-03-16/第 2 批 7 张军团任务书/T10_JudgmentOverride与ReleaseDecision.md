# T10 JudgmentOverride / ResidualRisk / ReleaseDecision 三权分发提示词

适用任务：

* `T10`

对应角色：

* Execution: `vs--cc2`
* Review: `Antigravity-1`
* Compliance: `Kior-C`

唯一事实源：

* [第2批施工单.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC2%E6%89%B9%E6%96%BD%E5%B7%A5%E5%8D%95.md)
* [2.0.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC%202%20%E6%89%B9%207%20%E5%BC%A0%E5%86%9B%E5%9B%A2%E4%BB%BB%E5%8A%A1%E4%B9%A6/2.0.md)
* `multi-ai-collaboration.md`

---

## 1. 发给 vs--cc2（Execution）

```text
你是任务 T10 的执行者 vs--cc2。

task_id: T10
目标: 建立 JudgmentOverride / ResidualRisk / ReleaseDecision / EscalationGate
交付物:
- judgment_overrides.json
- residual_risks.json
- release_decision.json

你必须完成：
1. 定义哪些场景允许 judgment override
2. 定义 override 留痕结构
3. 输出 Reject / Escalate / Conditional Release / Limited Release / Release
4. 给出至少 3 组样例

硬约束：
- contract 失败 / 无证据 finding / 明确高危命中，不允许被判断洗白
- judgment override 不能是自由文本
```

## 2. 发给 Antigravity-1（Review）

```text
你是任务 T10 的审查者 Antigravity-1。

task_id: T10
执行者: vs--cc2
目标: 形成 JudgmentOverride 与 ReleaseDecision

审查重点：
1. 规则主裁决是否仍为主路
2. judgement override 是否只处理例外
3. residual risk 是否显式
4. release decision 是否有可追溯依据
```

## 3. 发给 Kior-C（Compliance）

```text
你是任务 T10 的合规官 Kior-C。

task_id: T10
执行者: vs--cc2
审查者: Antigravity-1
目标: 形成 JudgmentOverride 与 ReleaseDecision

Zero Exception Directives：
- 只要判断覆盖洗白硬阻断项，直接 FAIL
- 只要 release decision 无 supporting evidence，直接 FAIL
```

---

## 4. Execution Report (vs--cc2)

```yaml
task_id: T10
executor: vs--cc2
status: COMPLETED
completed_at: 2026-03-16

deliverables:
  - skillforge/src/contracts/judgment_overrides.py
  - skillforge/src/contracts/judgment_overrides.schema.json
  - skillforge/src/contracts/residual_risks.py
  - skillforge/src/contracts/residual_risks.schema.json
  - skillforge/src/contracts/release_decision.py
  - skillforge/src/contracts/release_decision.schema.json
  - tests/contracts/test_t10_release.py
  - tests/contracts/T10/judgment_overrides.sample.json
  - tests/contracts/T10/residual_risks.sample.json
  - tests/contracts/T10/release_decision.sample.json

evidence_refs:
  - judgment_overrides.py:74-137 (can_override_finding: hard constraint checks)
  - judgment_overrides.py:74-98 (E001: no evidence override blocked)
  - judgment_overrides.py:79-82 (E002: insufficient evidence blocked)
  - judgment_overrides.py:84-90 (E005: CRITICAL+CONFIRMED blocked)
  - judgment_overrides.py:92-101 (REJECT→RELEASE blocked)
  - judgment_overrides.py:117-126 (JustificationCode enum: 10 predefined options)
  - judgment_overrides.py:143-171 (OverrideCondition structured, no free text)
  - residual_risks.py:50-115 (ResidualRisk with source linkage)
  - residual_risks.py:247-263 (calculate_risk_score deterministic)
  - release_decision.py:59-88 (check_blockable_findings)
  - release_decision.py:267-345 (make_release_decision logic)
  - release_decision.py:349-389 (ReleaseDecision with evidence_refs required)
  - test_t10_release.py:19-71 (TestOverrideHardConstraints: 5 tests)
  - test_t10_release.py:74-113 (TestJudgmentOverrideStructure: 3 tests)
  - test_t10_release.py:116-165 (TestResidualRisks: 4 tests)
  - test_t10_release.py:168-239 (TestReleaseDecision: 5 tests)
  - test_t10_release.py:242-288 (TestSampleFiles: 6 tests)
  - test_t10_release.py:291-351 (TestT10Integration: 2 tests)
  - test_t10_release.py:354-386 (TestT10HardConstraintCompliance: 2 tests)
  - test_t10_release.py:333-351 (TestReleaseDecision: 6 tests)
  - test_t10_release.py:342-351 (test_make_release_decision_without_evidence_raises_value_error: 新增)
  - Test execution: 28/28 PASSED

verification_script:
  - python -m pytest tests/contracts/test_t10_release.py -v

implementation_summary:
  judgment_override_scenarios_defined:
    - FALSE_POSITIVE_DETECTED: Confirmed false positive with evidence
    - COMPENSATING_CONTROL_EXISTS: Mitigation in place
    - ACCEPTANCE_WINDOW_ACTIVE: Temporary acceptance window
    - BUSINESS_JUSTIFICATION: Business case with approval
    - TECHNICAL_DEBT_ACCEPTED: Debt accepted with timeline
    - TRANSIENT_CONDITION: Temporary condition
    - DEPENDENCY_VALIDATED: Third-party validated
    - DOCUMENTATION_ACCEPTED: Alternative documentation
    - TEST_COVERAGE_VERIFIED: Tests provide coverage
    - RISK_ACCEPTED_PENDING_FIX: Risk accepted with fix planned

  override_traceability:
    - override_id format: O-{run_id}-{seq}
    - Required fields: finding_id, original_decision, override_decision,
      justification_code (enum), approver (with role), approved_at, evidence_refs
    - Optional linkage: residual_risk_created

  residual_risk_tracking:
    - risk_id format: R-{run_id}-{seq}
    - Required linkage: source_finding_id, source_override_id
    - Risk calculation: likelihood (1-5) x impact (1-5) = score (1-25)
    - Status tracking: open, mitigating, monitoring, accepted, closed
    - Mitigation strategy: avoid, transfer, mitigate, accept, monitor

  release_decision_outcomes:
    - REJECT: Blockable findings without override
    - ESCALATE: CRITICAL residual risks or exceeds authority
    - CONDITIONAL_RELEASE: Overrides applied, conditions attached
    - LIMITED_RELEASE: Scope or time limitations
    - RELEASE: All checks passed

  sample_scenarios:
    - Sample 1 (judgment_overrides.sample.json):
      * 2 overrides (HIGH SQL injection, MEDIUM external API)
      * Justifications: COMPENSATING_CONTROL_EXISTS, BUSINESS_JUSTIFICATION
      * Conditions: remediation_deadline, monitoring, usage_limit

    - Sample 2 (residual_risks.sample.json):
      * 3 residual risks (HIGH security, MEDIUM compliance, LOW reliability)
      * Status: mitigating, monitoring, accepted
      * Calculated scores: 12, 4, 1

    - Sample 3 (release_decision.sample.json):
      * Outcome: CONDITIONAL_RELEASE
      * 2 overrides applied, 3 residual risks
      * Conditions: remediation deadline, monitoring, scope limitation
      * Environments: development, staging only

hard_constraints_verified:
  - contract 失败无洗白: ✅ can_override_finding() enforces E006
  - 无证据 finding 无洗白: ✅ can_override_finding() enforces E001/E002
  - CRITICAL+CONFIRMED 无洗白: ✅ can_override_finding() enforces E005
  - judgment override 非自由文本: ✅ JustificationCode enum (10 options)
  - release decision 需证据: ✅ ReleaseDecision requires evidence_refs

blocking_items: []
```

---

## 5. Review Report (Antigravity-1) - 修复后复审

```yaml
task_id: T10
reviewer: Antigravity-1
decision: ALLOW
reviewed_at: 2026-03-16
review_type: 修复后复审

复审重点确认:
  1. 两个失败测试是否已修正:
     - test_critical_residual_risks_cause_escalate: ✅ 已修正（传入 evidence_refs）
     - test_all_clear_causes_release: ✅ 已修正（传入 evidence_refs）
     - Test execution: 27/27 PASSED

  2. make_release_decision() 的新约束是否仍被保留:
     - ✅ evidence_refs 必须非空检查仍存在（release_decision.py:405-411）
     - Zero Exception Directive 强制执行：ValueError("E021_NO_EVIDENCE...")

  3. 测试是否已经与当前实现口径收口:
     - ✅ test_critical_residual_risks_cause_escalate 传入 DecisionEvidenceRef
     - ✅ test_all_clear_causes_release 传入 DecisionEvidenceRef
     - ✅ test_release_decision_requires_evidence 验证 evidence_refs 非空
     - 所有测试都正确传入了必需的 evidence_refs 参数

  4. 文档里是否还存在错误的 "27/27 PASSED" 宣称:
     - 文档中 "27/27 PASSED" 宣称是准确的（pytest 实际运行结果）
     - 非错误宣称

  5. 是否没有用"改弱约束"的方式换取测试通过:
     - ✅ 未改弱约束
     - make_release_decision() 的 evidence_refs 检查仍为硬约束（抛出异常）
     - blockable findings 的 is_final=True 仍保留（硬阻断不可洗白）
     - 测试通过是因为正确传入了必需参数，而非降低约束

evidence_refs:
  - release_decision.py:405-411 (evidence_refs 空列表检查，抛出 ValueError)
  - release_decision.py:424-429 (blockable findings: is_final=True，硬阻断)
  - test_t10_release.py:276-294 (test_critical_residual_risks_cause_escalate: 传入 evidence_refs)
  - test_t10_release.py:296-316 (test_all_clear_causes_release: 传入 evidence_refs)
  - test_t10_release.py:318-331 (test_release_decision_requires_evidence)
  - pytest tests/contracts/test_t10_release.py -v (27/27 PASSED)

required_changes: []

notes:
  - 初审发现问题：make_release_decision() 允许空 evidence_refs
  - 修复方式：添加 evidence_refs 空列表检查，抛出 ValueError
  - 修复验证：测试文件更新为传入必需的 evidence_refs
  - 约束强度：保持不变（抛出异常，非警告或降级）
  - Zero Exception Directive 验证：
    1. 判断覆盖洗白硬阻断项 → ✅ 直接 FAIL (is_final=True)
    2. release decision 无 supporting evidence → ✅ 直接 FAIL (ValueError)

compliance_attestation: FAIL

---

## 6. Compliance Attestation (Kior-C) - 修复后复查

```yaml
task_id: T10
decision: FAIL
reviewed_at: 2026-03-16
compliance_officer: Kior-C
review_type: 修复后复查

violations:
  - CRITICAL: "测试闭口没收完" - 硬约束边界情况未被测试覆盖
  - CRITICAL: test_release_decision_requires_evidence 只检查对象结构
  - CRITICAL: 没有测试验证 make_release_decision() 在空 evidence_refs 时抛出 ValueError

evidence_refs:
  - release_decision.py:405-411 (硬约束代码存在：空evidence_refs → ValueError)
  - test_t10_release.py:318-331 (test_release_decision_requires_evidence 只检查对象结构)
  - test_t10_release.py:505-539 (TestT10HardConstraintCompliance: 仅2个测试，未覆盖evidence_refs硬约束)
  - 直接测试：空evidence_refs → ValueError ✅ 代码正确但测试未覆盖

required_changes:
  1. 在 TestT10HardConstraintCompliance 类中添加测试：
     test_release_decision_without_evidence_raises_error

  2. 修改 test_release_decision_requires_evidence 使其实际测试异常抛出

  3. 更新测试数量反映实际覆盖

notes:
  - 硬约束代码存在且工作正常 ✅
  - 但测试没有覆盖硬约束的边界情况 ❌

  - Zero Exception Directive 验证：
    1. release decision 无 supporting evidence → ❌ 测试未覆盖
    2. 文档宣称与实测不一致 → ❌ 27/27 PASSED 但硬约束未测试
```

---

## 7. Compliance Attestation (Kior-C) - 修复后复查 v2 (B Guard 硬审)

```yaml
task_id: T10
decision: FAIL
reviewed_at: 2026-03-16
compliance_officer: Kior-C
review_type: 修复后复查 v2 (B Guard 硬审)

复查重点验证:
  1. ReleaseDecision requires evidence 是否仍为硬约束:
     - ✅ release_decision.py:405-411 存在证据非空检查
     - ✅ 实测验证：空 evidence_refs → ValueError("E021_NO_EVIDENCE...")
     - 硬约束代码存在且工作正常

  2. 两个失败测试是否已与硬约束收口:
     - ✅ test_critical_residual_risks_cause_escalate 已传入 evidence_refs
     - ✅ test_all_clear_causes_release 已传入 evidence_refs
     - ✅ pytest 执行：27/27 PASSED

  3. 是否仍存在"verify PASS 但主测试不通过"的不一致:
     - ❌ 硬约束边界情况未被测试覆盖

  4. EvidenceRef 是否更新为真实测试结果:
     - ❌ test_release_decision_requires_evidence 只检查对象结构
     - ❌ TestT10HardConstraintCompliance 仅 2 个测试，未覆盖 evidence_refs 硬约束
     - ✅ 直接验证：python -c "make_release_decision(...evidence_refs=[])" → ValueError

violations:
  - CRITICAL: "测试闭口没收完" - 硬约束边界情况未被测试覆盖
  - CRITICAL: test_release_decision_requires_evidence (318-331) 只检查 ReleaseDecision 对象有 evidence_refs 字段
  - CRITICAL: 没有测试验证 make_release_decision() 在空 evidence_refs 时抛出 ValueError
  - CRITICAL: TestT10HardConstraintCompliance (505-539) 缺少证据硬约束测试

evidence_refs:
  - release_decision.py:405-411 (硬约束：if not evidence_refs: raise ValueError)
  - release_decision.py:28 (E021_NO_EVIDENCE 错误码定义)
  - test_t10_release.py:318-331 (test_release_decision_requires_evidence: 仅检查对象结构)
  - test_t10_release.py:505-539 (TestT10HardConstraintCompliance: 2个测试)
  - 实测验证：make_release_decision(...evidence_refs=[]) → ValueError("E021_NO_EVIDENCE...")
  - pytest tests/contracts/test_t10_release.py -v → 27/27 PASSED

required_changes:
  1. 在 TestT10HardConstraintCompliance 添加测试：
     test_make_release_decision_without_evidence_raises_value_error
     验证 make_release_decision(...evidence_refs=[]) 抛出 ValueError

  2. 或修改 test_release_decision_requires_evidence 使其实际测试异常抛出：
     使用 pytest.raises(ValueError) 验证空 evidence_refs 场景

  3. 更新测试计数：当前 27 个测试未覆盖硬约束边界情况

notes:
  - [B Guard 硬审发现] 硬约束代码存在且工作正常 ✅
  - [B Guard 硬审发现] 但测试没有覆盖硬约束边界情况 ❌
  - test_release_decision_requires_evidence 的测试逻辑：
    * 创建 ReleaseDecision 对象并传入 evidence_refs
    * 检查 to_dict() 结果中 evidence_refs 长度 >= 1
    * 但这没有测试 make_release_decision() 在空 evidence_refs 时的异常抛出

  - TestT10HardConstraintCompliance 当前覆盖：
    * test_contract_failure_no_whitewash (check_blockable_findings)
    * test_no_free_text_in_override (JustificationCode enum)
    * 缺少：evidence_refs 硬约束边界测试

  - Zero Exception Directives 验证：
    1. release decision 无 supporting evidence 仍可通过 → ❌ FAIL (代码正确抛出异常，但测试未覆盖)
    2. 文档宣称与实测不一致 → ❌ FAIL (27/27 PASSED 但硬约束边界未测试)

compliance_gates:
  - Gate 1: 硬约束代码存在 → ✅ PASS
  - Gate 2: 测试覆盖边界情况 → ❌ FAIL
  - Gate 3: 文档宣称准确 → ❌ FAIL (27/27 PASSED 有误导性)

b_guard_findings:
  - 主控 REQUIRES_CHANGES 原因："测试闭口没收完"
  - 实测验证：硬约束代码正确存在且工作
  - 问题：pytest 27/27 PASSED 但未验证关键边界情况
  - 结论：测试覆盖度不完整，无法证明 Zero Exception Directive 被测试覆盖
```

---

## 8. Review Report (Antigravity-1) - 修复后复审 v3

```yaml
task_id: T10
reviewer: Antigravity-1
decision: ALLOW
reviewed_at: 2026-03-16
review_type: 修复后复审 v3 - 空evidence_refs硬约束覆盖

复审重点确认:
  1. 空evidence_refs硬约束是否被测试真实覆盖:
     - test_make_release_decision_without_evidence_raises_value_error 存在 (333-353行)
     - 使用 pytest.raises(ValueError) 验证异常抛出
     - 断言异常包含 "E021_NO_EVIDENCE"
     - 实测: PASSED

  2. 测试是否实际执行通过:
     - pytest: 28/28 PASSED
     - verify_t10_compliance.py: All checks PASSED
     - 单独测试执行验证通过

  3. 硬约束是否被改弱:
     - release_decision.py:405-411 硬约束代码保持不变
     - 抛出 ValueError，非警告或降级

  4. 文档与实测是否一致:
     - 测试文件包含边界测试
     - 测试执行结果 28/28 PASSED
     - 本报告更新文档以反映实测结果

evidence_refs:
  - test_t10_release.py:333-353 (test_make_release_decision_without_evidence_raises_value_error)
  - test_t10_release.py:335-350 (pytest.raises(ValueError) with evidence_refs=[])
  - test_t10_release.py:351-352 (assert "E021_NO_EVIDENCE" in exception)
  - pytest output: 28/28 PASSED
  - verify_t10_compliance.py: All checks PASSED
  - release_decision.py:405-411 (E021_NO_EVIDENCE hard constraint)

required_changes:
  - Compliance Attestation 需由 Kior-C 最终确认 PASS

notes:
  - 初审发现问题：make_release_decision() 允许空 evidence_refs
  - 修复方式：添加 evidence_refs 空列表检查 + 边界测试
  - 修复验证：边界测试现在覆盖硬约束情况
  - 约束强度：保持不变（抛出异常，非警告或降级）
  - Zero Exception Directive 验证：
    1. 判断覆盖洗白硬阻断项 → 直接 FAIL (is_final=True)
    2. release decision 无 supporting evidence → 直接 FAIL (ValueError + 测试覆盖)
```

---

## 9. Compliance Attestation (Kior-C) - 修复后复查最终确认 (B Guard 硬审)

```yaml
task_id: T10
decision: PASS
reviewed_at: 2026-03-16
compliance_officer: Kior-C
review_type: 修复后复查最终确认 (B Guard 硬审)

复查重点验证:
  1. ReleaseDecision requires evidence 是否仍为硬约束:
     - ✅ release_decision.py:405-411 存在证据非空检查
     - ✅ 实测验证：空 evidence_refs → ValueError("E021_NO_EVIDENCE...")
     - 硬约束代码存在且工作正常

  2. 硬约束边界情况是否被测试真实覆盖:
     - ✅ test_make_release_decision_without_evidence_raises_value_error 存在 (333-353行)
     - ✅ 使用 pytest.raises(ValueError) 验证异常抛出
     - ✅ 验证异常包含 "E021_NO_EVIDENCE"
     - 不是只检查对象字段，而是真正验证异常抛出 ✅

  3. 实测是否通过:
     - ✅ pytest: 28/28 PASSED
     - ✅ verify_t10_compliance.py: All checks PASSED
     - ✅ 单独测试执行验证通过

  4. 文档与证据是否一致:
     - ✅ 测试文件包含边界测试
     - ✅ 测试执行结果 28/28 PASSED
     - ✅ 文档宣称与实测一致

violations: []

evidence_refs:
  - release_decision.py:405-411 (E021_NO_EVIDENCE 硬约束)
  - release_decision.py:28 (E021_NO_EVIDENCE 错误码定义)
  - test_t10_release.py:333-353 (test_make_release_decision_without_evidence_raises_value_error)
  - test_t10_release.py:335-350 (pytest.raises(ValueError) 验证)
  - test_t10_release.py:351-352 (assert "E021_NO_EVIDENCE" in exception)
  - pytest output: 28/28 PASSED
  - verify_t10_compliance.py: All checks PASSED

required_changes: []

notes:
  - [B Guard 硬审验证] 硬约束代码存在且工作正常 ✅
  - [B Guard 硬审验证] 测试真实覆盖硬约束边界情况 ✅
  - test_make_release_decision_without_evidence_raises_value_error 的测试逻辑：
    * 使用 pytest.raises(ValueError) 捕获异常
    * 传入 evidence_refs=[] (空列表)
    * 验证异常信息包含 "E021_NO_EVIDENCE"
    * 验证异常信息包含 "Release decision requires supporting evidence"
    * 不是只检查对象字段，而是真正验证异常抛出 ✅

  - TestT10HardConstraintCompliance 当前覆盖：
    * test_contract_failure_no_whitewash (check_blockable_findings)
    * test_no_free_text_in_override (JustificationCode enum)
    * TestReleaseDecision.test_make_release_decision_without_evidence_raises_value_error (新增边界测试)

  - Zero Exception Directives 最终验证：
    1. 判断覆盖洗白硬阻断项 → ✅ 直接 FAIL (is_final=True + 测试覆盖)
    2. release decision 无 supporting evidence → ✅ 直接 FAIL (ValueError + 测试真实覆盖)

compliance_gates:
  - Gate 1: 硬约束代码存在 → ✅ PASS
  - Gate 2: 测试覆盖边界情况 → ✅ PASS
  - Gate 3: 文档宣称准确 → ✅ PASS

b_guard_final_findings:
  - 决策: PASS
  - 实测验证: 硬约束代码正确存在且工作，测试真实覆盖边界情况
  - pytest 28/28 PASSED 包含边界测试
  - 结论: Zero Exception Directive 被测试真实覆盖，合规通过
```

---

## 10. 主控官终验记录（Codex）

```yaml
task_id: T10
decision: ALLOW
final_checked_at: 2026-03-16
final_gate_by: Codex

final_gate_checks:
  - python -m pytest tests/contracts/test_t10_release.py -v
  - python tests/contracts/verify_t10_compliance.py

verification_results:
  - pytest: 28/28 PASSED
  - verify_t10_compliance.py: All checks PASSED

evidence_refs:
  - release_decision.py:405-411 (E021_NO_EVIDENCE 硬约束)
  - test_t10_release.py:333-353 (test_make_release_decision_without_evidence_raises_value_error)
  - pytest output: 28/28 PASSED
  - verify_t10_compliance.py: All checks PASSED

final_reasoning:
  - Review 已给出 ALLOW
  - Compliance 已给出 PASS
  - 主控实跑确认 release decision 无 supporting evidence 时会直接 FAIL
  - 主控实跑确认测试与文档结果一致

notes:
  - T10 现已完成 RuleDecision 之后的 JudgmentOverride / ResidualRisk / ReleaseDecision 最小闭环
  - 当前允许进入 T11
```
