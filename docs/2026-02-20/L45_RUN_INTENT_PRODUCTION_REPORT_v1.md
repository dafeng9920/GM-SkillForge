# L4.5 run_intent 生产化实现报告

> **Job ID**: L45-D2-ORCH-MINCAP-20260220-002
> **Skill ID**: l45_orchestration_min_capabilities
> **Task**: T7
> **Executor**: vs--cc3
> **Date**: 2026-02-20
> **Status**: ✅ COMPLETED

---

## 1. 任务概述

将 `run_intent` 从基础实现升级为生产级别的编排执行入口，固化最终裁决权在 SkillForge。

### 1.1 核心目标

1. **run_id 内部生成**：由 SkillForge 内部计算 run_id，不信任外部传入
2. **越权字段防护**：禁止 n8n 注入 gate_decision/release_allowed/evidence_ref/permit_id/run_id
3. **输出格式标准化**：所有输出必须包含 run_id/gate_decision/evidence_ref/release_allowed
4. **E001/E003 语义保持**：错误码语义不漂移

---

## 2. 交付物清单

| # | 文件 | 类型 | 状态 |
|---|------|------|------|
| 1 | `skillforge/src/api/routes/n8n_orchestration.py` | 修改 | ✅ |
| 2 | `skillforge/tests/test_n8n_run_intent_production.py` | 新建 | ✅ |
| 3 | `docs/2026-02-20/L45_RUN_INTENT_PRODUCTION_REPORT_v1.md` | 新建 | ✅ |

---

## 3. 实现细节

### 3.1 禁止字段扩展

```python
FORBIDDEN_N8N_FIELDS = [
    "gate_decision",
    "release_allowed",
    "permit_token",
    "evidence_ref",
    "permit_id",  # 生产新增
    "run_id",     # 生产新增
]
```

### 3.2 审计追踪功能

新增 `create_audit_trail()` 函数，支持：

- 记录完整执行上下文（run_id, intent_id, repo_url, commit_sha）
- 记录裁决结果（gate_decision, release_allowed）
- 关联证据（evidence_ref, permit_id）
- 记录 Job/Skill 标识

```python
def create_audit_trail(
    run_id: str,
    intent_id: str,
    repo_url: str,
    commit_sha: str,
    gate_decision: str,
    release_allowed: bool,
    evidence_ref: str,
    permit_id: Optional[str] = None,
    error_code: Optional[str] = None,
) -> dict:
    ...
```

### 3.3 run_id 生成规则

```python
def generate_run_id() -> str:
    ts = int(time.time())
    uid = uuid.uuid4().hex[:8].upper()
    return f"RUN-N8N-{ts}-{uid}"
```

格式：`RUN-N8N-{unix_timestamp}-{8位随机UID}`

---

## 4. 信封格式

### 4.1 成功信封

```json
{
    "ok": true,
    "data": {
        "intent_id": "...",
        "repo_url": "...",
        "commit_sha": "...",
        "at_time": "...",
        "execution_status": "COMPLETED",
        "permit_id": "...",
        "validation_timestamp": "...",
        "context": {...}
    },
    "gate_decision": "ALLOW",
    "release_allowed": true,
    "evidence_ref": "EV-N8N-INTENT-...",
    "run_id": "RUN-N8N-..."
}
```

### 4.2 错误信封

```json
{
    "ok": false,
    "error_code": "E001",
    "blocked_by": "PERMIT_REQUIRED",
    "message": "Permit token is required for execution",
    "evidence_ref": "EV-N8N-INTENT-...",
    "run_id": "RUN-N8N-...",
    "forbidden_field_evidence": {...}  // 可选
}
```

---

## 5. Gate 自动检查结果

### 5.1 生产测试

```bash
pytest -q skillforge/tests/test_n8n_run_intent_production.py
# 8 passed ✓
```

测试覆盖：
- ✅ 成功场景（有效 permit）
- ✅ E001 无 permit 阻断
- ✅ E003 坏签名阻断
- ✅ 禁止字段注入检测
- ✅ run_id 内部生成验证
- ✅ 输出信封格式验证
- ✅ Fail-closed 所有路径
- ✅ 审计追踪创建

### 5.2 GatePermit 基线测试

```bash
pytest -q skillforge/tests/test_gate_permit.py
# 19 passed ✓
```

---

## 6. 约束验证

| 约束 | 状态 | 说明 |
|------|------|------|
| run_id 由 SkillForge 内部生成 | ✅ | 前缀 RUN-N8N-，不信任外部 |
| 禁止注入 gate_decision | ✅ | 检测并拒绝 |
| 禁止注入 release_allowed | ✅ | 检测并拒绝 |
| 禁止注入 evidence_ref | ✅ | 检测并拒绝 |
| 禁止注入 permit_id | ✅ | 检测并拒绝 |
| 禁止注入 run_id | ✅ | 检测并拒绝 |
| 输出含 run_id | ✅ | 必填字段 |
| 输出含 gate_decision | ✅ | 必填字段 |
| 输出含 evidence_ref | ✅ | 必填字段 |
| 输出含 release_allowed | ✅ | 必填字段 |
| E001 语义保持 | ✅ | PERMIT_REQUIRED |
| E003 语义保持 | ✅ | PERMIT_INVALID |
| 不引入新依赖 | ✅ | 仅使用现有模块 |
| 不删除既有路由 | ✅ | /api/v1/n8n/run_intent 保留 |
| 不绕过 GatePermit | ✅ | 所有执行经过 GatePermit |

---

## 7. 手动验收确认

- [x] run_intent 成功分支可追溯到 permit 校验结果
- [x] 失败分支均 fail-closed，返回结构化错误信封
- [x] n8n 越权字段注入场景被阻断
- [x] 审计追踪完整记录执行上下文

---

## 8. 常量标识

```yaml
job_id: "L45-D2-ORCH-MINCAP-20260220-002"
skill_id: "l45_orchestration_min_capabilities"
run_id_prefix: "RUN-N8N"
evidence_ref_prefix: "EV-N8N-INTENT"
```

---

## 9. 后续依赖

本任务 (T7) 完成后，下游任务可启动：
- T10 (Kior-B): 依赖 T7, T8, T9

---

> **Gate Decision**: ✅ ALLOW
> **Reviewer**: Automated + Manual
> **Timestamp**: 2026-02-20
