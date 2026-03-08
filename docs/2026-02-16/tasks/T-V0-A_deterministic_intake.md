# T-V0-A: 确定性 Intake — commit_sha 强制 + Constitution 合规规则

## 背景
v0 Scope Lock（`orchestration/protocol_v0_scope.yml`）锚定：
- GitHub 输入：`repo_url` + `commit_sha` **MUST** → 缺 commit_sha 则 DENY
- 合法性边界：respect robots.txt + 禁止登录态/受限内容 → constitution_risk_gate 执行

当前代码状态：
- `intake_repo.py` 接受 `repo_url` + `branch`，没有 `commit_sha` 强制
- `constitution_gate.py` 有 capabilities/risk_tier 检查，没有 robots.txt / 登录态规则
- `original_repo_snapshot.json` 有 `snapshot_hash`，缺 `commit_sha` 字段

## 任务清单

### A1: intake_repo.py — 强制 commit_sha
**文件**: `skillforge/src/nodes/intake_repo.py`

1. `validate_input()` 增加校验：
   ```python
   # 当 mode == "github" 时：
   # - repo_url: MUST（已有）
   # - commit_sha: MUST → 缺失返回 ["commit_sha is required for reproducible audit"]
   ```
2. `execute()` 中将 `commit_sha` 写入输出：
   ```python
   result["commit_sha"] = input_data["input"]["commit_sha"]
   ```
3. `validate_output()` 校验输出中包含 `commit_sha`

### A2: pack_publish.py — 传播 commit_sha 到 Audit Pack
**文件**: `skillforge/src/nodes/pack_publish.py`

1. `_build_provenance()` 中增加 `commit_sha` 字段（从 `artifacts["intake_repo"]["commit_sha"]` 或 `artifacts["input"]["commit_sha"]` 获取）
2. `original_repo_snapshot` 输出增加 `commit_sha` 字段

### A3: constitution_gate.py — 合规规则
**文件**: `skillforge/src/nodes/constitution_gate.py`

在 `_evaluate_constitution_gate()` 或等效位置增加 2 条硬规则：

```python
# Rule: robots_txt — 如果 skill capabilities 包含 web_crawl，
# 默认配置必须 respect robots.txt
if capabilities.get("web_crawl") and not capabilities.get("respect_robots_txt", True):
    return DENY("web_crawl without robots.txt compliance is prohibited")

# Rule: auth_content — 禁止登录态/受限内容抓取
if capabilities.get("authenticated_access"):
    return DENY("Authenticated/restricted content access is prohibited in v0")
```

### A4: gate_engine.py — 同步规则
**文件**: `skillforge/src/orchestration/gate_engine.py`

在 `_evaluate_constitution_gate()` 中同步增加与 A3 相同的规则（gate_engine 是独立的评估器）。

### A5: 测试
**新文件**: `skillforge/tests/test_deterministic_intake.py`

```python
class TestCommitShaRequired:
    """commit_sha is MUST for github mode."""
    def test_missing_commit_sha_denied(self): ...
    def test_commit_sha_propagated_to_audit_pack(self): ...
    def test_commit_sha_in_snapshot(self): ...

class TestComplianceBoundaries:
    """Constitution gate enforces robots.txt + no-auth rules."""
    def test_web_crawl_without_robots_denied(self): ...
    def test_authenticated_access_denied(self): ...
    def test_normal_skill_allowed(self): ...
```

## 验收条件
- `python -m pytest skillforge/tests/test_deterministic_intake.py -v` 全过
- `python -m pytest skillforge/tests/test_acceptance.py -v` 不回归（12/12）
- `python tools/validate.py --audit-config` 不回归（10/10）

## 关键文件清单
```
skillforge/src/nodes/intake_repo.py          ← 修改
skillforge/src/nodes/pack_publish.py         ← 修改
skillforge/src/nodes/constitution_gate.py    ← 修改
skillforge/src/orchestration/gate_engine.py  ← 修改
skillforge/tests/test_deterministic_intake.py ← 新建
orchestration/protocol_v0_scope.yml          ← 只读参考
```
