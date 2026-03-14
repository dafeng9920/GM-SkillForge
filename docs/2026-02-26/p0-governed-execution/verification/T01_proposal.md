# T01 Proposal: 宪法防绕过基线

> Executor: Antigravity-2 | Reviewer: vs--cc2 | Compliance: Kior-C
> Wave: 1 | Depends On: none
> Created: 2026-02-26

---

## 1. PreflightChecklist（起飞前检查单）

### 1.1 Fail-Closed 风险枚举

| 风险场景 | 边缘条件 | 当前状态 | 缓解措施 |
|---------|---------|---------|---------|
| Constitution 文件缺失 | `docs/2026-02-16/constitution_v1.md` 不存在 | 已存在 | ConstitutionGate 已实现 fail-closed DENY |
| policy_check 绕过 | 入口未调用 policy_check | 部分入口缺失 | 本任务建立统一 wrapper |
| Schema 非法 | 输入不符合 schema 定义 | 有校验但不统一 | 建立 schema 校验前置 |
| 签名缺失 | 无有效签名 | 待 ISSUE-04 实现 | 本任务定义接口规范 |
| Nonce 缺失 | 无 challenge/nonce | 待 ISSUE-05 实现 | 本任务定义接口规范 |
| Node 未注册 | node_id 不在 registry | 待 ISSUE-06 实现 | 本任务定义接口规范 |

### 1.2 依赖环境（Env/Flags）

```yaml
environment:
  - CONSTITUTION_PATH: "docs/2026-02-16/constitution_v1.md"
  - POLICY_CHECK_STRICT_MODE: true  # 默认 strict，不可降级
  - AUDIT_LOG_PATH: "logs/policy_decisions.log"

feature_flags:
  - POLICY_CHECK_ENABLED: true  # 强制 true，无 false 选项
  - FAIL_CLOSED_DEFAULT: true   # 默认拒绝策略
```

### 1.3 历史债务扫描

| 现存问题 | 文件位置 | 债务类型 | 处理方式 |
|---------|---------|---------|---------|
| policy_check 非强制 | `gm_plugin_core_seed/src/services/orchestration/store_sqlite.py` | fallback 容错 | 移除 fallback，强制校验 |
| PolicyCheck 可选 | `orchestration_turn.py` policy_checks 可为空 | 可选字段 | 保持可选但定义默认空列表 |
| ConstitutionGate 仅限 stage 4 | `constitution_gate.py` | 范围限制 | 本任务定义通用入口 wrapper |

---

## 2. ExecutionContract（执行契约）

### 2.1 Input Constraints

**允许修改的文件：**
- `docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md` (新建)

**绝对不可修改的文件：**
- `skillforge-spec-pack/skillforge/src/nodes/constitution_gate.py` (保持现有实现)
- `gm_plugin_core_seed/` 下所有文件 (超出范围)
- 其他任务卡指定的文件 (T02-T11)

**输入依赖：**
- `docs/2026-02-16/constitution_v1.md` (已存在)
- `skillforge-spec-pack/skillforge/src/utils/constitution.py` (已存在)

### 2.2 Output Definition

**交付物形态：**
```yaml
deliverables:
  - path: "docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md"
    type: "新建"
    schema_ref: "self-defined in document"
    required_sections:
      - policy_check 规范
      - fail-closed 拒绝策略
      - 审计字段标准
      - 入口实现指南
```

**验收标准：**
1. 文档定义统一的 `policy_check()` 前置校验接口
2. 明确 fail-closed 拒绝条件清单
3. 定义标准审计字段: `trace_id`, `policy_version`, `decision_reason`, `evidence_ref`
4. 提供 API/CLI/Worker 三种入口的集成指南

### 2.3 Gate / Acceptance Check

```bash
# 自动化验收命令
rg --files docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md
# 预期：文件存在

rg "policy_check" docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md
# 预期：至少 5 处匹配

rg "fail-closed|fail_closed" docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md
# 预期：至少 3 处匹配

rg "trace_id|policy_version|decision_reason|evidence_ref" docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md
# 预期：4 个字段均存在
```

### 2.4 Rollback 方案

```bash
# 回滚命令（如需撤销）
rm docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md
# 影响：仅删除本文档，不影响现有代码
```

---

## 3. RequiredChanges（确切改动点）

### 3.1 新建文件

**文件：** `docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md`

**内容结构：**

```markdown
# 宪法防绕过基线规范 (ISSUE-00)

## 1. policy_check() 统一接口

### 1.1 函数签名
```python
def policy_check(
    entry_point: Literal["api", "cli", "worker"],
    payload: dict,
    context: PolicyContext
) -> PolicyDecision:
    ...
```

### 1.2 执行顺序（强制）
1. schema 校验
2. signature 校验（如适用）
3. nonce 校验（如适用）
4. node registry 校验（如适用）
5. constitution rule 校验

## 2. Fail-Closed 拒绝策略

| 拒绝条件 | 错误码 | HTTP 状态 |
|---------|-------|----------|
| Schema 非法 | SCHEMA_INVALID | 400 |
| 签名缺失/无效 | SIGNATURE_INVALID | 401 |
| Nonce 缺失/过期 | CHALLENGE_EXPIRED | 401 |
| Node 未注册 | NODE_UNTRUSTED | 403 |
| Constitution 规则违反 | CONSTITUTION_VIOLATION | 403 |

## 3. 审计字段标准

```json
{
  "trace_id": "uuid-v4",
  "policy_version": "constitution_v1",
  "decision_reason": "ALLOW|DENY|REQUIRES_CHANGES",
  "evidence_ref": {
    "id": "EV-xxx",
    "kind": "LOG|FILE|DIFF",
    "locator": "path:line",
    "sha256": "hash"
  }
}
```

## 4. 入口实现指南

### 4.1 API 入口
### 4.2 CLI 入口
### 4.3 Worker 入口
```

### 3.2 精确定位

- **行号范围：** 新文件，约 150-200 行
- **依赖模块：** 无新代码依赖，仅文档
- **防腐层：** 明确声明后续 ISSUE-01~06 的接口预留

---

## 4. 三权记录路径

| 产物 | 路径 |
|-----|-----|
| Execution Report | `docs/2026-02-26/p0-governed-execution/verification/T01_execution_report.yaml` |
| Gate Decision | `docs/2026-02-26/p0-governed-execution/verification/T01_gate_decision.json` |
| Compliance Attestation | `docs/2026-02-26/p0-governed-execution/verification/T01_compliance_attestation.json` |

---

## 5. Deny List（禁止事项）

- [x] 不得修改 ConstitutionGate 现有实现
- [x] 不得引入新的 Python 依赖
- [x] 不得定义与后续 ISSUE 冲突的接口
- [x] 不得绕过 Review/Compliance 直接执行
- [x] 不得无 EvidenceRef 宣称完成

---

*Proposal prepared by Antigravity-2 | Awaiting Review (vs--cc2) → Compliance (Kior-C)*
