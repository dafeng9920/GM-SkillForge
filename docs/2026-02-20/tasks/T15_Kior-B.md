# Task Skill Spec

```yaml
task_id: "T15"
executor: "Kior-B"
wave: "Wave 1"
depends_on: []
estimated_minutes: 90

input:
  description: "外部 Skill 治理门禁编排：导入前审计、导入后 tombstone/at-time 口径、fail-closed 阻断矩阵"
  context_files:
    - path: "skills/release-gate-skill/SKILL.md"
      purpose: "Experience Capture Mode 与治理基线"
    - path: "docs/2026-02-20/L4.5 启动清单 v2（2026-02-20）.md"
      purpose: "n8n 职责边界与 fail-closed 目标"
    - path: "docs/2026-02-20/task_dispatch_T12-T16_external_skill_governance.md"
      purpose: "读取批次目标与收口要求"
  constants:
    job_id: "L45-D3-EXT-SKILL-GOV-20260220-003"
    skill_id: "l45_external_skill_governance_batch1"

output:
  deliverables:
    - path: "docs/2026-02-20/L45_EXTERNAL_SKILL_GOVERNANCE_MATRIX_v1.md"
      type: "新建"
      schema_ref: "阻断矩阵 + 放行矩阵"
    - path: "docs/2026-02-20/n8n/l45_day3_external_skill_workflow.json"
      type: "新建"
      schema_ref: "外部 Skill 导入工作流"
    - path: "docs/2026-02-20/L45_EXTERNAL_SKILL_GOVERNANCE_RUNBOOK_v1.md"
      type: "新建"
      schema_ref: "执行与故障排查手册"
  constraints:
    - "必须定义 no-permit-no-import 规则"
    - "tombstone 默认不可见，仅 at-time 可回放"
    - "失败分支不得自动重试业务阻断错误"
    - "required_changes 必须可执行、可复核"

deny:
  - "不得让 n8n 直接写最终裁决"
  - "不得删除 E001/E003 等阻断语义"
  - "不得将 tombstone 设计为物理删除"

gate:
  auto_checks:
    - command: "python -m json.tool docs/2026-02-20/n8n/l45_day3_external_skill_workflow.json > nul"
      expect: "valid json"
  manual_checks:
    - "矩阵中包含成功/阻断/回放三类场景"
    - "runbook 能独立指导一次完整演练"
```

