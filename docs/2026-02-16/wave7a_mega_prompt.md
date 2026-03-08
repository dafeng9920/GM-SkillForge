# Wave 7A Mega Prompt — 8 剩余节点实现填充
# 目标：填充 intent_parser / source_strategy / github_discover / skill_composer / constitution_gate / scaffold_impl / sandbox_test / pack_publish
# 用法：整段复制 `## 提示词正文` 下的 code block 到 Claude 4.6

> ⚠️ 重要：Prompt 中包含 8 个骨架文件的完整内容，Claude 4.6 必须原封不动保留所有签名

---

## 提示词正文（复制以下全部内容）

```text
你是 GM OS SkillForge 的实现工程师。你需要为 8 个节点填充实现逻辑。
不要创建新文件，只输出这 8 个文件的完整替换内容。

## 硬约束

1. 不改变任何 class 签名（@dataclass）、方法签名、属性名
2. 不添加新的外部依赖（只用 Python 标准库 + 已有 import，可以 import uuid, time, hashlib, re, json）
3. validate_input() 返回 list[str]（空列表=通过，非空=错误列表）
4. validate_output() 返回 list[str]（同上）
5. execute() 返回 dict[str, Any]（符合 module-level Output Contract）
6. 错误码只能使用已定义的前缀：GATE_, AUDIT_, REG_, EXEC_, SCHEMA_, SYS_
7. 所有方法必须保留完整的 docstring
8. 保留 from __future__ import annotations
9. 每个 execute() 的实现是"可独立运行的本地逻辑"，不调用真实 HTTP API
10. 每个 node 通过 input_data[node_id] 获取前序节点的输出

## 数据传递约定（非常重要）

Pipeline 在执行节点链时，会把所有前序节点的输出合并到同一个 artifacts dict 中传给当前节点。
所以每个 node 的 input_data 不是只有自己的输入，而是整个 pipeline 的累积 artifacts。

具体来说：
- input_data["input"] = 用户最初的输入（含 natural_language, mode, repo_url 等）
- input_data["intent_parse"] = IntentParser.execute() 的输出
- input_data["source_strategy"] = SourceStrategy.execute() 的输出
- input_data["github_discover"] = GitHubDiscovery.execute() 的输出
- input_data["skill_compose"] = SkillComposer.execute() 的输出
- input_data["intake_repo"] = IntakeRepo.execute() 的输出
- input_data["draft_skill_spec"] = DraftSpec.execute() 的输出
- 供 constitution_gate 使用的 skill_spec 来自 "skill_compose" 或 "draft_skill_spec"
- input_data["constitution_risk_gate"] = ConstitutionGate.execute() 的输出
- input_data["scaffold_skill_impl"] = ScaffoldImpl.execute() 的输出
- input_data["sandbox_test_and_trace"] = SandboxTest.execute() 的输出
- 依此类推

每个 node 的 execute() 输出会以 node_id 为 key 存入 artifacts。

## ============================================================
## 以下是 8 个骨架文件的【当前完整内容】
## 你必须原封不动保留所有签名，只替换 raise NotImplementedError("TODO: implement")
## ============================================================

### 当前骨架 1: skillforge/src/nodes/intent_parser.py

```python
"""
IntentParser node — parses natural language into structured intent.

Path: A, A+B
Stage: pre-0 (-1)

Input Contract
--------------
{
    "natural_language": str,
    "options": { ... }   # pipeline options
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "intent": {
        "goal": str,
        "domain": str,
        "actions": list[str],
        "constraints": list[str],
        "target_environment": str,
        "intended_use": str
    },
    "confidence": float,   # 0.0 - 1.0
    "raw_input": str
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class IntentParser:
    """Parse natural-language skill descriptions into structured intent."""

    node_id: str = "intent_parse"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate that natural_language is present and non-empty."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Parse the natural language description into a structured intent dict.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate output against intent schema."""
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 2: skillforge/src/nodes/source_strategy.py

```python
"""
SourceStrategy node — decides whether to generate from scratch or search GitHub.

Path: A, A+B
Stage: pre-0 (-1)

Input Contract
--------------
{
    "intent": { ... },       # from IntentParser
    "mode": "nl" | "auto",
    "confidence": float
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "strategy": "generate" | "search_github" | "hybrid",
    "search_query": str | None,      # set when strategy includes github search
    "generation_hints": dict | None,  # set when strategy includes generation
    "reason": str
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SourceStrategy:
    """Decide source strategy based on parsed intent and mode."""

    node_id: str = "source_strategy"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate that intent and mode are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Determine source strategy.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate strategy output."""
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 3: skillforge/src/nodes/github_discover.py

```python
"""
GitHubDiscovery node — search GitHub for candidate repos matching intent.

Path: A+B only
Stage: pre-0 (-1)

Input Contract
--------------
{
    "search_query": str,
    "intent": { ... },
    "max_results": int       # default 5
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "candidates": [
        {
            "repo_url": str,
            "stars": int,
            "license": str | None,
            "fit_score_estimate": int,
            "match_reason": str
        }
    ],
    "selected": {
        "repo_url": str,
        "reason": str
    } | None,
    "fallback_to_generate": bool
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GitHubDiscovery:
    """Search GitHub for repos that match the parsed intent."""

    node_id: str = "github_discover"
    stage: int = -1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate search_query and intent are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Search GitHub and rank candidate repos.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate discovery output."""
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 4: skillforge/src/nodes/skill_composer.py

```python
"""
SkillComposer node — generate a skill spec from intent (no repo source).

Path: A only
Stage: A-only (stage index 1 within path A context)

Input Contract
--------------
{
    "intent": { ... },
    "generation_hints": dict | None,
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "skill_spec": {
        "name": str,
        "version": str,
        "description": str,
        "inputs": list[dict],
        "outputs": list[dict],
        "tools_required": list[str],
        "steps": list[dict],
        "constraints": list[str]
    },
    "source": "generated",
    "confidence": float
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SkillComposer:
    """Compose a skill specification directly from parsed intent."""

    node_id: str = "skill_compose"
    stage: int = -1  # A-only pre-shared stage

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate intent presence."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate a skill specification from intent.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate generated skill spec."""
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 5: skillforge/src/nodes/constitution_gate.py

```python
"""
ConstitutionGate node — risk assessment gate for skill safety and alignment.

Path: ALL
Stage: 4

Input Contract (conforms to gm-os-core constitution_risk_gate.schema.json)
--------------
{
    "skill_spec": { ... },      # from SkillComposer or DraftSpec
    "options": { ... }
}

Output Contract (GateDecision)
---------------
{
    "schema_version": "0.1.0",
    "gate_id": "constitution_risk_gate",
    "node_id": "constitution_risk_gate",
    "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
    "reason": str,
    "details": {
        "risk_score": float,        # 0.0 - 1.0
        "risk_categories": list[str],
        "mitigations_required": list[str],
        "constitution_version": str
    },
    "timestamp": str
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ConstitutionGate:
    """Evaluate skill spec against the GM OS constitution for safety and alignment."""

    node_id: str = "constitution_risk_gate"
    stage: int = 4

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate skill_spec is present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate skill spec against constitution risk criteria.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract (GateDecision).
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate GateDecision structure."""
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 6: skillforge/src/nodes/scaffold_impl.py

```python
"""
ScaffoldImpl node — generate skill implementation code from spec.

Path: ALL
Stage: 5

Input Contract (conforms to gm-os-core scaffold_skill_impl.schema.json)
--------------
{
    "skill_spec": { ... },
    "gate_decision": { ... },   # from ConstitutionGate (must be ALLOW)
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "bundle_path": str,         # path to generated skill bundle
    "files_generated": list[str],
    "entry_point": str,
    "language": str,
    "test_file": str | None,
    "manifest": {
        "skill_id": str,
        "version": str,
        "checksum": str
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ScaffoldImpl:
    """Generate skill implementation scaffolding from a validated spec."""

    node_id: str = "scaffold_skill_impl"
    stage: int = 5

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate skill_spec and gate_decision (ALLOW) are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate skill implementation bundle.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate scaffold output."""
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 7: skillforge/src/nodes/sandbox_test.py

```python
"""
SandboxTest node — run skill in sandbox and collect trace.

Path: ALL
Stage: 6

Input Contract (conforms to gm-os-core sandbox_test_and_trace.schema.json)
--------------
{
    "bundle_path": str,
    "skill_spec": { ... },
    "options": {
        "sandbox_mode": "strict" | "moderate" | "permissive",
        "timeout_seconds": int
    }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "success": bool,
    "test_report": {
        "total_runs": int,
        "passed": int,
        "failed": int,
        "success_rate": float,
        "avg_latency_ms": float,
        "total_cost_usd": float
    },
    "trace_events": [TraceEvent...],
    "sandbox_report": {
        "cpu_time_ms": int,
        "memory_peak_mb": float,
        "violations": list[str]
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SandboxTest:
    """Run skill bundle in sandbox and collect test results and traces."""

    node_id: str = "sandbox_test_and_trace"
    stage: int = 6

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate bundle_path is present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute skill in sandbox, run tests, collect trace.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate sandbox test output."""
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 8: skillforge/src/nodes/pack_publish.py

```python
"""
PackPublish node — build audit pack and publish to registry.

Path: ALL
Stage: 7

Input Contract (conforms to gm-os-core pack_audit_and_publish.schema.json)
--------------
{
    "bundle_path": str,
    "skill_spec": { ... },
    "test_report": { ... },
    "gate_decisions": [GateDecision...],
    "trace_events": [TraceEvent...],
    "options": {
        "visibility": "public" | "private" | "team"
    }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "audit_pack": {
        "audit_id": str,
        "skill_id": str,
        "version": str,
        "gate_decisions": [GateDecision...],
        "test_report": { ... },
        "trace_summary": { ... },
        "created_at": str
    },
    "audit_pack_path": str,
    "publish_result": {
        "skill_id": str,
        "version": str,
        "status": "published" | "rejected",
        "registry_url": str,
        "timestamp": str
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PackPublish:
    """Build the audit pack and publish the skill to the registry."""

    node_id: str = "pack_audit_and_publish"
    stage: int = 7

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate bundle_path, skill_spec, test_report are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Build audit pack and publish skill.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate publish output."""
        raise NotImplementedError("TODO: implement")
```

## ============================================================
## 以下是每个方法的具体实现要求
## ============================================================

## 文件 1：intent_parser.py

路径：skillforge/src/nodes/intent_parser.py

### validate_input 要求
- 从 input_data["input"] 获取 natural_language
- 必须存在且非空字符串
- 返回 list[str] 错误列表

### execute 要求
- import re 在文件顶部
- 从 input_data["input"] 获取 natural_language
- 使用关键词匹配进行 mock 解析：
  - goal: 从 natural_language 中截取前 100 字符作为 goal
  - domain: 基于关键词推断 — 含 "data" → "data_processing"; 含 "web" → "web_service"; 含 "ml"/"ai" → "machine_learning"; 默认 → "general"
  - actions: 从文本中提取动词关键词 ["analyze", "process", "generate", "transform", "compute"]，匹配到的放入列表
  - constraints: []（mock）
  - target_environment: "python" (默认 mock)
  - intended_use: "automation"
- confidence: 0.75（mock 固定值）
- raw_input: natural_language

### validate_output 要求
- 检查 schema_version, intent, confidence, raw_input 全部存在
- intent 必须包含 goal, domain
- confidence 在 0.0-1.0 之间

## 文件 2：source_strategy.py

路径：skillforge/src/nodes/source_strategy.py

### validate_input 要求
- 从 input_data["intent_parse"] 获取 intent_parse 输出
- 如果不存在：返回 "intent_parse output is required"

### execute 要求
- 从 input_data["intent_parse"] 获取 intent 和 confidence
- 从 input_data["input"] 获取 mode (默认 "nl")
- 策略决定规则：
  - mode == "github" → strategy = "search_github"
  - mode == "nl" 且 confidence > 0.8 → strategy = "generate"
  - mode == "auto" → strategy = "hybrid"
  - 默认 → strategy = "generate"
- search_query: 如果 strategy 含 github/hybrid → 从 intent["goal"] 取前 50 字符; 否则 None
- generation_hints: 如果 strategy 含 generate/hybrid → {"domain": intent["domain"], "actions": intent.get("actions", [])}; 否则 None
- reason: 描述策略选择原因

### validate_output 要求
- 检查 schema_version, strategy, reason 全部存在
- strategy 在 ["generate", "search_github", "hybrid"] 中

## 文件 3：github_discover.py

路径：skillforge/src/nodes/github_discover.py

### validate_input 要求
- 从 input_data["source_strategy"] 获取 source_strategy 输出
- 如果不存在：返回 "source_strategy output is required"
- 检查 source_strategy 的 search_query 存在

### execute 要求
- 从 input_data["source_strategy"] 获取 search_query
- 从 input_data["intent_parse"] 获取 intent
- max_results 默认 5
- 生成 mock候选列表（1-3 个固定 mock 候选）：
  - 每个候选: { repo_url: "https://github.com/mock-org/mock-{i}", stars: 100*(i+1), license: "MIT", fit_score_estimate: 70-i*10, match_reason: f"Matches intent domain: {intent['domain']}" }
- selected: 选择第一个候选
- fallback_to_generate: False（如果有候选）

### validate_output 要求
- 检查 schema_version, candidates, fallback_to_generate 全部存在
- candidates 必须为 list

## 文件 4：skill_composer.py

路径：skillforge/src/nodes/skill_composer.py

### validate_input 要求
- 从 input_data["intent_parse"] 获取 intent_parse 输出
- 如果不存在：返回 "intent_parse output is required"

### execute 要求
- 从 input_data["intent_parse"] 获取 intent
- 从 input_data.get("source_strategy", {}) 获取 generation_hints（可选）
- 构建 skill_spec 类似于 DraftSpec，但 source = "generated"：
  - name: f"skill-{intent['domain']}-{intent['goal'][:20].replace(' ', '-').lower()}"
  - version: "0.1.0"
  - description: intent["goal"]
  - inputs: [{"name": "input_data", "type": "object", "required": True}]
  - outputs: [{"name": "result", "type": "object"}]
  - tools_required: 基于 intent.get("target_environment", "python") 推断
  - steps: [{"id": "step_1", "action": "execute", "description": f"Execute {intent['goal'][:50]}"}]
  - constraints: intent.get("constraints", []) + ["risk_tier: L1"]
- source: "generated"
- confidence: intent_parse 的 confidence * 0.9

### validate_output 要求
- 检查 schema_version, skill_spec, source, confidence 全部存在
- skill_spec 必须包含 name, version, description
- source 必须为 "generated"

## 文件 5：constitution_gate.py

路径：skillforge/src/nodes/constitution_gate.py

### validate_input 要求
- 从 input_data 中寻找 skill_spec（来自 "skill_compose" 或 "draft_skill_spec"）
- 如果两者都不存在：返回 "skill_spec source is required (from skill_compose or draft_skill_spec)"

### execute 要求
- import time, uuid 在文件顶部
- 从 artifacts 获取 skill_spec（先查 skill_compose，再查 draft_skill_spec）
- 获取 options (input_data.get("input", {}).get("options", {}))
- sandbox_mode = options.get("sandbox_mode", "strict")
- 风险评估规则：
  - risk_categories: []
  - risk_score: 0.0
  - 如果 skill_spec 的 constraints 含 "L2" 或 "L3" → risk_score += 0.3, 加 "elevated_risk_tier"
  - 如果 skill_spec 的 tools_required 含 "subprocess" 或任何含 "shell" 的 → risk_score += 0.3, 加 "subprocess_access"
  - 如果 intent（从 intent_parse 获取）的 domain == "machine_learning" → risk_score += 0.1, 加 "ml_compute"
- 决定规则：
  - risk_score >= 0.7 → DENY
  - risk_score >= 0.3 → REQUIRES_CHANGES
  - 否则 → ALLOW
- mitigations_required: 如果 REQUIRES_CHANGES → ["Review subprocess usage", "Add resource limits"]
- 返回完整 GateDecision dict

### validate_output 要求
- 同 license_gate 的 validate_output 模式
- 额外检查 details 中有 risk_score, risk_categories, constitution_version

## 文件 6：scaffold_impl.py

路径：skillforge/src/nodes/scaffold_impl.py

### validate_input 要求
- 获取 skill_spec（从 skill_compose 或 draft_skill_spec）
- 获取 gate_decision（从 constitution_risk_gate）
- gate_decision.decision 必须为 "ALLOW"，否则返回 "Constitution gate must ALLOW before scaffolding"

### execute 要求
- import hashlib, uuid 在文件顶部
- 从 skill_spec 获取 name, version 等
- mock 实现（不创建真实文件）：
  - bundle_path: f"/tmp/skillforge/bundles/{skill_name}"
  - entry_point: "main.py"
  - language: skill_spec 的 tools_required 推断（有 python3 → Python; 有 node → JavaScript; 默认 Python）
  - files_generated: [f"{skill_name}/main.py", f"{skill_name}/manifest.json", f"{skill_name}/README.md"]
  - test_file: f"{skill_name}/test_skill.py"
  - manifest: { skill_id: skill_name, version: version, checksum: hashlib.sha256(skill_name.encode()).hexdigest()[:16] }

### validate_output 要求
- 检查 schema_version, bundle_path, files_generated, entry_point, manifest 全部存在
- manifest 必须包含 skill_id, version, checksum

## 文件 7：sandbox_test.py

路径：skillforge/src/nodes/sandbox_test.py

### validate_input 要求
- 从 input_data["scaffold_skill_impl"] 获取 scaffold 输出
- 如果不存在：返回 "scaffold_skill_impl output is required"
- 检查 bundle_path 存在

### execute 要求
- import time, uuid 在文件顶部
- 从 input_data["scaffold_skill_impl"] 获取 bundle_path
- mock 沙箱测试（不执行真实代码）：
  - success: True
  - test_report: { total_runs: 3, passed: 3, failed: 0, success_rate: 1.0, avg_latency_ms: 42.5, total_cost_usd: 0.001 }
  - trace_events: 生成 1 个 mock trace event: { event_id: uuid4, event_type: "sandbox_run", timestamp: ISO-8601, node_id: self.node_id, status: "completed", duration_ms: 42.5 }
  - sandbox_report: { cpu_time_ms: 85, memory_peak_mb: 12.3, violations: [] }

### validate_output 要求
- 检查 schema_version, success, test_report, sandbox_report 全部存在
- test_report 必须包含 total_runs, passed, failed
- success 必须是 bool

## 文件 8：pack_publish.py

路径：skillforge/src/nodes/pack_publish.py

### validate_input 要求
- 从 input_data 获取 scaffold_skill_impl 和 sandbox_test_and_trace 输出
- 两者任缺其一都返回错误
- 获取 skill_spec（从 skill_compose 或 draft_skill_spec）

### execute 要求
- import time, uuid, json 在文件顶部
- 从各 artifacts 获取必要信息：
  - scaffold = input_data["scaffold_skill_impl"]
  - sandbox = input_data["sandbox_test_and_trace"]
  - skill_spec（从 skill_compose 或 draft_skill_spec 获取）
  - 所有 gate_decisions = 从 artifacts 中收集所有 gate 输出（license_gate, constitution_risk_gate 的输出）
- 构筑 audit_pack:
  - audit_id: "audit-" + uuid4()[:8]
  - skill_id: skill_spec 的 name
  - version: skill_spec 的 version
  - gate_decisions: 收集的 gate decisions 列表
  - test_report: sandbox 的 test_report
  - trace_summary: { total_events: len(sandbox["trace_events"]), node_id: self.node_id }
  - created_at: ISO-8601 时间
- audit_pack_path: f"/tmp/skillforge/audit/{audit_id}.json"
- publish_result:
  - skill_id, version 同上
  - status: 如果 sandbox["success"] → "published"; 否则 "rejected"
  - registry_url: f"http://localhost:8080/skills/{skill_id}/{version}"
  - timestamp: ISO-8601

### validate_output 要求
- 检查 schema_version, audit_pack, publish_result 全部存在
- audit_pack 必须包含 audit_id, skill_id, version
- publish_result.status 在 ["published", "rejected"] 中

## 输出格式

请按以下格式输出每个文件：

## 文件: [相对路径]

```python
[完整文件内容，包括 module docstring、所有 import、class 定义和方法]
```

一共 8 个代码文件。请完整输出，不要省略任何内容。
```

---

## 交付后验收标准

```bash
cd D:\GM-SkillForge\skillforge-spec-pack

# 1. 现有测试不退化
pytest -q                          # >= 39 passed

# 2. IntentParser 单元测试
python -c "
from skillforge.src.nodes.intent_parser import IntentParser
ip = IntentParser()
errors = ip.validate_input({'input': {'natural_language': 'Build a data processing pipeline'}})
print(f'validate_input errors: {errors}')
result = ip.execute({'input': {'natural_language': 'Build a data processing pipeline'}})
print(f'domain={result[\"intent\"][\"domain\"]}, confidence={result[\"confidence\"]}')
"

# 3. Path A 链路测试（intent → strategy → composer → constitution → scaffold → sandbox → pack）
python -c "
from skillforge.src.nodes.intent_parser import IntentParser
from skillforge.src.nodes.source_strategy import SourceStrategy
from skillforge.src.nodes.skill_composer import SkillComposer
from skillforge.src.nodes.constitution_gate import ConstitutionGate
from skillforge.src.nodes.scaffold_impl import ScaffoldImpl
from skillforge.src.nodes.sandbox_test import SandboxTest
from skillforge.src.nodes.pack_publish import PackPublish

artifacts = {'input': {'mode': 'nl', 'natural_language': 'Build a data processing pipeline'}}

ip = IntentParser()
artifacts['intent_parse'] = ip.execute(artifacts)
print(f'intent: domain={artifacts[\"intent_parse\"][\"intent\"][\"domain\"]}')

ss = SourceStrategy()
artifacts['source_strategy'] = ss.execute(artifacts)
print(f'strategy: {artifacts[\"source_strategy\"][\"strategy\"]}')

sc = SkillComposer()
artifacts['skill_compose'] = sc.execute(artifacts)
print(f'compose: name={artifacts[\"skill_compose\"][\"skill_spec\"][\"name\"]}')

cg = ConstitutionGate()
artifacts['constitution_risk_gate'] = cg.execute(artifacts)
print(f'constitution: decision={artifacts[\"constitution_risk_gate\"][\"decision\"]}')

si = ScaffoldImpl()
artifacts['scaffold_skill_impl'] = si.execute(artifacts)
print(f'scaffold: bundle={artifacts[\"scaffold_skill_impl\"][\"bundle_path\"]}')

st = SandboxTest()
artifacts['sandbox_test_and_trace'] = st.execute(artifacts)
print(f'sandbox: success={artifacts[\"sandbox_test_and_trace\"][\"success\"]}')

pp = PackPublish()
artifacts['pack_audit_and_publish'] = pp.execute(artifacts)
print(f'publish: status={artifacts[\"pack_audit_and_publish\"][\"publish_result\"][\"status\"]}')
print('PATH A chain: OK')
"

# 4. validate.py 不退化
python tools/validate.py --all
```
