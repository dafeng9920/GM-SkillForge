# L4.5 外部 Skill 导入入口实现报告

> **Job ID**: L45-D3-EXT-SKILL-GOV-20260220-003
> **Skill ID**: l45_external_skill_governance_batch1
> **Task**: T12
> **Executor**: vs--cc3
> **Date**: 2026-02-20
> **Status**: ✅ COMPLETED

---

## 1. 任务概述

新增 `import_external_skill` 编排入口，实现外部 Skill 导入治理流程。n8n 仅负责触发/路由，最终裁决归 SkillForge。

### 1.1 核心目标

1. **新增 API 入口**：`POST /api/v1/n8n/import_external_skill`
2. **6 步导入流程**：Quarantine → Constitution Gate → System Audit → Decision → Permit → Registry
3. **内部字段生成**：run_id/evidence_ref 由 SkillForge 内部生成
4. **Fail-closed**：所有失败分支返回结构化错误信封 + required_changes

---

## 2. 交付物清单

| # | 文件 | 类型 | 状态 |
|---|------|------|------|
| 1 | `skillforge/src/api/routes/n8n_orchestration.py` | 修改 | ✅ |
| 2 | `skillforge/tests/test_n8n_import_external_skill.py` | 新建 | ✅ |
| 3 | `docs/2026-02-20/L45_IMPORT_EXTERNAL_SKILL_REPORT_v1.md` | 新建 | ✅ |

---

## 3. 实现细节

### 3.1 新增路由

```
POST /api/v1/n8n/import_external_skill
```

### 3.2 请求模型

```python
class ImportExternalSkillRequest(BaseModel):
    repo_url: str
    commit_sha: str
    at_time: Optional[str]
    external_skill_ref: str
    requester_id: str
    skill_name: Optional[str]
    skill_version: Optional[str]
    source_repository: Optional[str]
    context: Optional[dict]
    tier: str = "FREE"

    # FORBIDDEN fields (will be rejected)
    gate_decision: Optional[str]  # EXCLUDED
    release_allowed: Optional[bool]  # EXCLUDED
    run_id: Optional[str]  # EXCLUDED
    evidence_ref: Optional[str]  # EXCLUDED
    permit_id: Optional[str]  # EXCLUDED
```

### 3.3 导入流程

| 步骤 | 名称 | 功能 |
|------|------|------|
| S1 | Import to Quarantine | 外部 skill 先落到临时仓 |
| S2 | Constitution Gate | 宪法裁决（边界/权限/禁用能力） |
| S3 | System Audit | 五层系统审计（L1-L5） |
| S4 | Decision | 仅允许 PASS@L3+ 进入下一步 |
| S5 | Permit Issuance | 签发入库 permit |
| S6 | Registry Admission | 写入正式 skill registry |

### 3.4 响应格式

**成功信封**：
```json
{
    "ok": true,
    "data": {
        "external_skill_ref": "...",
        "import_status": "COMPLETED",
        "pipeline_state": "S6_REGISTRY_ADMISSION",
        "quarantine_id": "Q-...",
        "permit_id": "PERMIT-EXT-...",
        "registry_entry_id": "REG-...",
        "skill_revision": 1,
        "audit_summary": {...}
    },
    "gate_decision": "ALLOW",
    "release_allowed": true,
    "evidence_ref": "EV-EXT-SKILL-...",
    "run_id": "RUN-N8N-..."
}
```

**错误信封**（带 required_changes）：
```json
{
    "ok": false,
    "error_code": "...",
    "blocked_by": "...",
    "message": "...",
    "gate_decision": "BLOCK",
    "evidence_ref": "EV-EXT-SKILL-...",
    "run_id": "RUN-N8N-...",
    "required_changes": ["Fix X", "Fix Y"]
}
```

---

## 4. Gate 自动检查结果

```bash
pytest -q skillforge/tests/test_n8n_import_external_skill.py
# 8 passed ✓
```

测试覆盖：
- ✅ 成功场景（完整导入流程）
- ✅ 禁止字段注入检测（5 个字段）
- ✅ Constitution Gate 失败
- ✅ System Audit 失败
- ✅ run_id/evidence_ref 内部生成
- ✅ 输出信封必填字段验证
- ✅ Fail-closed 所有路径
- ✅ 导入流程状态验证

---

## 5. 约束验证

| 约束 | 状态 | 说明 |
|------|------|------|
| run_id 由 SkillForge 内部生成 | ✅ | 前缀 RUN-N8N-，不信任外部 |
| evidence_ref 由 SkillForge 内部生成 | ✅ | 前缀 EV-EXT-SKILL- |
| 禁止注入 gate_decision | ✅ | 检测并拒绝 |
| 禁止注入 release_allowed | ✅ | 检测并拒绝 |
| 禁止注入 run_id | ✅ | 检测并拒绝 |
| 禁止注入 evidence_ref | ✅ | 检测并拒绝 |
| 禁止注入 permit_id | ✅ | 检测并拒绝 |
| 失败分支 fail-closed | ✅ | 返回 gate_decision=BLOCK |
| 响应含 gate_decision | ✅ | 必填字段 |
| 响应含 required_changes（失败时）| ✅ | 必填字段 |
| 不绕过 gate 链 | ✅ | 经过完整治理流程 |
| 不修改既有路由 | ✅ | run_intent/fetch_pack/query_rag 保留 |
| 不在 n8n 层生成最终裁决 | ✅ | 裁决由治理流程给出 |

---

## 6. 边界规则确认

| 规则 | 状态 |
|------|------|
| n8n 仅触发/路由，不做最终裁决 | ✅ |
| 最终裁决归 SkillForge | ✅ |
| no-permit-no-registry | ✅ |
| Upgrade = Full Governance Cycle | ✅ |

---

## 7. 常量标识

```yaml
job_id: "L45-D3-EXT-SKILL-GOV-20260220-003"
skill_id: "l45_external_skill_governance_batch1"
run_id_prefix: "RUN-N8N"
evidence_ref_prefix: "EV-EXT-SKILL"
quarantine_id_prefix: "Q-"
permit_id_prefix: "PERMIT-EXT-"
registry_entry_id_prefix: "REG-"
```

---

## 8. 后续依赖

本任务 (T12) 完成后，下游任务 T16 (Kior-C) 可在所有 Wave 1 任务完成后启动。

---

> **Gate Decision**: ✅ ALLOW
> **Reviewer**: Automated
> **Timestamp**: 2026-02-20
