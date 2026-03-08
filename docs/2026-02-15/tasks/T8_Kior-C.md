# T8 任务书 - Kior-C

> **任务编号**：T8
> **波次**：Wave 3
> **依赖**：无（Wave 1-2 已完成）
> **预计时长**：30 分钟

## 目标

在 `orchestration/examples/tech_seo_audit/` 目录下创建 8 节点流水线的端到端 golden example，演示 `tech_seo_audit` 技能从入口到发布的完整数据流。

## 交付物

| 文件 | 类型 | 说明 |
|------|------|------|
| `orchestration/examples/tech_seo_audit/stage0_intake_repo.json` | 新建 | Stage 0 输入输出 |
| `orchestration/examples/tech_seo_audit/stage1_license_gate.json` | 新建 | Stage 1 输入输出 |
| `orchestration/examples/tech_seo_audit/stage2_repo_scan_fit_score.json` | 新建 | Stage 2 输入输出 |
| `orchestration/examples/tech_seo_audit/stage3_draft_skill_spec.json` | 新建 | Stage 3 输入输出 |
| `orchestration/examples/tech_seo_audit/stage4_constitution_risk_gate.json` | 新建 | Stage 4 输入输出 |
| `orchestration/examples/tech_seo_audit/stage5_scaffold_skill_impl.json` | 新建 | Stage 5 输入输出 |
| `orchestration/examples/tech_seo_audit/stage6_sandbox_test_and_trace.json` | 新建 | Stage 6 输入输出 |
| `orchestration/examples/tech_seo_audit/stage7_pack_audit_and_publish.json` | 新建 | Stage 7 输入输出 |

## 实现指导

### 每个 Stage JSON 的结构

每个文件必须遵循对应的 `orchestration/nodes/{node_id}.node.schema.json` 结构：

```json
{
  "node_id": "<对应节点 ID>",
  "stage": <0-7>,
  "input": { ... },   // 参照 node schema 的 input 定义
  "output": { ... }   // 参照 node schema 的 output 定义
}
```

### 关键数据流约束

数据必须前后衔接——上一个 Stage 的 output 应该能作为下一个 Stage 的 input 使用。

**统一使用以下贯穿值：**
- `repo_url`: `"https://github.com/nichochar/tech-seo-tool"`
- `job_id`: `"550e8400-e29b-41d4-a716-446655440000"`
- `commit_sha`: `"a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"`
- `license_spdx`: `"MIT"`
- `skill_id`: `"tech_seo_audit"`

### Stage 0 (intake_repo) 示例

```json
{
  "node_id": "intake_repo",
  "stage": 0,
  "input": {
    "repo_url": "https://github.com/nichochar/tech-seo-tool",
    "branch": "main",
    "target_environment": "python",
    "intended_use": "web"
  },
  "output": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "build_record": {
      "repo_name": "tech-seo-tool",
      "repo_owner": "nichochar",
      "default_branch": "main",
      "stars": 42,
      "last_commit": "a1b2c3d4",
      "license_detected": "MIT"
    }
  }
}
```

### Stage 4 (constitution_risk_gate) — 必须使用 gate_decision 合同格式

output 中的 `gate_decision` 字段必须符合 `schemas/gate_decision.schema.json`：
- `decision`: 使用 `"ALLOW"`
- `risk_tier`: 使用 `"L1"`

### Stage 7 (pack_audit_and_publish) — 输出需包含发布状态

output 中的 `publish_result` 字段需要包含 `status: "published"`。

### 参考文件

- 8 个 node schema: `orchestration/nodes/*.node.schema.json`
- 流水线定义: `orchestration/pipeline_v0.yml`（查看 consumes/produces）
- 产物流转图: `skillforge/docs/ARTIFACTS.md`

## 红线（不允许）

- ❌ 不得修改任何现有 schema 或 policy 文件
- ❌ 不得修改 `contract_tests/` 下的任何文件
- ❌ json 中不得出现注释（JSON 不支持注释）
- ❌ 数据流不得断链（Stage N 的 output 必须能衔接 Stage N+1 的 input）

## 验收标准

1. 8 个 JSON 文件全部是有效 JSON（可解析）
2. 每个文件的 `node_id` 和 `stage` 值与文件名一致
3. 数据流贯穿：job_id / commit_sha / skill_id 在各 Stage 中一致
4. `pytest -q` 仍然全绿（24+ passed）
5. 使用 `python tools/validate.py` 可手动校验 Stage 4 的 gate_decision 产出

```bash
# 验证 JSON 可解析
python -c "import json, pathlib; [json.loads(f.read_text()) for f in pathlib.Path('orchestration/examples/tech_seo_audit').glob('*.json')]"

# 验证 pytest 不受影响
pytest -q
```

## 汇报格式

```
任务编号：T8
执行者：Kior-C
状态：已完成

改动文件：
- orchestration/examples/tech_seo_audit/stage0_intake_repo.json (新建)
- orchestration/examples/tech_seo_audit/stage1_license_gate.json (新建)
- ... (共 8 个文件)

验证结果：
[粘贴 JSON 解析和 pytest 结果]

请主控官验收。
```
