# Wave 7B Mega Prompt — 3 Adapter 实现填充
# 目标：填充 github_fetch / sandbox_runner / registry_client adapter
# 用法：整段复制 `## 提示词正文` 下的 code block 到 Claude 4.6

> ⚠️ 重要：Prompt 中包含 3 个 adapter 骨架文件 + 类型文件的完整内容

---

## 提示词正文（复制以下全部内容）

```text
你是 GM OS SkillForge 的实现工程师。你需要为 3 个 Adapter 填充实现逻辑。
不要创建新文件，只输出这 3 个 adapter.py 文件的完整替换内容。
不要修改 types.py 文件。

## 硬约束

1. 不改变任何 class 签名（@dataclass）、方法签名、属性名
2. 不添加新的外部依赖（只用 Python 标准库 + 已有 import，可以 import uuid, time, hashlib）
3. 保留 from __future__ import annotations
4. 所有方法必须保留完整的 docstring
5. 每个 adapter 的实现是"可独立运行的本地 mock 逻辑"，不调用真实 HTTP API
6. health_check() 始终返回 True (mock)
7. execute() 是 action dispatch，根据 action 参数调用对应方法
8. 必须使用 types.py 中定义的 dataclass 作为返回类型

## ============================================================
## 以下是骨架文件和类型文件的【当前完整内容】
## ============================================================

### 类型文件 1: skillforge/src/adapters/github_fetch/types.py（只读参考，不要修改）

```python
"""Data types for the GitHub fetch adapter."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RepoInfo:
    """Basic metadata about a GitHub repository."""

    name: str
    owner: str
    default_branch: str
    stars: int
    license: str | None
    last_commit_sha: str
    languages: dict[str, int] = field(default_factory=dict)


@dataclass
class ScanResult:
    """Structural scan result for a repository."""

    fit_score: int  # 0-100
    repo_type: str  # workflow | cli | lib | service | template
    entry_points: list[str] = field(default_factory=list)
    dependencies: dict[str, str] = field(default_factory=dict)
    language_stack: str = ""


@dataclass
class DiscoveryResult:
    """Result of searching GitHub for candidate repos."""

    candidates: list[dict[str, object]] = field(default_factory=list)
    # Each candidate: { repo_url, stars, license, fit_score_estimate, match_reason }
    selected: dict[str, object] | None = None
```

### 类型文件 2: skillforge/src/adapters/sandbox_runner/types.py（只读参考，不要修改）

```python
"""Data types for the sandbox runner adapter."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SandboxConfig:
    """Configuration for a sandboxed skill execution."""

    timeout_seconds: int = 120
    max_tool_calls: int = 50
    sandbox_mode: str = "strict"  # strict | moderate | permissive
    allowed_domains: list[str] = field(default_factory=list)
    max_bytes_io: int = 10_000_000


@dataclass
class RunResult:
    """Result of running a skill bundle in the sandbox."""

    success: bool = False
    test_report: dict[str, object] = field(default_factory=dict)
    # test_report keys: total_runs, passed, failed, success_rate, avg_latency_ms, total_cost_usd
    trace_events: list[dict[str, object]] = field(default_factory=list)
    sandbox_report: dict[str, object] = field(default_factory=dict)
    # sandbox_report keys: cpu_time_ms, memory_peak_mb, violations
```

### 当前骨架 1: skillforge/src/adapters/github_fetch/adapter.py

```python
"""
GitHubFetchAdapter — interacts with GitHub API for repo info, scanning, discovery.

All methods return typed dataclasses or raise RuntimeError on failure.
Error codes used: SYS_ADAPTER_UNAVAILABLE, SYS_TIMEOUT.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from skillforge.src.adapters.github_fetch.types import (
    DiscoveryResult,
    RepoInfo,
    ScanResult,
)


@dataclass
class GitHubFetchAdapter:
    """
    Adapter for GitHub repository operations.

    Attributes:
        adapter_id: Unique adapter identifier.
        api_base_url: GitHub API base URL.
        token: Optional GitHub personal access token.
    """

    adapter_id: str = "github_fetch"
    api_base_url: str = "https://api.github.com"
    token: str | None = None

    def health_check(self) -> bool:
        """Return True if the GitHub API is reachable."""
        raise NotImplementedError("TODO: implement")

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic dispatch. Supported actions: fetch_repo_info, scan_repo_structure, discover_repos.
        """
        raise NotImplementedError("TODO: implement")

    def fetch_repo_info(self, repo_url: str) -> RepoInfo:
        """
        Fetch basic metadata for a GitHub repository.

        Args:
            repo_url: Full GitHub URL (e.g. https://github.com/owner/repo).

        Returns:
            RepoInfo dataclass.
        """
        raise NotImplementedError("TODO: implement")

    def scan_repo_structure(self, repo_url: str, branch: str = "main") -> ScanResult:
        """
        Scan repository structure and compute fit_score.

        Args:
            repo_url: Full GitHub URL.
            branch: Branch to scan.

        Returns:
            ScanResult dataclass with fit_score 0-100.
        """
        raise NotImplementedError("TODO: implement")

    def discover_repos(
        self, query: str, intent: dict[str, Any], max_results: int = 5
    ) -> DiscoveryResult:
        """
        Search GitHub for candidate repos matching a natural-language intent.

        Args:
            query: Search query string.
            intent: Parsed intent dict from IntentParser.
            max_results: Maximum candidates to return.

        Returns:
            DiscoveryResult with ranked candidates.
        """
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 2: skillforge/src/adapters/sandbox_runner/adapter.py

```python
"""
SandboxRunnerAdapter — runs skill bundles in an isolated sandbox.

Error codes used: EXEC_SANDBOX_VIOLATION, EXEC_TIMEOUT, SYS_ADAPTER_UNAVAILABLE.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from skillforge.src.adapters.sandbox_runner.types import RunResult, SandboxConfig


@dataclass
class SandboxRunnerAdapter:
    """
    Adapter for isolated skill execution and testing.

    Attributes:
        adapter_id: Unique adapter identifier.
    """

    adapter_id: str = "sandbox_runner"

    def health_check(self) -> bool:
        """Return True if the sandbox runtime is available."""
        raise NotImplementedError("TODO: implement")

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic dispatch. Supported actions: run_in_sandbox.
        """
        raise NotImplementedError("TODO: implement")

    def run_in_sandbox(self, bundle_path: str, config: SandboxConfig) -> RunResult:
        """
        Execute a skill bundle inside the sandbox.

        Args:
            bundle_path: Path to the skill bundle directory or archive.
            config: SandboxConfig controlling limits and permissions.

        Returns:
            RunResult with test_report, trace_events, and sandbox_report.
        """
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 3: skillforge/src/adapters/registry_client/adapter.py

```python
"""
RegistryClientAdapter — publish skills to and query the GM OS skill registry.

Error codes used: REG_DUPLICATE, REG_VALIDATION_FAILED, SYS_ADAPTER_UNAVAILABLE.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RegistryClientAdapter:
    """
    Adapter for the skill registry.

    Attributes:
        adapter_id: Unique adapter identifier.
        registry_url: Base URL of the registry service.
    """

    adapter_id: str = "registry_client"
    registry_url: str = "http://localhost:8080"

    def health_check(self) -> bool:
        """Return True if the registry service is reachable."""
        raise NotImplementedError("TODO: implement")

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Generic dispatch. Supported actions: publish, check_exists.
        """
        raise NotImplementedError("TODO: implement")

    def publish(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Publish a skill to the registry.

        Args:
            request: Dict conforming to gm-os-core registry_publish.schema.json
                     (RegistryPublishRequest).

        Returns:
            Dict conforming to RegistryPublishResult:
            {
                "schema_version": "0.1.0",
                "skill_id": str,
                "version": str,
                "status": "published" | "rejected",
                "registry_url": str,
                "timestamp": str
            }
        """
        raise NotImplementedError("TODO: implement")

    def check_exists(self, skill_id: str, version: str) -> bool:
        """
        Check whether a skill at the given version already exists in the registry.

        Args:
            skill_id: Skill identifier.
            version: Semantic version string.

        Returns:
            True if the skill+version combination already exists.
        """
        raise NotImplementedError("TODO: implement")
```

## ============================================================
## 以下是每个 adapter 的具体实现要求
## ============================================================

## Adapter 1：github_fetch/adapter.py

### health_check 要求
- 直接返回 True（mock，不做真实网络调用）

### execute 要求
- 根据 action 参数 dispatch：
  - "fetch_repo_info" → 调用 self.fetch_repo_info(params["repo_url"])，返回 dataclasses.asdict(result)
  - "scan_repo_structure" → 调用 self.scan_repo_structure(params["repo_url"], params.get("branch", "main"))，返回 asdict(result)
  - "discover_repos" → 调用 self.discover_repos(params["query"], params.get("intent", {}), params.get("max_results", 5))，返回 asdict(result)
  - 其他 → raise ValueError(f"Unsupported action: {action}")
- import dataclasses 在文件顶部

### fetch_repo_info 要求
- import uuid 在文件顶部
- 从 repo_url 解析 owner 和 name（同 IntakeRepo 的解析逻辑）
- 返回 RepoInfo(name=name, owner=owner, default_branch="main", stars=0, license=None, last_commit_sha="mock-sha-"+uuid4.hex[:8], languages={"Python": 100})

### scan_repo_structure 要求
- 从 repo_url 解析 name
- 返回 ScanResult(fit_score=70, repo_type="lib", entry_points=["main.py"], dependencies={}, language_stack="Python")

### discover_repos 要求
- 生成 min(max_results, 3) 个 mock 候选
- 每个候选：{ repo_url: f"https://github.com/mock-org/{query.replace(' ', '-')}-{i}", stars: 100*(i+1), license: "MIT", fit_score_estimate: 70-i*10, match_reason: f"Keyword match: {query}" }
- selected: 第一个候选（如果有）
- 返回 DiscoveryResult(candidates=candidates, selected=selected)

## Adapter 2：sandbox_runner/adapter.py

### health_check 要求
- 直接返回 True（mock）

### execute 要求
- "run_in_sandbox" → 创建 SandboxConfig 从 params，调用 self.run_in_sandbox(params["bundle_path"], config)，返回 dataclasses.asdict(result)
- 其他 → raise ValueError

### run_in_sandbox 要求
- import time, uuid 在文件顶部
- mock 执行：
  - success: True
  - test_report: { "total_runs": 3, "passed": 3, "failed": 0, "success_rate": 1.0, "avg_latency_ms": 42.5, "total_cost_usd": 0.001 }
  - trace_events: [{ "event_id": str(uuid4()), "event_type": "sandbox_execution", "timestamp": ISO时间, "node_id": "sandbox_runner", "status": "completed" }]
  - sandbox_report: { "cpu_time_ms": 85, "memory_peak_mb": 12.3, "violations": [] }
- 返回 RunResult(...)

## Adapter 3：registry_client/adapter.py

### health_check 要求
- 直接返回 True（mock）

### execute 要求
- "publish" → 调用 self.publish(params)，返回结果
- "check_exists" → 调用 self.check_exists(params["skill_id"], params["version"])，返回 {"exists": result}
- 其他 → raise ValueError

### publish 要求
- import time, uuid 在文件顶部
- mock 发布：
  - skill_id: request.get("skill_id", "unknown")
  - version: request.get("version", "0.1.0")
  - 返回 { "schema_version": "0.1.0", "skill_id": skill_id, "version": version, "status": "published", "registry_url": f"{self.registry_url}/skills/{skill_id}/{version}", "timestamp": ISO时间 }

### check_exists 要求
- mock：始终返回 False（没有真实 registry）

## 输出格式

请按以下格式输出每个文件：

## 文件: [相对路径]

```python
[完整文件内容，包括 module docstring、所有 import、class 定义和方法]
```

一共 3 个代码文件。请完整输出，不要省略任何内容。
```

---

## 交付后验收标准

```bash
cd D:\GM-SkillForge\skillforge-spec-pack

# 1. 现有测试不退化
pytest -q                          # >= 39 passed

# 2. Adapter 单元测试
python -c "
from skillforge.src.adapters.github_fetch.adapter import GitHubFetchAdapter
gf = GitHubFetchAdapter()
print('health:', gf.health_check())
info = gf.fetch_repo_info('https://github.com/owner/repo')
print(f'repo: {info.name}, owner: {info.owner}')
scan = gf.scan_repo_structure('https://github.com/owner/repo')
print(f'scan: fit={scan.fit_score}, type={scan.repo_type}')
disc = gf.discover_repos('data pipeline', {}, 3)
print(f'discover: {len(disc.candidates)} candidates')
"

python -c "
from skillforge.src.adapters.sandbox_runner.adapter import SandboxRunnerAdapter
from skillforge.src.adapters.sandbox_runner.types import SandboxConfig
sr = SandboxRunnerAdapter()
print('health:', sr.health_check())
result = sr.run_in_sandbox('/tmp/test-bundle', SandboxConfig())
print(f'sandbox: success={result.success}, passed={result.test_report[\"passed\"]}')
"

python -c "
from skillforge.src.adapters.registry_client.adapter import RegistryClientAdapter
rc = RegistryClientAdapter()
print('health:', rc.health_check())
print('exists:', rc.check_exists('test-skill', '0.1.0'))
result = rc.publish({'skill_id': 'test-skill', 'version': '0.1.0'})
print(f'publish: status={result[\"status\"]}')
"

# 3. validate.py 不退化
python tools/validate.py --all
```
