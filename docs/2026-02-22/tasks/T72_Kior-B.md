# T72 - Rollback 演练与证据形成

## 任务元数据
```yaml
task_id: "T72"
executor: "Kior-B"
reviewer: "vs--cc3"
compliance_officer: "Kior-C"
wave: "Wave 2"
depends_on: ["T60", "T61"]
estimated_minutes: 45
```

## 输入

### 任务描述
执行 rollback 演练并形成证据，验证系统在异常情况下能够安全回滚到稳定状态。

### 上下文文件
| 路径 | 用途 |
|------|------|
| `ui/app/src/pages/audit/SkillAuditPage.tsx` | 回滚目标文件 |
| `schemas/skill_audit_report.schema.json` | 回滚目标文件 |
| `reports/skill-audit/*.json` | 数据完整性验证 |

### 常量
```yaml
job_id: "L4-P1-FOUNDATION-20260222-002"
scope: "P1-2"
rollback_scope: "T61 deliverables"
```

## 输出

### 交付物
| 路径 | 类型 | 描述 |
|------|------|------|
| `docs/2026-02-22/tasks/T72_Kior-B.md` | 新建 | 任务定义 |
| `docs/2026-02-22/verification/T72_execution_report.yaml` | 新建 | 执行报告 |
| `docs/2026-02-22/verification/T72_gate_decision.json` | 新建 | 门禁决策 (A/B Guard) |
| `docs/2026-02-22/verification/T72_compliance_attestation.json` | 新建 | 合规证明 |
| `docs/2026-02-22/verification/rollback_drill.md` | 新建 | 演练文档 |
| `docs/2026-02-22/verification/rollback_tombstone.json` | 新建 | 墓碑文件 |

## 约束

### 必须满足
- [ ] 记录当前系统状态快照
- [ ] 模拟故障场景并执行回滚
- [ ] 验证回滚后系统可正常运行
- [ ] 形成 A/B Guard 结构的证据链

### 禁止行为
- [ ] 不得在生产数据上执行实际回滚
- [ ] 不得破坏已验证的交付物

## 门禁

### 自动检查
| 命令 | 预期结果 |
|------|----------|
| `git status --porcelain` | 干净工作区或仅有新增文档 |
| 文件存在性检查 | 所有交付物存在 |

### 手动检查
- [ ] rollback_tombstone.json 包含有效的时间戳和状态
- [ ] rollback_drill.md 包含完整的演练步骤和结果

## 合规

```yaml
required: true
attestation_path: "docs/2026-02-22/verification/T72_compliance_attestation.json"
permit_required_for_side_effects: false
```

## 演练计划

### Phase 1: 状态快照
1. 记录 T61 交付物的 SHA256
2. 记录当前 git 状态
3. 记录系统可用的审计数据

### Phase 2: 故障模拟
1. 定义故障场景 (schema 不兼容、数据损坏)
2. 模拟故障状态
3. 触发回滚流程

### Phase 3: 回滚验证
1. 验证文件恢复到已知良好状态
2. 运行构建验证
3. 验证数据完整性

### Phase 4: 证据形成
1. 生成 tombstone 文件
2. 记录演练结果
3. 形成合规证明
