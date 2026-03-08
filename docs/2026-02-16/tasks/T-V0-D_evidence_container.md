# T-V0-D: Evidence 容器闭环 — semgrep wrapper → evidence.jsonl 实际写入

## 背景
当前 `evidence.jsonl` 是 mock 生成的（`pack_publish.py` 中硬编码 4 条样例 evidence）。
v0 需要：
- 真实调用静态分析工具（semgrep）并捕获输出
- 将 semgrep findings 写入 `evidence.jsonl`（每行一条 JSON）
- `policy_matrix.findings[].evidence_ref` 指向真实 evidence 条目
- 整个链路形成闭环：semgrep → findings → evidence_ref → evidence.jsonl

## 任务清单

### D1: 创建 semgrep wrapper
**新文件**: `skillforge/src/analyzers/__init__.py`
**新文件**: `skillforge/src/analyzers/semgrep_runner.py`

```python
"""
SemgrepRunner — subprocess wrapper for semgrep static analysis.
Falls back to mock results if semgrep is not installed.
"""

class SemgrepRunner:
    def __init__(self, ruleset: str = "p/python"):
        self.ruleset = ruleset

    def analyze(self, target_path: str) -> AnalysisResult:
        """
        Run semgrep on target_path.

        Returns:
            AnalysisResult with:
            - findings: list[Finding]  # each has rule_id, severity, message, location
            - raw_output: str          # full semgrep JSON output
            - tool_version: str        # semgrep --version
            - exit_code: int
        """
        try:
            result = subprocess.run(
                ["semgrep", "--json", "--config", self.ruleset, target_path],
                capture_output=True, text=True, timeout=120
            )
            return self._parse_output(result)
        except FileNotFoundError:
            # semgrep not installed → return mock
            return self._mock_result(target_path)

    def _parse_output(self, result) -> AnalysisResult: ...
    def _mock_result(self, target_path) -> AnalysisResult: ...
```

关键设计：
- semgrep 不存在时 gracefully fallback 到 mock（v0 不强制安装 semgrep）
- 输出结构化为 `Finding` dataclass
- 超时 120s（与 `repro_env.yml` 的 `timeout_s: 120` 保持一致）

### D2: sandbox_test.py — 集成 semgrep runner
**文件**: `skillforge/src/nodes/sandbox_test.py`

在 `execute()` 中：
```python
from skillforge.src.analyzers.semgrep_runner import SemgrepRunner

runner = SemgrepRunner()
analysis = runner.analyze(target_path)

# 写入 artifacts
result["static_analysis"] = {
    "tool": "semgrep",
    "version": analysis.tool_version,
    "findings": [f.to_dict() for f in analysis.findings],
    "raw_output": analysis.raw_output,
}
```

### D3: pack_publish.py — 真实 evidence 写入
**文件**: `skillforge/src/nodes/pack_publish.py`

替换 mock evidence 生成逻辑，改为从 `artifacts["sandbox_test_and_trace"]` 提取：

```python
def _build_evidence_chain(self, artifacts):
    evidence = []

    # 1. intake provenance (已有)
    evidence.append(self._make_evidence("intake_provenance", ...))

    # 2. static analysis findings → evidence
    static = artifacts.get("sandbox_test_and_trace", {}).get("static_analysis", {})
    for finding in static.get("findings", []):
        eid = f"ev-{uuid4().hex[:8]}"
        evidence.append({
            "evidence_id": eid,
            "type": "static_analysis_finding",
            "source": "semgrep",
            "rule_id": finding["rule_id"],
            "severity": finding["severity"],
            "message": finding["message"],
            "location": finding["location"],
            "timestamp": _now_iso(),
        })

    # 3. gate decisions (已有)
    for gate in artifacts.get("gate_decisions", []):
        evidence.append(self._make_evidence("gate_decision", ...))

    return evidence
```

### D4: policy_matrix.json — evidence_ref 指向真实 evidence
**文件**: `skillforge/src/nodes/pack_publish.py`

`_build_policy_matrix()` 中：
```python
for finding in static_findings:
    matrix_finding = {
        "issue_key": self._map_to_issue_key(finding["rule_id"]),
        "severity": finding["severity"],
        "evidence_ref": finding["evidence_id"],  # 指向 evidence.jsonl 中的真实条目
        "location": finding["location"],
    }
    findings.append(matrix_finding)
```

### D5: static_analysis.log — 真实输出
**文件**: `skillforge/src/nodes/pack_publish.py`

`static_analysis.log` 改为写入 `analysis.raw_output`（semgrep 的原始 JSON 输出），
而非当前的 mock 字符串 `"[static_analysis] No findings"`。

### D6: 测试
**新文件**: `skillforge/tests/test_evidence_container.py`

```python
class TestSemgrepRunner:
    def test_mock_fallback_when_not_installed(self): ...
    def test_findings_structure(self): ...
    def test_timeout_handling(self): ...

class TestEvidenceChainReal:
    def test_static_findings_in_evidence(self): ...
    def test_evidence_ref_resolves(self): ...
    def test_policy_matrix_links_to_evidence(self): ...
    def test_static_analysis_log_contains_output(self): ...
```

## 设计要点

1. **不强制安装 semgrep** — FileNotFoundError → mock fallback，保证 CI 可过
2. **evidence_id 全局唯一** — 使用 `ev-{uuid_hex[:8]}` 格式
3. **幂等** — 同一 repo + commit_sha 的 semgrep 输出应一致（可复现审计）
4. **raw_output 保留** — `static_analysis.log` 存完整原始输出，用于手动复核

## 验收条件
- `python -m pytest skillforge/tests/test_evidence_container.py -v` 全过
- `python -m pytest skillforge/tests/test_acceptance.py -v` 不回归
- evidence.jsonl 中至少包含 `intake_provenance` + `gate_decision` 类型证据
- `policy_matrix.findings[].evidence_ref` 全部可在 evidence 中查到

## 关键文件清单
```
skillforge/src/analyzers/__init__.py              ← 新建
skillforge/src/analyzers/semgrep_runner.py         ← 新建
skillforge/src/nodes/sandbox_test.py               ← 修改
skillforge/src/nodes/pack_publish.py               ← 修改
skillforge/tests/test_evidence_container.py        ← 新建
orchestration/protocol_v0_scope.yml                ← 只读参考
```
