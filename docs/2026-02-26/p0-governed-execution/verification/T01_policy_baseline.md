# 宪法防绕过基线规范 (ISSUE-00 / T01)

> **版本**: v1.0
> **状态**: P0 基线
> **创建**: 2026-02-26
> **Executor**: Antigravity-2
> **关联 Issue**: ISSUE-00 (P0-10-issue-任务清单.md)

---

## 1. 概述

本文档定义 GM-SkillForge 系统的**宪法防绕过基线**，确保：

1. 任意入口（API/CLI/Worker）均先执行 `policy_check()`
2. 缺签名/缺 nonce/Schema 非法/Node 未注册一律**拒绝（fail-closed）**
3. 每次决策记录完整审计字段：`trace_id` / `policy_version` / `decision_reason` / `evidence_ref`

---

## 2. policy_check() 统一接口

### 2.1 函数签名

```python
from typing import Literal, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class DecisionType(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRES_CHANGES = "REQUIRES_CHANGES"

class EntryPoint(str, Enum):
    API = "api"
    CLI = "cli"
    WORKER = "worker"

@dataclass
class PolicyContext:
    """策略上下文"""
    node_id: str                           # 节点标识
    session_id: Optional[str] = None       # 会话 ID
    trace_id: str = ""                     # 追踪 ID（自动生成）
    timestamp: str = ""                    # 时间戳（自动生成）

@dataclass
class EvidenceRef:
    """证据引用"""
    id: str                                # 证据 ID (EV-xxx)
    kind: Literal["LOG", "FILE", "DIFF", "SNIPPET", "URL"]
    locator: str                           # 定位路径 (path:line 或 URL)
    sha256: Optional[str] = None           # 内容哈希

@dataclass
class PolicyDecision:
    """策略决策结果"""
    decision: DecisionType
    trace_id: str
    policy_version: str
    decision_reason: str
    evidence_ref: Optional[EvidenceRef] = None
    blocked: bool = False
    error_code: Optional[str] = None
    http_status: int = 200

def policy_check(
    entry_point: EntryPoint,
    payload: Dict[str, Any],
    context: PolicyContext
) -> PolicyDecision:
    """
    统一策略前置校验

    Args:
        entry_point: 入口类型 (api/cli/worker)
        payload: 请求负载
        context: 策略上下文

    Returns:
        PolicyDecision: 决策结果

    执行顺序（强制）:
        1. Schema 校验
        2. Signature 校验（如适用）
        3. Nonce 校验（如适用）
        4. Node Registry 校验（如适用）
        5. Constitution Rule 校验
    """
    ...
```

### 2.2 执行顺序（强制）

```
┌─────────────────────────────────────────────────────────────┐
│                    policy_check() 流程                       │
├─────────────────────────────────────────────────────────────┤
│  1. Schema Validation                                        │
│     └─ 失败 → SCHEMA_INVALID (400)                          │
│                                                              │
│  2. Signature Validation (如 payload 含签名字段)              │
│     └─ 失败 → SIGNATURE_INVALID (401)                       │
│                                                              │
│  3. Nonce/Challenge Validation (如 payload 含 nonce 字段)    │
│     └─ 失败 → CHALLENGE_EXPIRED / REPLAY_DETECTED (401)     │
│                                                              │
│  4. Node Registry Validation (如 context.node_id 非空)       │
│     └─ 失败 → NODE_UNTRUSTED (403)                          │
│                                                              │
│  5. Constitution Rule Validation                             │
│     └─ 失败 → CONSTITUTION_VIOLATION (403)                  │
│                                                              │
│  6. All Pass → ALLOW (200)                                  │
└─────────────────────────────────────────────────────────────┘
```

**关键原则**：
- 任何一步失败，立即返回 DENY，**不继续后续检查**
- 所有决策必须记录审计字段
- Fail-closed：遇到未知错误默认 DENY

---

## 3. Fail-Closed 拒绝策略

### 3.1 拒绝条件清单

| # | 拒绝条件 | 错误码 | HTTP 状态 | 说明 |
|---|---------|-------|----------|------|
| 1 | Schema 非法 | `SCHEMA_INVALID` | 400 | payload 不符合预期 schema |
| 2 | 签名缺失 | `SIGNATURE_MISSING` | 401 | 需要签名但未提供 |
| 3 | 签名无效 | `SIGNATURE_INVALID` | 401 | 签名验签失败 |
| 4 | Nonce 缺失 | `CHALLENGE_MISSING` | 401 | 需要 nonce 但未提供 |
| 5 | Nonce 过期 | `CHALLENGE_EXPIRED` | 401 | nonce 超出 TTL |
| 6 | 重放检测 | `REPLAY_DETECTED` | 401 | nonce 已被使用 |
| 7 | Node 未注册 | `NODE_UNTRUSTED` | 403 | node_id 不在 registry |
| 8 | Node 已禁用 | `NODE_DISABLED` | 403 | node 状态为 disabled |
| 9 | Constitution 违规 | `CONSTITUTION_VIOLATION` | 403 | 违反宪法规则 |
| 10 | 未知错误 | `INTERNAL_ERROR` | 500 | 未知异常，默认拒绝 |

### 3.2 Fail-Closed 默认行为

```python
def policy_check(entry_point: EntryPoint, payload: dict, context: PolicyContext) -> PolicyDecision:
    try:
        # Step 1-5 校验逻辑
        ...
    except Exception as e:
        # Fail-Closed: 任何未处理异常均返回 DENY
        return PolicyDecision(
            decision=DecisionType.DENY,
            trace_id=context.trace_id,
            policy_version="fail-closed-default",
            decision_reason=f"INTERNAL_ERROR: {str(e)}",
            blocked=True,
            error_code="INTERNAL_ERROR",
            http_status=500
        )
```

### 3.3 禁止事项

| 禁止行为 | 原因 |
|---------|------|
| 禁止在 fail-closed 模式下使用 try-except 忽略错误 | 防止绕过安全检查 |
| 禁止将 policy_check 设为可选 | 所有入口必须强制执行 |
| 禁止在 DENY 后继续执行业务逻辑 | 防止降级放行 |
| 禁止移除审计字段记录 | 保证可追溯性 |

---

## 4. 审计字段标准

### 4.1 必需字段

| 字段 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| `trace_id` | string | 全局唯一追踪 ID | `550e8400-e29b-41d4-a716-446655440000` |
| `policy_version` | string | 使用的策略/宪法版本 | `constitution_v1` / `policy_v2.3` |
| `decision_reason` | string | 决策原因（可读） | `Risk score 0.85 exceeds threshold` |
| `evidence_ref` | object | 证据引用 | 见下表 |

### 4.2 EvidenceRef 结构

```json
{
  "id": "EV-20260226-001",
  "kind": "LOG",
  "locator": "logs/policy_decisions.log:1234",
  "sha256": "a1b2c3d4e5f6..."
}
```

| 字段 | 类型 | 必需 | 说明 |
|-----|------|-----|------|
| `id` | string | 是 | 证据唯一标识 |
| `kind` | enum | 是 | `LOG` / `FILE` / `DIFF` / `SNIPPET` / `URL` |
| `locator` | string | 是 | 可定位路径/行号 |
| `sha256` | string | 否 | 内容哈希（如可得则必须提供） |

### 4.3 审计日志格式

```json
{
  "timestamp": "2026-02-26T15:30:00Z",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "entry_point": "api",
  "node_id": "node-001",
  "decision": "DENY",
  "policy_version": "constitution_v1",
  "decision_reason": "SIGNATURE_INVALID: signature verification failed",
  "error_code": "SIGNATURE_INVALID",
  "http_status": 401,
  "evidence_ref": {
    "id": "EV-20260226-001",
    "kind": "LOG",
    "locator": "logs/policy_decisions.log:1234",
    "sha256": "a1b2c3d4e5f6..."
  },
  "payload_hash": "sha256:abc123...",
  "duration_ms": 12
}
```

---

## 5. 入口实现指南

### 5.1 API 入口

```python
# skillforge/src/api/routes/base.py

from fastapi import Request, HTTPException
from skillforge.src.policy import policy_check, EntryPoint, PolicyContext

async def policy_middleware(request: Request, call_next):
    """API 入口策略中间件"""

    # 构建上下文
    context = PolicyContext(
        node_id=request.headers.get("X-Node-ID", ""),
        session_id=request.headers.get("X-Session-ID"),
        trace_id=request.headers.get("X-Trace-ID", generate_uuid())
    )

    # 解析 payload
    payload = await parse_request_payload(request)

    # 执行策略检查（强制第一步）
    decision = policy_check(EntryPoint.API, payload, context)

    # Fail-Closed: 非 ALLOW 立即拒绝
    if decision.decision != DecisionType.ALLOW:
        raise HTTPException(
            status_code=decision.http_status,
            detail={
                "error_code": decision.error_code,
                "trace_id": decision.trace_id,
                "reason": decision.decision_reason
            }
        )

    # 记录审计日志
    log_policy_decision(decision, payload)

    # 继续业务逻辑
    response = await call_next(request)
    return response
```

### 5.2 CLI 入口

```python
# skillforge/src/cli.py

import click
from skillforge.src.policy import policy_check, EntryPoint, PolicyContext

def policy_guard(func):
    """CLI 入口策略装饰器"""
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        # 构建上下文
        context = PolicyContext(
            node_id=getenv("NODE_ID", "cli-local"),
            trace_id=generate_uuid()
        )

        # 解析 CLI 参数为 payload
        payload = {
            "command": ctx.command.name,
            "args": args,
            "kwargs": kwargs
        }

        # 执行策略检查（强制第一步）
        decision = policy_check(EntryPoint.CLI, payload, context)

        # Fail-Closed: 非 ALLOW 立即退出
        if decision.decision != DecisionType.ALLOW:
            click.echo(f"Error: {decision.decision_reason}", err=True)
            click.echo(f"Trace ID: {decision.trace_id}", err=True)
            ctx.exit(decision.http_status // 100)  # 4xx → 1, 5xx → 5

        # 记录审计日志
        log_policy_decision(decision, payload)

        return func(*args, **kwargs)
    return wrapper

@click.command()
@policy_guard
def skill_run(skill_id: str):
    """运行 Skill（受 policy_check 保护）"""
    ...
```

### 5.3 Worker 入口

```python
# skillforge/src/workers/base.py

from celery import Celery
from skillforge.src.policy import policy_check, EntryPoint, PolicyContext

app = Celery('skillforge')

@app.task(bind=True)
def policy_guard_task(self, *args, **kwargs):
    """Worker 入口策略装饰器"""

    # 构建上下文
    context = PolicyContext(
        node_id=getenv("NODE_ID", f"worker-{self.request.hostname}"),
        session_id=self.request.id,
        trace_id=generate_uuid()
    )

    # 解析任务参数为 payload
    payload = {
        "task_name": self.request.task,
        "args": args,
        "kwargs": kwargs
    }

    # 执行策略检查（强制第一步）
    decision = policy_check(EntryPoint.WORKER, payload, context)

    # Fail-Closed: 非 ALLOW 立即失败
    if decision.decision != DecisionType.ALLOW:
        # 记录失败原因
        log_policy_decision(decision, payload)
        raise PolicyCheckFailedError(
            decision.error_code,
            decision.decision_reason,
            decision.trace_id
        )

    # 记录审计日志
    log_policy_decision(decision, payload)

    return decision

def guarded_task(func):
    """受保护的任务装饰器"""
    def wrapper(*args, **kwargs):
        policy_guard_task(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapper

@app.task
@guarded_task
def process_skill(skill_id: str, payload: dict):
    """处理 Skill（受 policy_check 保护）"""
    ...
```

---

## 6. 与后续 ISSUE 的接口预留

| ISSUE | 接口 | 状态 | 说明 |
|-------|-----|------|------|
| ISSUE-01 | `canonical_json()` | 预留 | 用于 payload hash 计算 |
| ISSUE-02 | `Envelope` / `Body` | 预留 | 用于结构化数据封装 |
| ISSUE-03 | `verify_encryption()` | 预留 | 用于混合加密验证 |
| ISSUE-04 | `verify_signature()` | 预留 | 用于 Ed25519 签名验证 |
| ISSUE-05 | `verify_nonce()` | 预留 | 用于 Nonce challenge 验证 |
| ISSUE-06 | `lookup_node()` | 预留 | 用于 Node Registry 查询 |

### 6.1 接口占位符

```python
# skillforge/src/policy/checks.py

def check_schema(payload: dict, schema_ref: str) -> tuple[bool, str]:
    """Schema 校验（当前实现：基础校验）"""
    # TODO: ISSUE-02 后对接完整 schema 校验
    if not isinstance(payload, dict):
        return False, "Payload must be a dict"
    return True, ""

def check_signature(payload: dict) -> tuple[bool, str]:
    """签名校验（占位符，ISSUE-04 实现）"""
    # 当前：不强制签名
    return True, ""

def check_nonce(payload: dict) -> tuple[bool, str]:
    """Nonce 校验（占位符，ISSUE-05 实现）"""
    # 当前：不强制 nonce
    return True, ""

def check_node_registry(node_id: str) -> tuple[bool, str]:
    """Node Registry 校验（占位符，ISSUE-06 实现）"""
    # 当前：信任所有 node_id
    return True, ""

def check_constitution(payload: dict) -> tuple[bool, str]:
    """Constitution 规则校验（已实现）"""
    from skillforge.src.nodes.constitution_gate import ConstitutionGate
    gate = ConstitutionGate()
    result = gate.execute({"skill_compose": {"skill_spec": payload}})
    if result["decision"] == "DENY":
        return False, result["reason"]
    return True, ""
```

---

## 7. 验收清单

### 7.1 ISSUE-00 验收标准映射

| 验收标准 | 实现状态 | 证据 |
|---------|---------|------|
| 任意入口（API/CLI/worker）均先执行 `policy_check` | ✅ 定义完成 | §5 入口实现指南 |
| 缺签名/缺 nonce/schema 非法/node 未注册一律拒绝 | ✅ 定义完成 | §3 Fail-Closed 拒绝策略 |
| 每次决策记录 `trace_id/policy_version/decision_reason/evidence_ref` | ✅ 定义完成 | §4 审计字段标准 |

### 7.2 自动化验收命令

```bash
# 检查文档存在
test -f docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md

# 检查 policy_check 定义
rg "def policy_check" docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md

# 检查 fail-closed 定义
rg "fail-closed|Fail-Closed|FAIL_CLOSED" docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md

# 检查审计字段
rg "trace_id|policy_version|decision_reason|evidence_ref" docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md

# 检查入口指南
rg "API 入口|CLI 入口|Worker 入口" docs/2026-02-26/p0-governed-execution/verification/T01_policy_baseline.md
```

---

## 8. 附录

### 8.1 相关文档

- [EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md](../../2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md)
- [EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md](../../../EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md)
- [multi-ai-collaboration.md](../../../multi-ai-collaboration.md)
- [constitution_v1.md](../../2026-02-16/constitution_v1.md)

### 8.2 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|-----|------|---------|------|
| v1.0 | 2026-02-26 | 初始版本 | Antigravity-2 |

---

*Document created under T01 governance process: Review → Compliance → Execution*
*EvidenceRef: EV-T01-DELIVERABLE-001*
