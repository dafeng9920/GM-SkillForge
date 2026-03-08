# T79: Git 治理与追溯基线

---
task_id: "T79"
executor: "Kior-C"
reviewer: "Antigravity-3"
compliance_officer: "vs--cc1"
wave: "Wave Governance"
depends_on: ["T70", "T71", "T72", "T73", "T74", "T75", "T76", "T77", "T78"]
estimated_minutes: 30
---

## 1. 任务目标

建立 Git 治理与追溯基线，确保所有 P2 任务变更可追溯、可审计、可回滚。

## 2. 输入规格

```yaml
input:
  description: "Git 治理与追溯基线建立"
  context_files:
    - path: "docs/2026-02-22/verification/"
      purpose: "验证文件目录"
    - path: ".git/"
      purpose: "Git 仓库状态"
    - path: "docs/2026-02-22/verification/closing_pack_index.json"
      purpose: "P1 收包基线"
  constants:
    job_id: "L4-P2-HARDENING-20260222-001"
    scope: "P2-GOVERNANCE"
```

## 3. 输出交付物

```yaml
output:
  deliverables:
    - path: "docs/2026-02-22/tasks/T79_Kior-C.md"
      type: "新建"
      purpose: "任务定义"
    - path: "docs/2026-02-22/verification/git_governance_baseline.md"
      type: "新建"
      purpose: "Git 治理基线文档"
    - path: "docs/2026-02-22/verification/T79_execution_report.yaml"
      type: "新建"
      purpose: "执行报告"
    - path: "docs/2026-02-22/verification/T79_gate_decision.json"
      type: "新建"
      purpose: "门禁决策"
    - path: "docs/2026-02-22/verification/T79_compliance_attestation.json"
      type: "新建"
      purpose: "合规认证"
  constraints:
    - "必须记录当前 Git 状态（分支、提交、变更）"
    - "必须列出所有待追溯文件"
    - "必须提供变更追溯表"
```

## 4. 禁止操作

```yaml
deny:
  - "不得修改 .git 目录"
  - "不得删除已有提交记录"
  - "不得伪造追溯信息"
```

## 5. Gate 检查

```yaml
gate:
  auto_checks:
    - command: "git status --porcelain"
      expect: "列出变更文件"
    - command: "验证 git_governance_baseline.md 存在"
      expect: "file_exists"
  manual_checks:
    - "Git 状态记录完整性"
    - "追溯表覆盖所有 P2 产物"
```

## 6. 治理基线数据结构

```yaml
git_governance_baseline:
  captured_at: "ISO-8601"
  repository_status:
    current_branch: "string"
    last_commit: "sha"
    uncommitted_changes: ["file list"]
  traceability_matrix:
    - task_id: "Txx"
      files_created: ["path"]
      files_modified: ["path"]
      evidence_refs: ["EV-xxx"]
  compliance_summary:
    all_tasks_traced: true|false
    orphan_files: ["path"]
```
