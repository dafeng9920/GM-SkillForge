# 腾讯云 Linux CLOUD-ROOT 部署验收 - 执行指南

## 📋 任务信息

| 项目 | 值 |
|------|-----|
| **任务 ID** | `tencent-deploy-20260305-1000` |
| **基线 ID** | `AG2-FIXED-CALIBER-TG1-20260304` |
| **目标** | 腾讯云 Linux 主机部署验收 |
| **执行环境** | 腾讯云 Linux CLOUD-ROOT |
| **复验环境** | Windows LOCAL-ANTIGRAVITY |

## ✅ 已完成 (LOCAL-ANTIGRAVITY)

```
✓ 任务合同已生成
✓ 执行脚本已创建
✓ 验收标准已定义
```

## 🚀 腾讯云 CLOUD-ROOT 执行步骤

### Step 1: 登录腾讯云 Linux 主机

```bash
ssh root@<tencent-cloud-ip>
# 或
ssh ubuntu@<tencent-cloud-ip>
```

### Step 2: 传输执行脚本和合同

**方法 1: 使用 scp**
```bash
# 在 Windows LOCAL-ANTIGRAVITY 执行
scp scripts/tencent_cloud_deploy_verify.sh root@<tencent-cloud-ip>:/tmp/
scp .tmp/openclaw-dispatch/tencent-deploy-20260305-1000/task_contract.json root@<tencent-cloud-ip>:/tmp/
```

**方法 2: 手动创建（复制粘贴）**
```bash
# 在腾讯云 Linux 主机执行
cd /tmp
cat > tencent_cloud_deploy_verify.sh << 'EOF_SCRIPT'
# ... 复制脚本内容 ...
EOF_SCRIPT
chmod +x tencent_cloud_deploy_verify.sh
```

### Step 3: 执行部署验收

```bash
# 在腾讯云 Linux 主机执行
cd /tmp
chmod +x tencent_cloud_deploy_verify.sh
./tencent_cloud_deploy_verify.sh tencent-deploy-20260305-1000
```

**预期输出**:
```
==========================================
Tencent Cloud Deployment Verification
(CLOUD-ROOT)
==========================================
Task ID: tencent-deploy-20260305-1000
Started at: 2026-03-05T10:00:00Z
==========================================

[STEP] 环境检查
[OK] ✓ 操作系统: Linux
[OK] ✓ Docker: 24.0.7
[OK] ✓ Docker Compose: 2.24.5
[OK] 环境检查通过

[STEP] 初始化任务目录
[OK] ✓ 任务目录: /tmp/tencent-deploy-20260305-1000

[STEP] 开始部署验收

[CHECKPOINT] 检查 1/7: 目录检查
[INFO] 执行: 检查 OpenClaw 目录
[OK] ✓ 检查 OpenClaw 目录
[INFO] 执行: 列出目录内容

[CHECKPOINT] 检查 2/7: Docker 环境检查
...

[CHECKPOINT] 检查 6/7: 6项健康检查
[INFO] 健康检查 1/6: HTTP 端点
[OK] ✓ HTTP 健康检查
[INFO] 健康检查 2/6: 容器日志
...
[INFO] 健康检查 6/6: 系统资源
[OK] ✓ 内存使用
[OK] ✓ 磁盘使用

[STEP] 生成执行回执
[OK] ✓ execution_receipt.json

[STEP] 生成审计事件
[OK] ✓ audit_event.json

[STEP] 验证四件套完整性
[OK] ✓ execution_receipt.json
[OK] ✓ stdout.log
[OK] ✓ stderr.log
[OK] ✓ audit_event.json
[OK] 四件套完整性验证通过

==========================================
📦 回传指令
==========================================

四件套已生成: /tmp/tencent-deploy-20260305-1000

请在 LOCAL-ANTIGRAVITY 执行以下命令：

方法 1: 使用 scp
  scp -r root@tencent-cloud:/tmp/tencent-deploy-20260305-1000 /d/GM-SkillForge/.tmp/openclaw-dispatch/

方法 2: 使用 rsync
  rsync -av root@tencent-cloud:/tmp/tencent-deploy-20260305-1000/ /d/GM-SkillForge/.tmp/openclaw-dispatch/tencent-deploy-20260305-1000/

方法 3: 打包后传输
  # 在 CLOUD-ROOT 打包
  cd /tmp
  tar -czf tencent-deploy-20260305-1000.tar.gz tencent-deploy-20260305-1000/
  # 传输到本地
  scp root@tencent-cloud:/tmp/tencent-deploy-20260305-1000.tar.gz /d/GM-SkillForge/.tmp/openclaw-dispatch/
  # 在本地解压
  cd /d/GM-SkillForge/.tmp/openclaw-dispatch
  tar -xzf tencent-deploy-20260305-1000.tar.gz

回传后运行双重门禁复验：
  bash scripts/cloud_lobster_dual_gate_verification.sh tencent-deploy-20260305-1000

==========================================

==========================================
[OK] ✓✓✓ 部署验收完成 ✓✓✓
==========================================
Task ID: tencent-deploy-20260305-1000
Exit code: 0
Completed at: 2026-03-05T10:05:00Z

四件套位置: /tmp/tencent-deploy-20260305-1000
  - execution_receipt.json
  - stdout.log
  - stderr.log
  - audit_event.json

等待双门禁复验 (Kior-C + Antigravity-1)
==========================================
```

### Step 4: 回传四件套到 LOCAL-ANTIGRAVITY

**在 Windows LOCAL-ANTIGRAVITY 执行**:

```powershell
# 方法 1: scp（推荐）
scp -r root@<tencent-cloud-ip>:/tmp/tencent-deploy-20260305-1000 /d/GM-SkillForge/.tmp/openclaw-dispatch/

# 方法 2: rsync
rsync -av root@<tencent-cloud-ip>:/tmp/tencent-deploy-20260305-1000/ /d/GM-SkillForge/.tmp/openclaw-dispatch/tencent-deploy-20260305-1000/

# 方法 3: 手动打包传输
# 先在腾讯云打包
ssh root@<tencent-cloud-ip> "cd /tmp && tar -czf tencent-deploy-20260305-1000.tar.gz tencent-deploy-20260305-1000/"
# 然后下载
scp root@<tencent-cloud-ip>:/tmp/tencent-deploy-20260305-1000.tar.gz /d/GM-SkillForge/.tmp/openclaw-dispatch/
# 最后解压
cd /d/GM-SkillForge/.tmp/openclaw-dispatch
tar -xzf tencent-deploy-20260305-1000.tar.gz
```

### Step 5: 双重门禁复验 (LOCAL-ANTIGRAVITY)

```powershell
# 在 Windows LOCAL-ANTIGRAVITY 执行
cd /d/GM-SkillForge
bash scripts/cloud_lobster_dual_gate_verification.sh tencent-deploy-20260305-1000
```

**预期结果**:
```
==========================================
Cloud Lobster Dual Gate Verification
(LOCAL-ANTIGRAVITY)
==========================================
Task ID: tencent-deploy-20260305-1000
Target: 2/2 PASS
Started at: 2026-03-05T10:06:00Z
==========================================

[INFO] 检查 LOCAL-ANTIGRAVITY 环境...
[OK] LOCAL-ANTIGRAVITY 环境检查通过

[STEP] 门禁 1/2: 回执校验 (verify_execution_receipt.py)
[INFO] 运行 verify_execution_receipt.py...
[OK] 门禁 1/2: PASS ✓

[STEP] 门禁 2/2: 强制门禁 (cloud_lobster_mandatory_gate.py)
[INFO] 运行 cloud_lobster_mandatory_gate.py...
[OK] 门禁 2/2: PASS ✓

==========================================
双重门禁复验结果
==========================================
✓ 门禁 1/2: PASS
✓ 门禁 2/2: PASS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓✓✓ 2/2 PASS - 目标达成 ✓✓✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
==========================================

[INFO] 生成结果报告: docs/2026-03-05/dual_gate_report_tencent-deploy-20260305-1000.json
[OK] 结果报告已生成

完成时间: 2026-03-05T10:06:05Z
```

## 📋 验收检查清单

### 7项验收检查

| # | 检查项 | 说明 | 验证方法 |
|---|--------|------|---------|
| 1 | 目录检查 | `/root/openclaw-box` 存在 | `test -d` |
| 2 | Docker 环境 | Docker 和 Compose 可用 | `docker version` |
| 3 | Compose 项目 | 项目配置正确 | `docker compose ls` |
| 4 | 容器状态 | 容器运行正常 | `docker compose ps` |
| 5 | 容器启动 | 成功启动容器 | `docker compose up -d` |
| 6 | 健康检查 | 6项健康检查全部通过 | 见下方 |
| 7 | 总结 | 验收总结报告 | 自动生成 |

### 6项健康检查

| # | 检查项 | 验证方法 |
|---|--------|---------|
| 1 | HTTP 端点 | `curl -f http://localhost:18789/health` |
| 2 | 容器日志 | `docker compose logs --tail 20` |
| 3 | 容器资源 | `docker stats --no-stream` |
| 4 | Docker 网络 | `docker network ls` |
| 5 | 容器重启状态 | `docker compose ps` 检查 Restarting |
| 6 | 系统资源 | `free -h`, `df -h` |

## 🛡️ 双门禁复验

### 门禁 1: verify_execution_receipt.py (Kior-C)

**检查项目**:
- ✅ 任务 ID 匹配
- ✅ 命令在 allowlist 内
- ✅ 退出码为 0
- ✅ 四件套完整
- ✅ 回执格式正确

### 门禁 2: cloud_lobster_mandatory_gate.py (Antigravity-1)

**检查项目**:
- ✅ 任务有有效的 task_contract.json
- ✅ 任务有完整的 execution_receipt.json
- ✅ 回执通过 verify_execution_receipt 验证
- ✅ 四件套完整
- ✅ 有 review/final_gate 决策

## 📁 文件清单

### CLOUD-ROOT (腾讯云 Linux)
```
/tmp/tencent-deploy-20260305-1000/
├── task_contract.json          # 任务合同
├── execution_receipt.json       # 执行回执
├── stdout.log                   # 标准输出
├── stderr.log                   # 标准错误
└── audit_event.json             # 审计事件
```

### LOCAL-ANTIGRAVITY (Windows)
```
.tmp/openclaw-dispatch/tencent-deploy-20260305-1000/
├── task_contract.json
├── execution_receipt.json
├── stdout.log
├── stderr.log
└── audit_event.json

docs/2026-03-05/
├── dual_gate_report_tencent-deploy-20260305-1000.json
└── verification/
    ├── tencent-deploy-20260305-1000_review_decision.json
    └── tencent-deploy-20260305-1000_final_gate.json
```

## ⚠️ 重要提醒

- ❌ **不要在 Windows 执行部署验收脚本**
- ✅ **只在腾讯云 Linux CLOUD-ROOT 执行**
- ✅ **四件套必须完整回传**
- ✅ **FAIL-CLOSED 策略：任何检查失败都会 DENY**
- ✅ **回传后等待 Kior-C 和 Antigravity-1 双门禁复验**

## 🔧 故障排查

### 问题 1: SSH 连接失败
```bash
# 检查 SSH 密钥
ssh-add ~/.ssh/id_rsa

# 检查防火墙
ping <tencent-cloud-ip>
telnet <tencent-cloud-ip> 22
```

### 问题 2: Docker 未运行
```bash
# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 检查状态
sudo systemctl status docker
```

### 问题 3: 容器启动失败
```bash
# 查看详细日志
cd /root/openclaw-box
docker compose logs --tail 100

# 检查配置
docker compose config
```

### 问题 4: 健康检查失败
```bash
# 手动测试
curl -v http://localhost:18789/health

# 检查端口
ss -lntp | grep 18789
```

---

**执行环境**: 腾讯云 Linux CLOUD-ROOT (执行) → Windows LOCAL-ANTIGRAVITY (复验)
**复验人员**: Kior-C + Antigravity-1
**目标**: 2/2 PASS
**策略**: FAIL-CLOSED
