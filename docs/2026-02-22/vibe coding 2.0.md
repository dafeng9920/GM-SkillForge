# Vibe Coding 2.0（流畅丝滑版）

## 1. 目标

把当前“强治理但偏手工”的协作模式，升级为“高流畅 + 高合规”的跨 IDE 多 Agent 中控系统：

- 前台体验：一句话需求，自动生成并分发任务。
- 后台治理：A/B Guard + 三权分立 + 证据链 + Gate 自动裁决。
- 产出标准：每次任务都可回放、可追责、可验收。

---

## 2. 2.0 的核心定义

Vibe Coding 2.0 不是减少规则，而是把规则“隐形自动化”。

一句话：
> 用户只需要说目标；系统自动完成规划、分派、审查、合规、执行回执收集和最终验收。

---

## 3. 设计原则

1. 流畅优先：交互输入最少，自动生成最多。  
2. 宪法优先：无 Compliance PASS 不执行。  
3. 证据优先：无 EvidenceRef 不算完成。  
4. 三权分立：Execution / Review / Compliance 强制隔离。  
5. 跨 IDE 优先：不依赖单一 IDE 插件，走外部中控。  

---

## 4. 架构蓝图（2.0）

### 4.1 控制平面（Orchestrator Core）

负责：
- 需求转任务（自动生成 task_dispatch + Task Skill Spec）
- 依赖调度（DAG）
- Guard 校验（A 提案前置，B 执行前置）
- 最终 Gate 裁决（ALLOW / REQUIRES_CHANGES / DENY）

### 4.2 执行平面（Agent Executors）

负责：
- 按任务书执行
- 提交 ExecutionReport
- 不触碰主控与合规裁决逻辑

### 4.3 治理平面（Review + Compliance）

负责：
- Review：质量与边界审查
- Compliance：Fail-Closed 合规拦截
- 输出标准化回执并阻断违规执行

---

## 5. 标准流转（丝滑版）

1. 用户输入一句需求。  
2. 中控自动生成：`task_dispatch + Txx 任务书 + Agent 提示词包`。  
3. Review 与 Compliance 自动预检（未通过不分发）。  
4. 分发到多 IDE Agent 并行执行。  
5. 自动收集 `execution_report / gate_decision / compliance_attestation`。  
6. 主控自动汇总并生成 `final_gate_decision.json`。  

---

## 6. 与现有体系的对齐

已对齐资产：
- `docs/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md`
- `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md`
- `multi-ai-collaboration.md`（v3 三权分立）

2.0 的工作是把这些“文档规范”升级为“自动化系统行为”。

---

## 7. MVP（两周可落地）

### M1（第 1 周）

1. `orchestrator generate`：一句话生成任务包  
2. `orchestrator dispatch`：按 DAG 分发执行  
3. `orchestrator collect`：收集并校验三类回执  

### M2（第 2 周）

4. `orchestrator gate`：自动生成最终裁决  
5. `orchestrator dashboard`：状态总览页（任务、阻塞、证据）  
6. `orchestrator close`：产出最终收口包（含 final_gate_decision）  

---

## 8. 2.0 验收标准（DoD）

1. 一句话需求可自动生成完整任务包。  
2. 跨 3 个 IDE 可并发执行并自动回执。  
3. 任一任务无 Compliance PASS 时被硬阻断。  
4. 每个 ALLOW 任务都具备可追踪 EvidenceRef。  
5. 自动产出 `final_gate_decision.json` 且可复现。  

---

## 9. 风险与防偏航

风险：
- 角色错配（把 compliance 当 execution）
- 回执格式漂移
- 任务依赖错配导致“先做后审”

防偏航机制：
- 角色字段强校验（不通过即 DENY）
- 回执 schema 校验（不通过即 REQUIRES_CHANGES）
- DAG 强约束（depends_on 未满足不得启动）

---

## 10. 预期收益

1. 协作效率：多 Agent 并行不混乱。  
2. 治理稳定：强约束不靠口头。  
3. 体验升级：流程“行云流水”，结果“可审计可追责”。  
4. 可扩展：可接入更多执行臂（含 Claude Code）而不破坏治理。  

---

## 11. 2.0 一句话愿景

> 前台像 Vibe Coding 一样丝滑，后台像审计系统一样铁律。  
