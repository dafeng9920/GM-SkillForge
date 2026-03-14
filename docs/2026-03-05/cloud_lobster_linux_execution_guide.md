# Cloud Lobster Linux CLOUD-ROOT 执行指南

## 📋 概述

本文档描述如何在 **Linux CLOUD-ROOT 环境**执行任务并在 **LOCAL-ANTIGRAVITY** 进行双重门禁复验。

**目标**: 2/2 PASS

**环境**:
- **CLOUD-ROOT**: Linux (执行环境)
- **LOCAL-ANTIGRAVITY**: Windows (验证环境)

## 🚀 完整流程

### 阶段 1: LOCAL-ANTIGRAVITY - 生成任务合同

```powershell
# 在 Windows LOCAL-ANTIGRAVITY 运行
python skills/cloud-lobster-closed-loop-skill/scripts/create_cloud_task_contract.py `
  --task-id "cl-linux-20260305-0900" `
  --baseline-id "AG2-FIXED-CALIBER-TG1-20260304" `
  --objective "Linux CLOUD-ROOT 执行演示 - 系统状态检查" `
  --allow "uname -a" `
  --allow "df -h" `
  --allow "free -m" `
  --allow "uptime" `
  --allow "cat /etc/os-release"
```

**输出**:
```
[ok] task_id=cl-linux-20260305-0900
[ok] contract=.tmp/openclaw-dispatch/cl-linux-20260305-0900/task_contract.json
```

### 阶段 2: 传输合同到 CLOUD-ROOT

将任务目录传输到 Linux CLOUD-ROOT 服务器：

```bash
# 方法 1: 使用 scp
scp -r .tmp/openclaw-dispatch/cl-linux-20260305-0900 user@cloud-root:/tmp/

# 方法 2: 使用 rsync
rsync -av .tmp/openclaw-dispatch/cl-linux-20260305-0900 user@cloud-root:/tmp/

# 方法 3: 使用 Git (如果已同步)
# 在 CLOUD-ROOT 服务器拉取最新代码
cd /root/openclaw-box
git pull
```

### 阶段 3: CLOUD-ROOT - 执行任务

**⚠️ 重要**: 此步骤**仅在 Linux CLOUD-ROOT** 环境执行

```bash
# 登录到 Linux CLOUD-ROOT 服务器
ssh user@cloud-root

# 导航到任务目录
cd /tmp/cl-linux-20260305-0900

# 或者在 openclaw-box 目录
cd /root/openclaw-box/.tmp/openclaw-dispatch/cl-linux-20260305-0900

# 下载执行脚本（如果还没有）
wget https://raw.githubusercontent.com/your-repo/GM-SkillForge/main/scripts/cloud_lobster_linux_executor.sh
# 或者从本地复制
# scp scripts/cloud_lobster_linux_executor.sh user@cloud-root:/tmp/

# 赋予执行权限
chmod +x cloud_lobster_linux_executor.sh

# 执行任务
./cloud_lobster_linux_executor.sh cl-linux-20260305-0900
```

**预期输出**:
```
==========================================
Cloud Lobster Linux Executor (CLOUD-ROOT)
==========================================
Task ID: cl-linux-20260305-0900
Started at: 2026-03-05T09:00:00Z
==========================================

[INFO] 检查执行环境...
[OK] 环境检查通过: Linux CLOUD-ROOT

[INFO] 检查任务合同...
[OK] 任务合同验证通过
[INFO] 命令列表 (5 个):
  1. uname -a
  2. df -h
  3. free -m
  4. uptime
  5. cat /etc/os-release

[INFO] 开始执行命令...
[INFO] 执行命令 1/5: uname -a
[OK] 命令执行成功 (退出码: 0)
[INFO] 执行命令 2/5: df -h
[OK] 命令执行成功 (退出码: 0)
...

[INFO] 生成审计事件...
[OK] 审计事件生成完成
[INFO] 生成执行回执...
[OK] 执行回执生成完成
[INFO] 验证四件套完整性...
[OK] ✓ execution_receipt.json
[OK] ✓ stdout.log
[OK] ✓ stderr.log
[OK] ✓ audit_event.json
[OK] 四件套完整性验证通过

==========================================
[OK] 执行完成
==========================================
Task ID: cl-linux-20260305-0900
Exit code: 0
Completed at: 2026-03-05T09:00:10Z

四件套位置:
  - cl-linux-20260305-0900/execution_receipt.json
  - cl-linux-20260305-0900/stdout.log
  - cl-linux-20260305-0900/stderr.log
  - cl-linux-20260305-0900/audit_event.json
```

### 阶段 4: 回传四件套到 LOCAL-ANTIGRAVITY

```bash
# 在 CLOUD-ROOT 服务器上
# 方法 1: 使用 scp
scp -r /tmp/cl-linux-20260305-0900 user@local-antigravity:/d/GM-SkillForge/.tmp/openclaw-dispatch/

# 方法 2: 使用 rsync
rsync -av /tmp/cl-linux-20260305-0900/ user@local-antigravity:/d/GM-SkillForge/.tmp/openclaw-dispatch/cl-linux-20260305-0900/

# 方法 3: 打包后传输
cd /tmp
tar -czf cl-linux-20260305-0900.tar.gz cl-linux-20260305-0900/
scp cl-linux-20260305-0900.tar.gz user@local-antigravity:/d/GM-SkillForge/.tmp/openclaw-dispatch/
# 在本地解压
cd /d/GM-SkillForge/.tmp/openclaw-dispatch
tar -xzf cl-linux-20260305-0900.tar.gz
```

### 阶段 5: LOCAL-ANTIGRAVITY - 双重门禁复验

```powershell
# 在 Windows LOCAL-ANTIGRAVITY 运行

# 下载执行权限（PowerShell）
# 如果脚本没有执行权限，先赋予
# git config core.fileMode false  # Windows 下不需要 file mode

# 运行双重门禁复验
bash scripts/cloud_lobster_dual_gate_verification.sh cl-linux-20260305-0900
```

**预期输出（成功）**:
```
==========================================
Cloud Lobster Dual Gate Verification
(LOCAL-ANTIGRAVITY)
==========================================
Task ID: cl-linux-20260305-0900
Target: 2/2 PASS
Started at: 2026-03-05T09:01:00Z
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

[INFO] 生成结果报告: docs/2026-03-05/dual_gate_report_cl-linux-20260305-0900.json
[OK] 结果报告已生成

完成时间: 2026-03-05T09:01:05Z
```

## 📁 文件清单

### CLOUD-ROOT (Linux)
```
/tmp/cl-linux-20260305-0900/
├── task_contract.json          # 任务合同
├── execution_receipt.json       # 执行回执
├── stdout.log                   # 标准输出
├── stderr.log                   # 标准错误
├── audit_event.json             # 审计事件
└── cloud_lobster_linux_executor.sh  # 执行脚本
```

### LOCAL-ANTIGRAVITY (Windows)
```
.tmp/openclaw-dispatch/cl-linux-20260305-0900/
├── task_contract.json
├── execution_receipt.json
├── stdout.log
├── stderr.log
└── audit_event.json

docs/2026-03-05/
├── dual_gate_report_cl-linux-20260305-0900.json  # 双重门禁报告
├── verification/
│   ├── cl-linux-20260305-0900_review_decision.json
│   └── cl-linux-20260305-0900_final_gate.json
```

## 🛡️ 双重门禁说明

### 门禁 1: verify_execution_receipt.py

**检查项目**:
- ✅ 任务 ID 匹配
- ✅ 命令在 allowlist 内
- ✅ 退出码为 0
- ✅ 四件套完整
- ✅ 回执格式正确

**失败条件**:
- 任务 ID 不匹配
- 命令超出 allowlist
- 退出码非 0
- 四件套缺失

### 门禁 2: cloud_lobster_mandatory_gate.py

**检查项目**:
- ✅ 任务有有效的 task_contract.json
- ✅ 任务有完整的 execution_receipt.json
- ✅ 回执通过 verify_execution_receipt 验证
- ✅ 四件套完整
- ✅ 有 review/final_gate 决策

**失败条件**:
- 无合同或合同无效
- 无回执或回执无效
- 四件套缺失
- 验证失败

## ✅ 验证清单

执行前检查：
- [ ] 在 LOCAL-ANTIGRAVITY 生成了任务合同
- [ ] 合同已传输到 CLOUD-ROOT
- [ ] CLOUD-ROOT 环境是 Linux
- [ ] 执行脚本有执行权限

执行后检查：
- [ ] 四件套已生成
- [ ] 四件套已回传到 LOCAL-ANTIGRAVITY
- [ ] 门禁 1 (verify_execution_receipt): PASS
- [ ] 门禁 2 (cloud_lobster_mandatory_gate): PASS
- [ ] 目标达成: 2/2 PASS

## 🔧 故障排查

### 问题 1: 环境检查失败

```
[ERROR] 当前环境不是 Linux: MINGW64_NT
```

**解决**: 在 Windows 上不要运行 `cloud_lobster_linux_executor.sh`，只在 Linux CLOUD-ROOT 运行。

### 问题 2: 合同不存在

```
[ERROR] 任务合同不存在: cl-linux-20260305-0900/task_contract.json
```

**解决**: 确保合同已传输到 CLOUD-ROOT，并在正确的目录执行。

### 问题 3: 门禁 1 失败

```
[FAIL] 门禁 1/2: FAIL
```

**解决**: 检查回执格式，确保所有必需字段都存在。

### 问题 4: 门禁 2 失败

```
[FAIL] 门禁 2/2: FAIL
```

**解决**: 检查四件套完整性，确保所有文件都已回传。

## 📊 成功标准

```
✓✓✓ 2/2 PASS - 目标达成 ✓✓✓
```

- ✅ 门禁 1: PASS
- ✅ 门禁 2: PASS
- ✅ 无违规记录
- ✅ 四件套完整
- ✅ FAIL-CLOSED 策略生效

---

**执行环境**: Linux CLOUD-ROOT (执行) → Windows LOCAL-ANTIGRAVITY (验证)
**目标**: 2/2 PASS
**策略**: FAIL-CLOSED
