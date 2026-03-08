# T-B1/B2: 核心 Intents 合同冻结与校验

> **执行者**: vs--cc2
> **波次**: Batch-A
> **优先级**: P0
> **预计时间**: 90 分钟

---

## 任务目标

1. **T-B1**: 冻结 4 个核心 intents 合同（audit/generate/upgrade/tombstone）
2. **T-B2**: 验证合同 9 字段标准全部通过校验

---

## 输入合同

### 需要阅读的文件

| 文件 | 用途 |
|------|------|
| `docs/2026-02-18/contracts/permit_contract_v1.yml` | 理解合同格式 |
| `docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts/` | 检查现有契约 |

### 贯穿常量

```yaml
core_intents:
  - audit
  - generate
  - upgrade
  - tombstone
version: "v1"
```

---

## 输出合同

### 交付物 (T-B1)

| 文件路径 | 类型 | 说明 |
|----------|------|------|
| `docs/2026-02-19/contracts/audit_intent_contract_v1.yml` | 新建 | audit 合同 |
| `docs/2026-02-19/contracts/generate_intent_contract_v1.yml` | 新建 | generate 合同 |
| `docs/2026-02-19/contracts/upgrade_intent_contract_v1.yml` | 新建 | upgrade 合同 |
| `docs/2026-02-19/contracts/tombstone_intent_contract_v1.yml` | 新建 | tombstone 合同 |

### 交付物 (T-B2)

| 文件路径 | 类型 | 说明 |
|----------|------|------|
| `docs/2026-02-19/L3_B2_contract_validation_report.md` | 新建 | 合同校验报告 |

### 合同 9 字段标准

```yaml
contract_schema:
  required_fields:
    - intent_id          # 意图ID
    - intent_type         # 意图类型
    - input_schema        # 输入 Schema
    - output_schema       # 输出 Schema
    - error_codes         # 错误码映射
    - fail_closed_rules   # Fail-Closed 规则
    - evidence_fields     # Evidence 字段
    - version             # 版本
    - frozen_at           # 冻结时间
```

---

## 硬约束

1. 合同必须包含 9 字段
2. 合同必须通过 YAML 格式校验
3. 不得修改已有合同的核心字段

---

## 红线 (Deny List)

- [ ] 不得修改 `docs/2026-02-18/contracts/` 中的已有文件
- [ ] 不得引入新依赖

---

## 质量门禁

### 自动检查

```powershell
# YAML 格式校验
python -c "import yaml; yaml.safe_load(open('docs/2026-02-19/contracts/audit_intent_contract_v1.yml'))"
# 预期: 无错误
```

### 人工检查

- [ ] 4 个合同文件创建
- [ ] 每个合同包含 9 字段
- [ ] YAML 格式正确
- [ ] 合同校验报告完整

---

## 回传格式

```yaml
task_id: "T-B1/B2"
executor: "vs--cc2"
status: "完成 | 部分完成 | 阻塞"

deliverables:
  - path: "docs/2026-02-19/contracts/audit_intent_contract_v1.yml"
    action: "新建"
  - path: "docs/2026-02-19/contracts/generate_intent_contract_v1.yml"
    action: "新建"
  - path: "docs/2026-02-19/contracts/upgrade_intent_contract_v1.yml"
    action: "新建"
  - path: "docs/2026-02-19/contracts/tombstone_intent_contract_v1.yml"
    action: "新建"
  - path: "docs/2026-02-19/L3_B2_contract_validation_report.md"
    action: "新建"

gate_self_check:
  - command: "python -c \"import yaml; [yaml.safe_load(open(f'docs/2026-02-19/contracts/{c}_intent_contract_v1.yml')) for c in ['audit','generate','upgrade','tombstone']]\""
    result: "4/4 PASS"

evidence_ref: "EV-L3-B1-B2-xxx"

notes: "特殊情况说明"
```

---

## 验收标准

- [ ] 4 个合同文件创建
- [ ] 每个合同 9 字段完整
- [ ] YAML 格式校验通过
- [ ] 校验报告创建

---

*任务生成时间: 2026-02-19*
