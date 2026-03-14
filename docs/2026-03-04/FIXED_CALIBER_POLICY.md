# Fixed-Caliber Binding Policy

**执行环境**: LOCAL-ANTIGRAVITY
**Policy Version**: 1.0.0
**Effective Date**: 2026-03-04

---

## 默认口径 (Active Caliber)

```
Caliber ID: AG2-FIXED-CALIBER-TG1-20260304
Status: ACTIVE
```

### 配置

| 属性 | 值 |
|------|-----|
| **Permit** | permits/default/tg1_baseline_permit.json |
| **Permit ID** | PERMIT-TG1-BASELINE-20260304-RESIGNED |
| **Revision** | tg1_baseline_rev_002 |
| **配置文件** | orchestration/fixed_caliber_binding.yml |

### 三权绑定

| 文件 | 路径 | 哈希 |
|------|------|------|
| Demand | .tmp/pr1_smoke/demand.json | 0aadae06454b317fbefc9c997e63336128752993552909090ead5ccfd8039429 |
| Contract | .tmp/pr1_smoke/contract.json | cf9436bed520a4d6edd0e084ab3da4df1b3cf7a6c540a571daf8503a20465f8a |
| Decision | .tmp/pr1_smoke/decision.json | 80bbb0b07dc13e01e32a93f8c405686f0f011bae172749b8a3e39db3f7d51e2a |
| Manifest | .tmp/pr1_smoke/MANIFEST.json | v0 |

---

## 后续任务策略

### ✅ 默认行为：复用当前口径

**所有后续任务默认使用 AG2-FIXED-CALIBER-TG1-20260304**

无需额外配置，直接使用：
- Permit: `permits/default/tg1_baseline_permit.json`
- 三权文件: `.tmp/pr1_smoke/{demand,contract,decision,manifest}.json`
- 配置: `orchestration/fixed_caliber_binding.yml`

### 🔄 变更口径流程

如果需要更换口径，必须按顺序执行：

#### Step 1: 更新 fixed_caliber_binding.yml

```yaml
# 修改以下字段:
caliber_id: "NEW-CALIBER-ID"
caliber_status: "ACTIVE"

fixed_binding:
  permit:
    path: "path/to/new/permit.json"
    permit_id: "NEW-PERMIT-ID"
    revision: "NEW-REVISION"

  three_rights:
    demand:
      path: "path/to/new/demand.json"
      hash: "NEW-DEMAND-HASH"
    # ... 更新其他三权文件
```

#### Step 2: 重新生成 Permit

使用 Antigravity-2 Guard 重新签发 Permit：

```bash
python scripts/antigravity_2_guard.py \
  --permit permits/default/new_permit.json \
  --demand path/to/new/demand.json \
  --contract path/to/new/contract.json \
  --decision path/to/new/decision.json \
  --manifest path/to/new/MANIFEST.json \
  --output guard_decision.json
```

#### Step 3: 验证新口径

确保新 Permit 通过所有检查：
- Permit 绑定: ✅ PASS
- 固定口径绑定: ✅ PASS
- Permit 哈希一致性: ✅ PASS
- 交付完整性: ✅ PASS
- 三哈希守卫: ✅ PASS

#### Step 4: 归档

将新口径的验证结果归档到对应日期的 verification 目录。

---

## 禁止事项

❌ **禁止以下操作**：

1. 禁止回退到 `PERMIT-TG1-BASELINE-20260304` (rev_001)
2. 禁止使用其他来源的 demand/contract/decision 文件
3. 禁止手动修改 Permit 中的哈希值
4. 禁止绕过 Antigravity-2 Guard 的固定口径校验
5. 禁止在未更新 fixed_caliber_binding.yml 的情况下更换口径

---

## 合规证据

### Final Gate 决策

- **文件**: docs/2026-03-04/verification/Antigravity-1_Final_Gate_Decision_ALLOW.json
- **决策**: ✅ ALLOW
- **时间**: 2026-03-04T15:10:20Z

### AG2 验证

- **文件**: docs/2026-03-04/AG2_fixed_caliber_final.json
- **决策**: ✅ ALLOW
- **时间**: 2026-03-04T14:53:31Z

### 验证索引

- **文件**: docs/2026-03-04/verification/verification_index_2026-03-04.json
- **归档时间**: 2026-03-04T15:10:25Z

---

## FAIL_CLOSED 守门链

| 守门 | 状态 | 环境 |
|------|------|------|
| Antigravity-1 | ✅ ACTIVE | LOCAL-ANTIGRAVITY |
| Antigravity-2 | ✅ ACTIVE | LOCAL-ANTIGRAVITY |
| Antigravity-3 | ✅ ACTIVE | CLOUD-ROOT |

**策略**: 任何检查失败 = DENY + 阻断

---

## 执行环境确认

**当前环境**: LOCAL-ANTIGRAVITY
**固定口径**: AG2-FIXED-CALIBER-TG1-20260304
**状态**: ✅ ACTIVE

---

## 总结

```
┌─────────────────────────────────────────────────────────────┐
│  Fixed-Caliber Policy                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  默认口径: AG2-FIXED-CALIBER-TG1-20260304                 │
│  状态: ACTIVE                                               │
│                                                             │
│  后续任务 → 自动复用该口径                                  │
│                                                             │
│  变更口径 → 更新 binding + 重签 Permit + 验证 + 归档       │
│                                                             │
│  禁止 → 绕过守门链、手动修改哈希、混用文件                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
