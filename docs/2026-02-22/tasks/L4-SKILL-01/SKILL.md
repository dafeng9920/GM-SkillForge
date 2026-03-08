# Guard Signature Verify Skill (L4-SKILL-01)

## Metadata
- **task_id**: L4-SKILL-01
- **skill_name**: guard-signature-verify-skill
- **execution**: Antigravity-1
- **review**: vs--cc2
- **compliance**: Kior-C
- **created_at**: 2026-02-22T09:00:00Z
- **version**: v1.0

## Purpose
此技能提供 Guard 签名验证能力，用于验证执行报告、门控决策和合规证明文件的完整性和真实性。

## Inputs
| 文件 | 类型 | 描述 |
|------|------|------|
| T70_execution_report.yaml | YAML | 执行报告样例 |
| T70_gate_decision.json | JSON | 门控决策样例 |
| T70_compliance_attestation.json | JSON | 合规证明样例 |
| EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md | Markdown | A Guard 提案约束技能 |
| EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md | Markdown | B Guard 执行约束技能 |

## Outputs
| 文件 | 类型 | 描述 |
|------|------|------|
| verify_guard_signature.py | Python | 签名验证脚本 |
| L4-SKILL-01_execution_report.yaml | YAML | 执行报告 |
| L4-SKILL-01_gate_decision.json | JSON | 门控决策 |
| L4-SKILL-01_compliance_attestation.json | JSON | 合规证明 |

## Core Functionality

### 1. 签名算法
- **Algorithm**: HMAC-SHA256
- **Key Source**: 环境变量 `GUARD_SIGNATURE_KEY` 或默认开发密钥
- **Signature Field**: `guard_signature`

### 2. 支持的文件类型
- YAML 文件 (`*_execution_report.yaml`, `*_compliance_attestation.yaml`)
- JSON 文件 (`*_gate_decision.json`, `*_compliance_attestation.json`)

### 3. 验证模式
```bash
# 批量验证
python scripts/verify_guard_signature.py --verify-all --report <report_path>

# 单文件验证
python scripts/verify_guard_signature.py --file <file_path> --verify

# 签名文件
python scripts/verify_guard_signature.py --sign <file_path>
```

## Verification Steps

### Preflight Checklist
- [x] 依赖 T70 已完成
- [x] verify_guard_signature.py 脚本存在
- [x] 脚本可独立执行
- [x] HMAC-SHA256 算法实现正确

### Gate Rule Verification
- **PASS Condition**: 对真实文件验签成功
- **FAIL Condition**: 对篡改样例验签失败

## API Reference

### Functions

#### `compute_signature(content: str, key: bytes) -> str`
计算内容的 HMAC-SHA256 签名。

#### `verify_yaml_signature(file_path: Path, key: bytes) -> Tuple[bool, str, Optional[str]]`
验证 YAML 文件签名。
- Returns: `(is_valid, message, existing_signature)`

#### `verify_json_signature(file_path: Path, key: bytes) -> Tuple[bool, str, Optional[str]]`
验证 JSON 文件签名。
- Returns: `(is_valid, message, existing_signature)`

#### `sign_yaml_file(file_path: Path, key: bytes) -> bool`
为 YAML 文件添加签名。

#### `sign_json_file(file_path: Path, key: bytes) -> bool`
为 JSON 文件添加签名。

## Exit Codes
| Code | Description |
|------|-------------|
| 0 | 所有签名有效 |
| 1 | 存在无效签名 |
| 2 | 执行错误 |

## Constraints
1. 签名算法必须使用 SHA256 + HMAC
2. 必须验证所有已存在的 execution_report.yaml 文件
3. 必须验证所有已存在的 gate_decision.json 文件
4. 输出报告必须包含通过率和失败详情

## Deny Rules
- 不得省略签名验证失败的处理逻辑
- 不得在签名无效时返回成功状态

## Evidence Requirements
- 脚本必须可独立执行
- 必须支持批量验证
- 必须支持报告生成
- 所有函数必须包含错误处理

## References
- [EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md](../../EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md)
- [EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md](../../EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md)
- [verify_guard_signature.py](../../../scripts/verify_guard_signature.py)
