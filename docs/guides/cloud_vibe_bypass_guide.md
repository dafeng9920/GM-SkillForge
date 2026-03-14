---
name: CLOUD_VIBE_BYPASS
description: 绕过企业级 VPN（如 Cisco AnyConnect）全隧道限制，建立云开发环境的“影子连接”协议。
---

# CLOUD_VIBE_BYPASS (云端氛围穿透协议)

本协议旨在解决开发者在受限网络环境（如 Cisco AnyConnect 全隧道锁定）下，无法通过常规 SSH/TCP 连接远程服务器的问题。通过利用 VS Code Remote Tunnels 的 HTTPS 转发机制，实现“降维打击”。

## 🚨 触发条件 (Pre-flight Check)
- **目标**：连接远程云服务器（如腾讯云、AWS）。
- **阻碍**：本地开启了企业级 VPN，且处于 `Full Tunnel` 模式（劫持了 `0.0.0.0/0`）。
- **表现**：`ping` 可能通（UDP/ICMP），但 `ssh` 永远超时或被拦截（TCP 转发失败）。

## 🛠️ 核心步骤 (Protocol Steps)

### 第一阶段：云端守门人 (Server-side Setup)
1. **安装 VS Code CLI**：
   ```bash
   curl -Lk 'https://code.visualstudio.com/sha/download?build=stable&os=linux-x64' | tar -xz
   chmod +x ./code
   ```
2. **启动 HTTPS 隧道**：
   ```bash
   ./code tunnel
   ```
3. **完成 GitHub 授权**：
   - 访问 [github.com/login/device](https://github.com/login/device)
   - 输入命令行显示的 8 位验证码。

### 第二阶段：本地破壁人 (Local-side Setup)
1. **安装插件**：在 VS Code 中安装 `Remote - Tunnels` 扩展。
2. **身份同步**：在本地 VS Code 中登录同一个 GitHub 账号。
3. **瞬间移动**：
   - 按 `Ctrl + Shift + P` -> `Remote Tunnels: Connect to Tunnel`。
   - 选择云端展示的机器名（如 `vm-0-5-opencloudos`）。

### 第三阶段：多重闪现 (Advanced Bypass)
如果在隧道建立过程中遇到 DNS 或底层路由干扰，可配合 **Tailscale Mesh** 使用：
- 远程开启：`tailscale up --ssh`
- 本地配合：`ProxyCommand "C:\Program Files\Tailscale\tailscale.exe" nc %h %p` (仅在 Tunnels 失败时作为备选)。

## 💡 方案优势
- **无视路由表**：隧道流量伪装成标准 HTTPS (443)，VPN 驱动无法识别其为开发流量。
- **免公网 IP**：不需要在腾讯云开放 22 端口，安全性更高。
- **持久化**：只要服务器端进程不关，本地可随时一秒连入。

## 🧛 持久化守门人 (Persistence Strategy)
为了防止腾讯云网页黑窗口关闭导致隧道断开，必须在服务器端建立守护进程：
```bash
# 在云端执行此连招
cd /root/VSCode-linux-x64/bin
nohup ./code tunnel > tunnel.log 2>&1 &
```
*执行后即可放心关闭网页终端，隧道将永久挂载。*

## 🕹️ 日常作战流 (Daily Dual-Window Workflow)

### 窗口 A：本地指挥部 (Local Context)
- **打开方式**：直接启动 VS Code。
- **职责**：代码编写、Git 提交、本地文档。
- **路径**：`D:\GM-SkillForge`

### 窗口 B：云端火力中心 (Cloud Context)
- **打开方式**：
  1. 点击 VS Code 左下角【双箭头】图标。
  2. 选择 `Connect to Tunnel...`。
  3. 选中 `vm-0-5-opencloudos`。
- **职责**：高性能扫描 (AIO Scanner)、Docker 挂机、新加坡出口代理、24/7 任务执行。

---
*Generated for the "Blue Lobster" mission to ensure Vibe Coding never dies.* 🦞🔵☁️🛡️⚔️
