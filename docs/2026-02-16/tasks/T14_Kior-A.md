# T14 — Kior-A：从骨架代码反推 Skill Spec

**执行者**: Kior-A  
**日期**: 2026-02-16  
**依赖**: 无（与 T11 并行，直接从 `docs/2026-02-15/claude的输出.md` 读取）  
**预计耗时**: 40 分钟

---

## 背景

我们违反了"先 Skill Spec 后代码"的原则 —— 先让 Claude 4.6 产出了 33 个骨架代码文件,跳过了 Skill Spec 层。现在需要从骨架代码的 docstring 和 Protocol 定义中,反向提炼出标准格式的 Skill Spec。

## 目标

为 SkillForge 实现层的每个可独立定义的模块,产出 Skill Spec YAML 文件。

## 输出位置

```
skillforge-spec-pack/skillforge/specs/
├── pipeline_engine.skill.yml
├── node_runner.skill.yml
├── gate_engine.skill.yml
├── adapters/
│   ├── github_fetch.skill.yml
│   ├── sandbox_runner.skill.yml
│   └── registry_client.skill.yml
└── nodes/
    ├── intent_parse.skill.yml
    ├── source_strategy.skill.yml
    ├── github_discover.skill.yml
    ├── skill_compose.skill.yml
    ├── intake_repo.skill.yml
    ├── license_gate.skill.yml
    ├── repo_scan_fit_score.skill.yml
    ├── draft_skill_spec.skill.yml
    ├── constitution_risk_gate.skill.yml
    ├── scaffold_skill_impl.skill.yml
    ├── sandbox_test_and_trace.skill.yml
    └── pack_audit_and_publish.skill.yml
```

共 **18 个** Skill Spec 文件。

## Skill Spec YAML 格式

每个 `.skill.yml` 必须遵循以下格式：

```yaml
schema_version: "0.1.0"
skill_id: "<node_id 或 module_id>"
name: "<人类可读名称>"
description: "<一句话描述>"
version: "0.1.0"

# 所属路径（仅 node 类型需要）
paths: ["A", "B", "AB"]  # 该节点出现在哪些路径中
stage: 4                   # pipeline stage 编号，pre-0 用 -1

# 输入合同
input:
  required:
    - field_name:
        type: "string"
        description: "..."
  optional:
    - field_name:
        type: "integer"
        default: 10
        description: "..."

# 输出合同
output:
  required:
    - field_name:
        type: "string"
        description: "..."
  optional:
    - field_name:
        type: "object"
        description: "..."

# 能力声明
capabilities:
  network: false        # 是否需要网络
  filesystem: false     # 是否需要文件系统
  subprocess: false     # 是否需要子进程
  gpu: false            # 是否需要 GPU

# 风险等级
risk_tier: "L0"  # L0(无风险) | L1(低) | L2(中) | L3(高)

# 依赖
dependencies:
  adapters: []         # 依赖哪些 adapter
  schemas: []          # 依赖哪些 gm-os-core schema
  error_codes: []      # 会使用的错误码

# 错误处理
errors:
  - code: "GATE_DENIED"
    retryable: false
    description: "门禁拒绝"
```

## 数据来源

从 `docs/2026-02-15/claude的输出.md` 中各文件的 **docstring** 提取 input/output contract。例如：

**intent_parser.py 的 docstring**：
```
Input Contract:  { "natural_language": str, "options": { ... } }
Output Contract: { "schema_version": "0.1.0", "intent": { "goal": str, ... }, "confidence": float, "raw_input": str }
```

→ 转换为 `intent_parse.skill.yml` 的 input/output 部分。

## 每个模块的关键信息

| skill_id | paths | stage | capabilities.network | risk_tier | adapters |
|----------|-------|-------|---------------------|-----------|----------|
| intent_parse | A, AB | -1 | false | L0 | - |
| source_strategy | A, AB | -1 | false | L0 | - |
| github_discover | AB | -1 | true | L1 | github_fetch |
| skill_compose | A | -1 | false | L1 | - |
| intake_repo | B, AB | 0 | true | L1 | github_fetch |
| license_gate | B, AB | 1 | false | L0 | - |
| repo_scan_fit_score | B, AB | 2 | true | L1 | github_fetch |
| draft_skill_spec | B, AB | 3 | false | L1 | - |
| constitution_risk_gate | ALL | 4 | false | L0 | - |
| scaffold_skill_impl | ALL | 5 | false | L1 | - |
| sandbox_test_and_trace | ALL | 6 | true | L2 | sandbox_runner |
| pack_audit_and_publish | ALL | 7 | true | L1 | registry_client |
| github_fetch (adapter) | - | - | true | L1 | - |
| sandbox_runner (adapter) | - | - | true | L2 | - |
| registry_client (adapter) | - | - | true | L1 | - |
| pipeline_engine | - | - | false | L0 | - |
| node_runner | - | - | false | L0 | - |
| gate_engine | - | - | false | L0 | - |

## 验收标准

```bash
# 1. 文件数量
find skillforge/specs -name "*.skill.yml" | wc -l   # == 18

# 2. 每个文件 YAML 格式合法
python -c "
import yaml
from pathlib import Path
specs_dir = Path('skillforge/specs')
for f in sorted(specs_dir.rglob('*.skill.yml')):
    data = yaml.safe_load(f.read_text(encoding='utf-8'))
    assert 'skill_id' in data, f'{f}: missing skill_id'
    assert 'input' in data, f'{f}: missing input'
    assert 'output' in data, f'{f}: missing output'
    print(f'  [PASS] {f.name}')
print(f'Total: {len(list(specs_dir.rglob(\"*.skill.yml\")))} specs')
"

# 3. skill_id 与文件名一致
python -c "
import yaml
from pathlib import Path
for f in sorted(Path('skillforge/specs').rglob('*.skill.yml')):
    data = yaml.safe_load(f.read_text(encoding='utf-8'))
    expected = f.stem.replace('.skill', '')
    assert data['skill_id'] == expected, f'{f}: skill_id mismatch {data[\"skill_id\"]} != {expected}'
print('All skill_id checks passed')
"
```

## 注意事项

- 这个任务与 T11 **完全并行**，不需要等 T11 完成
- 数据来源是 `claude的输出.md` 中的 docstring，不需要实际运行代码
- `capabilities` 要基于模块实际需求判断，不要全填 false
- adapter 类型的 Skill Spec 不需要 `paths` 和 `stage` 字段
