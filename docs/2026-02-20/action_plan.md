# L4.5 Day-1 行动计划（AI 军团）

> 日期: 2026-02-20  
> 任务主题: 接入 n8n 编排边界（n8n 仅触发/路由，SkillForge 负责最终裁决）  
> 方法论: `multi-ai-collaboration.md`（Skill 化 5 步）

---

## 1. 目标与范围

### 1.1 目标
- 建立 n8n 与 SkillForge 的硬边界：n8n 不得持有最终裁决权。
- 打通最小编排闭环：`run_intent` -> `fetch_pack` -> `query_rag(at_time)`。
- 全链路保留 fail-closed：E001/E003 语义不漂移。

### 1.2 范围内交付
- 边界契约（文档 + machine-readable contract）
- SkillForge 编排入口与边界校验实现
- n8n 最小工作流（真实可跑）
- 端到端验证与验收文档

### 1.3 范围外（本轮不做）
- 新业务策略功能扩展（trend_following / multi_factor 业务逻辑）
- 市场交易规则产品化 UI
- L5 模型级全量审计扩展

---

## 2. 不可回退硬约束

1. n8n 只允许 `trigger/route/retry/notify`。
2. n8n 禁止 `final decision / release override / direct registry admission`。
3. SkillForge 必须输出最终 `gate_decision + release_allowed + evidence_ref + run_id`。
4. 输入固定为 `repo_url + commit_sha + at_time`，禁止 latest 漂移。
5. no-permit-no-release 不得放松。

---

## 3. 波次编排

### Wave 1（并行实现）
- T1 `vs--cc3`: 核心 API 边界与编排入口
- T2 `vs--cc2`: n8n 边界适配与入参白名单
- T3 `Kior-B`: n8n 工作流落地
- T4 `vs--cc1`: 契约与证据字段固化

### Wave 2（集成）
- T5 `Kior-A`: 前后端 + n8n + SkillForge 胶合联调

### Wave 3（验收）
- T6 `Kior-C`: E2E、回归、文档验收与 Gate 决策包

---

## 4. Day-1 通过条件

1. n8n 最小工作流真实跑通 >= 1 次。
2. n8n 越权裁决被阻断（注入 `gate_decision` 无效或拒绝）。
3. E001 / E003 阻断语义无漂移。
4. 证据链完整：`run_id + evidence_ref + gate_decision`。
5. 收口文档齐全并可审计。

---

## 5. 交付目录

```text
docs/2026-02-20/
├── action_plan.md
├── task_dispatch.md
├── tasks/
│   ├── T1_vs--cc3.md
│   ├── T2_vs--cc2.md
│   ├── T3_Kior-B.md
│   ├── T4_vs--cc1.md
│   ├── T5_Kior-A.md
│   └── T6_Kior-C.md
└── verification/
    └── (由 T6 生成验收文件)
```

