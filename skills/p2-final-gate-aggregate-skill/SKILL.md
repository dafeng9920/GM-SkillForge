# p2-final-gate-aggregate-skill

## 元数据
- **skill_id**: L4-SKILL-06.1
- **skill_name**: p2-final-gate-aggregate-skill
- **version**: v1.2.0
- **created_at**: 2026-02-22
- **execution**: vs--cc2
- **review**: Codex
- **compliance**: Kior-C

## 1. 目的
聚合 T70-T79 所有任务的 gate_decision 和 compliance_attestation 文件，根据三权门禁规则产出最终的 P2 阶段门禁决策。

## 2. 三权门禁聚合规则

### 2.1 输入要求
每个任务必须具备完整的 triad 文件：
- `{task_id}_execution_report.yaml` - 执行报告
- `{task_id}_gate_decision.json` - 门禁决策
- `{task_id}_compliance_attestation.json` - 合规认证

### 2.2 聚合逻辑

#### 最终决策判定规则
```
FINAL_PASS 条件:
  - 所有任务的 gate_decision.decision == "ALLOW"
  - 所有任务的 compliance_attestation.decision == "PASS"
  - 所有 triad 文件完整存在

FINAL_FAIL 条件:
  - 任一任务的 gate_decision.decision == "DENY"
  - 任一任务的 compliance_attestation.decision == "FAIL"
  - 任一任务的 compliance_attestation.status == "FAIL"

REQUIRES_CHANGES 条件:
  - 缺失任一 triad 文件
  - triad 文件格式无效（无法解析）
  - 必要字段缺失（decision 字段）
```

#### 三权分立验证
- **Execution**: 执行者完成交付物
- **Review**: 审查者产出 gate_decision（decision: ALLOW/DENY）
- **Compliance**: 合规官产出 compliance_attestation（decision: PASS/FAIL）

### 2.3 证据聚合
- 收集所有任务的 evidence_refs
- 生成聚合证据索引
- 计算通过率和完整性指标

## 3. L4-SKILL-07 密码学签名门禁 (Fail-Closed)

### 3.1 功能说明
当启用 `--require-crypto-signature` 时，系统将执行严格的密码学签名验证：

- **缺失签名字段**: 返回 `REQUIRES_CHANGES`
- **验签失败**: 返回 `DENY`
- **signer_id 不在允许名单**: 返回 `DENY`
- **禁止仅时间戳即通过**: 必须有有效的 guard_signature

### 3.2 允许的 signer_id 列表
```
ALLOWED_SIGNER_IDS = {
    "Antigravity-1",   # Execution role
    "Antigravity-2",   # Review role
    "Kior-C",          # Compliance role
    "Codex",           # Orchestrator role
    "vs--cc2",         # Execution agent
    "vs--cc3"          # Execution agent
}
```

### 3.3 签名字段要求
- `guard_signature`: HMAC-SHA256 签名
- `signer_id`: 签名者身份标识

## 4. 输出文件

### 4.1 聚合脚本
- `aggregate_final_gate.py` - 执行聚合逻辑的 Python 脚本
- `scripts/verify_guard_signature.py` - 密码学签名验证脚本

### 4.2 输出产物
- `L4-SKILL-06.1_execution_report.yaml` - 本技能执行报告
- `L4-SKILL-06.1_gate_decision.json` - 聚合门禁决策
- `L4-SKILL-06.1_compliance_attestation.json` - 聚合合规认证

## 5. 使用方法

```bash
# 基本聚合
python skills/p2-final-gate-aggregate-skill/aggregate_final_gate.py \
  --verification-dir docs/2026-02-22/verification \
  --task-range T70-T79 \
  --output-dir docs/2026-02-22/verification

# 启用时间戳签名验证
python skills/p2-final-gate-aggregate-skill/aggregate_final_gate.py \
  --require-signatures \
  --verification-dir docs/2026-02-22/verification \
  --task-range T70-T79

# 启用密码学签名验证 (L4-SKILL-07 Fail-Closed)
python skills/p2-final-gate-aggregate-skill/aggregate_final_gate.py \
  --require-crypto-signature \
  --verification-dir docs/2026-02-22/verification \
  --task-range T70-T79

# 验证输出
python skills/p2-final-gate-aggregate-skill/aggregate_final_gate.py \
  --verify \
  --output-dir docs/2026-02-22/verification
```

## 6. 约束条件

### 6.1 必须满足 (MUST)
- 验证所有指定范围内的任务文件存在
- 解析 JSON/YAML 文件必须成功
- 聚合逻辑必须与三权门禁规则一致
- 缺失文件必须报告为 REQUIRES_CHANGES

### 6.2 禁止行为 (DENY)
- 不得跳过任何任务的验证
- 不得在文件缺失时伪造通过
- 不得忽略 DENY 或 FAIL 决策
- 不得绕过 triad 完整性检查
- 不得从非标准字段推导 PASS（保持 L4-SKILL-06.1 strict rules）

### 6.3 L4-SKILL-07 特定约束
- 启用 `--require-crypto-signature` 时，仅时间戳不足
- signer_id 必须在允许名单内
- guard_signature 验证失败必须 DENY

## 7. 依赖
- Python 3.8+
- PyYAML 库
- EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md（宪法参考）
- EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md（执行约束参考）
- scripts/verify_guard_signature.py（密码学签名验证）

## 8. 告警代码

| 代码 | 说明 |
|------|------|
| MISSING_DECISION_FIELD | compliance_attestation 缺少 decision 字段 |
| PENDING_SIGNATURES | reviewer/compliance 时间戳为空 |
| NON_PASS_COMPLIANCE | compliance decision 非 PASS/VERIFIED |
| MISSING_CRYPTO_SIGNATURE | guard_signature 字段缺失 |
| SIGNATURE_MISMATCH | 签名验证失败 |
| INVALID_SIGNER_ID | signer_id 不在允许名单 |
| MISSING_SIGNER_ID | signer_id 字段缺失 |

## 9. 版本历史
| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0.0 | 2026-02-22 | 初始版本，实现 T70-T79 聚合逻辑 |
| v1.1.0 | 2026-02-22 | 添加 --require-signatures 时间戳验证 |
| v1.2.0 | 2026-02-22 | L4-SKILL-07: 添加 --require-crypto-signature 密码学签名验证 (Fail-Closed) |
