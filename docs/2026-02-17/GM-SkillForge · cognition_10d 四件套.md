# GM-SkillForge · cognition_10d 四件套（可直接落盘版）

## 0. 说明
- 本文为四件套交付包（单文件汇总）。
- 已清洗：去除 `DownloadCopy code` 噪声、修复语法、统一术语。
- 术语冻结：`10D == 10阶 == L1-L10 结构化输出`。

---

## A. 文件：`cognition_10d.intent.md`

### 1) 元信息
| field | value |
|---|---|
| intent_id | cognition_10d |
| version | 1.0.0 |
| owner | gm-skillforge |
| fail_mode | CLOSED |

### 2) Request Schema（全部必填）
```yaml
request:
  repo_url: { type: string, format: uri, required: true }
  commit_sha: { type: string, pattern: "^[0-9a-f]{40}$", required: true }
  at_time: { type: string, format: date-time, required: true }
  rubric_version: { type: string, pattern: "^\\d+\\.\\d+\\.\\d+$", required: true }
  requester_id: { type: string, required: true }
```

### 3) Response Schema
```yaml
response:
  intent_id: { type: string, const: cognition_10d }
  status: { type: string, enum: [PASSED, REJECTED] }
  repo_url: { type: string }
  commit_sha: { type: string }
  at_time: { type: string }
  rubric_version: { type: string }
  dimensions:
    type: array
    minItems: 10
    maxItems: 10
    items:
      type: object
      required: [dim_id, label, score, threshold, verdict, evidence_ref]
      properties:
        dim_id: { type: string }
        label: { type: string }
        score: { type: number, minimum: 0, maximum: 100 }
        threshold: { type: number }
        verdict: { type: string, enum: [PASS, FAIL] }
        evidence_ref: { type: string }
  overall_pass_count: { type: integer, minimum: 0, maximum: 10 }
  rejection_reasons: { type: array, items: { type: string } }
  audit_pack_ref: { type: string }
  generated_at: { type: string, format: date-time }
```

### 4) Fail-Closed
- FC-1 repo_url 非法 -> REJECTED
- FC-2 commit_sha 非 40 位 hex -> REJECTED
- FC-3 at_time 非 ISO-8601 -> REJECTED
- FC-4 rubric_version 未注册 -> REJECTED
- FC-5 dimensions 数量 != 10 -> REJECTED
- FC-6 任一 evidence_ref 为空/不可解析 -> REJECTED
- FC-7 任一维缺 required 字段 -> REJECTED

### 5) 治理边界
- n8n：只编排（触发/路由/重试/通知）。
- SkillForge：裁决与证据。
- 无 permit：禁止 publish/tag/release。

---

## B. 文件：`cognition_10d_generator.skill.md`

### 1) 元信息
| field | value |
|---|---|
| skill_id | cognition_10d_generator |
| implements | cognition_10d intent v1.0.0 |
| type | evaluator |
| fail_mode | CLOSED |

### 2) 职责
- 输入：确定性快照 + rubric。
- 输出：L1-L10 评分、每维 evidence_ref、总体 status。

### 3) 非目标
- 不发布。
- 不签发 permit。
- 不修改 rubric。

### 4) Entry Guard
先跑 FC-1..FC-4；失败直接 REJECTED，并返回 10 维哨兵：
- score=0
- verdict=FAIL
- evidence_ref="N/A:input_validation_failed"

### 5) 证据检查点
- CP-1: `entry_guard_result.json`
- CP-2: `dimension_evidence/L{n}.md`
- CP-3: `scores_matrix.json`
- CP-4: `verdict.json`
- CP-5: `summary.json`

证据头统一：
```yaml
_meta:
  skill_id: cognition_10d_generator
  repo_url: <repo_url>
  commit_sha: <commit_sha>
  at_time: <at_time>
  rubric_version: <rubric_version>
  checkpoint: <CP-N>
  written_at: <ISO-8601>
```

### 6) AuditPack 布局
```text
AuditPack/
  cognition_10d/
    {commit_sha}/
      entry_guard_result.json
      scores_matrix.json
      verdict.json
      summary.json
      dimension_evidence/L1.md ... L10.md
      traces/trace.log
```

audit_pack_ref：`AuditPack/cognition_10d/{commit_sha}/`

### 7) Gate 协议
- generator -> gate: `cognition_10d.completed` + `summary.json`
- gate -> downstream: `permit_granted` | `permit_denied`
- generator 永不签发 permit。

---

## C. 文件：`cognition_10d_rubric.yml`

```yaml
rubric_id: cognition_10d_rubric
rubric_version: "1.0.0"
effective_from: "2026-02-17T00:00:00Z"
schema_compat: "cognition_10d.intent/1.0.0"

dimensions:
  - { dim_id: L1, label: "事实提取", threshold: 60 }
  - { dim_id: L2, label: "概念抽象", threshold: 55 }
  - { dim_id: L3, label: "因果推理", threshold: 60 }
  - { dim_id: L4, label: "结构解构", threshold: 55 }
  - { dim_id: L5, label: "风险感知", threshold: 60 }
  - { dim_id: L6, label: "时序建模", threshold: 50 }
  - { dim_id: L7, label: "跨域关联", threshold: 50 }
  - { dim_id: L8, label: "不确定性标注", threshold: 55 }
  - { dim_id: L9, label: "建议可行性", threshold: 55 }
  - { dim_id: L10, label: "叙事连贯性", threshold: 60 }

overall_policy:
  pass_min_count: 8
  critical_dimensions: [L1, L3, L5, L10]
  rule: "pass_count >= 8 且 critical_dimensions 全 PASS 才是 PASSED"

meta:
  created_by: gm-skillforge
  created_at: "2026-02-17T00:00:00Z"
  change_policy: "变更必须升级版本并保留旧版以支持 at-time 回放"
```

---

## D. 目录：`cognition_10d_cases/`

### `README.md`
```md
# cognition_10d regression cases

- rubric: cognition_10d_rubric v1.0.0
- total: 4
- pass: 2
- reject: 2

files:
- case_pass_full_score.yml
- case_pass_boundary.yml
- case_reject_critical_fail.yml
- case_reject_input_invalid.yml
```

### `case_pass_full_score.yml`
```yaml
case_id: case_pass_full_score
expected: { status: PASSED, overall_pass_count: 10, rejection_reasons: [] }
assertions:
  - 'len(dimensions) == 10'
  - 'all(d.evidence_ref != "" for d in dimensions)'
```

### `case_pass_boundary.yml`
```yaml
case_id: case_pass_boundary
expected: { status: PASSED, overall_pass_count: 8, rejection_reasons: [] }
assertions:
  - 'critical(L1,L3,L5,L10) are PASS'
  - 'len(dimensions) == 10'
```

### `case_reject_critical_fail.yml`
```yaml
case_id: case_reject_critical_fail
expected: { status: REJECTED, overall_pass_count: 9, rejection_reasons: [L5] }
assertions:
  - 'L5 verdict == FAIL'
  - 'len(dimensions) == 10'
```

### `case_reject_input_invalid.yml`
```yaml
case_id: case_reject_input_invalid
mock_input:
  commit_sha: "abcdef1234567890abcd"
expected:
  status: REJECTED
  overall_pass_count: 0
  rejection_reasons: ["FC-2:commit_sha_invalid"]
assertions:
  - 'all(d.score == 0 for d in dimensions)'
  - 'all(d.verdict == "FAIL" for d in dimensions)'
  - 'all(d.evidence_ref == "N/A:input_validation_failed" for d in dimensions)'
```

---

## 交付检查（本版）
- `contracts-first`：已覆盖
- `evidence_ref`：已覆盖
- `L3 AuditPack`：已覆盖
- `Fail-Closed`：已覆盖
- `确定性输入`：已覆盖
- `n8n 不裁决`：已覆盖
- `无 permit 不发布`：已覆盖
