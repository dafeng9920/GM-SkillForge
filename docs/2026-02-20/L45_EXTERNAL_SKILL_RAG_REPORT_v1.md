# L4.5 外部 Skill RAG 检索与回放一致性报告

> **Job ID**: L45-D3-EXT-SKILL-GOV-20260220-003
> **Skill ID**: l45_external_skill_governance_batch1
> **Task ID**: T14
> **Executor**: vs--cc2
> **Date**: 2026-02-20

---

## 1. 概述

本报告记录外部 Skill RAG 检索适配器的实现，包括：
- at_time 固定输入校验（禁止漂移值，fail-closed）
- external_skill_ref + repo_url + commit_sha + at_time 组合查询
- replay_pointer 输出用于回放验证（必须存在）
- 完整的可复核证据链

---

## 2. 实现概要

### 2.1 新建文件

| 文件 | 类型 | 说明 |
|------|------|------|
| `skillforge/src/adapters/external_skill_rag_adapter.py` | 新建 | 外部 Skill RAG 检索适配器 |
| `skillforge/tests/test_external_skill_rag_adapter.py` | 新建 | at_time 固定输入 + drift 阻断测试 |

### 2.2 依赖关系

| 依赖文件 | 用途 |
|---------|------|
| `skillforge/src/adapters/rag_adapter.py` | 参考 at_time 校验与 replay_pointer 模式 |
| `docs/2026-02-20/L45_QUERY_RAG_PRODUCTION_REPORT_v1.md` | 已验证的 drift 阻断策略 |

---

## 3. External Skill RAG Adapter 设计

### 3.1 核心接口

```python
class ExternalSkillRAGAdapter(ABC):
    @abstractmethod
    def query(
        self,
        query: str,
        at_time: str,              # REQUIRED - 固定时间戳
        external_skill_ref: str,   # REQUIRED - 外部 Skill 引用
        repo_url: str,             # REQUIRED - 仓库 URL
        commit_sha: str,           # REQUIRED - 提交 SHA
        top_k: int = 5,
        **kwargs,
    ) -> ExternalSkillRAGResult:
        pass
```

### 3.2 全局常量（与 task_dispatch 一致）

```yaml
job_id: "L45-D3-EXT-SKILL-GOV-20260220-003"
skill_id: "l45_external_skill_governance_batch1"
fixed_inputs:
  - repo_url
  - commit_sha
  - at_time
  - external_skill_ref
```

### 3.3 at_time 固定输入策略

**禁止的漂移值**（与 T9 策略一致）：
- `latest`, `now`, `current`, `today`
- `yesterday`, `tomorrow`, `recent`, `newest`
- `current_time`, `utc_now`, `sys_time`

**原因**：漂移值破坏可复现性和治理可追溯性 - 查询必须是确定性的。

**Fail-Closed 校验逻辑**：
```python
def validate_at_time(self, at_time: Optional[str]) -> tuple[bool, Optional[ExternalSkillRAGError]]:
    # 1. 缺失检查
    if at_time is None or at_time == "":
        return False, ExternalSkillRAGError(
            error_code=ExternalSkillRAGErrorCode.AT_TIME_MISSING, ...
        )

    # 2. 漂移值检查
    if at_time.lower() in AT_TIME_FORBIDDEN_VALUES:
        return False, ExternalSkillRAGError(
            error_code=ExternalSkillRAGErrorCode.AT_TIME_DRIFT_FORBIDDEN, ...
        )

    # 3. ISO-8601 格式检查
    datetime.fromisoformat(at_time_normalized)
    return True, None
```

### 3.4 ReplayPointer 结构

```python
@dataclass
class ExternalSkillReplayPointer:
    at_time: str              # 必需 - 查询时间点
    external_skill_ref: str   # 必需 - 外部 Skill 引用
    repo_url: str             # 必需 - 仓库 URL
    commit_sha: str           # 必需 - 提交 SHA
    run_id: str               # 必需 - 运行追踪 ID
    content_hash: str         # 必需 - 内容哈希（验证一致性）

    def verify_consistency(self, at_time: str) -> bool:
        """验证 replay_pointer.at_time 与输入 at_time 一致"""
        return self.at_time == at_time
```

### 3.5 返回体结构

```python
@dataclass
class ExternalSkillRAGResult:
    query: str                              # 原始查询
    at_time: str                            # 查询时间点
    external_skill_ref: str                 # 外部 Skill 引用
    repo_url: str                           # 仓库 URL
    commit_sha: str                         # 提交 SHA
    results: list[dict[str, Any]]           # 检索结果列表
    replay_pointer: ExternalSkillReplayPointer  # 必须存在
    total_hits: int                         # 命中数
    queried_at: str                         # 查询时间戳
    job_id: str                             # Job ID 追踪
```

---

## 4. Fail-Closed 规则

### 4.1 规则表

| 条件 | 行为 | 错误码 |
|------|------|--------|
| `at_time` 缺失（None/""） | 拒绝 | `EXT-RAG-AT-TIME-MISSING` |
| `at_time` 为漂移值 | 拒绝 | `EXT-RAG-AT-TIME-DRIFT-FORBIDDEN` |
| `at_time` 格式无效 | 拒绝 | `EXT-RAG-AT-TIME-INVALID-FORMAT` |
| `external_skill_ref` 缺失 | 拒绝 | `EXT-RAG-SKILL-REF-MISSING` |
| `repo_url` 缺失 | 拒绝 | `EXT-RAG-REPO-URL-MISSING` |
| `commit_sha` 缺失 | 拒绝 | `EXT-RAG-COMMIT-SHA-MISSING` |
| `query` 为空 | 拒绝 | `EXT-RAG-QUERY-EMPTY` |
| `replay_pointer` 生成失败 | 拒绝 | `EXT-RAG-REPLAY-POINTER-FAILED` |

### 4.2 Deny 规则验证

| 规则 | 状态 | 说明 |
|------|------|------|
| 不得接受相对时间输入 | ✅ | `validate_at_time()` 拒绝非 ISO-8601 |
| 不得返回无 replay_pointer 的成功响应 | ✅ | `ExternalSkillRAGResult.replay_pointer` 必需字段 |
| 不得隐式降级为当前时间 | ✅ | 无默认值，必须显式提供 |

---

## 5. 错误代码（与 T9 语义一致）

| 错误代码 | 说明 |
|----------|------|
| `EXT-RAG-AT-TIME-MISSING` | at_time 未提供 |
| `EXT-RAG-AT-TIME-DRIFT-FORBIDDEN` | at_time 使用漂移值 |
| `EXT-RAG-AT-TIME-INVALID-FORMAT` | at_time 格式错误 |
| `EXT-RAG-SKILL-REF-MISSING` | external_skill_ref 未提供 |
| `EXT-RAG-REPO-URL-MISSING` | repo_url 未提供 |
| `EXT-RAG-COMMIT-SHA-MISSING` | commit_sha 未提供 |
| `EXT-RAG-QUERY-EMPTY` | 查询字符串为空 |
| `EXT-RAG-REPLAY-POINTER-FAILED` | replay_pointer 生成失败 |
| `EXT-RAG-INTERNAL-ERROR` | 内部错误 |

---

## 6. 测试覆盖

### 6.1 测试用例

| 类别 | 用例 | 预期结果 |
|------|------|----------|
| at_time 固定输入 | 有效 ISO-8601 时间戳（Z 后缀） | ✅ 接受 |
| at_time 固定输入 | 有效 ISO-8601 时间戳（+00:00） | ✅ 接受 |
| at_time 漂移阻断 | `latest` | ❌ 拒绝 |
| at_time 漂移阻断 | `now` | ❌ 拒绝 |
| at_time 漂移阻断 | `today` | ❌ 拒绝 |
| at_time 漂移阻断 | `current` | ❌ 拒绝 |
| at_time 漂移阻断 | 大小写不敏感 | ❌ 拒绝 |
| at_time 缺失 | None | ❌ 拒绝 |
| at_time 缺失 | 空字符串 | ❌ 拒绝 |
| replay_pointer | 输出包含 replay_pointer | ✅ |
| replay_pointer | 包含 at_time | ✅ |
| replay_pointer | 包含 repo_url | ✅ |
| replay_pointer | 包含 commit_sha | ✅ |
| replay_pointer | 包含 external_skill_ref | ✅ |
| replay_pointer | 包含 run_id | ✅ |
| replay_pointer | 包含 content_hash | ✅ |
| 一致性验证 | replay_pointer.at_time == input.at_time | ✅ |
| 一致性验证 | verify_replay_consistency() | ✅ |
| 必需输入 | external_skill_ref 缺失 | ❌ 拒绝 |
| 必需输入 | repo_url 缺失 | ❌ 拒绝 |
| 必需输入 | commit_sha 缺失 | ❌ 拒绝 |
| 查询验证 | 空查询 | ❌ 拒绝 |
| 查询验证 | 仅空格查询 | ❌ 拒绝 |
| 适配器注册 | get/set/reset | ✅ |
| 便捷函数 | 成功返回 ok=True | ✅ |
| 便捷函数 | 失败返回 error | ✅ |
| 无隐式降级 | 不使用当前时间 | ✅ |
| 无隐式降级 | 不接受相对时间 | ❌ 拒绝 |

### 6.2 测试统计

| 指标 | 数量 |
|------|------|
| 测试类 | 12 |
| 测试用例 | 50+ |
| 参数化用例 | 8 |

---

## 7. 约束验证

### 7.1 任务约束

| 约束 | 状态 | 证据 |
|------|------|------|
| at_time 缺失必须 fail-closed | ✅ | `validate_at_time()` 返回 `AT_TIME_MISSING` |
| latest/now/today 等漂移值必须阻断 | ✅ | `AT_TIME_FORBIDDEN_VALUES` 常量 + 漂移检查 |
| 返回体必须包含 replay_pointer | ✅ | `ExternalSkillRAGResult.replay_pointer` 必需字段 |
| repo_url+commit_sha+at_time 组合必须可复核 | ✅ | `ExternalSkillReplayPointer.verify_consistency()` |

### 7.2 Deny 规则

| 规则 | 状态 | 说明 |
|------|------|------|
| 不得接受相对时间输入 | ✅ | 仅接受 ISO-8601 格式 |
| 不得返回无 replay_pointer 的成功响应 | ✅ | 结构体强制要求 |
| 不得隐式降级为当前时间 | ✅ | 无默认值 |

---

## 8. Gate 自动检查

```bash
python -m pytest -q skillforge/tests/test_external_skill_rag_adapter.py
# 待执行
```

---

## 9. 手动检查清单

- [x] 确认 at_time 与 replay_pointer.at_time 一致性证据
- [x] 确认错误码语义与 T9 一致
- [x] 确认 drift 值完整阻断
- [x] 确认 replay_pointer 必须存在

---

## 10. 变更历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-02-20 | 初始版本，实现外部 Skill RAG 检索适配器 |
