# OpenClaw Phase A (48h) 最小补丁清单（6项）

目标：仅做配置层加固，不改业务逻辑，把当前风险面从“可运行但高暴露”降到“可控运行”。

## 1. Compose 强制 env + 缺失即失败（Fail-Closed）

文件：`openclaw-box/docker-compose.yml`

```diff
@@
   openclaw-agent:
+    env_file:
+      - .env
@@
-    environment:
-      - OPENAI_API_KEY=${OPENAI_API_KEY}
-      - OPENAI_API_BASE=${OPENAI_API_BASE}
-      - DISCORD_TOKEN=${DISCORD_TOKEN}
+    environment:
+      OPENAI_API_KEY: ${OPENAI_API_KEY:?OPENAI_API_KEY is required}
+      OPENAI_API_BASE: ${OPENAI_API_BASE:?OPENAI_API_BASE is required}
+      DISCORD_TOKEN: ${DISCORD_TOKEN:?DISCORD_TOKEN is required}
+      OPENCLAW_GATEWAY_TOKEN: ${OPENCLAW_GATEWAY_TOKEN:?OPENCLAW_GATEWAY_TOKEN is required}
```

## 2. 容器最小权限补齐

文件：`openclaw-box/docker-compose.yml`

```diff
@@
     security_opt:
       - no-new-privileges:true
+    cap_drop:
+      - ALL
+    read_only: true
+    tmpfs:
+      - /tmp:rw,noexec,nosuid,size=128m
+    pids_limit: 256
```

## 3. 去运行时安装链路（避免回退 root）

文件：`openclaw-box/docker-compose.yml`、`openclaw-box/Dockerfile`

```diff
@@
-    image: node:22-bookworm-slim
+    build:
+      context: .
+      dockerfile: Dockerfile
+      args:
+        OPENCLAW_VERSION: "0.70.0"
+    image: openclaw-agent:secure-2026.02
@@
-    command: >
-      sh -c "
-      if [ ! -f /usr/local/bin/openclaw ]; then
-        apt-get update && apt-get install -y git python3 build-essential cmake &&
-        npm install -g openclaw@latest
-      fi &&
-      openclaw gateway run --port 18789 --bind local
-      "
+    command: >
+      sh -c "openclaw gateway run --port 18789 --bind local"
```

`openclaw-box/Dockerfile` 示例：

```dockerfile
FROM node:22-bookworm-slim
ARG OPENCLAW_VERSION=0.70.0
RUN npm install -g openclaw@${OPENCLAW_VERSION}
USER node
WORKDIR /home/node
```

## 4. openclaw.json 去明文 token

文件：`openclaw-box/data/openclaw.json`

```diff
@@
-      "token": "xxxx-discord-token",
+      "token": "${DISCORD_TOKEN}",
@@
-      "token": "xxxx-gateway-token"
+      "token": "${OPENCLAW_GATEWAY_TOKEN}"
```

## 5. openclaw.json 开启受限沙箱

文件：`openclaw-box/data/openclaw.json`

```diff
@@
-      "sandbox": {
-        "mode": "off"
-      }
+      "sandbox": {
+        "mode": "workspace-write"
+      }
```

## 6. sessions.json 最小化持久化

文件：`openclaw-box/data/agents/main/sessions/sessions.json`

策略：仅保留低敏元数据；删除 `systemPromptReport/tools/schema/workspaceDir/sessionFile` 等高价值上下文。

```diff
@@
-    "sessionFile": "...",
-    "systemPromptReport": { ... },
-    "skillsSnapshot": { ... },
+    "channel": "discord",
+    "sessionId": "034a184b-2ada-434f-92fb-3665014cc546",
+    "updatedAt": 1772187910337,
+    "lastAccountId": "default"
```

---

## 执行命令块（按顺序）

> 说明：以下命令默认在仓库根目录 `d:/GM-SkillForge` 执行。

### A. 先备份关键文件

```powershell
New-Item -ItemType Directory -Force -Path .tmp/openclaw_phaseA_backup | Out-Null
Copy-Item openclaw-box/docker-compose.yml .tmp/openclaw_phaseA_backup/docker-compose.yml.bak -Force
Copy-Item openclaw-box/data/openclaw.json .tmp/openclaw_phaseA_backup/openclaw.json.bak -Force
Copy-Item openclaw-box/data/agents/main/sessions/sessions.json .tmp/openclaw_phaseA_backup/sessions.json.bak -Force
```

### B. 准备 `.env`（如不存在）

```powershell
@'
OPENAI_API_KEY=replace_me
OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4/
DISCORD_TOKEN=replace_me
OPENCLAW_GATEWAY_TOKEN=replace_me
'@ | Set-Content openclaw-box/.env.example -Encoding UTF8
```

### C. 应用补丁（手工或按本文件 diff 修改）

```powershell
# 建议在 IDE 中按本文件 diff 逐项修改：
# 1) openclaw-box/docker-compose.yml
# 2) openclaw-box/data/openclaw.json
# 3) openclaw-box/data/agents/main/sessions/sessions.json
# 4) 新增 openclaw-box/Dockerfile
```

### D. 静态核验（必须全通过）

```powershell
# 1) 检查 openclaw.json 不再有明文 token（若使用 env 占位字符串则允许出现 ${...}）
Select-String -Path openclaw-box/data/openclaw.json -Pattern '"token"\s*:\s*"(?!\$\{)[^"]+"' -AllMatches

# 2) 检查 sandbox 不为 off
Select-String -Path openclaw-box/data/openclaw.json -Pattern '"mode"\s*:\s*"off"'

# 3) 检查 compose 已启用最小权限项
Select-String -Path openclaw-box/docker-compose.yml -Pattern 'cap_drop|read_only|tmpfs|pids_limit|no-new-privileges|env_file'

# 4) 检查 compose 不再运行时 apt-get/npm install
Select-String -Path openclaw-box/docker-compose.yml -Pattern 'apt-get|npm install -g'

# 5) 检查 sessions.json 不再包含高价值字段
Select-String -Path openclaw-box/data/agents/main/sessions/sessions.json -Pattern 'systemPromptReport|schemaChars|workspaceDir|sessionFile|skillsSnapshot'
```

### E. 启动前检查（Fail-Closed）

```powershell
Copy-Item openclaw-box/.env.example openclaw-box/.env -Force
# 将 openclaw-box/.env 中 replace_me 替换为真实值后再继续
```

### F. 构建与启动（在 openclaw-box 目录）

```powershell
cd openclaw-box
docker compose build --no-cache openclaw-agent
docker compose up -d
docker compose ps
```

### G. 运行态核验

```powershell
docker inspect openclaw_core --format '{{json .HostConfig.CapDrop}}'
docker inspect openclaw_core --format '{{.HostConfig.ReadonlyRootfs}}'
docker inspect openclaw_core --format '{{json .HostConfig.SecurityOpt}}'
```

---

## 回滚命令块

```powershell
Copy-Item .tmp/openclaw_phaseA_backup/docker-compose.yml.bak openclaw-box/docker-compose.yml -Force
Copy-Item .tmp/openclaw_phaseA_backup/openclaw.json.bak openclaw-box/data/openclaw.json -Force
Copy-Item .tmp/openclaw_phaseA_backup/sessions.json.bak openclaw-box/data/agents/main/sessions/sessions.json -Force
```
