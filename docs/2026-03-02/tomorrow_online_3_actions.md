# Tomorrow Online: Only 3 Actions

## Scope

For next login window (20:30-21:00), only do these 3 actions.

## Action 1: Pull R0 evidence package

Check and collect:

- `stability/stability_report.json`
- `stability/monitor.log` tail 40
- `crontab -l`
- top line conclusion: `RHYTHM_FIX_VERIFIED=true|false`

Decision:

- If `false`: no business contract, execute only minimal fix
- If `true`: continue to Action 2

## Action 2: Local gate decision

Run local gate decision with evidence:

1. Verify rhythm fix requirements (2 cron samples, +1 hour_index, +1 consecutive pass)
2. Verify critical errors all zero
3. Set gate result:
   - `OPEN` => can prepare next contract
   - `CLOSED` => keep freeze mode

## Action 3: Decide P3 unlock

Unlock P3 only if:

- R0 hard rules all pass
- gate state remains `OPEN`
- no rollback event unresolved

If unlocked:

- create `P3-A` read-only reconnaissance contract first
- do not start write/deploy actions in P3-A

If not unlocked:

- keep P3 blocked
- continue hourly stability observation

