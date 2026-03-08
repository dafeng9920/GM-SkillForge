# T73 - Policy SHA256 锁定

## 任务元数据
```yaml
task_id: "T73"
executor: "vs--cc1"
reviewer: "Antigravity-2"
compliance_officer: "Kior-C"
wave: "Wave A"
depends_on: []
estimated_minutes: 30
```

## 输入

### 任务描述
落实 `policy_sha256` 锁定机制，确保审计策略文件 `configs/audit_policy_v1.json` 的哈希值被固化到冻结索引中，并在门控验证阶段进行校验。

### 上下文文件
| 路径 | 用途 |
|------|------|
| `configs/audit_policy_v1.json` | 需要锁定的审计策略文件 |
| `docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md` | A Guard 规范 |
| `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md` | B Guard 规范 |
| `docs/2026-02-22/P2_HARDENING_TODO.md` | P2 加固任务列表 |

### 常量
```yaml
job_id: "L4-P2-HARDENING-20260222-073"
scope: "P2-04"
policy_file: "configs/audit_policy_v1.json"
policy_sha256: "5f7b3189d40a4398094ae9a297add3c26bce4c7ac9a2c086c3550d4839985e60"
policy_version: "v1.0.0-20260222"
```

## 输出

### 交付物
| 路径 | 类型 | 描述 |
|------|------|------|
| `docs/2026-02-22/tasks/T73_vs--cc1.md` | 新建 | 任务定义 |
| `docs/2026-02-22/verification/T73_execution_report.yaml` | 新建 | 执行报告 |
| `docs/2026-02-22/verification/T73_gate_decision.json` | 新建 | 门禁决策 (A/B Guard) |
| `docs/2026-02-22/verification/T73_compliance_attestation.json` | 新建 | 合规证明 |
| `docs/2026-02-22/verification/policy_lock_report.json` | 新建 | 策略锁定报告 |

## 约束

### 必须满足
- [x] 计算 `configs/audit_policy_v1.json` 的 SHA256 哈希值
- [x] 创建冻结索引，将策略哈希固化
- [x] 验证哈希值可被门控系统校验
- [x] 形成 A/B Guard 结构的证据链

### 禁止行为
- [ ] 不得修改已锁定的策略文件内容
- [ ] 不得使用非确定性或时间相关的哈希算法

## A Guard 结构

### PreflightChecklist
```yaml
- check_id: "PC-001"
  description: "策略文件存在性检查"
  target: "configs/audit_policy_v1.json"
  expected: "FILE_EXISTS"
  status: "PASS"

- check_id: "PC-002"
  description: "策略文件格式校验"
  target: "configs/audit_policy_v1.json"
  expected: "VALID_JSON"
  status: "PASS"

- check_id: "PC-003"
  description: "策略版本字段存在"
  target: "configs/audit_policy_v1.json#policy_version"
  expected: "FIELD_EXISTS"
  status: "PASS"
```

### ExecutionContract
```json
{
  "contract_version": "v1",
  "intent_id": "T73-policy-sha256-lock",
  "ruleset_revision": "v1.0.0-20260222",
  "constitution_ref": "docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md",
  "inputs": {
    "policy_file": "configs/audit_policy_v1.json"
  },
  "outputs": {
    "policy_lock_report": "docs/2026-02-22/verification/policy_lock_report.json",
    "frozen_hash": "sha256:5f7b3189d40a4398094ae9a297add3c26bce4c7ac9a2c086c3550d4839985e60"
  },
  "controls": {
    "timeout_ms": 60000,
    "max_targets": 1,
    "network_policy": "DENY_BY_DEFAULT",
    "file_policy": "READONLY"
  },
  "side_effects": [],
  "roles": {
    "execution": {
      "responsibilities": ["计算策略哈希", "创建锁定报告", "固化冻结索引"],
      "allowed_actions": ["READ_FILE", "COMPUTE_HASH", "WRITE_REPORT"]
    },
    "review": {
      "responsibilities": ["验证哈希正确性", "确认锁定机制有效"],
      "checks": ["HASH_VERIFICATION", "LOCK_INTEGRITY"]
    },
    "compliance": {
      "responsibilities": ["合规复查", "签发合规证明"],
      "must_follow": "docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md"
    }
  },
  "acceptance_tests": [
    {
      "id": "AT-001",
      "assertion": "策略文件 SHA256 哈希值已计算并记录",
      "evidence_required": ["EV_KIND:FILE:policy_lock_report.json"]
    },
    {
      "id": "AT-002",
      "assertion": "冻结索引包含策略哈希条目",
      "evidence_required": ["EV_KIND:FILE:policy_lock_report.json#frozen_policies"]
    },
    {
      "id": "AT-003",
      "assertion": "门控验证逻辑可校验策略哈希",
      "evidence_required": ["EV_KIND:FILE:policy_lock_report.json#verification"]
    }
  ],
  "artifacts_expected": ["POLICY_LOCK_REPORT", "EVIDENCE"],
  "evidence_requirements": [
    {
      "for_acceptance_id": "AT-001",
      "evidence_kind": "FILE",
      "locator_hint": "docs/2026-02-22/verification/policy_lock_report.json"
    },
    {
      "for_acceptance_id": "AT-002",
      "evidence_kind": "FILE",
      "locator_hint": "docs/2026-02-22/verification/policy_lock_report.json#frozen_policies"
    },
    {
      "for_acceptance_id": "AT-003",
      "evidence_kind": "FILE",
      "locator_hint": "docs/2026-02-22/verification/policy_lock_report.json#verification"
    }
  ]
}
```

### RequiredChanges
```yaml
# 无需更改 - 所有前置条件已满足
status: "NONE"
```

## B Guard 结构

### Decision
```json
{
  "task_id": "T73",
  "decision": "ALLOW",
  "confidence": "HIGH"
}
```

### Violations
```yaml
violations: []
```

### Evidence Ref
```yaml
evidence_refs:
  - id: "EV-T73-001"
    kind: "FILE"
    locator: "configs/audit_policy_v1.json"
    sha256: "5f7b3189d40a4398094ae9a297add3c26bce4c7ac9a2c086c3550d4839985e60"
    description: "原始策略文件"

  - id: "EV-T73-002"
    kind: "FILE"
    locator: "docs/2026-02-22/verification/policy_lock_report.json"
    description: "策略锁定报告"

  - id: "EV-T73-003"
    kind: "LOG"
    locator: "sha256sum command output"
    description: "哈希计算命令输出"
```

## 门禁

### 自动检查
| 命令 | 预期结果 |
|------|----------|
| `sha256sum configs/audit_policy_v1.json` | 输出匹配冻结哈希 |
| `jq '.frozen_policies[0].sha256' docs/2026-02-22/verification/policy_lock_report.json` | 哈希值存在 |

### 手动检查
- [x] policy_lock_report.json 包含有效的冻结索引
- [x] 哈希值与实际文件匹配
- [x] 锁定时间戳正确记录

## 合规

```yaml
required: true
attestation_path: "docs/2026-02-22/verification/T73_compliance_attestation.json"
permit_required_for_side_effects: false
```

## 执行步骤

### Phase 1: 前置校验
1. 验证策略文件存在
2. 验证 JSON 格式有效
3. 验证版本字段存在

### Phase 2: 哈希计算
1. 使用 SHA256 算法计算文件哈希
2. 记录计算命令和输出
3. 形成证据引用

### Phase 3: 冻结索引创建
1. 构建冻结索引结构
2. 记录策略元数据
3. 记录锁定时间戳

### Phase 4: 验证与报告
1. 验证哈希可重现
2. 生成 policy_lock_report.json
3. 形成合规证明
