# CLOUD-ROOT 复验与最终签发指南

## 执行状态

**当前状态**: PENDING 实机证据收集
**环境**: LOCAL-ANTIGRAVITY (规划) → CLOUD-ROOT (实机抽查) → LOCAL-ANTIGRAVITY (最终签发)

---

## 已完成工作

### 1. D3 SHA256 不一致修复 ✅

三处文件已同步:
- `reports/l5-replay/baseline_2026-03-05.json`
- `docs/2026-03-05/verification/L5_day1_gate_decision.json`
- `docs/2026-03-05/D3_FIX_COMPLETION_REPORT.md`

**最终 SHA256**: `257197eec3c1e57bb33576713ae7490a08f98bc4907b9cb4819c3b0ab549f894`

### 2. 云迁移证据文件补齐 ✅

| 文件 | 状态 |
|---|---|
| `cloud_root_migration_stdout.log` | ✅ |
| `cloud_root_migration_stderr.log` | ✅ |
| `cloud_root_migration_audit.json` | ✅ |
| `cloud_root_service_status.md` | ✅ |

### 3. 收集脚本创建 ✅

- `openclaw-box/scripts/collect_cloud_root_live_status.sh` - Linux 脚本
- `openclaw-box/scripts/collect_cloud_root_evidence.bat` - Windows 包装脚本

---

## 待执行工作

### P0: CLOUD-ROOT 实机证据收集

**执行位置**: CLOUD-ROOT (必须在实际服务器上执行)

#### 方法 1: 直接 SSH 执行

```bash
# SSH 连接到 CLOUD-ROOT
ssh cloud-root@CLOUD-HOST

# 执行收集脚本
bash openclaw-box/scripts/collect_cloud_root_live_status.sh
# 或
bash /opt/gm-skillforge/scripts/collect_cloud_root_live_status.sh
```

#### 方法 2: 从 LOCAL-ANTIGRAVITY 远程执行

```bash
# 从 Windows 执行
cd d:\GM-SkillForge
openclaw-box\scripts\collect_cloud_root_evidence.bat
```

#### 必需命令输出

```bash
# 1. 服务活性状态
systemctl is-active cloud-root-*
# 预期: 4×active, 1×inactive (mandatory_gate 为 oneshot)

# 2. 服务自启动状态
systemctl is-enabled cloud-root-*
# 预期: 5×enabled

# 3. 健康检查
curl -s http://localhost:8081/health
# 预期: 200 OK, {"status":"healthy"}

curl -s http://localhost:8082/health
# 预期: 200 OK, {"status":"healthy"}
```

---

### P1: 最终 Gate 决策签发

**执行位置**: LOCAL-ANTIGRAVITY (收到实机证据后)

#### 判定标准

| 标准 | 要求 | 结果 | 备注 |
|---|---|---|---|
| Services Active | ≥ 4/5 | 待实机 | mandatory_gate 为 oneshot，可能 inactive |
| Services Enabled | 5/5 | 待实机 | 所有服务必须自启动 |
| Health Endpoints | 2/2 | 待实机 | contract-generator (8081), dispatch-queue (8082) |
| Fail-Closed Enforced | Yes | 已验证 | Restart=on-failure 配置已确认 |

#### 期望输出格式

**txt 格式** (`cloud_root_live_status_<timestamp>.txt`):
```markdown
# CLOUD-ROOT Live Status Evidence
# Generated: <UTC timestamp>
# Host: <hostname>

## 1. Service Active Status
active
active
inactive
active
active

## 2. Service Enabled Status
enabled
enabled
enabled
enabled
enabled

## 9. Status Summary
| Service | is-active | is-enabled | Health Check |
|--------|-----------|------------|--------------|
| contract-generator | active | enabled | 200 OK |
| dispatch-queue | active | enabled | 200 OK |
| mandatory-gate | inactive | enabled | N/A |
| receipt-verifier | active | enabled | N/A |
| audit-archive | active | enabled | N/A |

## 12. Gate Decision Recommendation
**Recommendation**: ALLOW
All critical services are active, enabled, and healthy.
```

**json 格式** (`cloud_root_live_status_<timestamp>.json`):
```json
{
  "collection_type": "cloud_root_live_status",
  "timestamp": "<UTC timestamp>",
  "hostname": "<hostname>",
  "evidence_file": "cloud_root_live_status_<timestamp>.txt",
  "services": [...],
  "summary": {
    "total_services": 5,
    "active_services": 4,
    "enabled_services": 5,
    "healthy_endpoints": 2,
    "decision": "ALLOW"
  },
  "fail_closed_audit": {...}
}
```

#### Gate 决策文件

- 若全 PASS → 创建 `CLOUD_ROOT_OPERATION_FINAL_ALLOW.json`
- 若有 FAIL → 创建 `CLOUD_ROOT_OPERATION_REQUIRES_CHANGES.json`

---

## 文件清单

### 配置文件 (仓库中)

| 文件 | 类型 | 状态 |
|---|---|---|
| `openclaw-box/systemd/*.service` | Systemd 服务配置 | ✅ 已创建 |
| `openclaw-box/monitoring/cloud-root-monitoring.yml` | 监控配置 | ✅ 已创建 |
| `openclaw-box/monitoring/cloud_root_monitor.py` | 监控守护进程 | ✅ 已创建 |
| `openclaw-box/deploy/deploy_to_cloud_root.sh` | 部署脚本 | ✅ 已创建 |
| `openclaw-box/tests/verify_closed_loop.py` | 闭测测试脚本 | ✅ 已创建 |

### 证据文件 (模板)

| 文件 | 类型 | 状态 |
|---|---|---|
| `docs/2026-03-05/verification/cloud_root_migration_stdout.log` | 部署输出模板 | ✅ |
| `docs/2026-03-05/verification/cloud_root_migration_stderr.log` | 错误输出模板 | ✅ |
| `docs/2026-03-05/verification/cloud_root_migration_audit.json` | 审计事件模板 | ✅ |
| `docs/2026-03-05/verification/cloud_root_service_status.md` | 服务状态模板 | ✅ |

### 待生成证据 (CLOUD-ROOT 实机)

| 文件 | 类型 | 状态 |
|---|---|---|
| `docs/2026-03-05/verification/cloud_root_live_status_<timestamp>.txt` | Markdown 实机证据 | ⏳ 待收集 |
| `docs/2026-03-05/verification/cloud_root_live_status_<timestamp>.json` | JSON 实机证据 | ⏳ 待收集 |

### Gate 决策文件

| 文件 | 类型 | 状态 |
|---|---|---|
| `CLOUD_ROOT_OPERATION_PENDING.json` | 当前状态 | ✅ |
| `CLOUD_ROOT_OPERATION_FINAL_ALLOW.json` | 最终决定 (模板) | ⏳ 待签发 |
| `CLOUD_ROOT_MIGRATION_GATE_DECISION.json` | 配置部署决定 | ✅ |

---

## 执行步骤

### Step 1: 在 CLOUD-ROOT 上收集证据

```bash
# 方法 A: 直接 SSH
ssh cloud-root@CLOUD-HOST
bash /opt/gm-skillforge/scripts/collect_cloud_root_live_status.sh

# 方法 B: 远程执行
cd d:\GM-SkillForge
openclaw-box\scripts\collect_cloud_root_evidence.bat
```

### Step 2: 验证证据完整性

检查 `docs/2026-03-05/verification/` 目录下是否包含:
- `cloud_root_live_status_<timestamp>.txt`
- `cloud_root_live_status_<timestamp>.json`

**验证清单**:
- [ ] txt 文件包含完整的服务状态输出
- [ ] json 文件包含完整的结构化数据
- [ ] Services Active ≥ 4/5
- [ ] Services Enabled = 5/5
- [ ] Health Endpoints = 2/2
- [ ] 决策建议为 ALLOW

### Step 3: 根据 Gate 判定签发最终决定

**允许条件 (ALLOW)**:
- Services Active: ≥ 4/5
- Services Enabled: 5/5
- Health Endpoints: 2/2

**需要修改 (REQUIRES_CHANGES)**:
- 任一条件不满足

---

## 快速命令参考

```bash
# CLOUD-ROOT 上执行
bash /opt/gm-skillforge/scripts/collect_cloud_root_live_status.sh

# 验证证据文件
ls docs/2026-03-05/verification/cloud_root_live_status_*

# 更新最终 Gate 决策 (手动或脚本)
# 编辑 CLOUD_ROOT_OPERATION_PENDING.json
# 创建 CLOUD_ROOT_OPERATION_FINAL_ALLOW.json 或 CLOUD_ROOT_OPERATION_REQUIRES_CHANGES.json
```

---

*更新时间: 2026-03-05T10:15:00Z*
*环境: LOCAL-ANTIGRAVITY*
*状态: PENDING_CLOUD_ROOT_EVIDENCE*
