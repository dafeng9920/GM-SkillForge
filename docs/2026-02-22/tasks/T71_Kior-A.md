# T71: evidence_sha256 交叉校验链实现

---
task_id: "T71"
executor: "Kior-A"
reviewer: "vs--cc1"
compliance_officer: "Kior-C"
wave: "Wave Evidence"
depends_on: []
estimated_minutes: 45
---

## 1. 任务目标

实现 `evidence_sha256` 交叉校验链，确保所有证据文件通过 SHA256 哈希值形成不可篡改的校验链。

## 2. A/B Guard 结构

### A Guard（提案约束）
- 所有证据文件必须生成 SHA256 哈希
- 哈希值必须写入校验链报告
- 校验链必须支持增量追加

### B Guard（执行约束）
- 无有效 SHA256 的证据不被接受
- 校验链断裂时执行阻断
- 哈希碰撞检测必须通过

## 3. 输入规格

```yaml
input:
  description: "实现证据 SHA256 交叉校验链"
  context_files:
    - path: "docs/multi-ai-collaboration.md"
      purpose: "理解三权分立流程"
  constants:
    chain_version: "1.0.0"
    hash_algorithm: "SHA256"
```

## 4. 输出交付物

```yaml
output:
  deliverables:
    - path: "scripts/verify_evidence_chain.py"
      type: "新建"
      purpose: "Python 校验脚本"
    - path: "docs/2026-02-22/verification/evidence_chain_report.json"
      type: "新建"
      purpose: "校验链报告"
    - path: "docs/2026-02-22/verification/T71_execution_report.yaml"
      type: "新建"
      purpose: "执行报告"
    - path: "docs/2026-02-22/verification/T71_gate_decision.json"
      type: "新建"
      purpose: "Gate 决策"
    - path: "docs/2026-02-22/verification/T71_compliance_attestation.json"
      type: "新建"
      purpose: "合规证明"
  constraints:
    - "校验脚本必须独立可运行"
    - "支持增量证据追加"
    - "输出 JSON 格式报告"
```

## 5. 禁止操作

```yaml
deny:
  - "不得修改已有 schema 文件"
  - "不得引入外部网络依赖"
  - "不得绕过 SHA256 校验"
```

## 6. Gate 检查

```yaml
gate:
  auto_checks:
    - command: "python scripts/verify_evidence_chain.py --validate"
      expect: "exit_code=0"
    - command: "python scripts/verify_evidence_chain.py --chain-integrity"
      expect: "CHAIN_VALID"
  manual_checks:
    - "校验链逻辑正确性审查"
    - "三权记录完整性检查"
```

## 7. 合规要求

```yaml
compliance:
  required: true
  attestation_path: "docs/2026-02-22/verification/T71_compliance_attestation.json"
  permit_required_for_side_effects: false
  evidence_sha256_required: true
```

## 8. 校验链设计

### 8.1 链式结构

```
[Genesis Block]
     |
     v
[Evidence 1] --SHA256--> [Chain Entry 1]
     |
     v
[Evidence 2] --SHA256--> [Chain Entry 2] --prev_hash--> [Chain Entry 1]
     |
     v
[... N Evidence Blocks ...]
```

### 8.2 校验规则

1. **完整性校验**: 每个链节点的 `prev_hash` 必须等于前一节点的 `hash`
2. **存在性校验**: 证据文件必须存在且 SHA256 匹配
3. **时序性校验**: `timestamp` 必须单调递增
4. **签名校验**: 链根必须有合规官签名

### 8.3 数据结构

```json
{
  "chain_id": "evidence-chain-001",
  "version": "1.0.0",
  "genesis": {
    "hash": "sha256:...",
    "created_at": "2026-02-22T00:00:00Z",
    "signed_by": "Kior-C"
  },
  "entries": [
    {
      "index": 1,
      "evidence_id": "EV-001",
      "evidence_path": "docs/2026-02-22/verification/T71_execution_report.yaml",
      "evidence_sha256": "sha256:abc123...",
      "chain_hash": "sha256:def456...",
      "prev_hash": "sha256:genesis...",
      "timestamp": "2026-02-22T10:00:00Z",
      "metadata": {
        "task_id": "T71",
        "executor": "Kior-A"
      }
    }
  ]
}
```

## 9. 脚本功能

`scripts/verify_evidence_chain.py` 提供:

1. `--init`: 初始化新校验链
2. `--add <file>`: 添加证据到链
3. `--validate`: 验证链完整性
4. `--chain-integrity`: 完整性+存在性双重校验
5. `--report`: 生成 JSON 报告
