name: n8n-workflow-automation
description: [SHC-CERTIFIED] Industrial-grade n8n workflow designer with baked-in Fail-Closed logic and Triple-Hash auditing.
version: 1.0.0-SHC
status: HARDENING_CERTIFIED (SHC-v1.0)
tier: ENTERPRISE_GOVERNED
security_policy: FAIL_CLOSED
risk_level: MEDIUM (Internal Orchestration)
last_audit_at: 2026-03-05
---

# n8n-workflow-automation-skill

## Trigger Conditions

- Need to automate cross-app tasks (Notion, Zapier, Trello, etc.)
- Requirement for auditable and failsafe workflow JSON
- Complex branching logic or external API orchestration

## Input

```yaml
input:
  workflow_intent: "Sync emails to Notion and notify Zapier"
  apps_to_link: ["Email", "Notion", "Zapier"]
  reliability_level: "HIGH (Retry + Dead Letter Queue)"
  human_in_the_loop: true
```

## Output

```yaml
output:
  n8n_workflow_json: { ... }  # Standard n8n JSON format
  runbook_template: "Runbook-2026-03-04-n8n.md"
  audit_metadata:
    idempotency_key: "SF-N8N-XXXX"
    error_handling_strategy: "FAIL_OVER_TO_REVIEW_QUEUE"
```

## Core Design Principles (Premium Aesthetics & Reliability)

1.  **Idempotency First**: Use deterministic node IDs and check for existing records before creation.
2.  **Graceful Degradation**: Every critical node must have an "On Error" path to a "Review Queue" or "Logging Node".
3.  **Visual Clarity**: Organize nodes in a logical left-to-right flow with clear annotations.
4.  **No Silent Failures**: Use the `Error Trigger` node to capture global workflow failures.

## Implementation Steps

### Step 1: Design Workflow JSON
Generate the `.json` structure compatible with n8n v1.0+.
- Include `Webhook`, `HTTP Request`, or `App Specific` (Notion/Trello) nodes.
- Ensure `alwaysOutputData: true` is set for critical nodes.

### Step 2: Create Runbook Template
Provide a markdown runbook that describes:
- **Authentication**: Which credentials need to be linked in n8n.
- **Webhook Config**: The production URL mapping.
- **Rollback**: How to manually revert actions if the workflow partially fails.

## Example Pattern: Notion + Zapier + Trello
1.  **Webhook Trigger**: Receives data from OpenClaw.
2.  **Item Lists Node**: Normalizes data.
3.  **Notion Node**: Creates/Updates page.
4.  **Zapier Webhook Node**: Triggers external Slack/Notification.
5.  **Trello Node**: Syncs status to the board.

## DoD

- [ ] n8n Workflow JSON generated (valid schema)
- [ ] Runbook template with auth instructions provided
- [ ] Idempotency keys included in JSON
- [ ] Error paths defined for all external API nodes
- [ ] Security scan "Benign" status noted in metadata

---

> "Automation is not just making it run; it's making it survive the unexpected."
