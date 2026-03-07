# GM-SkillForge 全局架构审查报告

> **审查者身份**：世界级软件架构师（Google/Meta/Amazon 级别 Distinguished Engineer 视角）
> **审查时间**：2026-03-06
> **审查范围**：全库完整扫描（51 个子目录，45+ 关键文件，核心路径精读）

---

## 推理链（审查前置思维展示）

我的审查按如下顺序推理：

1. **系统意图**：contracts-first 的 Skill 生产流水线：Demand DSL → Constitution Contract → 8 Gate 顺序评估 → L3 AuditPack + Permit 签发
2. **核心信任链**：三哈希绑定（demand_hash / contract_hash / decision_hash）是整个系统的信任根，一旦被绕过，所有审计都失效
3. **关键问题排查序**：API 层（surface）→ 核心引擎（trust）→ 存储 / 注册（durability）→ CI / schema（correctness）

---

## 架构总体评价

**系统设计理念是对的。** contracts-first + fail-closed + 三哈希审计链是企业级 AI-Ops 流水线的正确方向。DSL Validator 的硬校验规则、feature flags 的 fail-closed 默认、pack_and_permit 的 AuditPack 设计，这些都体现了架构师水准。

但这套设计**在实现层存在严重的"门面完整、核心空洞"问题**——外部看起来像铁板一块，内部关键路径在悄悄 ALLOW-by-default。

---

## 🔴 致命问题（必须在上线前修复，否则整个信任体系形同虚设）

---

### 🔴 ~~1. Gate Engine Fallback 是 ALLOW-by-default — 信任根被穿透~~ ✅ **FIXED** `2026-03-06T01:03Z`

**文件**：`core/gate_engine.py`，第 28–53 行

```python
try:
    from skillforge.src.orchestration.gate_engine import GateEngine
    ...
except ImportError:
    @dataclass
    class GateEngine:
        def evaluate(self, ...):
            return {
                "decision": "ALLOW",   # ← 这里是炸弹
                "reason": "Fallback gate engine - no specialized evaluator",
                ...
            }
```

**问题本质**：当 `skillforge-spec-pack` 路径不可用时（部署错误、路径变更、容器挂载失败），系统**静默降级为 ALLOW-all**。整个 8 Gate 流程、三哈希绑定、AuditPack 的审计意义全部归零。攻击者只需让 import 失败就能绕过所有门控。

**可执行修改**：

```python
# 改法：fallback 必须 DENY，不允许 ALLOW
except ImportError as exc:
    raise RuntimeError(
        f"[FATAL] GateEngine implementation not found. "
        f"Gate evaluation cannot proceed in fail-open mode. "
        f"Ensure skillforge-spec-pack is properly installed. Error: {exc}"
    ) from exc
```

如果需要"无法导入时仍能运行"，fallback 应该是：
```python
decision": "DENY",
"reason": "GateEngine not available — fail-closed by policy",
```

---

### 🔴 ~~2. simple_api.py 的 10D 认知分析是纯伪代码 — 已被发布为"真实分析"~~ ✅ **FIXED** `2026-03-06T01:07Z`

**文件**：`simple_api.py`，第 61–62 行

```python
input_hash = hashlib.md5(user_input.encode()).hexdigest()
base_score = int(input_hash[:2], 16) % 40 + 50  # 50-90基础分
```

**问题本质**：这个"10维认知分析"的评分完全由 MD5 的前两字节决定，与输入内容的实际质量**零相关**。但 API 响应包含 `model: "skillforge-10d-analyzer-v1"`, `provider: "skillforge"`，对调用方声称这是真实的 AI 分析。

这不是"MVP 简化"，这是**功能性欺骗**。如果有合同承诺或 SLA 基于这个 API，存在法律风险。

**可执行修改**：两个方向选一个——

**方向 A（诚实 MVP）**：明确标注为 mock
```python
"model": "mock-scorer-v0",
"provider": "development-only",
"warning": "This is a deterministic mock. Do not use for production decisions.",
```

**方向 B（接入真实 LLM）**：调用 OpenAI / Gemini API，传入 commit diff 和代码上下文，用 structured output 返回真实的多维评分。这是系统真正应该做的事。

---

### 🔴 ~~3. Permit 验证逻辑是长度校验 — 任何 >10 字符的字符串都能通过~~ ✅ **FIXED** `2026-03-06T01:07Z`

**文件**：`simple_api.py`，第 346 行

```python
permit_valid = len(request.permit_token) > 10  # 简单验证
```

**问题本质**：`"hello world!"` 可以通过验证。这个 API endpoint 对外暴露后，任何人只需提供 11 个字符的随机字符串就能执行工作项。Permit 体系的整个设计（三哈希绑定 + AuditPack）在 API 层被一行代码完全架空。

**可执行修改**：
```python
# 最低限度：校验 JWT 签名 + 哈希格式
import hmac, hashlib

def validate_permit_token(token: str) -> bool:
    # 至少验证：1. 格式（PERMIT-XXXXXXXX）2. 能在 permits/ 目录找到对应记录
    # 3. permit 状态为 ISSUED 且未过期
    return (
        token.startswith("PERMIT-") 
        and len(token) == 15  # PERMIT- + 8 chars
        and _permit_exists_in_store(token)  # 查询 registry/permits.jsonl
    )
```

---

### 🔴 ~~4. 外部仓库摄取缺乏 Token 防火墙 (LLM Context Exhaustion)~~ ✅ **FIXED** `2026-03-07T22:05Z`

**文件/模块**：`intake_repo` 及 LLM 直连抓取模块（如 OpenClaw 小龙虾底座）

**问题本质**：系统在拉取并分析外部代码仓库时，**完全没有进行上下文防爆（Token Sandbox/Firewall）隔离**。对于任何外部传入的不可信 Git 仓库，系统默认会进行全量文件的透传和抓取。如果遇到恶意的大型仓库（包含数万个碎文件、几百万行的日志或被故意放大的混淆源码），会瞬间打爆 LLM 的 Context Window（引发 `model_context_window_exceeded` 崩溃），导致整个处理中枢宕机。这是经典的 CWE-400（无边界不可信输入导致的资源耗竭）漏洞。

**可执行修改**：
必须在 `intake_repo` 节点和 LLM 抓取动作前架设强制“防爆盾”：
1. **绝对体积熔断**：设置单文件 Max Size (如 `50KB`)，超过直接阶段或丢弃；设定单次摄取总 Chunk Size 阈值。
2. **摄取白名单约束**：严格过滤只摄取特定后缀名（`.py`, `.js`, `.ts`, `.md` 等），强行拦截 `.png`, `.map`, `.jar` 以及 `.git/` 树。
3. **AST 骨干降级**：当遇到庞大文件时，不要完整透传源码，而是通过 Tree-sitter 等工具抽取类图和函数签名（Skeleton extraction）交由大模型评估。

---

## 🟡 重要问题（影响系统可靠性和安全边界，建议 1 个 sprint 内解决）

---

### 🟡 ~~4. CORS allow_origins=["*"] — 跨域攻击面完全开放~~ ✅ **FIXED** `2026-03-06T01:07Z`

**文件**：`simple_api.py`，第 30 行

```python
allow_origins=["*"],  # In production, restrict this
```

注释说"In production restrict this"，但没有任何机制阻止它带着这个配置上生产。feature_flags 已经有 env-aware 配置，CORS 策略应该走同样的路径。

**可执行修改**：
```python
import os
_env = os.getenv("SKILLFORGE_ENV", "unknown")
_cors_origins = {
    "prod": ["https://skillforge.genesismind.ai"],
    "staging": ["https://staging.skillforge.genesismind.ai", "http://localhost:5173"],
    "dev": ["*"],
}.get(_env, [])  # unknown 环境 → 空列表 → fail-closed

app.add_middleware(CORSMiddleware, allow_origins=_cors_origins, ...)
```

---

### 🟡 5. Registry 只有 SQLite + JSONL，无并发安全保障

**路径**：`db/skills.db` (12KB SQLite) + `registry/skills.jsonl`

SQLite 不支持多写并发。多个 Gate 并行执行时（或多实例部署时），`skills.db` 会出现 `database is locked` 错误和数据竞争。JSONL 追加写入也缺乏原子性保证。

**可执行修改（短期）**：
```python
# 在所有 DB 写操作加 WAL mode + timeout
conn = sqlite3.connect(db_path, timeout=30)
conn.execute("PRAGMA journal_mode=WAL;")
conn.execute("PRAGMA busy_timeout=5000;")
```

**可执行修改（中期）**：引入 PostgreSQL 或 Redis 替换双存储，或明确"单进程单线程"约束并在 README 写清楚。

---

### 🟡 6. pack_and_permit 的 DeliveryCompleteness 校验走 try/except 降级

**文件**：`core/pack_and_permit.py`，第 273–278 行

```python
except Exception as e:
    return {
        "valid": False,   # ← 这里还好，返回了 False
        "error": f"Delivery validation failed: {e}",
    }
```

这里的降级行为是返回 `valid: False`（fail-closed），尚可接受。但问题是：**异常被静默吞掉了**，没有日志、没有告警，运维根本不知道校验模块崩溃了。在生产环境，这会导致所有 Permit 签发请求都因"Delivery incomplete"被拒绝，且无法定位根因。

**可执行修改**：
```python
import logging
logger = logging.getLogger(__name__)

except Exception as e:
    logger.error(
        "delivery_validation_crashed",
        extra={"error": str(e), "base_path": str(base_path)},
        exc_info=True
    )
    return {"valid": False, "error": f"Delivery validation module crashed: {e}"}
```

---

### 🟡 7. 55 个 Skill 目录无统一接入点 — 技术债爆炸风险

**路径**：`skills/` 目录下 55 个 skill，其中大量名称存在语义重叠：

- `execution-guard-a-proposal-skill` vs `execution-guard-b-compliance-skill` vs `execution-guard-b-execution-skill`
- `p0-final-adjudicator-skill` vs `p1-closing-freeze-skill` vs `p2-final-gate-aggregate-skill` vs `l4-final-gate-aggregator-skill`
- `final-gate-adjudicator-skill` vs `final-gate-recheck-skill`

**问题本质**：Skills 是系统的核心扩展点，但 Registry 里只有 `skills.db`（12KB，几乎为空）和 `skills.jsonl`（253字节，2条记录）。这意味着这 55 个 skill 目录大部分**没有被注册**，处于"存在但不可寻址"的状态。

**可执行修改**：
```bash
# 1. 立即扫描并注册所有 skills
python scripts/rewrite_registry.py --scan-all --output registry/skills.jsonl

# 2. 在 skills/ 根目录建立 index.yml
# 3. 为每个 skill 建立标准 manifest.json（schema 已有 skill_audit_report.schema.json）
# 4. 删除语义重复的 skill（先合并，再删除）
```

---

## 🟢 改进建议（不紧急，但影响长期健康性）

---

### 🟢 8. requirements.txt 缺少版本锁定 — 可重现性无法保证

当前：
```
jsonschema>=4.0.0
fastapi  # ← 完全没有！simple_api 依赖 fastapi 但 requirements.txt 里没有
uvicorn  # ← 同上
```

**修改**：生成 `requirements-lock.txt`（`pip freeze > requirements-lock.txt`），CI 用锁定版本安装。FastAPI + uvicorn + pydantic 必须加入 `requirements.txt`。

---

### 🟢 9. 根目录存在 10+ 个临时脚本未清理 — 认知负担

根目录散落：`bulk_patch_imports.py`, `patch_imports.py`, `patch_script.py`, `patch_test.py`, `test_regex.py`, `test_regex2.py`, `test_regex3.py`, `create_dummy_packs.py`, `create_valid_dummy_packs.py`, `extract_template.py`, `extract_template_v2.py`, `heal_template.py`, `insert_debug.py`...

这些一次性脚本污染根目录，新人无法区分"这是核心代码"还是"这是临时工具"。

**修改**：统一移入 `scripts/oneshot/` 或 `scratch/` 并在 `.gitignore` 中标记，只保留 `scripts/` 下有明确用途的工具。

---

### 🟢 10. 缺少 API 认证层 — 当前 FastAPI 为完全开放

`simple_api.py` 的三个 endpoint 完全无认证。Permit 执行是状态变更操作，必须有身份验证。

**最简修改**：
```python
from fastapi.security import APIKeyHeader
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("SKILLFORGE_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
```

---

## 总结优先级矩阵

| # | 问题 | 风险等级 | 修复难度 | 必须上线前修复 |
|---|------|---------|---------|--------------|
| 1 | GateEngine fallback ALLOW-all | 🔴 致命 | 低（改3行）| ✅ **已修复** `2026-03-06T01:03Z` |
| 2 | 10D 分析为伪评分 | 🔴 致命 | 中（接入 LLM）| ✅ **已修复** `2026-03-06T01:07Z` |
| 3 | Permit 验证仅靠长度 | 🔴 致命 | 低（加存储查询）| ✅ **已修复** `2026-03-06T01:07Z` |
| 4 | 外部仓库缺乏 Token 防火墙 | 🔴 致命 | 中（加摄取过滤）| ✅ **已修复** `2026-03-07T22:05Z` |
| 5 | CORS allow_origins=["*"] | 🟡 重要 | 低（读 env）| ✅ **已修复** `2026-03-06T01:07Z` |
| 6 | SQLite 无并发安全 | 🟡 重要 | 中（WAL + 迁移）| ✅ **已修复** `2026-03-06T13:38Z` |
| 7 | Delivery 外检校验异常被吞 | 🟡 重要 | 低（加 logging）| ✅ **已修复** `2026-03-06T13:38Z` |
| 8 | 55 Skill 目录未注册 | 🟡 重要 | 高（需系统整理）| ✅ **已修复** `2026-03-06T13:38Z` |
| 8 | requirements.txt 不完整 | 🟢 建议 | 低 | 下个 PR |
| 9 | 根目录临时脚本堆积 | 🟢 建议 | 低 | 下个 PR |
| 10 | API 无认证层 | 🟢 建议 | 低 | 下个 PR |

---

## 架构亮点（值得保留和发扬）

1. **DSLValidator 硬校验** — 正确实现了 fail-closed 语义，10 个维度全是 BLOCKER 级别，代码质量是整个 core/ 里最好的
2. **三哈希绑定（demand/contract/decision）** — 这个设计思路一流，确保了事后可追溯和防篡改
3. **feature_flags.yml 的 fail-closed 默认** — `default_if_missing: "unknown"` 让未知环境自动走最严格策略，非常正确
4. **AuditPack 的 calculate_pack_hash()** — SHA256 内容寻址的 canonical JSON hash，抗篡改设计完整
5. **gate_plan 固定顺序** — 不允许调用方重排 8 Gate 顺序，防止绕过关键检查点

---

> **结论**：这是一个架构设计优秀、但实现层存在严重安全漏洞的系统。**3 个 🔴 致命问题必须在任何真实流量进入前修复**，否则整个审计链和许可证体系的可信度为零。结构性重构不是当务之急，当务之急是把"门面完整、核心空洞"的漏洞填上。
