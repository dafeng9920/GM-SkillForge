---
name: GOVERNANCE_PROTOCOL
description: "强制性 AI 治理协议。用于在执行高风险、系统级或破坏性操作（如 Shell, File, DB, Network）时实施 Fail-Closed 治理、人工介入和审计追踪。"
---

# GOVERNANCE_PROTOCOL

本技能定义了 SkillForge 体系下的 **“安全缰绳 (Safety Bridle)”** 协议。任何具备高能力的智能体在接触底层系统资源时，必须激活此技能以确保操作的可审计性和可拒斥性。

## 1. 核心准则 (Core Principles)

- **Fail-Closed (故障闭锁)**: 如果治理系统不可用或权限未校验，严禁执行操作。
- **Contract-First (契约先行)**: 每一项高风险操作必须输出“执行合规合同”。
- **Human-in-the-Loop (人工介入)**: 破坏性操作必须获得具备权限的人类队友许可。

## 2. 强制执行流程 (Mandatory Workflow)

当检测到高风险意图（如删除文件、修改核心配置、执行未过滤 Shell）时，Agent **必须** 按顺序执行：

### Step A: Preflight Checklist (预检清单)
在提交流转前，必须在对话中输出：
1. [ ] **IsolationCheck**: 运行环境是否处于沙箱 (Sandbox)？
2. [ ] **ScopeCheck**: 目标路径是否在允许的工作区范围内？
3. [ ] **ImpactCheck**: 该操作是否会导致不可逆的数据丢失？

### Step B: Execution Contract (执行合同)
使用三段式结构公开你的执行意图：
- **Intent**: 描述你要做什么（例如：`DELETE /root/.openclaw/test.txt`）。
- **Risk**: 评估潜在风险。
- **Mitigation**: 说明防御措施（例如：`INTERCEPTED_BY_G9_PERMIT_GATE`）。

### Step C: Audit Pack Generation (审计生成)
执行完毕（或被拦截）后，必须确保在 `AuditPack/evidence/` 目录下生成对应的证据文件。

## 3. 治理门控 (Gate Mapping)

- **G2 (Scan Gate)**: 扫描指令是否存在针对治理层的绕过或注入攻击。
- **G9 (Permit Gate)**: 核心拦截点。对 `FILE_DELETE` 和 `SHELL_EXECUTION` 等 Action 进行鉴权。

## 4. 最佳实践 (Best Practices)

- **Do Not Guess**: 如果治理 API 返回 403，严禁尝试以其他方式绕过（如利用其它插件执行）。
- **Trace Everything**: 即使是用户的“试探性”指令，也要作为审计事件记录。
- **Transparency**: 总是通过 `notify_user` 告知用户治理层已生效。

---
> "If it works, it's automation; if it breaks, it's a 'learning opportunity'. If it's governed, it's a PROFESSION."
