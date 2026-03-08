task_id: "T76"
executor: "vs--cc3"
reviewer: "Antigravity-1"
compliance_officer: "Kior-B"
wave: "Wave B"
depends_on: ["T70", "T71", "T72", "T73"]
estimated_minutes: 60

input:
  description: "P2-07 n8n 集成状态探针与安全边界验证"
  context_files:
    - path: "ui/app/src/pages/execute/RunIntentPage.tsx"
      purpose: "n8n run_intent 端点调用"
    - path: "ui/app/src/mocks/orchestrationProjection.mock.ts"
      purpose: "n8n mock 数据与 fail-closed 场景"
    - path: "ui/app/src/app/layout/AppShell.tsx"
      purpose: "设计规范：不出现 n8n 顶层导航"
  constants:
    job_id: "L3-P2-HARDENING-20260222-001"
    task_scope: "P2-07"

output:
  deliverables:
    - path: "docs/2026-02-22/verification/n8n_probe_report.json"
      type: "新建"
  constraints:
    - "n8n 端点/集成点必须列出 pass/fail 状态"
    - "fail-closed 行为必须有证据"

deny:
  - "不得伪造端点状态"
  - "不得声称 IMPLEMENTED 但无证据"

gate:
  auto_checks:
    - command: "cat docs/2026-02-22/verification/n8n_probe_report.json"
      expect: "valid JSON with probe results"
  manual_checks:
    - "探针报告覆盖所有已知 n8n 集成点"
    - "fail-closed 场景有代码引用"

acceptance_criteria:
  - "所有 n8n 端点状态为 VERIFIED 或 NOT_IMPLEMENTED（非 UNKNOWN）"
  - "fail-closed 边界有代码级证据"
  - "报告包含可复现检查步骤"
