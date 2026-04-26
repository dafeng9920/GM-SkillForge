你是任务 `UI3` 的审查者 `vs--cc1`。

你只做 review，不做 execution，不做 compliance。
权威项目树以 `D:\\gm-lite` 为准。

## Must read
- `D:\\gm-lite\\docs\\2026-04-01\\verification\\gm_lite_dialog_first_triad_surface_fix\\UI3_execution_report.md`

## Must write
- `D:\\gm-lite\\docs\\2026-04-01\\verification\\gm_lite_dialog_first_triad_surface_fix\\UI3_review_report.md`

## Review focus
- Verify the dialog provides explicit recovery actions for common failure states.
- Verify it tells the user where the chain is blocked.
- Verify the report points to real code paths in `D:\\gm-lite`.

## Required fields
1. `task_id: UI3`
2. `reviewer / executor`
3. `PASS / REQUIRES_CHANGES / FAIL`
4. error recovery review focus
5. at least one `EvidenceRef`

## Default next hop
- compliance -> `Kior-C`
