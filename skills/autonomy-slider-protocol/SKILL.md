---
name: autonomy-slider-protocol
description: OpenClaw 的“自主性滑块”协议。根据 Commander 的信任级别，动态调整 Agent 的审批颗粒度和决策权限。
---

# autonomy-slider-protocol

## 信任级别 (Trust Levels)

### 1. 🟢 LEVEL 1: SUPERVISED (受控模式)
- **定义**: “你是我的超级助手”。
- **规则**: 
  - 每一个工具调用（Tool Call）必须通过 `Approval Gate`。
  - 每一个 Shell 指令必须由 Commander 手动确认（Ok/No）。
  - 适合：高额金盘交易、敏感系统配置修改。

### 2. 🟡 LEVEL 2: SEMI-AUTO (战术授权)
- **定义**: “在我的任务边界内，你可以自由发挥”。
- **规则**: 
  - 任务开始时授权：Commander 对整个任务目标（Task Objective）点击“Approve”。
  - 任务执行中：自动执行符合目标的子任务（Sub-tasks），无需每步提问。
  - 触发报警：遇到安全红线（Aegis Audit 拦截）或超出预算时，必须暂停并请求。
  - 适合：深度行情搜集、策略回测、常规文件处理。

### 3. 🔴 LEVEL 3: FULL-AUTO (统帅代理)
- **定义**: “你是我的数字代理。结果说话，过程自理”。
- **规则**: 
  - 全权委托：Agent 自主拆解目标、调度军团、执行闭环。
  - 报告模式：仅在“上帝视角 (God View)”同步进度快照，不干扰 Commander。
  - 熔断机制：仅在系统级错误或灾难性偏离时紧急制动（Kill Switch）。
  - 适合：长效情报监控、24/7 策略挖矿。

## 切换指令 (Switching)

- `!set autonomy level 1` - 切回手动挡。
- `!set autonomy level 3` - 开启代理驾驶。

---

## 结合 `aegis-audit-skill`

- 无论级别，`aegis-audit` 始终作为硬件级防火墙开启。
- Level 3 并不意味着可以绕过安全审计，而是将审计结果的“通过”动作自动化。
