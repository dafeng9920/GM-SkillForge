# Wave 6 Mega Prompt — Path B 节点实现填充
# 目标：填充 intake_repo / license_gate / repo_scan / draft_spec 的 3 个方法
# 用法：整段复制 `## 提示词正文` 下的 code block 到 Claude 4.6

> ⚠️ 重要：Prompt 中包含 4 个骨架文件的完整内容，Claude 4.6 必须原封不动保留所有签名

---

## 提示词正文（复制以下全部内容）

```text
你是 GM OS SkillForge 的实现工程师。你需要为 4 个 Path B 节点填充实现逻辑。
不要创建新文件，只输出这 4 个文件的完整替换内容。

## 硬约束

1. 不改变任何 class 签名（@dataclass）、方法签名、属性名
2. 不添加新的外部依赖（只用 Python 标准库 + 已有 import，可以 import uuid, time）
3. validate_input() 返回 list[str]（空列表=通过，非空=错误列表）
4. validate_output() 返回 list[str]（同上）
5. execute() 返回 dict[str, Any]（符合 module-level Output Contract）
6. 错误码只能使用已定义的前缀：GATE_, AUDIT_, REG_, EXEC_, SCHEMA_, SYS_
7. 所有方法必须保留完整的 docstring
8. 保留 from __future__ import annotations
9. 每个 execute() 的实现是"可独立运行的本地逻辑"，不调用真实 HTTP API

## ============================================================
## 以下是 4 个骨架文件的【当前完整内容】
## 你必须原封不动保留所有签名，只替换 raise NotImplementedError("TODO: implement")
## ============================================================

### 当前骨架 1: skillforge/src/nodes/intake_repo.py

```python
"""
IntakeRepo node — fetch and validate a GitHub repository.

Path: B, A+B
Stage: 0

Input Contract (conforms to gm-os-core intake_repo.schema.json)
--------------
{
    "repo_url": str,
    "branch": str,
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "repo_info": {
        "name": str,
        "owner": str,
        "default_branch": str,
        "stars": int,
        "license": str | None,
        "last_commit_sha": str,
        "languages": dict
    },
    "fetch_status": "ok" | "error",
    "local_path": str | None
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class IntakeRepo:
    """Fetch and intake a GitHub repository."""

    node_id: str = "intake_repo"
    stage: int = 0

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_url is present and well-formed."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Fetch repository information and clone/download.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate intake output."""
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 2: skillforge/src/nodes/license_gate.py

```python
"""
LicenseGate node — gate that checks repository license compatibility.

Path: B, A+B
Stage: 1

Input Contract (conforms to gm-os-core license_gate.schema.json)
--------------
{
    "repo_info": { ... },    # from IntakeRepo
    "options": { ... }
}

Output Contract (GateDecision)
---------------
{
    "schema_version": "0.1.0",
    "gate_id": "license_gate",
    "node_id": "license_gate",
    "decision": "ALLOW" | "DENY" | "REQUIRES_CHANGES",
    "reason": str,
    "details": {
        "license_detected": str | None,
        "compatible": bool,
        "allowed_licenses": list[str]
    },
    "timestamp": str
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LicenseGate:
    """Evaluate license compatibility for an ingested repo."""

    node_id: str = "license_gate"
    stage: int = 1

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_info is present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Check repository license and produce GateDecision.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract (GateDecision).
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate GateDecision structure."""
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 3: skillforge/src/nodes/repo_scan.py

```python
"""
RepoScan node — scan repository structure and compute fit score.

Path: B, A+B
Stage: 2

Input Contract (conforms to gm-os-core repo_scan_fit_score.schema.json)
--------------
{
    "repo_info": { ... },
    "local_path": str,
    "options": { ... }
}

Output Contract
---------------
{
    "schema_version": "0.1.0",
    "fit_score": int,          # 0-100
    "repo_type": str,          # workflow | cli | lib | service | template
    "entry_points": list[str],
    "dependencies": dict[str, str],
    "language_stack": str,
    "complexity_metrics": {
        "total_files": int,
        "total_loc": int,
        "avg_function_length": float
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RepoScan:
    """Scan repo structure and produce a fit score."""

    node_id: str = "repo_scan_fit_score"
    stage: int = 2

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate repo_info and local_path are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Scan repo structure and compute fit score.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate scan result."""
        raise NotImplementedError("TODO: implement")
```

### 当前骨架 4: skillforge/src/nodes/draft_spec.py

```python
"""
DraftSpec node — draft a skill specification from scan results.

Path: B, A+B
Stage: 3

Input Contract (conforms to gm-os-core draft_skill_spec.schema.json)
--------------
{
    "repo_info": { ... },
    "scan_result": { ... },     # from RepoScan
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
    "source": "repo",
    "derived_from": {
        "repo_url": str,
        "commit_sha": str
    }
}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DraftSpec:
    """Draft a skill specification from repository scan results."""

    node_id: str = "draft_skill_spec"
    stage: int = 3

    def validate_input(self, input_data: dict[str, Any]) -> list[str]:
        """Validate scan_result and repo_info are present."""
        raise NotImplementedError("TODO: implement")

    def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Draft skill specification from scan.

        Input: see module-level Input Contract.
        Output: see module-level Output Contract.
        """
        raise NotImplementedError("TODO: implement")

    def validate_output(self, output_data: dict[str, Any]) -> list[str]:
        """Validate drafted spec."""
        raise NotImplementedError("TODO: implement")
```

## ============================================================
## 以下是每个方法的具体实现要求
## ============================================================


## 数据传递约定（非常重要）

Pipeline 在执行节点链时，会把所有前序节点的输出**合并到同一个 artifacts dict** 中传给当前节点。
所以每个 node 的 input_data 不是只有自己的输入，而是整个 pipeline 的累积 artifacts。

具体来说：
- input_data["input"] = 用户最初的输入（含 repo_url, mode 等）
- input_data["intake_repo"] = IntakeRepo.execute() 的输出
- input_data["license_gate"] = LicenseGate.execute() 的输出
- input_data["repo_scan_fit_score"] = RepoScan.execute() 的输出
- 依此类推…

每个 node 的 execute() 输出会以 node_id 为 key 存入 artifacts。

## 文件 1：intake_repo.py

路径：skillforge/src/nodes/intake_repo.py

### Skill Spec 合同
- input.required: repo_url (string)
- input.optional: branch (string, default "main")
- output: schema_version, repo_info{name, owner, default_branch, stars, license, last_commit_sha, languages}, fetch_status, local_path
- capabilities: network=true
- error_codes: REPO_NOT_FOUND, REPO_FETCH_FAILED

### validate_input 要求
- 检查 input_data 中有 "input" key（pipeline artifacts 格式）
- 从 input_data["input"] 获取 repo_url
- repo_url 不能为空
- repo_url 必须包含 "github.com" 或以 "git://" / "https://" 开头
- 返回 list[str] 错误列表

### execute 要求
- 从 input_data["input"] 获取 repo_url 和 branch (默认 "main")
- 解析 repo_url：提取 owner 和 repo name（从 URL 路径中取后两段）
- 返回 mock repo_info：
  - name: 解析出的 repo name
  - owner: 解析出的 owner
  - default_branch: branch 参数
  - stars: 0（mock）
  - license: None（mock，后续可被 adapter 填充）
  - last_commit_sha: "mock-sha-" + uuid4()[:8]
  - languages: {"Python": 100}（mock）
- fetch_status: "ok"
- local_path: None（无真实下载）

### validate_output 要求
- 检查 schema_version 存在且为 "0.1.0"
- 检查 repo_info 存在且为 dict
- 检查 repo_info 必须包含 name, owner, default_branch
- 检查 fetch_status 存在

## 文件 2：license_gate.py

路径：skillforge/src/nodes/license_gate.py

### Skill Spec 合同
- input.required: repo_info (object，含 license 字段)
- output: GateDecision（schema_version, gate_id, node_id, decision, reason, details, timestamp）
- 白名单: ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD", "Unlicense"]

### validate_input 要求
- 从 artifacts 中获取 intake_repo 的输出（input_data.get("intake_repo")）
- 如果不存在，返回错误：需要 intake_repo 阶段的输出
- 检查 repo_info 字段存在

### execute 要求
- import uuid, time 在文件顶部
- 从 input_data["intake_repo"]["repo_info"] 获取 license
- ALLOWED_LICENSES = ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD", "Unlicense"]
- 如果 license 为 None 或 ""：decision = "DENY"，reason = "No license detected"
- 如果 license 不在白名单：decision = "DENY"，reason = f"License '{license}' is not approved"
- 否则：decision = "ALLOW"，reason = f"License '{license}' is approved"
- 输出完整 GateDecision dict

### validate_output 要求
- 检查 schema_version, gate_id, node_id, decision, reason, timestamp 全部存在
- decision 必须在 ["ALLOW", "DENY", "REQUIRES_CHANGES"] 中

## 文件 3：repo_scan.py

路径：skillforge/src/nodes/repo_scan.py

### Skill Spec 合同
- input.required: repo_info (object), local_path (string) 或 从 artifacts 中获取
- output: schema_version, fit_score (0-100), repo_type, entry_points, dependencies, language_stack, complexity_metrics

### validate_input 要求
- 从 input_data["intake_repo"] 获取 repo_info
- 如果缺失：返回 "intake_repo output is required"

### execute 要求
- 从 input_data["intake_repo"]["repo_info"] 获取信息
- 从 repo_info["languages"] 推断 language_stack（取第一个 key）
- fit_score: 基于简单规则（有 license → +20; 有多语言 → +10; 有 Python → +30; 基础 40; 总计 clamp 到 0-100）
- repo_type: 基于语言推断（Python → "lib"; JavaScript → "service"; default → "template"）
- entry_points: ["main.py"]（mock）
- dependencies: {}（mock）
- complexity_metrics: { total_files: 1, total_loc: 0, avg_function_length: 0.0 }（mock）

### validate_output 要求
- 检查 schema_version, fit_score, repo_type, entry_points, language_stack 全部存在
- fit_score 在 0-100 之间
- repo_type 在 ["workflow", "cli", "lib", "service", "template"] 中

## 文件 4：draft_spec.py

路径：skillforge/src/nodes/draft_spec.py

### Skill Spec 合同
- input.required: repo_info (object), scan_result (object)
- output: schema_version, skill_spec{name, version, description, inputs, outputs, tools_required, steps, constraints}, source, derived_from

### validate_input 要求
- 从 input_data 获取 "intake_repo" 和 "repo_scan_fit_score"
- 两者任缺其一都返回错误

### execute 要求
- intake = input_data["intake_repo"]
- scan = input_data["repo_scan_fit_score"]
- 构筑 skill_spec：
  - name: f"skill-{intake['repo_info']['name']}"
  - version: "0.1.0"
  - description: f"Auto-drafted skill from {intake['repo_info']['owner']}/{intake['repo_info']['name']}"
  - inputs: 基于 scan["entry_points"] 生成 [{"name": ep, "type": "file", "required": True} for ep in entry_points]
  - outputs: [{"name": "result", "type": "object"}]
  - tools_required: 基于 scan["language_stack"] 推断（Python → ["python3", "pip"]）
  - steps: [{"id": "step_1", "action": "execute", "description": f"Run {entry_points[0]}"}]
  - constraints: [f"risk_tier: L1", f"fit_score >= 40 (actual: {scan['fit_score']})"]
- source: "repo"
- derived_from: { repo_url: input_data["input"]["repo_url"], commit_sha: intake["repo_info"]["last_commit_sha"] }
- confidence: min(scan["fit_score"] / 100, 0.95)

### validate_output 要求
- 检查 schema_version, skill_spec, source 全部存在
- skill_spec 必须包含 name, version, description
- source 必须为 "repo"

## 输出格式

请按以下格式输出每个文件：

## 文件: [相对路径]

```python
[完整文件内容，包括 module docstring、所有 import、class 定义和方法]
```

一共 4 个代码文件。请完整输出，不要省略任何内容。
```

---

## 交付后验收标准

```bash
cd D:\GM-SkillForge\skillforge-spec-pack

# 1. 现有测试不退化
pytest -q                          # >= 39 passed

# 2. node 不再抛 NotImplementedError
python -c "
from skillforge.src.nodes.intake_repo import IntakeRepo
ir = IntakeRepo()
errors = ir.validate_input({'input': {'repo_url': 'https://github.com/owner/repo'}})
print(f'validate_input errors: {errors}')
result = ir.execute({'input': {'repo_url': 'https://github.com/owner/repo'}})
print(f'fetch_status={result[\"fetch_status\"]}, owner={result[\"repo_info\"][\"owner\"]}, name={result[\"repo_info\"][\"name\"]}')
"

# 3. license_gate 功能测试
python -c "
from skillforge.src.nodes.license_gate import LicenseGate
lg = LicenseGate()
result = lg.execute({'intake_repo': {'repo_info': {'license': 'MIT'}}})
print(f'decision={result[\"decision\"]}')
"

# 4. 完整 Path B 链路测试（手动串联）
python -c "
from skillforge.src.nodes.intake_repo import IntakeRepo
from skillforge.src.nodes.license_gate import LicenseGate
from skillforge.src.nodes.repo_scan import RepoScan
from skillforge.src.nodes.draft_spec import DraftSpec

artifacts = {'input': {'mode': 'github', 'repo_url': 'https://github.com/owner/test-repo'}}

# Stage 0: intake
ir = IntakeRepo()
artifacts['intake_repo'] = ir.execute(artifacts)
print(f'intake: {artifacts[\"intake_repo\"][\"fetch_status\"]}')

# Stage 1: license gate
lg = LicenseGate()
artifacts['license_gate'] = lg.execute(artifacts)
print(f'license: {artifacts[\"license_gate\"][\"decision\"]}')

# Stage 2: repo scan
rs = RepoScan()
artifacts['repo_scan_fit_score'] = rs.execute(artifacts)
print(f'scan: fit={artifacts[\"repo_scan_fit_score\"][\"fit_score\"]}')

# Stage 3: draft spec
ds = DraftSpec()
artifacts['draft_skill_spec'] = ds.execute(artifacts)
print(f'spec: name={artifacts[\"draft_skill_spec\"][\"skill_spec\"][\"name\"]}')
print('PATH B chain: OK')
"

# 5. validate.py 不退化
python tools/validate.py --all
```
