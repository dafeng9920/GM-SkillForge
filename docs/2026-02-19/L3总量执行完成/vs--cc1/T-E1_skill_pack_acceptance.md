# T-E1: 3+1 Skill 包验收

> **执行者**: vs--cc1 (Antigravity-3)
> **波次**: Batch-B
> **优先级**: P1
> **依赖**: Batch-A 全部 PASS
> **预计时间**: 30 分钟

---

## 任务目标

验收 4 个 Skill 包（permit-governance, release-gate, rollback-tombstone, ci-skill-validation）。

---

## 输入合同

### 需要阅读的文件

| 文件 | 用途 |
|------|------|
| `skills/permit-governance-skill/SKILL.md` | 检查 Skill 定义 |
| `skills/release-gate-skill/SKILL.md` | 检查 Skill 定义 |
| `skills/rollback-tombstone-skill/SKILL.md` | 检查 Skill 定义 |
| `skills/ci-skill-validation-skill/SKILL.md` | 检查 Skill 定义 |

### 贯穿常量

```yaml
skill_count: 4
skills:
  - permit-governance-skill
  - release-gate-skill
  - rollback-tombstone-skill
  - ci-skill-validation-skill
```

---

## 输出合同

### 交付物

| 文件路径 | 类型 | 说明 |
|----------|------|------|
| `docs/2026-02-19/L3_E1_skill_pack_acceptance.md` | 新建 | Skill 包验收报告 |

### 报告必须包含

```yaml
report_structure:
  - skill_list:
      - name: string
        has_skill_md: bool
        has_openai_yaml: bool
        has_references: bool
        ci_passed: bool
  - acceptance_summary:
      total: 4
      passed: int
      failed: int
  - per_skill_results:
      - skill_name: string
        structure_check: PASS | FAIL
        contract_markers: PASS | FAIL
        evidence_refs: PASS | FAIL
```

---

## 硬约束

1. 必须验证 4 个 Skill 包
2. 必须运行 skillization CI gate

---

## 红线 (Deny List)

- [ ] 不得修改 Skill 包内容
- [ ] 不得绕过 CI 检查

---

## 质量门禁

### 自动检查

```powershell
pwsh -File ci/run_skillization_gate.ps1
# 预期: 5/5 PASS
```

### 人工检查

- [ ] 4 个 Skill 包结构完整
- [ ] CI gate 全绿
- [ ] 验收报告格式正确

---

## 回传格式

```yaml
task_id: "T-E1"
executor: "vs--cc1"
status: "完成 | 部分完成 | 阻塞"

deliverables:
  - path: "docs/2026-02-19/L3_E1_skill_pack_acceptance.md"
    action: "新建"
    lines_changed: int

gate_self_check:
  - command: "pwsh -File ci/run_skillization_gate.ps1"
    result: "5/5 PASS"

evidence_ref: "EV-L3-E1-xxx"

notes: "特殊情况说明"
```

---

## 验收标准

- [ ] 4 个 Skill 包结构验证
- [ ] CI gate 5/5 PASS
- [ ] 验收报告创建

---

*任务生成时间: 2026-02-19*
