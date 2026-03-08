# Phase 2 Mega Prompt — 给 Claude 4.6
# 目标：产出 SkillForge 实现层的全部接口合同 + 骨架代码
# 用法：整段复制粘贴到 Claude 4.6，它会输出所有文件

---

## 提示词正文（复制以下全部内容）

```text
你是 GM OS SkillForge 的"合同优先架构师"。你需要在已有的 gm-os-core 合同基础上，为 SkillForge 实现层（skillforge/src/）产出全部接口合同和骨架代码。

## 背景

### 项目定位
SkillForge 是一个"Skill 生产线"——可以从自然语言描述或 GitHub 仓库出发，自动生成、审计、测试、发布可信赖的 Skill。

### 已完成的工作（你不需要创建这些）
- 7 个核心 schema（gate_decision, audit_pack, registry_publish, execution_pack, trace_event, granularity_rules, common）
- 8 个 pipeline node schema（intake_repo, license_gate, repo_scan_fit_score, draft_skill_spec, constitution_risk_gate, scaffold_skill_impl, sandbox_test_and_trace, pack_audit_and_publish）
- error_codes.yml, error_policy.yml, pipeline_v0.yml
- 20 个 tech_seo_audit issue_key 在 issue_catalog.yml
- 24 个 contract_tests（全部通过）
- tech_seo_audit input/output schema

### 你需要产出的内容
在 `skillforge/src/` 下创建实现层接口。SkillForge 只依赖 gm-os-core 的 schema/error_codes，不依赖任何实现。

## 架构：双路径流水线

SkillForge 支持三种模式：
- **mode: "nl"** — 路径 A：用户提供自然语言描述 → 直接生成 Skill
- **mode: "github"** — 路径 B：用户提供 GitHub URL → 扫描优化生成 Skill  
- **mode: "auto"** — 路径 A+B：NL 解析意图 → 搜索 GitHub → 有则优化 / 无则从零生成

```
路径 A:  intent_parse → source_strategy → skill_compose → constitution_risk_gate → scaffold → sandbox → publish
路径 B:  intake_repo → license_gate → repo_scan → draft_spec → constitution_risk_gate → scaffold → sandbox → publish
路径 A+B: intent_parse → source_strategy → github_discover → intake_repo → ... → publish
```

Stage 4-7 是所有路径共享的"可信层"。

## 硬约束

1. **单向依赖**：skillforge/src/ 只能 import gm-os-core 的 schema/types，不能反向
2. **Protocol-first**：所有模块用 Python Protocol 定义接口，实现分开
3. **schema_version**：所有对外数据结构必须包含 schema_version = "0.1.0"  
4. **错误码**：只能使用 error_codes.yml 中的错误码（GATE_*, AUDIT_*, REG_*, EXEC_*, SCHEMA_*, SYS_*）
5. **trace 强制**：每个 node 执行必须产出 trace_event
6. **Python 3.11+**，类型注解完整，使用 dataclass

## 交付清单

你需要输出以下文件的完整内容（每个文件用 ```python 代码块包裹，文件路径作为注释写在第一行）：

### 1. 核心协议 (protocols.py)

文件路径: `skillforge/src/protocols.py`

定义 3 个 Python Protocol：

```python
class NodeHandler(Protocol):
    node_id: str
    stage: int
    def validate_input(self, input_data: dict) -> list[str]: ...
    def execute(self, input_data: dict) -> dict: ...
    def validate_output(self, output_data: dict) -> list[str]: ...

class GateEvaluator(Protocol):
    def evaluate(self, node_id: str, artifacts: dict) -> dict: ...  # 返回 GateDecision

class Adapter(Protocol):
    adapter_id: str
    def health_check(self) -> bool: ...
    def execute(self, action: str, params: dict) -> dict: ...
```

### 2. Pipeline Engine (engine.py)

文件路径: `skillforge/src/orchestration/engine.py`

```python
class PipelineEngine:
    """
    双路径编排引擎。

    Input Contract:
    {
        "mode": "nl" | "github" | "auto",
        "natural_language": str | None,
        "repo_url": str | None,
        "branch": str = "main",
        "options": {
            "target_environment": "python" | "node" | "docker",
            "intended_use": "automation" | "data" | "web" | "ops",
            "visibility": "public" | "private" | "team",
            "sandbox_mode": "strict" | "moderate" | "permissive"
        }
    }

    Output Contract:
    {
        "job_id": "UUID",
        "status": "completed" | "failed" | "gate_denied",
        "path_taken": "A" | "B" | "AB",
        "stages_completed": int,
        "gate_decisions": [GateDecision...],
        "audit_pack_path": str | None,
        "publish_result": PublishResult | None,
        "trace_events": [TraceEvent...],
        "duration_ms": int,
        "error": { "code": str, "message": str } | None
    }
    """
```

关键行为：
- 按 mode 决定路径（A/B/AB）
- 维护 artifacts: dict[str, Any]，每个 stage 产出存入，下一个读取
- Gate 返回 DENY → 立即终止，status = "gate_denied"
- Gate 返回 REQUIRES_CHANGES → 根据 error_policy 决定回退
- 遵循 error_policy.yml 的重试策略
- 每个 step 产出 trace_event

### 3. Node Runner (node_runner.py)

文件路径: `skillforge/src/orchestration/node_runner.py`

```python
class NodeRunner:
    """单节点执行器，附加 trace、timeout、retry"""
```

行为：
1. 加载 node schema → 校验 input
2. 调用 handler.execute(input) 
3. 校验 output
4. 产出 trace_event（start/complete/error）
5. timeout 按 pipeline_v0.yml
6. retry 按 error_policy.yml

### 4. Gate Engine (gate_engine.py)

文件路径: `skillforge/src/orchestration/gate_engine.py`

```python
class GateEngine:
    """门禁评估引擎"""
    def evaluate(self, node_id: str, artifacts: dict) -> dict: ...
```

返回标准 GateDecision 格式。

### 5. 三个适配器

#### github_fetch adapter

文件路径: `skillforge/src/adapters/github_fetch/`

三个文件：__init__.py, adapter.py, types.py

```python
@dataclass
class RepoInfo:
    name: str
    owner: str
    default_branch: str
    stars: int
    license: str | None
    last_commit_sha: str
    languages: dict[str, int]

@dataclass
class ScanResult:
    fit_score: int  # 0-100
    repo_type: str  # workflow | cli | lib | service | template
    entry_points: list[str]
    dependencies: dict[str, str]
    language_stack: str

@dataclass
class DiscoveryResult:
    candidates: list[dict]  # repo_url, stars, license, fit_score_estimate, match_reason
    selected: dict | None

class GitHubFetchAdapter:
    adapter_id = "github_fetch"
    def health_check(self) -> bool: ...
    def fetch_repo_info(self, repo_url: str) -> RepoInfo: ...
    def scan_repo_structure(self, repo_url: str, branch: str = "main") -> ScanResult: ...
    def discover_repos(self, query: str, intent: dict, max_results: int = 5) -> DiscoveryResult: ...
```

#### sandbox_runner adapter

文件路径: `skillforge/src/adapters/sandbox_runner/`

三个文件：__init__.py, adapter.py, types.py

```python
@dataclass
class SandboxConfig:
    timeout_seconds: int = 120
    max_tool_calls: int = 50
    sandbox_mode: str = "strict"  # strict | moderate | permissive
    allowed_domains: list[str] = field(default_factory=list)
    max_bytes_io: int = 10_000_000

@dataclass  
class RunResult:
    success: bool
    test_report: dict  # { total_runs, passed, failed, success_rate, avg_latency_ms, total_cost_usd }
    trace_events: list[dict]  # TraceEvent[]
    sandbox_report: dict  # resource usage, violations

class SandboxRunnerAdapter:
    adapter_id = "sandbox_runner"
    def health_check(self) -> bool: ...
    def run_in_sandbox(self, bundle_path: str, config: SandboxConfig) -> RunResult: ...
```

#### registry_client adapter

文件路径: `skillforge/src/adapters/registry_client/`

两个文件：__init__.py, adapter.py

```python
class RegistryClientAdapter:
    adapter_id = "registry_client"
    def health_check(self) -> bool: ...
    def publish(self, request: dict) -> dict: ...  # RegistryPublishRequest → RegistryPublishResult
    def check_exists(self, skill_id: str, version: str) -> bool: ...
```

### 6. 十二个节点处理器（骨架）

每个节点一个文件，位于 `skillforge/src/nodes/`。

每个节点文件包含：
- 一个实现 NodeHandler Protocol 的 class
- node_id 和 stage 属性
- validate_input / execute / validate_output 三个方法
- execute 方法内有详细的 docstring 说明 input/output contract
- 方法体用 `raise NotImplementedError("TODO: implement")` 占位

12 个节点：

| 文件名 | class | node_id | stage | 路径 |
|--------|-------|---------|-------|------|
| intent_parser.py | IntentParser | intent_parse | pre-0 | A, A+B |
| source_strategy.py | SourceStrategy | source_strategy | pre-0 | A, A+B |
| github_discover.py | GitHubDiscovery | github_discover | pre-0 | A+B |
| skill_composer.py | SkillComposer | skill_compose | A-only | A |
| intake_repo.py | IntakeRepo | intake_repo | 0 | B, A+B |
| license_gate.py | LicenseGate | license_gate | 1 | B, A+B |
| repo_scan.py | RepoScan | repo_scan_fit_score | 2 | B, A+B |
| draft_spec.py | DraftSpec | draft_skill_spec | 3 | B, A+B |
| constitution_gate.py | ConstitutionGate | constitution_risk_gate | 4 | ALL |
| scaffold_impl.py | ScaffoldImpl | scaffold_skill_impl | 5 | ALL |
| sandbox_test.py | SandboxTest | sandbox_test_and_trace | 6 | ALL |
| pack_publish.py | PackPublish | pack_audit_and_publish | 7 | ALL |

### 7. 两个新 Schema

#### pipeline_input.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PipelineInput",
  "type": "object",
  "required": ["mode"],
  "properties": {
    "mode": { "enum": ["nl", "github", "auto"] },
    "natural_language": { "type": "string" },
    "repo_url": { "type": "string", "format": "uri" },
    "branch": { "type": "string", "default": "main" },
    "options": { ... }
  },
  "allOf": [
    { "if mode=nl, then natural_language required" },
    { "if mode=github, then repo_url required" }
  ]
}
```

#### pipeline_output.schema.json

对应 Engine 的 Output Contract。

### 8. CLI 入口 (cli.py)

文件路径: `skillforge/src/cli.py`

```python
"""
Usage:
  skillforge refine --mode nl "我需要一个SEO审计工具"
  skillforge refine --mode github https://github.com/user/repo
  skillforge refine --mode auto "一个能分析网页SEO的Python工具"
"""
```

### 9. __init__.py 文件

为以下目录创建 __init__.py：
- skillforge/src/__init__.py
- skillforge/src/orchestration/__init__.py
- skillforge/src/adapters/__init__.py
- skillforge/src/adapters/github_fetch/__init__.py
- skillforge/src/adapters/sandbox_runner/__init__.py
- skillforge/src/adapters/registry_client/__init__.py
- skillforge/src/nodes/__init__.py

### 10. 合同测试 (test_protocols.py)

文件路径: `skillforge/tests/test_protocols.py`

测试内容：
1. 所有 12 个 NodeHandler 都有 node_id, stage, execute, validate_input, validate_output
2. 所有 3 个 Adapter 都有 adapter_id, health_check, execute
3. pipeline_input.schema.json / pipeline_output.schema.json 存在且合法
4. Engine 的 Input/Output 符合 schema

## 输出格式

请按以下格式输出每个文件：

```
## 文件: [相对路径]

​```python  (或 json)
[完整文件内容]
​```
```

确保：
1. 每个文件可以直接保存使用
2. import 路径正确
3. 类型注解完整
4. docstring 详细说明 input/output contract
5. 所有方法体用 NotImplementedError 占位（骨架模式）
6. 不要输出解释性长文，只给代码

一共大约 25-28 个文件。请完整输出所有文件。
```

---

## 交付后的验收标准

当你把 Claude 4.6 的输出放回项目后，我会用以下命令验收：

```bash
# 1. 文件结构完整
find skillforge/src -name "*.py" | wc -l   # 应该 >= 20

# 2. 导入不报错
python -c "from skillforge.src.protocols import NodeHandler, GateEvaluator, Adapter"

# 3. schema 校验
python tools/validate.py --all

# 4. 现有测试不退化
pytest -q   # 应该 >= 39 passed

# 5. 新增测试
pytest skillforge/tests/test_protocols.py -v
```
