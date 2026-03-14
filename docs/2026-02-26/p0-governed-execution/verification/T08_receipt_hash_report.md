# T08 Receipt Hash Report

**任务**: ISSUE-07 - 审计回执哈希修正
**执行人**: vs--cc3
**执行日期**: 2026-02-26

---

## 1. 任务目标

移除 `Python hash()`，统一使用 `SHA-256(canonical_payload)` 生成审计回执哈希。

## 2. 验收标准

| # | 标准 | 状态 |
|---|------|------|
| 1 | receipt hash = SHA-256(canonical payload) | ✅ PASS |
| 2 | 去除 Python hash() | ✅ PASS |
| 3 | 提供一致性测试结果 | ✅ PASS |
| 4 | EvidenceRef 完整 | ✅ PASS |

---

## 3. 实现内容

### 3.1 新增模块: `receipt_hash.py`

**位置**: `skillforge-spec-pack/skillforge/src/utils/receipt_hash.py`

**导出内容**:
- `EvidenceRef` - 证据引用数据类
- `ReceiptPayload` - 回执载荷数据类
- `compute_receipt_hash()` - 计算 SHA-256(canonical payload)
- `compute_receipt_hash_from_dict()` - 从字典计算哈希
- `verify_receipt_consistency()` - 验证哈希一致性
- `create_evidence_ref()` - 创建证据引用
- `create_receipt_payload()` - 创建回执载荷

### 3.2 核心函数: `compute_receipt_hash()`

```python
def compute_receipt_hash(payload: ReceiptPayload) -> str:
    """Compute SHA-256 hash of canonical receipt payload."""
    return canonical_json_hash(payload.to_dict())
```

**依赖**:
- `canonical_json_hash()` - 来自 `canonical_json.py`
- 使用 `hashlib.sha256` 确保跨环境一致性

### 3.3 EvidenceRef 数据结构

```python
@dataclass
class EvidenceRef:
    envelope_id: str           # 证据包唯一标识
    envelope_hash: str         # SHA-256 哈希
    storage_location: str      # 存储 URI/Path
    received_at: str           # ISO-8601 时间戳
    verified: bool = False     # 签名验证状态
    evidence_type: str = "evidence_envelope.v1"
    node_id: Optional[str] = None
```

---

## 4. 测试结果

### 4.1 测试文件

**位置**: `skillforge-spec-pack/skillforge/tests/test_receipt_hash.py`

### 4.2 测试执行

```bash
cd skillforge-spec-pack
python -m pytest skillforge/tests/test_receipt_hash.py -v
```

### 4.3 测试覆盖

| 测试类 | 测试数量 | 状态 |
|--------|----------|------|
| TestEvidenceRef | 2 | ✅ PASS |
| TestReceiptPayload | 2 | ✅ PASS |
| TestComputeReceiptHash | 5 | ✅ PASS |
| TestVerifyReceiptConsistency | 3 | ✅ PASS |
| TestConvenienceFunctions | 2 | ✅ PASS |
| TestIntegrationEvidenceRefComplete | 3 | ✅ PASS |

**总计**: 17/17 通过

### 4.4 关键测试验证

#### 哈希长度验证
```python
def test_hash_length_is_64(self):
    """SHA-256 产生 64 位十六进制字符"""
    hash_val = compute_receipt_hash(payload)
    assert len(hash_val) == 64
```

#### 一致性验证 (100次迭代)
```python
def test_consistent_payload(self):
    result = verify_receipt_consistency(payload, iterations=100)
    assert result["consistent"] is True
    assert result["unique_hashes"] == 1
```

#### EvidenceRef 完整性
```python
def test_evidence_ref_all_fields(self):
    ref = EvidenceRef(
        envelope_id="ev-test-001",
        envelope_hash="abcd1234" * 8,
        storage_location="file:///data/ev/test-001.json",
        received_at="2026-02-26T15:30:00Z",
        verified=True,
        evidence_type="evidence_envelope.v1",
        node_id="skillforge-node-01",
    )
    # 所有字段验证通过
```

---

## 5. 技术验证

### 5.1 无 Python hash() 使用

搜索结果确认：
- ❌ 代码库中未发现使用 Python 内置 `hash()` 函数
- ✅ 所有哈希操作使用 `hashlib.sha256`

### 5.2 Canonical JSON 序列化

`receipt_hash.py` 依赖的 `canonical_json.py` 提供：
- 键排序确定性
- 跨平台一致序列化
- SHA-256 哈希输出

### 5.3 跨环境一致性

测试验证了以下场景的一致性：
- 不同迭代次数 (10, 50, 100, 200, 500)
- 不同载荷复杂度
- 多个 EvidenceRef

**结果**: 所有测试显示 `unique_hashes == 1`

---

## 6. 集成状态

### 6.1 模块导出

`skillforge/src/utils/__init__.py` 已更新：

```python
from .receipt_hash import (
    EvidenceRef,
    ReceiptPayload,
    compute_receipt_hash,
    compute_receipt_hash_from_dict,
    verify_receipt_consistency,
    create_evidence_ref,
    create_receipt_payload,
)

__all__ += [
    "EvidenceRef",
    "ReceiptPayload",
    "compute_receipt_hash",
    "compute_receipt_hash_from_dict",
    "verify_receipt_consistency",
    "create_evidence_ref",
    "create_receipt_payload",
]
```

### 6.2 使用示例

```python
from skillforge.src.utils import (
    create_evidence_ref,
    create_receipt_payload,
    compute_receipt_hash,
    verify_receipt_consistency,
)

# 创建证据引用
evidence = create_evidence_ref(
    envelope_id="ev-001",
    envelope_hash="abcd" * 16,
    storage_location="/storage/ev-001.json",
    received_at="2026-02-26T12:00:00Z",
    verified=True,
)

# 创建回执载荷
payload = create_receipt_payload(
    audit_id="audit-001",
    job_id="job-001",
    created_at="2026-02-26T12:00:00Z",
    node_id="node-001",
    decision="PASSED",
    evidence_refs=[evidence],
)

# 计算哈希
receipt_hash = compute_receipt_hash(payload)
assert len(receipt_hash) == 64  # SHA-256

# 验证一致性
result = verify_receipt_consistency(payload, iterations=100)
assert result["consistent"] is True
```

---

## 7. 结论

**T08 (ISSUE-07): 审计回执哈希修正 - ✅ 完成**

所有验收标准已满足：
1. ✅ Receipt hash 使用 SHA-256(canonical payload)
2. ✅ 已去除 Python hash()
3. ✅ 提供一致性测试结果 (17/17 通过)
4. ✅ EvidenceRef 数据结构完整

**交付物**:
- [x] `skillforge/src/utils/receipt_hash.py` - Receipt hash 生成器
- [x] `skillforge/tests/test_receipt_hash.py` - 一致性测试套件
- [x] `docs/2026-02-26/p0-governed-execution/verification/T08_receipt_hash_report.md` - 本报告
- [x] `docs/2026-02-26/p0-governed-execution/verification/T08_execution_report.yaml` - 执行报告

---

## 附录: 文件清单

| 文件 | 类型 | 位置 |
|------|------|------|
| receipt_hash.py | 源代码 | skillforge/src/utils/receipt_hash.py |
| test_receipt_hash.py | 测试 | skillforge/tests/test_receipt_hash.py |
| __init__.py | 更新 | skillforge/src/utils/__init__.py |
| T08_receipt_hash_report.md | 报告 | docs/2026-02-26/p0-governed-execution/verification/ |
| T08_execution_report.yaml | 报告 | docs/2026-02-26/p0-governed-execution/verification/ |
