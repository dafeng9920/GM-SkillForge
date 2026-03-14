# Dual Gate Verification: tg1-official-20260305-0816-bd6a

**Generated At**: 2026-03-05T08:16:56+00:00Z
**Overall Decision**: FAIL
**Reason**: All gates failed

## Summary

- **Total Gates**: 2
- **Passed**: 0
- **Failed**: 2

## Gate 1: Receipt Verification

**Status**: FAIL
**Timestamp**: 2026-03-05T08:16:56+00:00Z

FAIL
- receipt status must be success for acceptance, got: failure



## Gate 2: Cloud Lobster Mandatory Gate

**Status**: DENY
**Timestamp**: 2026-03-05T08:16:56+00:00Z

============================================================
[CL-MG] Cloud Lobster Mandatory Gate
[CL-MG] Started at 2026-03-05T08:16:56.376905+00:00
[CL-MG] Environment: LOCAL-ANTIGRAVITY -> CLOUD-ROOT
[CL-MG] Dispatch dir: .tmp\openclaw-dispatch
============================================================
============================================================
[CL-MG] Final Decision: DENY
============================================================

[CL-MG] DENY - Cloud lobster mandatory gate failed
[CL-MG] Error code: SF_CLOUD_LOBSTER_BYPASS_ATTEMPT

[CL-MG] Errors (1):
  [SF_CLOUD_LOBSTER_BYPASS_ATTEMPT] 1 task(s) failed cloud lobster mandatory gate

[CL-MG] Required changes (1):
  1. Use cloud-lobster-closed-loop-skill for all CLOUD-ROOT executions

[CL-MG] Violation reports written to: docs\compliance_reviews
DENY



## Overall Decision

FAIL: All gates failed
