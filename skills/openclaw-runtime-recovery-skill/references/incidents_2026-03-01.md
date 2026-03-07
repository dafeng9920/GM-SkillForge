# OpenClaw Runtime Incident Log (2026-03-01)

## Incident Summary

- Symptom: Bot online in Discord but no reply or intermittent failure message.
- Environment: Tencent Cloud VPS, docker-compose deployment.
- Impact: Reply path unavailable for long window (~20h troubleshooting period).

## Observed Error Patterns

1. `Unknown model: openai/glm-5.0` / `openai/glm-5` / `openai/glm-4-flash`
2. `No API key found for provider "zai"`
3. `EACCES: permission denied, mkdir '/root/.openclaw/agents/main/sessions'`
4. `failed to bind host port ... 127.0.0.1:18789 ... address already in use`
5. `cannot remove container ... did not receive an exit event`
6. Discord API: `Unknown Channel (10003)` when wrong channel id was used.

## Root Cause Tree

### A. Runtime/Process layer

- Host had stray `openclaw-gateway` process occupying `127.0.0.1:18789`.
- Compose could not rebind, causing restart loop and false model/auth noise.

### B. Permission layer

- OpenClaw attempted to write under `/root/.openclaw/...`.
- Container runs as non-root user, resulting in `EACCES` on session mkdir.
- Data directory ownership mismatch amplified failure.

### C. Config/Auth layer

- Provider/model mapping changed multiple times during debugging.
- `zai` provider selected without valid API key in active auth path.
- Temporary config corruption occurred once (invalid JSON5 quoting/escaping).

### D. Discord verification layer

- Guild and bot token were valid.
- Initial channel debugging used bot/app id as `CHANNEL_ID`, causing 10003.

## Effective Fixes

1. Kill host stray process (`openclaw-gateway`) and release port 18789.
2. Force-remove stuck container and recreate compose stack.
3. Ensure data ownership: `chown -R 1000:1000 /root/openclaw-box/data`.
4. Keep compose runtime home pinned to `/home/node/.openclaw`.
5. Validate channel access via real text channel id (`type=0`) before bot tests.

## Final Recovery Signal

- `docker compose ps` shows `openclaw_core Up`.
- Logs show `logged in to discord as ...`.
- Discord mention test succeeded:
  - User: `@小龙虾的游泳池 1`
  - Bot: `收到！🦞 有什么需要帮忙的吗？`

## Preventive Controls

- Add single-command recovery script and keep it versioned.
- Maintain fixed compose baseline (HOME/OPENCLAW_HOME/user/localhost bind).
- Add a daily smoke check:
  - Discord mention probe
  - last 3m log grep for `EACCES|Unknown model|No API key|Embedded agent failed`

