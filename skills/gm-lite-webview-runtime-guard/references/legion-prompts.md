# Legion Prompts

Use these prompts when the AI legion needs to work on GM-Lite webview runtime faults.

## Execution Prompt

```text
Use $gm-lite-webview-runtime-guard at D:\GM-SkillForge\skills\gm-lite-webview-runtime-guard.

Task: diagnose or repair the GM-Lite main workbench webview runtime.

Mandatory rules:
1. Classify the fault strictly as boot, snapshot delivery, or render layer.
2. Collect evidence from both:
   - GM-Lite webview frame console
   - Extension Host logs
3. Do not conclude triad/backend failure before WV0/WV2 evidence is checked.
4. Do not claim PASS unless the page is visibly restored or the targeted hop is explicitly verified.
5. Output these sections only:
   - Failure Hop
   - Evidence
   - Root Cause
   - Changed Files
   - Verification
   - Remaining Risk

Expected evidence markers include:
- external bootstrap loaded
- webview script booted
- snapshot message received
- SNAPSHOT / TRIAD render errors
```

## Review Prompt

```text
Use $gm-lite-webview-runtime-guard at D:\GM-SkillForge\skills\gm-lite-webview-runtime-guard.

Review the submitted GM-Lite webview runtime repair.

Mandatory review rules:
1. Reject if the execution report skips WV0/WV2 evidence.
2. Reject if the report uses only backend snapshot logs.
3. Reject if the report claims PASS without proving which hop was fixed.
4. Distinguish:
   - boot fixed
   - snapshot delivery fixed
   - render layer fixed
5. Output:
   - Verdict
   - Findings
   - Missing Evidence
   - Required Changes
```

## Compliance Prompt

```text
Use $gm-lite-webview-runtime-guard at D:\GM-SkillForge\skills\gm-lite-webview-runtime-guard.

Perform B-Guard style compliance review for a GM-Lite webview runtime repair.

Mandatory compliance rules:
1. Compliance cannot pass unless Review is PASS.
2. Compliance cannot pass if evidence is only oral or only backend-side.
3. Compliance must state exactly which hop is verified:
   - boot
   - snapshot delivery
   - render layer
4. If page restoration is claimed, require concrete runtime evidence.
5. Output:
   - Compliance Verdict
   - Verified Hop
   - Evidence Basis
   - Rejection Reason or Approval Basis
```

## Fast Operator Prompt

```text
Use $gm-lite-webview-runtime-guard at D:\GM-SkillForge\skills\gm-lite-webview-runtime-guard.

Give me the next single most useful check for the current GM-Lite webview runtime fault.
Return only:
- Current Hop
- Next Check
- Pass Condition
- Fail Condition
```
