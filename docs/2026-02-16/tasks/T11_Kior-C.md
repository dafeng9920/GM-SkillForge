# T11 — Kior-C：从 Claude 输出中提取文件落盘

**执行者**: Kior-C  
**日期**: 2026-02-16  
**依赖**: 无  
**预计耗时**: 30 分钟

---

## 目标

将 `docs/2026-02-15/claude的输出.md` 中的 33 个代码文件，逐个提取并写入 `skillforge/` 目录中正确的路径。

## 输入

- 源文件：`D:\GM-SkillForge\docs\2026-02-15\claude的输出.md`
- 文件分隔标记：每段代码前有 `文件: [相对路径]` 标记行
- 代码起始标记：`pythonDownloadCopy code` 或 `jsonDownloadCopy code`（这是网页复制产生的噪声，提取时去掉）

## 提取规则

1. 读取 `claude的输出.md`, 按 `文件:` 标记拆分成 33 段
2. 每段中，去掉 `pythonDownloadCopy code` 或 `jsonDownloadCopy code` 行头噪声
3. 所有 `__init__.py` 文件名在源文件中被压缩为 `init.py`（如 `skillforge/src/init.py`），写盘时恢复为 `__init__.py`
4. 写入路径基准：`D:\GM-SkillForge\skillforge-spec-pack\`（所有 `skillforge/` 前缀保留）

## 文件清单（33 个）

### __init__.py (7 个)
| # | 源文件标记路径 | 实际目标路径 |
|---|---------------|-------------|
| 1 | `skillforge/src/init.py` | `skillforge/src/__init__.py` |
| 2 | `skillforge/src/orchestration/init.py` | `skillforge/src/orchestration/__init__.py` |
| 3 | `skillforge/src/adapters/init.py` | `skillforge/src/adapters/__init__.py` |
| 4 | `skillforge/src/adapters/github_fetch/init.py` | `skillforge/src/adapters/github_fetch/__init__.py` |
| 5 | `skillforge/src/adapters/sandbox_runner/init.py` | `skillforge/src/adapters/sandbox_runner/__init__.py` |
| 6 | `skillforge/src/adapters/registry_client/init.py` | `skillforge/src/adapters/registry_client/__init__.py` |
| 7 | `skillforge/src/nodes/init.py` | `skillforge/src/nodes/__init__.py` |

### 核心模块 (4 个)
| # | 目标路径 |
|---|---------|
| 8 | `skillforge/src/protocols.py` |
| 9 | `skillforge/src/orchestration/engine.py` |
| 10 | `skillforge/src/orchestration/node_runner.py` |
| 11 | `skillforge/src/orchestration/gate_engine.py` |

### 适配器 (5 个)
| # | 目标路径 |
|---|---------|
| 12 | `skillforge/src/adapters/github_fetch/types.py` |
| 13 | `skillforge/src/adapters/github_fetch/adapter.py` |
| 14 | `skillforge/src/adapters/sandbox_runner/types.py` |
| 15 | `skillforge/src/adapters/sandbox_runner/adapter.py` |
| 16 | `skillforge/src/adapters/registry_client/adapter.py` |

### 节点处理器 (12 个)
| # | 目标路径 |
|---|---------|
| 17 | `skillforge/src/nodes/intent_parser.py` |
| 18 | `skillforge/src/nodes/source_strategy.py` |
| 19 | `skillforge/src/nodes/github_discover.py` |
| 20 | `skillforge/src/nodes/skill_composer.py` |
| 21 | `skillforge/src/nodes/intake_repo.py` |
| 22 | `skillforge/src/nodes/license_gate.py` |
| 23 | `skillforge/src/nodes/repo_scan.py` |
| 24 | `skillforge/src/nodes/draft_spec.py` |
| 25 | `skillforge/src/nodes/constitution_gate.py` |
| 26 | `skillforge/src/nodes/scaffold_impl.py` |
| 27 | `skillforge/src/nodes/sandbox_test.py` |
| 28 | `skillforge/src/nodes/pack_publish.py` |

### Schema (2 个)
| # | 目标路径 |
|---|---------|
| 29 | `skillforge/schemas/pipeline_input.schema.json` |
| 30 | `skillforge/schemas/pipeline_output.schema.json` |

### CLI + Tests (3 个)
| # | 目标路径 |
|---|---------|
| 31 | `skillforge/src/cli.py` |
| 32 | `skillforge/tests/__init__.py` |
| 33 | `skillforge/tests/test_protocols.py` |

## 验收标准

```bash
# 1. 文件计数
find skillforge/src -name "*.py" | wc -l   # >= 28

# 2. import 不报错
cd D:\GM-SkillForge\skillforge-spec-pack
python -c "from skillforge.src.protocols import NodeHandler, GateEvaluator, Adapter; print('OK')"

# 3. 所有骨架方法为 NotImplementedError
python -c "
from skillforge.src.nodes.intake_repo import IntakeRepo
try:
    IntakeRepo().execute({})
    print('FAIL: should raise')
except NotImplementedError:
    print('OK: raises NotImplementedError')
"

# 4. 如果 test_protocols.py 能跑更好（依赖 import 链路通）
pytest skillforge/tests/test_protocols.py -v 2>&1 | tail -5
```

## 注意事项

- 提取时注意编码用 UTF-8
- Python 文件的缩进保持 4 空格
- JSON schema 文件需要验证 JSON 格式合法（`python -m json.tool < file.json`）
- 如果某个文件内容边界不清晰，以 `文件:` 标记行作为分界线
