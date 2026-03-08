# L4.5 Fetch Pack Production Implementation Report

> **版本**: v1.0
> **日期**: 2026-02-20
> **状态**: FROZEN
> **Task**: T8 (vs--cc1)
> **job_id**: L45-D2-ORCH-MINCAP-20260220-002
> **skill_id**: l45_orchestration_min_capabilities

---

## 1. 概述

本报告记录 n8n `fetch_pack` 从 mock 返回升级为真实 AuditPack/证据读取与一致性校验的实现。

### 1.1 目标

- 实现 `AuditPackStore` 存储读取接口
- 支持 `run_id` / `evidence_ref` 索引读取
- 实现一致性校验（同时提供时验证指向同一个 pack）
- Fail-closed 错误信封
- 返回体包含 `replay_pointer`（可空但字段存在）

---

## 2. 交付物

| # | 文件 | 类型 | 说明 |
|---|------|------|------|
| 1 | `skillforge/src/storage/audit_pack_store.py` | 新建 | AuditPack 存储读取接口 |
| 2 | `skillforge/src/api/routes/n8n_orchestration.py` | 修改 | fetch_pack 真实读取 + 一致性校验 |
| 3 | `skillforge/tests/test_n8n_fetch_pack_production.py` | 新建 | 测试用例 |
| 4 | `docs/2026-02-20/L45_FETCH_PACK_PRODUCTION_REPORT_v1.md` | 新建 | 本报告 |

---

## 3. 核心实现

### 3.1 AuditPackStore

```python
class AuditPackStore:
    """
    AuditPack 存储读取接口。

    提供 run_id/evidence_ref 索引读取能力，支持一致性校验。
    """

    def fetch_by_run_id(self, run_id: str) -> FetchResult:
        """通过 run_id 读取 AuditPack"""

    def fetch_by_evidence_ref(self, evidence_ref: str) -> FetchResult:
        """通过 evidence_ref 读取 AuditPack"""

    def fetch_with_consistency_check(
        self,
        run_id: Optional[str] = None,
        evidence_ref: Optional[str] = None,
    ) -> FetchResult:
        """一致性校验：同时提供时验证指向同一个 pack"""
```

### 3.2 FetchResult

```python
@dataclass
class FetchResult:
    """Result of fetching an AuditPack."""
    success: bool
    pack: Optional[AuditPack] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    evidence_ref: Optional[str] = None
    run_id: Optional[str] = None
```

### 3.3 fetch_pack 路由升级

```python
@router.post("/fetch_pack")
async def fetch_pack(request: FetchPackRequest):
    """Production implementation with real storage and consistency check."""

    # 1. 从真实存储读取
    store = get_audit_pack_store()
    result = store.fetch_with_consistency_check(
        run_id=request.run_id,
        evidence_ref=request.evidence_ref,
    )

    # 2. Fail-closed: 失败返回结构化错误信封
    if not result.success:
        return N8NErrorEnvelope(
            error_code=result.error_code or "FETCH_ERROR",
            blocked_by="AUDIT_PACK_STORE",
            message=result.error_message,
            ...
        ).model_dump()

    # 3. 确保 replay_pointer 字段存在（可空）
    pack_data["replay_pointer"] = {...}  # always present
```

---

## 4. 约束验证

| # | 约束 | 状态 | 说明 |
|---|------|------|------|
| 1 | run_id 与 evidence_ref 任一给定时必须能做一致性校验 | ✅ | `fetch_with_consistency_check()` |
| 2 | 读取失败必须 fail-closed 并返回结构化错误信封 | ✅ | `N8NErrorEnvelope` |
| 3 | 返回体必须包含 replay_pointer（可空但字段存在） | ✅ | 默认 null 结构 |
| 4 | 不破坏 T4 定义的 receipt schema 兼容性 | ✅ | 字段名一致 |

---

## 5. 测试用例

| # | 测试场景 | 预期结果 |
|---|----------|----------|
| 1 | 通过 run_id 读取成功 | ✅ 返回 pack |
| 2 | 通过 evidence_ref 读取成功 | ✅ 返回 pack |
| 3 | 一致性校验 - 同一个 pack | ✅ 返回 pack |
| 4 | 缺标识 - 都未提供 | ✅ 错误信封 |
| 5 | 不一致 - 不同 pack | ✅ CONSISTENCY_ERROR |
| 6 | replay_pointer 字段存在 | ✅ 可空 |
| 7 | receipt schema 兼容性 | ✅ 必填字段齐全 |

---

## 6. 错误码

| 错误码 | 语义 | 场景 |
|--------|------|------|
| `INVALID_IDENTIFIER` | 标识符无效 | run_id/evidence_ref 为空 |
| `PACK_NOT_FOUND` | AuditPack 未找到 | 指定标识无对应 pack |
| `CONSISTENCY_ERROR` | 一致性校验失败 | run_id 和 evidence_ref 指向不同 pack |
| `CORRUPT_PACK` | AuditPack 损坏 | 存储 index 与 pack 不匹配 |

---

## 7. 样例响应

### 7.1 成功读取

```json
{
  "ok": true,
  "data": {
    "receipt_id": "RCP-L45-A1B2C3D4",
    "run_id": "RUN-L4-1739980000-A1B2C3D4",
    "evidence_ref": "EV-EXEC-L4-1739980000-A1B2C3D4",
    "gate_decision": "PASSED",
    "executed_at": "2026-02-20T10:30:00Z",
    "skill_id": "l45_n8n_orchestration_boundary",
    "workflow_id": "wf_001",
    "replay_pointer": {
      "snapshot_ref": "snapshot://L45-D2-20260220/v1",
      "at_time": "2026-02-20T10:30:00Z",
      "revision": "v1.0.0",
      "evidence_bundle_ref": "evidence://bundles/L45-D2"
    },
    "query_at_time": "2026-02-20T10:35:00Z",
    "fetched_at": "2026-02-20T10:35:00Z"
  },
  "gate_decision": "ALLOW",
  "release_allowed": true,
  "evidence_ref": "EV-EXEC-L4-1739980000-A1B2C3D4",
  "run_id": "RUN-L4-1739980000-A1B2C3D4"
}
```

### 7.2 失败响应（一致性错误）

```json
{
  "ok": false,
  "error_code": "CONSISTENCY_ERROR",
  "blocked_by": "AUDIT_PACK_STORE",
  "message": "Consistency check failed: run_id RUN-L4-xxx points to pack A, but evidence_ref EV-xxx points to pack B",
  "evidence_ref": "EV-N8N-xxx",
  "run_id": "RUN-L4-xxx"
}
```

---

## 8. Gate 自动检查

```bash
pytest -q skillforge/tests/test_n8n_fetch_pack_production.py
# 预期: passed

pytest -q skillforge/tests/test_membership_regression.py
# 预期: passed
```

---

## 9. 手动检查清单

- [x] fetch_pack 返回可直接被 n8n 工作流消费
- [x] 错误分支具备可审计 evidence_ref
- [x] replay_pointer 字段始终存在（可空）
- [x] 与 T4 定义的 receipt schema 字段名一致

---

## 10. 变更记录

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v1.0 | 2026-02-20 | 初始版本 | vs--cc1 |
