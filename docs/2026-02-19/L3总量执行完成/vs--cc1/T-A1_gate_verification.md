# T-A1: 8/9 Gate 稳定运行验证

> **执行者**: vs--cc1
> **波次**: Batch-A
> **优先级**: P0
> **预计时间**: 45 分钟

---

## 任务目标

确认 8/9 Gate 清单并验证稳定运行。

---

## 输入合同

### 需要阅读的文件

| 文件 | 用途 |
|------|------|
| `docs/2026-02-16/完整版模块清单 + 全量接口契约目录/完整版模块清单 + 全量接口契约目录.md` | 理解 Gate 链定义 |
| `skillforge/src/skills/gates/` | 检查 Gate 实现状态 |
| `docs/2026-02-18/business_phase1_execution_report_v1.md` | 检查已有运行证据 |

### 贯穿常量

```yaml
run_id: "RUN-20260218-BIZ-PHASE1-001"
phase: "L3"
```

---

## 输出合同

### 交付物

| 文件路径 | 类型 | 说明 |
|----------|------|------|
| `docs/2026-02-19/L3_A1_gate_verification_report.md` | 新建 | Gate 验证报告 |

### 报告必须包含

```yaml
report_structure:
  - gate_list:          # 9 个 Gate 清单
      - name: string
      - status: IMPLEMENTED | NOT_IMPLEMENTED
      - test_coverage: bool
  - verification_results:
      - gate_name: string
      - test_command: string
      - result: PASS | FAIL
  - summary:
      total: 9
      passed: int
      failed: int
```

---

## 硬约束

1. 必须列出 9 个 Gate 清单
2. 必须标记每个 Gate 的运行状态
3. 不得修改现有 Gate 实现代码

---

## 红线 (Deny List)

- [ ] 不得修改 `skillforge/src/skills/gates/*.py`
- [ ] 不得引入新依赖

---

## 质量门禁

### 自动检查

```powershell
pwsh -File ci/check_skill_structure.ps1
# 预期: PASS
```

### 人工检查

- [ ] 9 个 Gate 清单完整
- [ ] 8/9 Gate 状态为 PASS
- [ ] 报告格式符合 Schema

---

## 回传格式

```yaml
task_id: "T-A1"
executor: "vs--cc1"
status: "完成 | 部分完成 | 阻塞"

deliverables:
  - path: "docs/2026-02-19/L3_A1_gate_verification_report.md"
    action: "新建"
    lines_changed: int

gate_self_check:
  - command: "pwsh -File ci/check_skill_structure.ps1"
    result: "PASS | FAIL"

evidence_ref: "EV-L3-A1-xxx"

notes: "特殊情况说明"
```

---

## 验收标准

- [ ] 9 个 Gate 清单列出
- [ ] 8/9 Gate 运行状态验证
- [ ] 报告文件创建
- [ ] Gate Self Check 通过

---

*任务生成时间: 2026-02-19*

4.任务 T-B1/B2 已完成
交付物
文件	状态
audit_intent_contract_v1.yml	✅ 新建
generate_intent_contract_v1.yml	✅ 新建
upgrade_intent_contract_v1.yml	✅ 新建
tombstone_intent_contract_v1.yml	✅ 新建
L3_B2_contract_validation_report.md	✅ 新建
校验结果
YAML 格式校验: 4/4 PASS
9 字段标准: 4/4 PASS
总体状态: ✅ 完成
每个合同都包含完整的 9 字段标准：

intent_id - 意图ID
intent_type - 意图类型
input_schema - 输入 Schema
output_schema - 输出 Schema
error_codes - 错误码映射
fail_closed_rules - Fail-Closed 规则
evidence_fields - Evidence 字段
version - 版本
frozen_at - 冻结时间