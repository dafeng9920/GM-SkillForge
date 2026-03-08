# Rollback Drill Skill v1.0

---
skill_id: "rollback-drill-skill"
skill_version: "1.0.0"
skill_level: 4
created_by: "L4-SKILL-03_Kior-B"
created_at: "2026-02-22"
---

## 1. Skill 概述

Rollback Drill Skill 是一个 L4 级别的运维安全技能，用于执行系统回滚演练，验证系统在故障场景下的恢复能力。

### 1.1 核心能力
- **状态快照**: 捕获演练前的系统状态指纹
- **故障模拟**: 在隔离环境中模拟各类故障场景
- **回滚执行**: 执行回滚操作并验证恢复效果
- **证据形成**: 生成完整的 tombstone 记录和合规证明

### 1.2 Gate 规则
```
通过条件 = 回滚与恢复都可复现且有前后状态证据
任一步失败 = DENY
```

---

## 2. ExecutionContract

### 2.1 输入
```yaml
inputs:
  target_scope:
    type: "object"
    required: true
    description: "演练目标范围（文件/目录/服务）"

  drill_type:
    type: "string"
    enum: ["DATA_CORRUPTION", "SCHEMA_INCOMPATIBLE", "CODE_BUG", "FULL_ROLLBACK"]
    required: true

  backup_location:
    type: "string"
    required: true
    description: "备份存储路径"

  guard_refs:
    type: "array"
    items:
      - "docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md"
      - "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
```

### 2.2 输出
```yaml
outputs:
  artifacts:
    - path: "rollback_drill.md"
      type: "演练文档"
    - path: "rollback_tombstone.json"
      type: "回滚墓碑记录"
    - path: "{task_id}_execution_report.yaml"
      type: "执行报告"
    - path: "{task_id}_gate_decision.json"
      type: "门禁决策"
    - path: "{task_id}_compliance_attestation.json"
      type: "合规证明"
```

### 2.3 Controls
```yaml
controls:
  timeout_ms: 300000        # 5 分钟超时
  max_targets: 10           # 最多 10 个目标文件
  network_policy: "DENY_BY_DEFAULT"
  file_policy: "ALLOWLIST"  # 仅允许备份目录读写
  simulation_mode: true     # 默认模拟模式，不实际破坏生产
```

### 2.4 Side Effects
```yaml
side_effects:
  - kind: "FILE"
    details: "读取目标文件、写入备份文件"
  - kind: "FILE"
    details: "创建 .bak 备份文件"
```

### 2.5 Roles
```yaml
roles:
  execution:
    responsibilities:
      - "执行备份操作"
      - "执行故障模拟"
      - "执行回滚恢复"
      - "生成 tombstone 记录"
    allowed_actions:
      - "file_read"
      - "file_write_backup"
      - "file_verify_sha256"
    forbidden_actions:
      - "network_request"
      - "production_modify"
      - "delete_without_backup"

  review:
    responsibilities:
      - "检查演练范围是否合理"
      - "验证备份完整性"
      - "确认恢复证据链完整"
    checks:
      - "pre_state_snapshot_exists"
      - "post_state_matches_pre"
      - "tombstone_complete"

  compliance:
    responsibilities:
      - "验证无生产影响"
      - "验证备份保留完整"
      - "验证系统稳定性"
    must_follow: "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
```

---

## 3. 三角色协作流程

### Phase 1: Review（审查者 vs--cc3）
1. 检查 target_scope 是否在允许范围内
2. 验证 backup_location 可访问
3. 确认 drill_type 合法
4. **不放行**，仅输出审查意见

### Phase 2: Compliance（合规者 Kior-C）
1. 验证 simulation_mode = true（无生产影响）
2. 检查备份策略合规
3. 输出 ComplianceAttestation（PASS/FAIL）

### Phase 3: Execution（执行者 Kior-B）
1. 仅在 Compliance=PASS 时执行
2. 按步骤执行演练
3. 生成 EvidenceRef

---

## 4. 验收测试

```yaml
acceptance_tests:
  - id: "AT-001"
    assertion: "演练前状态快照完整"
    evidence_required:
      - "FILE: pre_drill_snapshot.json"
      - "SHA256: 所有目标文件指纹"

  - id: "AT-002"
    assertion: "故障模拟成功执行"
    evidence_required:
      - "LOG: 故障注入记录"
      - "FILE: corrupted_data_sample"

  - id: "AT-003"
    assertion: "回滚操作成功"
    evidence_required:
      - "LOG: 回滚执行日志"
      - "FILE: rollback_tombstone.json"

  - id: "AT-004"
    assertion: "恢复后状态与快照一致"
    evidence_required:
      - "SHA256: 恢复后文件指纹"
      - "DIFF: pre vs post comparison"

  - id: "AT-005"
    assertion: "无生产环境影响"
    evidence_required:
      - "LOG: simulation_mode=true 确认"
      - "FILE: compliance_attestation.json"
```

---

## 5. Evidence Requirements

```yaml
evidence_requirements:
  - for_acceptance_id: "AT-001"
    evidence_kind: "FILE"
    locator_hint: "rollback_tombstone.json.scope.files"

  - for_acceptance_id: "AT-002"
    evidence_kind: "LOG"
    locator_hint: "演练执行日志"

  - for_acceptance_id: "AT-003"
    evidence_kind: "FILE"
    locator_hint: "rollback_tombstone.json.simulation.steps_executed"

  - for_acceptance_id: "AT-004"
    evidence_kind: "DIFF"
    locator_hint: "SHA256 前后对比"

  - for_acceptance_id: "AT-005"
    evidence_kind: "FILE"
    locator_hint: "{task_id}_compliance_attestation.json"
```

---

## 6. 失败码

| 失败码 | 含义 | 处理 |
|--------|------|------|
| `SF_DRILL_BACKUP_FAILED` | 备份创建失败 | DENY, 检查磁盘空间 |
| `SF_DRILL_CORRUPT_FAILED` | 故障模拟失败 | DENY, 检查文件权限 |
| `SF_DRILL_ROLLBACK_FAILED` | 回滚执行失败 | DENY, 检查备份完整性 |
| `SF_DRILL_VERIFY_FAILED` | 恢复验证失败 | DENY, 文件指纹不匹配 |
| `SF_DRILL_PRODUCTION_IMPACT` | 检测到生产影响 | DENY, 立即停止 |

---

## 7. 使用示例

```bash
# 运行回滚演练
python run_rollback_drill.py \
  --scope "reports/skill-audit/*.json" \
  --drill-type "DATA_CORRUPTION" \
  --backup-dir ".drill-backups" \
  --simulation-mode \
  --output "docs/2026-02-22/verification/"

# 验证演练结果
python run_rollback_drill.py \
  --verify \
  --tombstone "docs/2026-02-22/verification/rollback_tombstone.json"
```

---

## 8. 依赖

- Python 3.8+
- hashlib (标准库)
- json (标准库)
- shutil (标准库)

---

## 9. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-02-22 | 初始版本，支持 DATA_CORRUPTION 场景 |
