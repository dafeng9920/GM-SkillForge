结论：
给你。**Gap Analysis 模板属于 v0 范围**——但要克制：v0 只需要支持“让 AI 可修复 + 让审计器可复核”的最小字段集（不做复杂推理、不给自由发挥）。它是你“硬裁决 + 软修复”的桥梁，不做它 v0 也能跑，但会显著降速、增加人工介入。

置信度：0.88

关键风险点：

1. Gap 过于自由文本化 → AI 修复不稳定、审计不可复核
2. Gap 过于细碎（上来就全覆盖）→ 开发成本爆炸
3. Gap 直接修改宪法/合同 → 破坏需求复现（必须通过迭代流程）

---

# Gap Analysis v0 模板（可喂给 AI 修复 & 可被审计复核）

> 文件建议名：`audit/gaps/<revision_id>.gap.json`
> 设计原则：**机器可验证（可复核）+ 机器可执行（可修复）**
> 其中 “evidence_refs + pointers + policy_refs + expected_vs_observed” 是审计可复核的关键。

```json id="zeb6fo"
{
  "schema_version": "gap_analysis_v0",
  "revision": {
    "revision_id": "rev_...",
    "demand_hash": "sha256:...",
    "contract_hash": "sha256:...",
    "decision_hash": "sha256:..."
  },

  "scope": {
    "intent_id": "generate_skill_from_nl",
    "level_target": "L3",
    "gate_name": "constitution_risk_gate",
    "error_code": "SF_CONSTITUTION_VIOLATION",
    "severity": "BLOCKER" 
  },

  "anchors": {
    "policy_refs": [
      { "ref": "#Policy[Default_L3_Constitution]", "version": "v0" }
    ],
    "asset_refs": [
      { "ref": "#API[Notion_v1]", "version": "2026-01" },
      { "ref": "#Schema[Notion_Report_v1]", "version": "1.0.0" }
    ]
  },

  "summary": {
    "title": "Unbounded network access detected in sink module",
    "one_liner": "Code introduces outbound HTTP calls that violate network_policy=deny_by_default.",
    "confidence": 0.86
  },

  "findings": [
    {
      "finding_id": "F_001",
      "category": "CONTROL_VIOLATION",
      "severity": "BLOCKER",

      "expected": {
        "rule_id": "NET_001",
        "statement": "network_policy must be deny_by_default; outbound calls allowed only to allowlist domains",
        "constraint_path": "/controls/network_policy",
        "expected_value": "deny_by_default"
      },

      "observed": {
        "signal_type": "static_scan",
        "signal_id": "SCAN_NET_443",
        "location": {
          "repo_path": "skills/email_pdf_to_notion/sink.py",
          "line_start": 42,
          "line_end": 55
        },
        "observed_snippet_hash": "sha256:...", 
        "observed_value": "requests.get('https://example.com/...')"
      },

      "evidence_refs": [
        {
          "evidence_ref_id": "ev_...",
          "content_hash": "sha256:...",
          "locator": "artifacts://static_analysis.log#L120-L145",
          "tool_revision": "static_denylist_scan@v0.1"
        }
      ],

      "impact": {
        "why_it_matters": "Violates constitution; cannot sign Permit.",
        "blast_radius": "All deployments",
        "risk_tags": ["network", "exfiltration"]
      },

      "required_changes": [
        {
          "change_id": "C_001",
          "kind": "CODE_EDIT",
          "target": {
            "repo_path": "skills/email_pdf_to_notion/sink.py",
            "range": { "line_start": 42, "line_end": 55 }
          },
          "instruction": "Remove outbound HTTP call. Replace with approved Notion API client only.",
          "acceptance_assertions": [
            "static_scan.denylist_hits == 0",
            "no_new_network_calls == true"
          ]
        },
        {
          "change_id": "C_002",
          "kind": "CONFIG_EDIT",
          "target": {
            "path": "contracts/demand/email_pdf_to_notion.demand.yml",
            "json_pointer": "/controls/allowed_domains"
          },
          "instruction": "If outbound domain is truly required, add to allowlist with explicit justification; otherwise keep empty.",
          "acceptance_assertions": [
            "allowed_domains contains only approved domains",
            "rationale provided for allowlist change"
          ]
        }
      ],

      "fix_hints_for_ai": {
        "do": [
          "Prefer existing adapters referenced in AssetRefs",
          "Keep changes minimal; do not modify controls unless explicitly required"
        ],
        "dont": [
          "Do not change gate_plan",
          "Do not add new external dependencies",
          "Do not add secrets to code or logs"
        ]
      }
    }
  ],

  "regression_safety": {
    "must_not_break": [
      { "test_id": "T1_valid_pdf_creates_page" },
      { "test_id": "T2_failure_notifies" }
    ],
    "run_plan": {
      "mode": "tests_only",
      "commands": [
        { "name": "pytest", "argv": ["pytest", "-q"], "timeout_sec": 300 }
      ]
    }
  },

  "closure": {
    "closure_rule": "All BLOCKER findings resolved AND acceptance_assertions satisfied",
    "recheck_gates": ["constitution_risk_gate", "sandbox_test_and_trace", "pack_audit_and_publish"],
    "outputs_expected": [
      "updated_decision_hash",
      "updated_audit_pack_hash",
      "permit_issued == true"
    ]
  }
}
```

---

## 为什么这个模板“AI 好修 + 审计可复核”

### AI 能修的关键字段

* `required_changes[*].instruction`（明确该改什么）
* `target`（明确改哪里）
* `do/dont`（防止越界）
* `acceptance_assertions`（改完怎么判定通过）

### 审计能复核的关键字段

* `expected`（合同/宪法的可定位约束：constraint_path + rule_id）
* `observed.location + observed_snippet_hash`（对齐到具体代码/日志片段）
* `evidence_refs`（hash+locator+tool_revision）
* `closure`（何时算闭环）

---

# 这是不是 v0 范围？

是，但建议按下面口径收敛成 **v0-min**：

v0 必须有：

* `revision（三哈希引用）`
* `scope(gate_name/error_code/severity)`
* 每条 finding 的：`expected/observed/evidence_refs/required_changes`
* `closure(closure_rule/recheck_gates)`

v0 可选（先不做也行）：

* `impact` 的复杂风险建模
* `regression_safety` 的复杂策略
* `confidence` 的模型评分体系

> v0 的目标不是“全自动修复一切”，而是：**FAIL → 结构化差异 → AI 按指令改 → Gate 重跑 → PASS**。

---

