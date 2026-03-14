# L4-02 任务卡（vs--cc1）

## 目标
复用既有中间件资产，打通 n8n 触发入口与桥接脚本（最小可跑通）。

## 关键约束（必须）
1. **禁止重建五段式编排与三张卡片逻辑**，必须优先复用现有实现/契约。
2. n8n 仅做 `trigger/route/retry/notify`，不得持有最终裁决权。
3. 若现有资产可用，仅允许做“适配层补丁”，不得推翻重写。
4. **前后关系固定**：先产出五段式编排结果，再由三张卡片读取该结果生成展示结构（不得反向依赖）。
5. **主路固定**：必须对齐 `NL -> System` 这条唯一路径，不新增并行主路。

## 依赖
- L4-01 = ALLOW + PASS

## 复用优先资产（先读后改）
- `docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md`（3.6：五段式编排 + 三张卡片）
- `docs/2026-02-20/integration/l45_request_response_samples.json`
- `skillforge/src/contracts/api/n8n_boundary_v1.yaml`
- `skillforge/src/contracts/governance/n8n_execution_receipt.schema.json`
- `skillforge/src/api/routes/n8n_orchestration.py`
- `skillforge/tests/test_n8n_orchestration.py`
- `skillforge/tests/test_n8n_run_intent_production.py`
- `skillforge/tests/test_n8n_fetch_pack_production.py`
- `skillforge/tests/test_n8n_query_rag_production.py`

## 交付
- `docs/2026-02-26/l4-n8n-execution/verification/L4-02_execution_report.yaml`
- `docs/2026-02-26/l4-n8n-execution/verification/L4-02_gate_decision.json`
- `docs/2026-02-26/l4-n8n-execution/verification/L4-02_compliance_attestation.json`

## DoD
1. 可触发一次 n8n -> 本地处理链路。
2. 失败路径有错误码与证据引用。
3. 明确说明“复用了哪些既有资产、改了哪些适配层、为什么不重建”。
4. 输出五段式与三卡片映射结果（字段级对照）。
5. 明确提供链路证明：`NL 输入 -> 五段式结果 -> 三卡片 -> System 执行`。
