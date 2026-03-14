# L4-04 任务卡（Kior-B）

## 目标
接入 AEV 计算模块（`V_token + V_compute + V_risk + V_trust`）。

## 依赖
- L4-02, L4-03 = ALLOW + PASS

## 交付
- `docs/2026-02-26/l4-n8n-execution/verification/L4-04_execution_report.yaml`
- `docs/2026-02-26/l4-n8n-execution/verification/L4-04_gate_decision.json`
- `docs/2026-02-26/l4-n8n-execution/verification/L4-04_compliance_attestation.json`

## DoD
1. AEV 公式可运行。
2. 每个分项有来源说明。

## 执行命令（模型固定）

优先模型：`gpt-5.1-mini`

```bash
# 示例：将你的执行命令加上模型参数
<EXEC_COMMAND> --model gpt-5.1-mini
```

## 模型降级策略（避免中断）

若出现 “model not found / no access”：

1. `--model gpt-5.1-mini`（首选）
2. `--model gpt-5-mini`
3. `--model gpt-5`

要求：
1. 发生降级时在 `L4-04_execution_report.yaml` 记录实际模型名。
2. 不因模型切换改变任务目标与交付路径。
