# T11 Owner Review Layer 三权分发提示词

适用任务：

* `T11`

对应角色：

* Execution: `Kior-A`
* Review: `vs--cc3`
* Compliance: `Kior-C`

唯一事实源：

* [第2批施工单.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC2%E6%89%B9%E6%96%BD%E5%B7%A5%E5%8D%95.md)
* [2.0.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC%202%20%E6%89%B9%207%20%E5%BC%A0%E5%86%9B%E5%9B%A2%E4%BB%BB%E5%8A%A1%E4%B9%A6/2.0.md)
* `multi-ai-collaboration.md`

---

## 1. 发给 Kior-A（Execution）

```text
你是任务 T11 的执行者 Kior-A。

task_id: T11
目标: 建立 Owner Review Layer（二层报告制）
交付物:
- owner_review.json
- owner_review.md

你必须完成：
1. 单 finding 裁决卡固定 7 字段
2. owner summary
3. 不直接把技术 finding 原样堆给 owner

硬约束：
- 不做大 dashboard
- 不把 owner review 写成技术原始日志堆叠
```

## 2. 发给 vs--cc3（Review）

```text
你是任务 T11 的审查者 vs--cc3。

task_id: T11
执行者: Kior-A
目标: 形成 owner_review.json / owner_review.md

审查重点：
1. 是否保留 blocking findings
2. 是否做成 owner 可判内容
3. 是否仍残留技术层原始报告堆叠
```

## 3. 发给 Kior-C（Compliance）

```text
你是任务 T11 的合规官 Kior-C。

task_id: T11
执行者: Kior-A
审查者: vs--cc3
目标: 形成 Owner Review Layer

Zero Exception Directives：
- 只要 owner review 隐藏 blocking findings，直接 FAIL
- 只要把未覆盖项包装成已确认结论，直接 FAIL
```

---

## 4. Compliance Attestation (Kior-C) - B Guard 硬审

```yaml
task_id: T11
decision: FAIL
reviewed_at: 2026-03-16
compliance_officer: Kior-C
review_type: B Guard 硬审

violations:
  - CRITICAL: "_build_owner_cards() 不检查 blocking_findings"
  - CRITICAL: 测试文件导入错误，无法运行
  - CRITICAL: decision_summary.blocking_issues 不是真实 blocking findings

evidence_refs:
  - owner_review.py:513-529 (_build_owner_cards 过滤逻辑)
  - owner_review.py:439-440 (blocking_issues 只是 CRITICAL+HIGH 计数)
  - test_t11_owner_review.py:12-18 (错误导入 FindingSource)
  - test_t11_owner_review.py:125-128 (错误 Finding 构造)
  - pytest ImportError: cannot import FindingSource

required_changes:
  1. _build_owner_cards() 必须检查 release_decision.blocking_findings
  2. 修复测试文件导入和 Finding 构造
  3. decision_summary.blocking_issues 应使用真实 blocking findings 计数

notes:
  - [B Guard 硬审] coverage_note 正确报告 not_covered ✅
  - [B Guard 硬审] blocking findings 可能被隐藏 ❌

  Zero Exception Directives 验证：
    1. owner review 隐藏 blocking findings → ❌ FAIL
    2. 未覆盖项包装成已确认结论 → ✅ PASS
```

---

## 5. Execution Report (Kior-A) - 修复完成

```yaml
task_id: T11
executed_by: Kior-A
executed_at: 2026-03-16
status: FIXED

fixed_files:
  - skillforge/src/contracts/owner_review.py
  - tests/contracts/test_t11_owner_review.py

what_was_wrong:
  1. _build_owner_cards() 没有检查 release_decision.blocking_findings
  2. decision_summary.blocking_issues 只用 CRITICAL+HIGH 计数代替
  3. 测试文件导入错误 (FindingSource 不存在，应该是 FindingSourceType)
  4. Finding 构造使用了错误的嵌套字典结构

what_was_changed:
  1. owner_review.py:
     - _build_owner_cards() 现在接受 release_decision 参数
     - 从 release_decision.blocking_findings 获取阻断项 ID
     - 阻断项总是被标记为 BLOCKS_RELEASE
     - _build_decision_summary() 中 blocking_issues 现在使用 len(release_decision.blocking_findings)
     - _finding_to_owner_card() 增加 is_blocking 参数
     - _determine_business_impact() 增加 is_blocking 参数，阻断项强制返回 BLOCKS_RELEASE

  2. test_t11_owner_review.py:
     - 修复导入：从 finding_builder 导入正确的类
     - 修复 Finding 构造：使用扁平参数而非嵌套字典
     - 修复 FindingsReport 构造：使用正确的字段
     - 新增 test_t11_blocking_findings_must_be_exposed 测试

verification_results:
  - pytest tests/contracts/test_t11_owner_review.py -v
  - 17 passed in 0.12s
  - 所有测试通过，包括新增的阻断项暴露验证

evidence_refs:
  - owner_review.py:500-560 (_build_owner_cards 现在检查 blocking_findings)
  - owner_review.py:446-448 (blocking_issues 来自真实 blocking_findings)
  - owner_review.py:533-570 (_finding_to_owner_card 和 _determine_business_impact 处理 is_blocking)
  - test_t11_owner_review.py:497-525 (test_t11_blocking_findings_must_be_exposed)
  - pytest 运行日志: 17 passed

reviewer_focus:
  - 验证 release_decision.blocking_findings 中的 ID 确实出现在 owner_cards 中
  - 验证这些卡的 business_impact 都是 BLOCKS_RELEASE
  - 验证 decision_summary.blocking_issues 计数与 blocking_findings 长度一致
```

---

## 6. Review Attestation (vs--cc3) - 复审结论

```yaml
task_id: T11
decision: ALLOW
reviewer: vs--cc3
reviewed_at: 2026-03-16
review_type: 复审 (B Guard 硬审后修复验证)

violations: []

evidence_refs:
  - owner_review.py:525-565 (_build_owner_cards 检查 blocking_findings)
  - owner_review.py:527 (blocking_finding_ids = set(release_decision.blocking_findings))
  - owner_review.py:535 (is_blocking = finding.finding_id in blocking_finding_ids)
  - owner_review.py:554-565 (验证所有 blocking findings 都有 cards)
  - owner_review.py:446-448 (blocking_issues = len(release_decision.blocking_findings))
  - owner_review.py:677-679 (is_blocking 强制返回 BLOCKS_RELEASE)
  - test_t11_owner_review.py:501-543 (test_t11_blocking_findings_must_be_exposed)
  - test_t11_owner_review.py:324-325 (assert blocking_issues == 1)
  - test_t11_owner_review.py:524-525 (assert blocking_issues == len(blocking_finding_ids))
  - test_t11_owner_review.py:537-543 (assert business_impact == BLOCKS_RELEASE)
  - pytest output: 17/17 PASSED in 0.06s

verification_script:
  - python -m pytest tests/contracts/test_t11_owner_review.py -v

required_changes: []

review_points_verified:
  1. Owner Review 是否已显式展示真实 blocking findings:
     ✅ PASS - _build_owner_cards() 从 release_decision.blocking_findings 获取
     ✅ PASS - is_blocking 标记正确传递到 _determine_business_impact
     ✅ PASS - 验证逻辑确保所有 blocking findings 都有 cards (L554-565)

  2. decision_summary.blocking_issues 是否已改为真实 blocking_findings 计数:
     ✅ PASS - 使用 len(release_decision.blocking_findings or []) (L448)
     ✅ PASS - 不再是 CRITICAL+HIGH 的近似值
     ✅ PASS - 测试 assert blocking_issues == len(blocking_finding_ids) 通过

  3. tests/contracts/test_t11_owner_review.py 是否已可运行并真正覆盖边界:
     ✅ PASS - 17/17 tests PASSED
     ✅ PASS - test_t11_blocking_findings_must_be_exposed 验证阻断项暴露
     ✅ PASS - fixture 中 blocking_findings=["F-rule_scan_E401_abc12345"] 正确设置
     ✅ PASS - 测试验证 business_impact == BLOCKS_RELEASE for blocking findings

notes:
  - [复审] T11 所有 B Guard 硬审发现的问题已修复 ✅
  - [复审] 阻断项暴露逻辑有完整验证 ✅
  - [复审] 测试覆盖关键边界情况 ✅
  - [复审] 区分了"severity 高"与"真实 blocking" ✅
```

---

## 7. Compliance Attestation (Kior-C) - 修复后复查最终确认

```yaml
task_id: T11
decision: PASS
reviewed_at: 2026-03-16
compliance_officer: Kior-C
review_type: 修复后复查（B Guard 硬审）

violations: []

evidence_refs:
  - owner_review.py:525-565 (_build_owner_cards 显式检查 blocking_findings)
  - owner_review.py:527 (blocking_finding_ids = set(release_decision.blocking_findings))
  - owner_review.py:535 (is_blocking = finding.finding_id in blocking_finding_ids)
  - owner_review.py:543-547 (if not is_blocking: 才进行过滤)
  - owner_review.py:554-565 (验证所有 blocking findings 都有 cards)
  - owner_review.py:446-448 (blocking_issues = len(release_decision.blocking_findings))
  - owner_review.py:678-679 (if is_blocking: return BLOCKS_RELEASE)
  - owner_review.py:807-810 (not_covered.extend 总是包含限制项)
  - test_t11_owner_review.py:555-597 (test_t11_blocking_findings_must_be_exposed)
  - pytest output: 17/17 PASSED

verification_script:
  - python -m pytest tests/contracts/test_t11_owner_review.py -v

required_changes: []

notes:
  - [修复后复查] owner review 不再可能隐藏 blocking findings ✅
  - [修复后复查] blocking_issues 来自真实 blocking_findings ✅
  - [修复后复查] 测试真实覆盖"阻断项必须展示" ✅
  - [修复后复查] pytest 可运行，无导入错误 ✅
  - [修复后复查] coverage_note 正确报告 not_covered ✅

  Zero Exception Directives 最终验证：
    1. owner review 隐藏 blocking findings → ✅ PASS
    2. 未覆盖项包装成已确认结论 → ✅ PASS
```
