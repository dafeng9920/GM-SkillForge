# T12 IssueRecord 与 FixRecommendation 三权分发提示词

适用任务：

* `T12`

对应角色：

* Execution: `Antigravity-2`
* Review: `vs--cc1`
* Compliance: `Kior-C`

唯一事实源：

* [第2批施工单.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC2%E6%89%B9%E6%96%BD%E5%B7%A5%E5%8D%95.md)
* [2.0.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC%202%20%E6%89%B9%207%20%E5%BC%A0%E5%86%9B%E5%9B%A2%E4%BB%BB%E5%8A%A1%E4%B9%A6/2.0.md)
* `multi-ai-collaboration.md`

---

## 1. 发给 Antigravity-2（Execution）

```text
你是任务 T12 的执行者 Antigravity-2。

task_id: T12
目标: 建立 IssueRecord 与 FixRecommendation，把问题推进到资产化前半段
交付物:
- issue_records.json
- fix_recommendations.json

你必须完成：
1. 定义 IssueRecord
2. 定义 FixRecommendation
3. 形成 Finding -> IssueRecord -> FixRecommendation 链路

硬约束：
- 未经裁决的 finding 不得直接进 issue 资产层
- fix recommendation 必须回指 issue_id
```

## 2. 发给 vs--cc1（Review）

```text
你是任务 T12 的审查者 vs--cc1。

task_id: T12
执行者: Antigravity-2
目标: 形成 issue_records.json / fix_recommendations.json

审查重点：
1. issue 是否都来源于 adjudication 结果
2. fix recommendation 是否可回指
3. 是否偷带 RevisionCandidate / ReauditResult
```

## 3. 发给 Kior-C（Compliance）

```text
你是任务 T12 的合规官 Kior-C。

task_id: T12
执行者: Antigravity-2
审查者: vs--cc1
目标: 形成问题资产化前半段

Zero Exception Directives：
- 只要未经裁决的 finding 直接进入 issue 资产层，直接 FAIL
- 只要未经复审的修复建议被记作关闭，直接 FAIL
```

---

## 4. Compliance Attestation (Kior-C) - B Guard 硬审

```yaml
task_id: T12
decision: PASS
reviewed_at: 2026-03-16
compliance_officer: Kior-C
review_type: B Guard 硬审

violations: []

evidence_refs:
  - issue_record.py:297-303 (create_issue_from_decision 硬约束)
  - issue_record.py:402-404 (create_issues_from_adjudication_report 跳过非 PASS/FAIL)
  - issue_record.py:44-50 (E1201_INVALID_DECISION 错误码)
  - test_t12_issue_tracking.py:175-199 (test_waive_decision_does_not_create_issue)
  - test_t12_issue_tracking.py:201-225 (test_defer_decision_does_not_create_issue)
  - test_t12_issue_tracking.py:463-500 (test_only_pass_fail_create_issues)
  - verify_t12.py:176-226 (WAIVE/DEFER 验证)
  - pytest output: 19/19 PASSED
  - verify_t12.py: 11 checks PASSED

verification_script:
  - python -m pytest tests/contracts/test_t12_issue_tracking.py -v
  - python tests/contracts/verify_t12.py

required_changes: []

notes:
  - FixRecommendation 类无 status 字段，不存在"关闭"状态 ✅
  - issue 创建必须来自 RuleDecision（adjudication 结果） ✅
  - 只有 PASS/FAIL 决策创建 issue ✅

  Zero Exception Directives 最终验证：
    1. 未经裁决的 finding 直接进入 issue 资产层 → ✅ PASS
    2. 未经复审的修复建议被记作关闭 → ✅ PASS
```

---

## 5. 主控官终验记录（Codex）

```yaml
task_id: T12
decision: ALLOW
final_checked_at: 2026-03-16
final_gate_by: Codex

final_gate_checks:
  - python tests/contracts/verify_t12.py
  - python -m pytest tests/contracts/test_t12_issue_tracking.py -v

verification_results:
  - verify_t12.py: T12 DELIVERY VERIFIED
  - pytest: 19/19 PASSED

evidence_refs:
  - issue_record.py:297-303 (仅 PASS/FAIL 可进入 IssueRecord)
  - fix_recommendation.py:169-170 (FixRecommendation 必须回指 issue_id)
  - tests/contracts/test_t12_issue_tracking.py: 19/19 PASSED
  - tests/contracts/verify_t12.py: 11/11 checks PASSED
  - docs/2026-03-16/review/T12_vs-cc1_review_report.md

final_reasoning:
  - Execution 交付物完整，Finding -> IssueRecord -> FixRecommendation 链路成立
  - Review 已确认 issue 来源、fix 回指、无 RevisionCandidate/ReauditResult 偷带
  - Compliance 已确认 Zero Exception 两条通过
  - 主控实测确认验证脚本与测试套件全绿

notes:
  - T12 完成了第 2 批“问题资产化前半段”的核心对象
  - 当前允许进入 T13
```
