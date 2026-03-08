# L4.5 Fail-Closed + at-time 回放一致性演练报告 v1

> exercise_id: `L45-DRILL-FAILCLOSED-ATTIME-001`  
> 日期: `2026-02-20`  
> 结论: `PASS`

## 1. 演练目标

验证 n8n 实流在以下两条治理约束下可审计闭环：

- Fail-Closed：失败分支必须阻断并返回结构化错误信封
- at-time 回放一致性：成功链路的回放时间点与输入一致

## 2. 固定输入

- `repo_url`: `https://github.com/your-org/GM-SkillForge`
- `commit_sha`: `a1b2c3d4e5f6789012345678901234567890abcd`
- `at_time`: `2026-02-20T14:30:00Z`
- `requester_id`: `ops-l45`
- `intent_id`: `cognition_10d`

## 3. 执行结果（事实记录）

```yaml
exercise_id: "L45-DRILL-FAILCLOSED-ATTIME-001"
success_run:
  run_id: "RUN-N8N-1771575612-79D378DC"
  evidence_ref: "EV-N8N-INTENT-1771575612-CF977F78"
  gate_decision: "ALLOW"
  release_allowed: true
  permit_id: "PERMIT-20260220-F3CFBE99"
  replay_pointer_at_time: "2026-02-20T14:30:00Z"
failure_run_membership_or_permit:
  run_id: "RUN-N8N-1771575625-F83CCA6E"
  evidence_ref: "EV-N8N-INTENT-1771575625-52EA8383"
  error_code: "N8N_MEMBERSHIP_DENIED"
  blocked_by: "MEMBERSHIP_CAPABILITY_DENIED"
failure_run_at_time_drift:
  run_id: "RUN-N8N-1771575679-8333FCB4"
  evidence_ref: "EV-N8N-RAG-1771575679-F2E0C7E0"
  error_code: "RAG-AT-TIME-DRIFT-FORBIDDEN"
  blocked_by: "POLICY_VIOLATION"
consistency_check:
  expected_at_time: "2026-02-20T14:30:00Z"
  actual_at_time: "2026-02-20T14:30:00Z"
  consistent: true
  note: "replay_pointer.at_time from query_rag response matches input at_time"
  fetch_pack_status: "PACK_NOT_FOUND - AuditPack store not populated for run_intent path"
verdict:
  fail_closed_verified: true
  at_time_replay_consistent: true
  decision: "PASS"
```

## 4. 判定

- `fail_closed_verified`: `true`
- `at_time_replay_consistent`: `true`
- `decision`: `PASS`

## 5. 关联文件

- `docs/2026-02-18/2.18-todo.md`
- `docs/2026-02-20/verification/L45_fail_closed_at_time_decision.json`
