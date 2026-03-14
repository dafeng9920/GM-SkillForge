# Cloud Lobster 快速参考卡片

## 🎯 目标
**2/2 PASS** - 双重门禁复验全部通过

## 🖥️ 环境划分

| 环境 | 系统 | 用途 |
|------|------|------|
| **CLOUD-ROOT** | Linux | 执行任务 |
| **LOCAL-ANTIGRAVITY** | Windows | 验证结果 |

## 📋 快速流程

### Step 1: 生成合同 (LOCAL-ANTIGRAVITY)
```powershell
python skills/cloud-lobster-closed-loop-skill/scripts/create_cloud_task_contract.py `
  --task-id "cl-linux-20260305-0900" `
  --baseline-id "AG2-FIXED-CALIBER-TG1-20260304" `
  --objective "Linux 系统检查" `
  --allow "uname -a" `
  --allow "df -h" `
  --allow "free -m"
```

### Step 2: 传输到 CLOUD-ROOT
```bash
scp -r .tmp/openclaw-dispatch/cl-linux-20260305-0900 user@cloud-root:/tmp/
```

### Step 3: 执行任务 (CLOUD-ROOT - 仅 Linux!)
```bash
ssh user@cloud-root
cd /tmp/cl-linux-20260305-0900
chmod +x cloud_lobster_linux_executor.sh
./cloud_lobster_linux_executor.sh cl-linux-20260305-0900
```

### Step 4: 回传四件套
```bash
# 在 CLOUD-ROOT
scp -r /tmp/cl-linux-20260305-0900 user@local-antigravity:/d/GM-SkillForge/.tmp/openclaw-dispatch/
```

### Step 5: 双重门禁 (LOCAL-ANTIGRAVITY)
```powershell
bash scripts/cloud_lobster_dual_gate_verification.sh cl-linux-20260305-0900
```

## ✅ 预期结果

```
✓ 门禁 1/2: PASS
✓ 门禁 2/2: PASS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓✓✓ 2/2 PASS - 目标达成 ✓✓✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 📁 四件套清单

| 文件 | 说明 |
|------|------|
| `execution_receipt.json` | 执行回执 |
| `stdout.log` | 标准输出 |
| `stderr.log` | 标准错误 |
| `audit_event.json` | 审计事件 |

## 🛡️ 双重门禁

### 门禁 1: verify_execution_receipt.py
- 检查回执格式
- 验证命令在 allowlist
- 检查退出码

### 门禁 2: cloud_lobster_mandatory_gate.py
- 检查合同存在
- 验证四件套完整
- 运行门禁 1
- 检查决策存在

## ⚠️ 重要提醒

- ❌ **不要在 Windows 运行 `cloud_lobster_linux_executor.sh`**
- ✅ **只在 Linux CLOUD-ROOT 执行任务**
- ✅ **四件套必须完整回传**
- ✅ **FAIL-CLOSED 策略：任何检查失败都会 DENY**

## 🔧 故障排查

| 问题 | 解决方案 |
|------|---------|
| 环境检查失败 | 在 Linux CLOUD-ROOT 运行 |
| 合同不存在 | 传输合同到 CLOUD-ROOT |
| 门禁 1 失败 | 检查回执格式 |
| 门禁 2 失败 | 检查四件套完整性 |

## 📚 相关文档

- [完整执行指南](./cloud_lobster_linux_execution_guide.md)
- [快速开始](./cloud_lobster_quickstart.md)
- [架构文档](./mandatory_enforcement_architecture.md)

---

**目标**: 2/2 PASS
**策略**: FAIL-CLOSED
**环境**: Linux CLOUD-ROOT → Windows LOCAL-ANTIGRAVITY
