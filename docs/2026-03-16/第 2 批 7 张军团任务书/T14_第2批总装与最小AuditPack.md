# T14 第2批总装与最小 AuditPack 三权分发提示词

适用任务：

* `T14`

对应角色：

* Execution: `vs--cc3`
* Review: `Codex`
* Compliance: `Antigravity-1`

唯一事实源：

* [第2批施工单.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC2%E6%89%B9%E6%96%BD%E5%B7%A5%E5%8D%95.md)
* [2.0.md](/d:/GM-SkillForge/docs/2026-03-16/%E7%AC%AC%202%20%E6%89%B9%207%20%E5%BC%A0%E5%86%9B%E5%9B%A2%E4%BB%BB%E5%8A%A1%E4%B9%A6/2.0.md)
* `multi-ai-collaboration.md`

---

## 1. 发给 vs--cc3（Execution）

```text
你是任务 T14 的执行者 vs--cc3。

task_id: T14
目标: 把第 2 批对象串成”发现 -> 裁决 -> 交付”的最小闭环
交付物:
- audit_pack.json
- 回归样例
- 统一命令

你必须完成：
1. 串起 findings -> adjudication -> coverage -> evidence level -> release decision -> owner review -> issue/fix -> audit pack
2. 固定输出目录
3. 提供至少 3 组回归样例
4. 提供一条统一命令跑通

硬约束：
- 不得需要人工拼接
- 不得引入第 3 批 runtime 能力
- 无 EvidenceRef 不得宣称完成

统一命令：
```bash
# 基本用法（输出到 run/<run_id>/audit_pack.json）
python -m skillforge.src.contracts.run_t14_pipeline --run-id <run_id>

# 示例：使用 t14_test_demo
python -m skillforge.src.contracts.run_t14_pipeline --run-id t14_test_demo

# 验证现有 audit pack
python -m skillforge.src.contracts.run_t14_pipeline --run-id <run_id> --validate-only
```
```

## 2. 发给 Codex（Review）

```text
你是任务 T14 的审查者 Codex。

你只做审查，不做执行，不做合规放行。

task_id: T14
执行者: vs--cc3
目标: 把第 2 批对象串成最小 AuditPack 闭环

审查重点：
1. 是否仍需要人工拼接
2. 回归样例是否可重复运行
3. run 目录结构是否固定
4. 是否引入第 3 批能力
5. EvidenceRef 是否足以支撑总装结论
```

## 3. 发给 Antigravity-1（Compliance）

```text
你是任务 T14 的合规官 Antigravity-1。

你只做 B Guard 式硬审，不做执行，不做普通质量审查。

task_id: T14
执行者: vs--cc3
审查者: Codex
目标: 把第 2 批对象串成最小 AuditPack 闭环

Zero Exception Directives：
- 只要某步失败但整链继续成功，直接 FAIL
- 只要第 3 批能力混入，直接 FAIL
- 只要未覆盖被伪装成已完成，直接 FAIL
```

---

## 4. 主控官终验记录（Codex）

```yaml
task_id: T14
decision: ALLOW
final_checked_at: 2026-03-16
final_gate_by: Codex

final_gate_checks:
  - python -m pytest tests/contracts/test_t14_audit_pack.py -v
  - python tests/contracts/ci_validate_t14.py
  - python -m skillforge.src.contracts.run_t14_pipeline --run-id t14_test_demo --validate-only

verification_results:
  - pytest: 10/10 PASSED
  - ci_validate_t14.py: ALL VALIDATIONS PASSED
  - run_t14_pipeline --validate-only: Audit pack is VALID

evidence_refs:
  - tests/contracts/test_t14_audit_pack.py: 10/10 PASSED
  - tests/contracts/ci_validate_t14.py: ALL VALIDATIONS PASSED
  - skillforge/src/contracts/run_t14_pipeline.py:92-94 (--output 参数定义)
  - skillforge/src/contracts/run_t14_pipeline.py:209-214 (--output 参数实现)
  - skillforge/src/contracts/T14_DELIVERY.md
  - docs/2026-03-16/review/T14_vs-cc3_review_report.md

final_reasoning:
  - Execution 已补齐 AuditPack 统一命令、测试与交付说明
  - Review 已给出 ALLOW
  - Compliance 已确认 Zero Exception 三条通过
  - 主控实测确认 T14 自动化验证链可运行，且统一命令与文档口径一致

notes:
  - T14 完成了第 2 批“发现 -> 裁决 -> 交付”的最小 AuditPack 闭环
  - 第 2 批现已整体完成
```
