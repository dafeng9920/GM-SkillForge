# T-A2: no-permit-no-release 强制生效验证

> **执行者**: vs--cc1
> **波次**: Batch-A
> **优先级**: P0
> **依赖**: T-A1 完成后
> **预计时间**: 30 分钟

---

## 任务目标

验证 `no-permit-no-release` 在所有发布入口强制生效。

---

## 输入合同

### 需要阅读的文件

| 文件 | 用途 |
|------|------|
| `skills/permit-governance-skill/SKILL.md` | 理解约束定义 |
| `docs/2026-02-18/business_phase1_execution_report_v1.md` | 检查已有验证证据 |
| `skillforge/src/skills/gates/gate_permit.py` | 理解实现逻辑 |

### 贯穿常量

```yaml
run_id: "RUN-20260218-BIZ-PHASE1-001"
constraint: "no-permit-no-release"
```

---

## 输出合同

### 交付物

| 文件路径 | 类型 | 说明 |
|----------|------|------|
| `docs/2026-02-19/L3_A2_no_permit_no_release_verification.md` | 新建 | 约束验证报告 |

### 报告必须包含

```yaml
report_structure:
  - constraint_definition:
      name: "no-permit-no-release"
      semantics: "无 permit 时 release_allowed = false"
  - entry_points:           # 发布入口列表
      - name: string
        path: string
        enforced: bool
  - test_results:
      - scenario: "E001 无 permit"
        expected: "BLOCK"
        actual: "BLOCK"
        result: PASS | FAIL
      - scenario: "E003 签名异常"
        expected: "BLOCK"
        actual: "BLOCK"
        result: PASS | FAIL
  - conclusion:
      all_enforced: bool
      ready_for_L3: bool
```

---

## 硬约束

1. 必须覆盖 E001/E003 场景
2. 必须验证 `release_allowed` 默认值

---

## 红线 (Deny List)

- [ ] 不得修改 Gate 实现代码
- [ ] 不得绕过现有验证逻辑

---

## 质量门禁

### 人工检查

- [ ] E001 阻断验证通过
- [ ] E003 阻断验证通过
- [ ] `release_allowed=false` 在无 permit 场景成立
- [ ] 所有发布入口已覆盖

---

## 回传格式

```yaml
task_id: "T-A2"
executor: "vs--cc1"
status: "完成 | 部分完成 | 阻塞"

deliverables:
  - path: "docs/2026-02-19/L3_A2_no_permit_no_release_verification.md"
    action: "新建"
    lines_changed: int

evidence_ref: "EV-L3-A2-xxx"

notes: "特殊情况说明"
```

---

## 验收标准

- [ ] E001 阻断成立
- [ ] E003 阻断成立
- [ ] 报告文件创建
- [ ] 所有发布入口验证完成

---

