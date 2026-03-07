# T3-B: Overnight Unattended Runbook

> **版本**: v1.0
> **执行者**: Kior-C
> **审查**: Antigravity-1
> **合规**: Antigravity-2
> **生效日期**: 2026-03-07

---

## 目的

本 runbook 定义了**夜间无人值守执行**的标准操作流程，让非调试人员也能按步骤完成：
1. 夜间运行前准备 (Pre-shutdown)
2. 早晨结果收口 (Morning fetch/verify)
3. 失败分支处理 (Failure branch)

---

## 环境映射

| 环境 | 系统 | 用途 | 入口 |
|------|------|------|------|
| **LOCAL-ANTIGRAVITY** | Windows | 控制台与验证 | `ui/lobster_console_streamlit.py` 或 `scripts/lobsterctl.py` |
| **CLOUD-ROOT** | Linux | 任务执行 | SSH 远程执行 |

---

## 第一阶段: Pre-shutdown Checklist (夜间运行前)

### 目标
确保任务可以安全地在夜间无人值守状态下运行。

### 执行方式
**推荐**: Lobster Console UI (更直观)
**备选**: lobsterctl CLI (可脚本化)

---

### 1.1 环境健康检查

#### UI 方式
```powershell
# 1. 启动控制台
streamlit run ui/lobster_console_streamlit.py

# 2. 检查"环境状态"面板
#    - CLOUD-ROOT: CONNECTED
#    - Python 版本: 3.x
#    - 磁盘空间: > 1GB
```

#### CLI 方式
```powershell
# 检查 Python 环境
python --version
# 期望: Python 3.10+

# 检查磁盘空间
df -h
# 期望: /tmp 或工作目录 > 1GB

# 测试 SSH 连接
ssh <cloud-user>@<cloud-host> "echo OK"
# 期望: OK
```

**EvidenceRef**: `ui/lobster_console_streamlit.py:50-100` (环境状态面板)

---

### 1.2 任务合同准备

#### UI 方式
```powershell
# 在 Lobster Console:
# 1. 选择预设模板 (如: "R1 CLOUD-ROOT 基础回归")
# 2. 点击 "0) 一键准备并提交"
#    - 自动生成 task_contract.json
#    - 自动上传到 CLOUD-ROOT
```

#### CLI 方式
```powershell
# 1. 准备任务合同
python scripts/lobsterctl.py prepare `
  --task-id "overnight-<date>-<sequence>" `
  --baseline-id "AG2-FIXED-CALIBER-TG1-20260304" `
  --objective "夜间无人值守测试" `
  --allow "cd /root/gm-skillforge" `
  --allow "python3 scripts/run_r1_smoke_stable.py" `
  --allow "cat reports/smoke_tests/*.json"

# 2. 提交任务
python scripts/lobsterctl.py submit `
  --task-id "overnight-<date>-<sequence>" `
  --cloud-host "<your-cloud-host>" `
  --cloud-user "<your-cloud-user>" `
  --cloud-repo "/root/gm-skillforge"
```

**EvidenceRef**: `scripts/lobsterctl.py:40-93` (prepare/submit 命令)

---

### 1.3 提交前验证清单

| 检查项 | 命令/按钮 | 预期结果 | 证据路径 |
|--------|----------|----------|----------|
| 合同文件存在 | `ls .tmp/openclaw-dispatch/<task-id>/` | `task_contract.json` 存在 | 文件系统 |
| 命令白名单 | 检查合同 JSON | `command_allowlist` 非空 | 合同文件 |
| 必需制品 | 检查合同 JSON | `required_artifacts` 包含 4 个文件 | 合同文件 |
| 环境标记 | 检查合同 JSON | `environment == "CLOUD-ROOT"` | 合同文件 |

**EvidenceRef**: `docs/2026-03-05/cloud_lobster_quickstart.md:11-21` (合同生成流程)

---

### 1.4 启动夜间任务

#### UI 方式
```powershell
# 在 Lobster Console:
# 1. 点击 "1) Submit" (如果未在步骤 1.2 中提交)
# 2. 观察状态变化: PENDING → RUNNING
# 3. 记录 Task ID 以备早晨查询
```

#### CLI 方式
```powershell
# 提交任务 (如果未在 1.2 中提交)
python scripts/lobsterctl.py submit --task-id "overnight-<date>-<sequence>"

# 确认任务状态
python scripts/lobsterctl.py status --task-id "overnight-<date>-<sequence>"
# 期望: {"task_id": "...", "state": "RUNNING", ...}
```

**EvidenceRef**: `scripts/lobsterctl.py:149-212` (status 命令)

---

### 1.5 关机前确认

| 确认项 | 检查方法 | 通过条件 |
|--------|----------|----------|
| 任务已提交 | `lobsterctl status` | `state == "RUNNING"` 或 `"PENDING"` |
| Task ID 已记录 | 手工记录 | 写在便签/文档中 |
| 早晨流程已准备 | 检查本 runbook 第二阶段 | 熟悉 fetch/verify 步骤 |

**关闭本地机器，任务在 CLOUD-ROOT 继续运行。**

---

## 第二阶段: Morning Fetch/Verify Checklist (早晨收口)

### 目标
安全地获取夜间执行结果并验证完整性。

---

### 2.1 连接与状态查询

#### UI 方式
```powershell
# 1. 启动控制台
streamlit run ui/lobster_console_streamlit.py

# 2. 输入夜间记录的 Task ID
# 3. 点击 "2) Status" 查询状态
```

#### CLI 方式
```powershell
# 查询任务状态
python scripts/lobsterctl.py status --task-id "overnight-<date>-<sequence>"
```

**预期状态**:
- `EXITED` (正常完成)
- `FAILED` (执行失败，进入第三阶段)
- `RUNNING` (仍在运行，等待或检查超时)

**EvidenceRef**: `scripts/lobsterctl.py:149-212` (status 命令返回 JSON)

---

### 2.2 获取执行制品

#### UI 方式
```powershell
# 在 Lobster Console:
# 点击 "4) Fetch"
# - 自动下载四件套到 .tmp/openclaw-dispatch/<task-id>/
```

#### CLI 方式
```powershell
# 获取制品
python scripts/lobsterctl.py fetch --task-id "overnight-<date>-<sequence>"
```

**四件套清单**:
| 文件 | 说明 | 必需 |
|------|------|------|
| `execution_receipt.json` | 执行回执 | ✅ |
| `stdout.log` | 标准输出 | ✅ |
| `stderr.log` | 标准错误 | ✅ |
| `audit_event.json` | 审计事件 | ✅ |

**EvidenceRef**: `scripts/lobsterctl.py:96-112` (fetch 命令)

---

### 2.3 验证完整性

#### UI 方式
```powershell
# 在 Lobster Console:
# 点击 "5) Verify"
# - 自动运行双重门禁
# - 显示验证结果
```

#### CLI 方式
```powershell
# 验证结果
python scripts/lobsterctl.py verify --task-id "overnight-<date>-<sequence>"
```

**双重门禁**:
1. **Gate 1**: `verify_execution_receipt.py`
   - 回执格式检查
   - 命令白名单合规
   - 退出码检查

2. **Gate 2**: `cloud_lobster_mandatory_gate.py`
   - 合同存在性
   - 四件套完整性
   - Gate 1 结果
   - 决策文件存在

**预期输出**:
```
✓ 门禁 1/2: PASS
✓ 门禁 2/2: PASS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓✓✓ 2/2 PASS - 目标达成 ✓✓✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**EvidenceRef**: `scripts/cloud_lobster_mandatory_gate.py:1-100` (强制门禁)

---

### 2.4 归档成功结果

```powershell
# 创建归档目录
mkdir -p "reports/overnight/$(date +%Y%m%d)"

# 复制制品
cp -r ".tmp/openclaw-dispatch/overnight-<date>-<sequence>" \
     "reports/overnight/$(date +%Y%m%d)/"

# 生成验证报告
python scripts/cloud_lobster_mandatory_gate.py \
  --task-id "overnight-<date>-<sequence>" \
  --output "reports/overnight/$(date +%Y%m%d)/gate_decision.json"
```

**EvidenceRef**: `docs/2026-03-05/cloud_lobster_quick_reference.md:39-48` (四件套回传)

---

## 第三阶段: Failure Branch Checklist (失败分支)

### 目标
当任何检查失败时，按步骤诊断和修复。

---

### 3.1 诊断失败类型

| 失败现象 | 可能原因 | 诊断命令 |
|---------|----------|----------|
| `state == "RUNNING"` (超时) | 任务卡死/死循环 | `ssh cloud-host "ps aux \| grep task-id"` |
| `state == "FAILED"` | 执行错误 | 查看 `stderr.log` |
| 四件套缺失 | 传输失败 | 重新运行 `lobsterctl fetch` |
| Gate 1 FAIL | 回指无效 | 查看 `execution_receipt.json` |
| Gate 2 FAIL | 合规问题 | 查看 `docs/compliance_reviews/` |

**EvidenceRef**: `docs/2026-03-05/cloud_lobster_quickstart.md:81-108` (错误处理)

---

### 3.2 常见错误处理

#### 错误 E1: 没有合同
```
[SF_CLOUD_LOBSTER_NO_CONTRACT] No task_contract.json found
```
**解决**:
```powershell
# 检查任务目录
ls .tmp/openclaw-dispatch/<task-id>/

# 如果缺失，重新准备
python scripts/lobsterctl.py prepare --task-id "<task-id>" ...
```

#### 错误 E2: 四件套缺失
```
[SF_CLOUD_LOBSTER_ARTIFACTS_MISSING] Missing: stdout.log, audit_event.json
```
**解决**:
```powershell
# 1. 检查 CLOUD-ROOT 是否有文件
ssh <cloud-host> "ls /tmp/<task-id>/"

# 2. 如果有，重新 fetch
python scripts/lobsterctl.py fetch --task-id "<task-id>"

# 3. 如果没有，任务可能未完成，检查状态
python scripts/lobsterctl.py status --task-id "<task-id>"
```

#### 错误 E3: 验证失败
```
[SF_CLOUD_LOBSTER_VERIFICATION_FAILED] Command not in allowlist
```
**解决**:
```powershell
# 1. 查看执行回执
cat .tmp/openclaw-dispatch/<task-id>/execution_receipt.json

# 2. 检查命令是否在白名单
cat .tmp/openclaw-dispatch/<task-id>/task_contract.json | jq .command_allowlist

# 3. 如果命令合理但未在白名单，修改合同重新执行
```

#### 错误 E4: 绕过尝试
```
[SF_CLOUD_LOBSTER_BYPASS_ATTEMPT] Detected bypass attempt
```
**解决**:
**立即停止**，按照完整流程重新执行。不要尝试跳过任何门禁。

**EvidenceRef**: `scripts/cloud_lobster_mandatory_gate.py:34-42` (错误代码定义)

---

### 3.3 失败归档

即使失败，也要归档证据以供分析：

```powershell
# 创建失败归档
mkdir -p "reports/overnight-failed/$(date +%Y%m%d)"

# 复制所有可用文件
cp -r ".tmp/openclaw-dispatch/overnight-<date>-<sequence>" \
     "reports/overnight-failed/$(date +%Y%m%d)/"

# 记录失败原因
echo "Failure: <reason>" > \
     "reports/overnight-failed/$(date +%Y%m%d)/overnight-<date>-<sequence>/FAILURE_NOTE.md"
```

---

## 快速参考卡片

### UI 操作路径 (推荐新手)
```
1. streamlit run ui/lobster_console_streamlit.py
2. 选择预设模板
3. 点击 "0) 一键准备并提交"
4. [关机，夜间运行]
5. [早晨] 启动控制台，输入 Task ID
6. 点击 "4) Fetch"
7. 点击 "5) Verify"
8. 确认 "2/2 PASS"
```

### CLI 操作路径 (推荐脚本化)
```powershell
# Pre-shutdown
python scripts/lobsterctl.py prepare --task-id ...
python scripts/lobsterctl.py submit --task-id ...
python scripts/lobsterctl.py status --task-id ...  # 确认 RUNNING

# Morning
python scripts/lobsterctl.py status --task-id ...   # 确认 EXITED
python scripts/lobsterctl.py fetch --task-id ...
python scripts/lobsterctl.py verify --task-id ...
```

### 关键路径
| 文件 | 路径 |
|------|------|
| 控制台 UI | `ui/lobster_console_streamlit.py` |
| CLI 工具 | `scripts/lobsterctl.py` |
| 强制门禁 | `scripts/cloud_lobster_mandatory_gate.py` |
| 任务目录 | `.tmp/openclaw-dispatch/<task-id>/` |
| 合规记录 | `docs/compliance_reviews/` |

---

## 验证方式

### 自检命令
```powershell
# 检查 runbook 文件存在
ls docs/2026-03-07/T3-B_overnight_unattended_runbook.md

# 检查 UI 启动
streamlit run ui/lobster_console_streamlit.py --server.headless true

# 检查 CLI 帮助
python scripts/lobsterctl.py --help

# 检查门禁脚本
python scripts/cloud_lobster_mandatory_gate.py --help
```

### 手工验证
| 验证点 | 方法 | 预期 |
|--------|------|------|
| UI 可以启动 | `streamlit run ui/lobster_console_streamlit.py` | 浏览器可访问 |
| prepare 命令有效 | `lobsterctl prepare --task-id test-xxx` | 生成合同文件 |
| status 返回 JSON | `lobsterctl status --task-id test-xxx` | 可解析 JSON |
| verify 运行门禁 | `lobsterctl verify --task-id test-xxx` | 执行双重门禁 |

---

## Remaining Risks

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| R1: SSH 连接超时 | 无法 fetch | 使用 PowerShell 脚本的超时重试逻辑 |
| R2: CLOUD-ROOT 磁盘满 | 执行失败 | Pre-shutdown 检查磁盘空间 |
| R3: 网络中断 | 无法 fetch | Morning 检查网络后重试 |
| R4: 任务卡死 | 状态永远 RUNNING | 设置超时阈值，标记失败 |
| R5: 非调试人员误操作 | 状态混乱 | 使用 UI 预设模板，避免手工编辑合同 |

---

## 版本历史

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v1.0 | 2026-03-07 | 初始版本，基于 T3-A 分析结果 | Kior-C |

---

**EvidenceRef Summary**:
- UI 入口: `ui/lobster_console_streamlit.py:1-661`
- CLI 工具: `scripts/lobsterctl.py:1-260`
- 强制门禁: `scripts/cloud_lobster_mandatory_gate.py:1-582`
- 快速参考: `docs/2026-03-05/cloud_lobster_quick_reference.md`
- 错误处理: `docs/2026-03-05/cloud_lobster_quickstart.md:81-108`
