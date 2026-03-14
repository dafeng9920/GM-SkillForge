# 云端多 Agent 协作与受控交付协议 (v1)

## 1. 核心治理架构

为了确保云端执行的真实性与合规性，引入 **“三位一体 (Trinity)”** 协作模式：

### 1.1 角色定义 (The Trinity)
- **Executor (执行者 - 小龙虾-E)**: 负责按合同修改代码，产出 `.diff` 或产物。
- **Reviewer (审查者 - 小龙虾-R)**: 负责审计执行者的代码逻辑，验证 `execution_receipt` 的真实性。
- **Compliance (合规官 - 小龙虾-C)**: 负责检查权限边界、路径合规性，签署 `compliance_attestation`。

### 1.2 物理运行拓扑
- **隔离实验室**: 云端 Docker 容器，主仓挂载为 `:ro` (ReadOnly)。
- **交付出口 (Dropzone)**: 固定物理路径 `/home/node/dropzone/`。
- **缓冲区 (Staging)**: 宿主机 `./dropzone` 目录，产物在此等待主控（Local Controller）裁决。

---

## 2. 受控交付流程 (The Controlled Gate)

### Phase 0: 架构共识 (Architectural Consensus)
- **参与者**: 2 名执行者 (E1 & E2) 或 1 名 Architect + 1 名 Executor。
- **动作**: 提交一份 **“实现蓝图 (Implementation Blueprint)”**。
- **治理分级 (Tiered Guardrail)**:
  - **L1 (常规/文档)**: 双方达成共识即可进入 Phase 1。
  - **L2 (代码/契约)**: 
    - **在线模式**: 蓝图必须经 **本地主控** 签署 `PROCEED` 方可动工。
    - **离线模式 (AOE) [NEW]**: 若主控由于关机等原因离线，进入 **“代理核准”** 流程。由 Reviewer 充当 “Master Proxy”，执行最严苛的“反面论证”。必须产出一份 `Risk_Exposure_Statement` (风险暴露声明) 后方可降级执行。
- **价值**: 确保主控不在场时，系统依然具备基于“代理人”的逻辑刹车。
- **价值**: 确保“双龙议政”不变成“幻觉共振”，由更高能力的模型/人工进行逻辑兜底。

### Phase 1: 执行与初审
- **动作**: Executor 交付产物至 `dropzone/<task_id>/`；Reviewer 和 Compliance 在隔离区内完成联署签名。
2.  **信号发送**: 只有当 `completion_record.md` 包含全员联署（E+R+C）后，才会提醒主控。
3.  **主控验收**: 本地主控官（USER/Antigravity）通过 `cat` 或 `ls` 核查宿主机 `dropzone` 内容。
4.  **物理吸收 (Absorption)**: 
    - 主控下达 `ACCEPT` 指令。
    - 执行 `scripts/absorb.sh <task_id>`。
    - 产物从 `dropzone` 物理搬运至项目主仓 `docs/` 或 `src/`。

---

## 3. 分级交付目录规范 (Dropzone Layout)

每个任务必须严格遵循以下结构：
```text
dropzone/<task_id>/
├── artifacts/          # 实际代码产出 (.diff, .patch, 新文件)
├── evidence/           # 执行证据 (logs, test_results, screenshots)
├── governance/         # 治理对策
│   ├── execution_receipt.json    (Executor 签发)
│   ├── review_decision.json      (Reviewer 签发)
│   └── compliance_attestation.json (Compliance 签发)
├── completion_record.md # 综述与联署看板
└── resume_handoff.md    # 续跑说明
```

---

## 4. 自动化提升预设

- **宿主机监控 (Sentinel)**: 监视 `dropzone` 目录，一旦有新提交且三方签名齐全，立即生成“验收摘要”。
- **原子吸收**: `absorb.sh` 必须支持 Dry-run 和 Rollback。

---

## 5. 审计质量保障 (Reasoning Guardrails) [NEW]

为了防止云端模型推理疲劳或幻觉，实施以下规则：
1. **证据优先 (Evidence-First)**: Reviewer 的结论必须引用 `evidence/` 下的具体日志或截图，禁止使用模糊的“逻辑正常”表述。
2. **终极裁决 (Final Gate)**: 所有进入 `dropzone` 的产物，在物理吸收前，必须由宿主机 Antigravity 执行一次 **“影子审计 (Shadow Audit)”**。
3. **Fail-Closed**: 一旦 E/R/C 三方出现逻辑冲突且 2 轮内无法通过共识解决，任务强制挂起，等待主控人工介入。

---

## 5. 离线自治与安全熔断 (AOE Rules) [NEW]

在主控官离线期间（夜间模式），执行以下强制规则：
1. **代理权移交 (Proxy Delegation)**: Reviewer 自动获得“架构否决权”。任何一个 Agent 对 Phase 0 蓝图表示质疑，任务必须立即 **SUSPEND (挂起)**，严禁带疑执行。
2. **影子路径标记 (Shadow Labeling)**: 离线模式产出的所有文件必须在元数据中标记 `mode: AOE_DELEGATED`，以便次日主控进行 100% 物理回溯。
3. **熔断器 (Circuit Breaker)**: 
   - 禁止修改 `infrastructure/` 或 `auth/` 等高敏感目录。
   - 单次离线执行累计修改行数不得超过 `DELTA_LIMIT` (如 200 行)。
   - 一旦触发冲突或权限报错，立即执行 `Fail-Closed`，全线停工。

---
*版本: v1.2 (2026-03-08) - AOE 离线增强版*
*审核人: 架构大师 / Antigravity*
