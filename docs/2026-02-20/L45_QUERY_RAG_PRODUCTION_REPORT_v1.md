# L4.5 query_rag 生产化实现报告

> **Job ID**: L45-D2-ORCH-MINCAP-20260220-002
> **Skill ID**: l45_orchestration_min_capabilities
> **Task ID**: T9
> **Executor**: vs--cc2
> **Date**: 2026-02-20

---

## 1. 概述

本报告记录 query_rag 端点的生产化实现，包括：
- 可替换 RAG adapter 接口
- at_time 固定输入校验（禁止漂移值）
- replay_pointer 输出用于回放
- repo_url + commit_sha + at_time 组合查询支持

---

## 2. 实现概要

### 2.1 新建文件

| 文件 | 类型 | 说明 |
|------|------|------|
| `skillforge/src/adapters/__init__.py` | 新建 | 适配器模块入口 |
| `skillforge/src/adapters/rag_adapter.py` | 新建 | 可替换 RAG adapter 接口 |
| `skillforge/tests/test_n8n_query_rag_production.py` | 新建 | 生产化测试用例 |

### 2.2 修改文件

| 文件 | 类型 | 说明 |
|------|------|------|
| `skillforge/src/api/routes/n8n_orchestration.py` | 修改 | query_rag 调用 adapter + at_time 固定校验 |

---

## 3. RAG Adapter 接口设计

### 3.1 核心接口

```python
class RAGAdapter(ABC):
    @abstractmethod
    def query(
        self,
        query: str,
        at_time: str,          # REQUIRED - 固定时间戳
        repo_url: Optional[str] = None,
        commit_sha: Optional[str] = None,
        top_k: int = 5,
        **kwargs,
    ) -> RAGQueryResult:
        pass
```

### 3.2 at_time 固定输入策略

**禁止的漂移值**：
- `latest`, `now`, `current`, `today`
- `yesterday`, `tomorrow`, `recent`, `newest`

**原因**：漂移值破坏可复现性 - 查询必须是确定性的。

**校验逻辑**：
```python
AT_TIME_FORBIDDEN_VALUES = frozenset([
    "latest", "now", "current", "today",
    "yesterday", "tomorrow", "recent", "newest",
])

def validate_at_time(self, at_time: Optional[str]) -> tuple[bool, Optional[RAGQueryError]]:
    if at_time is None:
        return False, RAGQueryError(error_code=RAGErrorCode.AT_TIME_MISSING, ...)
    if at_time.lower() in AT_TIME_FORBIDDEN_VALUES:
        return False, RAGQueryError(error_code=RAGErrorCode.AT_TIME_DRIFT_FORBIDDEN, ...)
    # Try to parse as ISO-8601
    datetime.fromisoformat(at_time_normalized)
    return True, None
```

### 3.3 ReplayPointer 结构

```python
@dataclass
class ReplayPointer:
    at_time: str              # 必需
    repo_url: Optional[str]   # 可选
    commit_sha: Optional[str] # 可选
    run_id: Optional[str]     # 可选（追踪标识）
```

### 3.4 可替换实现

```python
# 获取当前适配器
adapter = get_rag_adapter()

# 切换到 mock 适配器（测试用）
set_rag_adapter(MockRAGAdapter())

# 重置为默认适配器
reset_rag_adapter()
```

---

## 4. API 端点修改

### 4.1 query_rag 端点流程

```
1. 验证 at_time 存在 → 缺失则返回 RAG-AT-TIME-MISSING
2. 验证 at_time 非漂移值 → 漂移值返回 RAG-AT-TIME-DRIFT-FORBIDDEN
3. 调用 RAG adapter 执行查询
4. 返回结果（必须包含 replay_pointer）
```

### 4.2 错误代码

| 错误代码 | 说明 |
|----------|------|
| `RAG-AT-TIME-MISSING` | at_time 未提供 |
| `RAG-AT-TIME-DRIFT-FORBIDDEN` | at_time 使用漂移值 |
| `RAG-AT-TIME-INVALID-FORMAT` | at_time 格式错误 |
| `RAG-QUERY-EMPTY` | 查询字符串为空 |
| `RAG-VALIDATION-ERROR` | 验证错误 |
| `RAG-INTERNAL-ERROR` | 内部错误 |

---

## 5. 测试覆盖

### 5.1 测试用例

| 类别 | 用例 | 预期结果 |
|------|------|----------|
| at_time 验证 | 有效 ISO-8601 时间戳 | ✅ 接受 |
| at_time 验证 | `latest` 漂移值 | ❌ 拒绝 |
| at_time 验证 | `now` 漂移值 | ❌ 拒绝 |
| at_time 验证 | `today` 漂移值 | ❌ 拒绝 |
| at_time 验证 | 空字符串 | ❌ 拒绝 |
| at_time 验证 | None | ❌ 拒绝 |
| replay_pointer | 输出包含 replay_pointer | ✅ |
| replay_pointer | 包含 at_time | ✅ |
| replay_pointer | 包含 repo_url | ✅ |
| replay_pointer | 包含 commit_sha | ✅ |
| replay_pointer | 包含 run_id | ✅ |
| 组合查询 | repo_url + commit_sha + at_time | ✅ 接受 |
| 结果元数据 | 包含 commit_sha 和 at_time | ✅ |
| 可替换适配器 | 默认为 MockRAGAdapter | ✅ |
| 可替换适配器 | 运行时切换 | ✅ |
| 可替换适配器 | 重置为默认 | ✅ |
| 查询验证 | 空查询 | ❌ 拒绝 |
| 查询验证 | top_k 参数限制 | ✅ |

---

## 6. 约束验证

### 6.1 任务约束

| 约束 | 状态 | 证据 |
|------|------|------|
| 必须拒绝 latest/now/today 漂移输入 | ✅ | `AT_TIME_FORBIDDEN_VALUES` 常量 + `validate_at_time()` 方法 |
| query_rag 返回 replay_pointer | ✅ | `RAGQueryResult.replay_pointer` 字段 |
| 支持 repo_url+commit_sha+at_time 组合 | ✅ | `query()` 方法参数 |
| adapter 必须可替换 | ✅ | `get_rag_adapter()` / `set_rag_adapter()` / `reset_rag_adapter()` |

### 6.2 Deny 规则

| 规则 | 状态 | 说明 |
|------|------|------|
| 不得将 query_rag 做成直接放行裁决入口 | ✅ | query_rag 不涉及 gate_decision |
| 不得在 adapter 中写入最终 gate_decision | ✅ | adapter 只返回查询结果 |
| 不得引入外部在线依赖作为必需条件 | ✅ | MockRAGAdapter 无外部依赖 |

---

## 7. Gate 自动检查

```bash
python -m pytest -q skillforge/tests/test_n8n_query_rag_production.py
# 待执行

python -m pytest -q skillforge/tests/test_l4_api_smoke.py
# 待执行
```

---

## 8. 手动检查清单

- [ ] query_rag 输出可被 fetch_pack 证据链引用
- [ ] at_time 固定输入策略在报告中有明示证据

---

## 9. 变更历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-02-20 | 初始版本，实现生产化 query_rag |
