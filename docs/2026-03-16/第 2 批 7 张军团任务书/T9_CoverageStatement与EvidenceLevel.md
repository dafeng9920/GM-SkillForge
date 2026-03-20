# T9 CoverageStatement 与 EvidenceLevel 三权分发提示词

适用任务：

* `T9`

对应角色：

* Execution: `vs--cc1`
* Review: `Antigravity-2`
* Compliance: `Kior-C`

唯一事实源：

* [第2批施工单.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC2%E6%89%B9%E6%96%BD%E5%B7%A5%E5%8D%95.md)
* [2.0.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC%202%20%E6%89%B9%207%20%E5%BC%A0%E5%86%9B%E5%9B%A2%E4%BB%BB%E5%8A%A1%E4%B9%A6/2.0.md)
* `multi-ai-collaboration.md`

---

## 1. 发给 vs--cc1（Execution）

```text
你是任务 T9 的执行者 vs--cc1。

task_id: T9
目标: 把“测了什么、没测什么、证据有多强”对象化
交付物:
- coverage_statement.json
- evidence_level.json
- 必要测试

你必须完成：
1. 定义 CoverageStatement
2. 定义 EvidenceLevel（E1-E5 最小口径）
3. 显式列出未覆盖项
4. 生成固定样例与验证命令

硬约束：
- 不得把未覆盖写成已完成
- 不得提前做组合态全覆盖框架
```

## 2. 发给 Antigravity-2（Review）

```text
你是任务 T9 的审查者 Antigravity-2。

task_id: T9
执行者: vs--cc1
目标: 形成 CoverageStatement 与 EvidenceLevel

审查重点：
1. 已覆盖 / 未覆盖边界是否明确
2. 证据等级是否有稳定口径
3. 是否存在“默认全覆盖”倾向
4. EvidenceRef 是否完整
```

## 3. 发给 Kior-C（Compliance）

```text
你是任务 T9 的合规官 Kior-C。

task_id: T9
执行者: vs--cc1
审查者: Antigravity-2
目标: 形成 CoverageStatement 与 EvidenceLevel

Zero Exception Directives：
- 只要未覆盖项被伪装成已完成，直接 FAIL
- 只要 evidence level 无证据支撑，直接 FAIL
```

---

## 4. Compliance Attestation (Kior-C)

```yaml
task_id: T9
decision: PASS
reviewed_at: 2026-03-16
compliance_officer: Kior-C

violations: []

evidence_refs:
  # 基础证据（同前）
  - coverage_statement.py:224-234 (add_covered 强制要求 evidence_refs)
  - coverage_statement.py:224-228 (add_covered 强制验证 E1-E5)
  - coverage_statement.py:296-315 (compute_summary: silence=not_covered)
  - coverage_statement.schema.json:136-139 (evidence_refs minItems=1)
  - evidence_level.py:62-216 (E1-E5 完整定义)
  - test_t9_coverage.py:400-460 (基础合规测试)

  # E5 dual-gate + receipt 修复证据
  - evidence_level.py:50-52 (E915/E916/E917 错误码)
  - evidence_level.py:342-370 (E5 dual-gate + receipt 强制验证)
  - evidence_level.py:344-345 (has_entry_gate/has_exit_gate 检查)
  - evidence_level.py:346-349 (has_receipt 检查，支持RUN_ID)
  - evidence_level.py:351-356 (缺少entry → E915)
  - evidence_level.py:358-363 (缺少exit → E916)
  - evidence_level.py:365-370 (缺少receipt → E917)
  - test_t9_coverage.py:333-389 (E5 dual-gate 测试套件)
  - verify_t9.py: 完整验证脚本 (12项全PASS)
  - Test execution: 37/37 PASSED (含E5专项测试)

required_changes: []

notes:
  - Zero Exception Directive 1: 未覆盖项伪装防护 ✅
    * coverage_statement.py:296-315 只计算明确声明的 covered/uncovered
    * exclusions 明确不计入 total
    * 空语句 → coverage_percent=0.0（silence = not covered）
    * add_covered() 强制要求至少 1 个 evidence_ref（E904）

  - Zero Exception Directive 2: E5 dual-gate + receipt 强制执行 ✅
    * validate_evidence_refs() 对E5强制检查三要素
    * 缺少entry_gate → E915_ENTRY_GATE_MISSING
    * 缺少exit_gate → E916_EXIT_GATE_MISSING
    * 缺少receipt → E917_RECEIPT_MISSING
    * 直接测试：只有entry/只有exit/entry+exit无receipt 全部被拒绝
    * 完整三者（entry+exit+receipt）→ PASS

  - verify_t9.py 已同步更新 ✅
    * 运行结果：12/12 检查通过
    * test suite: 37 passed (含E5专项)
```

---

## 4.1. 修复后复查记录（Kior-C）

```yaml
task_id: T9
review_type: RE_EXAMINATION_AFTER_FIX
original_decision: PASS
re_examined_at: 2026-03-16
issue_found: E5 缺少 dual-gate + receipt 强制验证

fix_verified:
  - E5 现在强制要求 entry_gate_decision
  - E5 现在强制要求 exit_gate_decision
  - E5 现在强制要求 receipt (支持RUN_ID或显式receipt)
  - 三者缺一不可，不完整gate证据全部被拒绝

direct_test_results:
  - 只有entry: FAIL (E916+E917)
  - 只有exit: FAIL (E915+E917)
  - entry+exit无receipt: FAIL (E917)
  - 完整三者: PASS

re_examined_decision: PASS
```

---

## 5. 主控官终验记录（Codex）

- **task_id**: T9
- **decision**: **ALLOW** (修复后)
- **reviewed_at**: 2026-03-16

### 终验依据

- `python tests/contracts/verify_t9.py`
  - 结果：`12/12 PASSED`
- `python -m pytest tests/contracts/test_t9_coverage.py -v`
  - 结果：`37 passed` (含E5 dual-gate专项测试)
- E5 dual-gate 验证直接测试：
  - 只有entry → FAIL (E916+E917)
  - 只有exit → FAIL (E915+E917)
  - entry+exit无receipt → FAIL (E917)
  - 完整三者 → PASS

### 主控结论

- T9 已具备完整的 CoverageStatement 与 EvidenceLevel 输出能力
- "silence = not covered" 原则强制执行
- E1-E5 证据等级定义稳定
- E5 dual-gate + receipt 强制验证已修复
- evidence_refs 强制要求
- 无默认全覆盖/默认证据强度

### required_changes

无。允许进入 `T10`。

