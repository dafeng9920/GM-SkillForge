# T12 — vs--cc1：文件落盘后验证 + CI 对齐

**执行者**: vs--cc1  
**日期**: 2026-02-16  
**依赖**: T11 完成  
**预计耗时**: 20 分钟

---

## 目标

T11 将 33 个文件落盘后，运行全量验证确保：
1. import 链路畅通
2. Protocol 一致性测试通过
3. 现有 39 个 contract_tests 不退化
4. CI 配置覆盖新增测试

## 验证步骤

### 1. 基础 import 验证

```bash
cd D:\GM-SkillForge\skillforge-spec-pack

# 核心协议
python -c "from skillforge.src.protocols import NodeHandler, GateEvaluator, Adapter; print('[PASS] protocols')"

# 编排层
python -c "from skillforge.src.orchestration.engine import PipelineEngine; print('[PASS] engine')"
python -c "from skillforge.src.orchestration.node_runner import NodeRunner; print('[PASS] node_runner')"
python -c "from skillforge.src.orchestration.gate_engine import GateEngine; print('[PASS] gate_engine')"

# 12 个节点
python -c "from skillforge.src.nodes import IntentParser, SourceStrategy, GitHubDiscovery, SkillComposer, IntakeRepo, LicenseGate, RepoScan, DraftSpec, ConstitutionGate, ScaffoldImpl, SandboxTest, PackPublish; print('[PASS] all 12 nodes')"

# 3 个适配器
python -c "from skillforge.src.adapters.github_fetch import GitHubFetchAdapter; print('[PASS] github_fetch')"
python -c "from skillforge.src.adapters.sandbox_runner import SandboxRunnerAdapter; print('[PASS] sandbox_runner')"
python -c "from skillforge.src.adapters.registry_client import RegistryClientAdapter; print('[PASS] registry_client')"
```

### 2. 新增测试运行

```bash
pytest skillforge/tests/test_protocols.py -v --tb=short
# 预期: ~103 个参数化测试全部 PASSED
```

### 3. 现有测试不退化

```bash
pytest contract_tests/ -q
# 预期: >= 39 passed, 0 failed
```

### 4. validate.py 不退化

```bash
python tools/validate.py --all
# 预期: 全部通过
```

### 5. Schema 合法性

```bash
python -m json.tool skillforge/schemas/pipeline_input.schema.json > NUL && echo "[PASS] input schema"
python -m json.tool skillforge/schemas/pipeline_output.schema.json > NUL && echo "[PASS] output schema"
```

## 如果发现问题

| 故障类型 | 处理方式 |
|----------|----------|
| ImportError (模块找不到) | 检查 `__init__.py` 是否正确创建，路径是否拼写正确 |
| SyntaxError | 回查 `claude的输出.md` 提取是否有截断/噪声残留 |
| 现有测试退化 | 检查是否误覆盖了 `skillforge-spec-pack/schemas/` 中的现有文件 |
| JSON 格式错误 | `python -m json.tool` 定位语法错误位置 |

## 输出报告格式

```yaml
task: T12
executor: vs--cc1
decision: ALLOW | DENY
results:
  import_check: PASS | FAIL
  protocol_tests: "X passed, Y failed"
  contract_tests: "X passed, Y failed"
  validate_py: PASS | FAIL
  schema_check: PASS | FAIL
issues: []
```
