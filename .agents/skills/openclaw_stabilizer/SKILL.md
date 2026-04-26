---
name: openclaw_stabilizer
description: 自动稳定与修复 OpenClaw 2026.x 云端/本地全生态连接。处理由于端口错位、安全上下文封锁或设备未授权导致的"黑屏"问题。
---

# OpenClaw 稳定器 (openclaw_stabilizer)

此技能用于检测并修复 OpenClaw 2026.x 集群的连接问题。重点解决跨网络环境（宿主机与云端容器）下的配置不一致。

## 适用场景
- 网页报 `Connection Refused` 或 `Connection Reset`。
- 网页报 `Secure Context Required` (非 HTTPS 访问公网 IP)。
- 网页报 `Pairing Required` 或 `Unauthorized`。
- 容器进入 `Restarting` 无限循环。
- WebSocket 报 1008/1006 错误。

## 已知致命陷阱 (2026-04-03 总结)

### 🔴 陷阱 #1: 端口映射双杀
- `docker-compose.yml` 的 `ports` 必须内外一致: `0.0.0.0:18793:18793`
- 容器内网关端口由 `OPENCLAW_GATEWAY_PORT` 环境变量控制（当前为 18793）
- 如果映射为 `18793:18789`，Docker 转发到 18789 但网关在 18793 监听 → **永久黑屏**
- SSH 隧道已失效（Port 22 被封），必须用 `0.0.0.0` 绑定而非 `127.0.0.1`

### 🔴 陷阱 #2: auth 缺失触发安全自杀
- `entrypoint.sh` 使用 `--bind lan`（绑定 0.0.0.0）
- OpenClaw 2026 安全策略: **非 Loopback + 无认证 = 进程崩溃**
- `openclaw.json` 必须包含 `gateway.auth.mode: "token"` 和有效 token
- **禁止使用** `mode: "none"` 或 `mode: "off"`

### 🔴 陷阱 #3: doctor --fix 会重写配置
- `entrypoint.sh` 在启动前执行 `openclaw doctor --fix`
- 此命令可能将硬编码 Token 替换为 `${ENV_VAR}` 引用
- 产生 `.clobbered.*` 备份文件
- 解法: 使用 `${DISCORD_TOKEN}` 和 `${OPENCLAW_GATEWAY_TOKEN}` 语法 (OpenClaw 原生支持)

### 🟡 陷阱 #4: devices approve --all 不可用
- 2026.x 不支持 `--all` 参数
- 必须 `devices list` 然后 `devices approve <REQUEST_ID>` 逐个审批

## 核心组件

| 组件 | 路径 |
|------|------|
| 集群定义 | `D:\GM-SkillForge\openclaw-box\openclaw_cluster.json` |
| 原修复脚本 (SSH, 已废弃) | `D:\GM-SkillForge\scripts\openclaw_host_repair.ps1` |
| Lighthouse 紧急修复脚本 | `D:\GM-SkillForge\openclaw-box\scripts\lighthouse_emergency_fix.sh` |
| Docker Compose | `D:\GM-SkillForge\openclaw-box\docker-compose.yml` |
| 核心配置 | `D:\GM-SkillForge\openclaw-box\data\openclaw.json` |
| 环境变量 | `D:\GM-SkillForge\openclaw-box\.env` |

## 执行流程

### 场景 A: Lighthouse 终端紧急修复 (SSH 不可用时)
当 SSH 隧道超时且容器处于 Restarting 状态：

```bash
# 在 Lighthouse 网页终端执行
bash /root/openclaw-box/scripts/lighthouse_emergency_fix.sh
```

此脚本会自动：
1. 停止所有容器并备份配置
2. 重写 `.env` 和 `openclaw.json`（包含 `gateway.auth.mode: token`）
3. 修复端口映射为 `0.0.0.0:18793:18793`
4. 全盘搜索消失的 Skills（Docker 卷 + overlay2 残留）
5. 重构并启动容器
6. 引导设备审批

### 场景 B: 宿主机侧修复 (SSH 可用时)
如果 SSH 恢复可用：

```powershell
.\scripts\openclaw_host_repair.ps1 -Mode Cloud
```

### 场景 C: 设备审批
```bash
# 列出待审批设备
docker exec openclaw_core openclaw devices list

# 审批单个设备
docker exec openclaw_core openclaw devices approve <requestId>
```

## 访问 Dashboard

### 无 SSH 隧道 (当前状态)
1. 确保腾讯云防火墙放行 TCP 18793
2. 浏览器访问: `http://43.153.199.229:18793/?token=123456`
3. Chrome Secure Context 修复:
   - `chrome://flags/#unsafely-treat-insecure-origin-as-secure`
   - 添加 `http://43.153.199.229:18793`
   - 设为 Enabled → 重启 Chrome

### 有 SSH 隧道
1. 连通后端口统一为 `http://localhost:18793`
2. 不需要 Chrome Flags 修复

## 配置文件正确结构 (最小可用)

```json
{
  "gateway": {
    "port": 18793,
    "mode": "local",
    "controlUi": {
      "allowedOrigins": ["*"],
      "dangerouslyAllowHostHeaderOriginFallback": true
    },
    "auth": {
      "mode": "token",
      "token": "${OPENCLAW_GATEWAY_TOKEN}"
    }
  },
  "channels": {
    "discord": {
      "enabled": true,
      "token": "${DISCORD_TOKEN}"
    }
  }
}
```

## 注意事项
- **端口对齐**: docker-compose 端口映射必须与 `OPENCLAW_GATEWAY_PORT` 环境变量一致
- **权限边界**: 云端微信插件路径必须为 `755` 权限，禁止 `777`
- **Token 安全**: 紧急恢复用 `123456` 后，应尽快更换为强密码
- **环境隔离**: `.env` 文件中的 Token 是唯一真实来源，`openclaw.json` 中使用 `${...}` 引用
