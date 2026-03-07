---
name: openclaw-runtime-recovery-skill
description: OpenClaw 运行态故障恢复技能。用于处理 Discord 在线但不回复、模型不识别、权限拒绝、端口占用、容器僵死重启等高频故障。
---

# openclaw-runtime-recovery-skill

## 适用场景

- Discord 可见 bot 在线，但 `@bot` 不回复
- 日志出现 `Unknown model`
- 日志出现 `No API key found for provider "zai"`
- 日志出现 `EACCES: permission denied, mkdir '/root/.openclaw/...`
- 日志出现 `address already in use`（通常是 `127.0.0.1:18789`）
- 容器频繁 `Restarting (137)` 或 `did not receive an exit event`

## 输入

```yaml
input:
  project_dir: "/root/openclaw-box"
  compose_service: "openclaw-agent"
  data_dir: "/root/openclaw-box/data"
  bot_token_env: "DISCORD_TOKEN"
  guild_id: "1475477499814215782"
  text_channel_id: "1475477500506411162"
```

## 输出

```yaml
output:
  status: "RECOVERED|PARTIAL|FAILED"
  root_cause:
    - "PORT_CONFLICT_18789"
    - "HOST_STRAY_GATEWAY_PROCESS"
    - "HOME_PATH_PERMISSION_MISMATCH"
    - "MODEL_PROVIDER_MISMATCH"
  actions_applied:
    - "kill stray openclaw-gateway"
    - "chown data to 1000:1000"
    - "compose down/up rebuild"
  acceptance:
    - "discord logged in"
    - "mention reply works"
    - "no EACCES/Unknown model/No API key in last 3m logs"
```

## 标准流程

### 1) 快速定位

```bash
cd /root/openclaw-box
docker compose ps
docker compose logs --since 10m openclaw-agent | tail -n 300
ss -lntp | grep 18789 || true
```

### 2) API 与频道可达性核验

```bash
source /root/openclaw-box/.env
curl -sS -H "Authorization: Bot $DISCORD_TOKEN" https://discord.com/api/v10/users/@me/guilds
curl -sS -H "Authorization: Bot $DISCORD_TOKEN" "https://discord.com/api/v10/channels/1475477500506411162/messages?limit=5"
```

判定规则:
- 返回 `Unknown Channel (10003)`：用了错误 `CHANNEL_ID`（常见把 bot id 当 channel id）
- 返回消息数组：Discord 权限和频道可达性正常

### 2.5) 记忆库清理 (Token 防爆盾补充)

若日志持续出现 `model_context_window_exceeded`，执行以下脚本清理历史上下文：

```bash
cd /root/openclaw-box
# 执行一键清理（含自动备份）
bash scripts/clear_openclaw_memory.sh
```

### 3) 强制恢复 (端口冲突 + 僵尸容器)

按顺序执行:

```bash
cd /root/openclaw-box
pkill -f openclaw-gateway || true
ss -lntp | grep 18789 || true
docker rm -f openclaw_core || true
docker compose down --remove-orphans || true
chown -R 1000:1000 /root/openclaw-box/data
docker compose up -d --build
docker compose ps
```

若仍卡在 `did not receive an exit event`:

```bash
systemctl restart docker
cd /root/openclaw-box
docker compose up -d --build
```

### 4) 模型与鉴权核验

```bash
docker compose logs --since 5m openclaw-agent | grep -E "Unknown model|No API key|EACCES|logged in|lane task error|Embedded agent failed"
```

判定规则:
- 出现 `Unknown model`：模型名或 provider 映射错误
- 出现 `No API key found for provider "zai"`：缺少 `ZAI_API_KEY` 或 auth profile 未注入
- 出现 `EACCES ... /root/.openclaw`：HOME/OPENCLAW_HOME 路径或 data 目录属主错误

### 5) 验收闭环

- 在 Discord 频道发送 `@小龙虾的游泳池 1`
- 必须收到 bot 回复
- 最近 3 分钟日志无以下关键字:
  - `EACCES`
  - `Unknown model`
  - `No API key`
  - `Embedded agent failed`

## Compose 基线要求

`docker-compose.yml` 必须满足:

- `user: "1000:1000"`
- `HOME=/home/node`
- `OPENCLAW_HOME=/home/node/.openclaw`
- 端口仅绑定 `127.0.0.1:18789:18789`
- data 映射到 `/home/node/.openclaw`

## 交付物

- 事故时间线与根因: `references/incidents_2026-03-01.md`
- 一键急救脚本: `scripts/recover_openclaw.sh`
- 记忆清理脚本: `scripts/clear_openclaw_memory.sh`

## 扩展维护
若发现服务器整体磁盘占用率过高，请查阅并执行 [server-maintenance-slimming-skill](file:///d:/GM-SkillForge/skills/server-maintenance-slimming-skill/SKILL.md) 进行系统级瘦身。

