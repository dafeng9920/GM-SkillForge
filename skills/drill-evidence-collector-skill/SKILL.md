# drill-evidence-collector-skill

> 版本: v0.1.0  
> 适用阶段: 单次可审计演练（Fail-Closed / at-time 一致性）

---

## 触发词

- `单次可审计演练`
- `drill 报告`
- `收集 run_id evidence_ref`
- `Fail-Closed 演练`
- `at-time 回放一致性`

---

## 输入

```yaml
input:
  exercise_id: string
  success_run_response: object
  failure_run_response: object
  replay_response: object         # 可选（query_rag/fetch_pack）
  report_file: string             # L45_*_DRILL_REPORT_v1.md
  output_yaml_file: string        # verification/*.yaml
```

---

## 步骤

1. 抽取成功链路证据：`run_id/evidence_ref/gate_decision/release_allowed/permit_id`。  
2. 抽取失败链路证据：`error_code/blocked_by/run_id/evidence_ref`。  
3. 抽取回放一致性证据：`expected_at_time` 与 `actual_at_time`。  
4. 生成标准 YAML 结论块并回填到演练报告。  
5. 给出最终 `PASS/FAIL` 判定与阻断项。  

---

## DoD

- 成功链路和失败链路都具备真实 `run_id + evidence_ref`。  
- 失败链路包含可复核 `error_code + blocked_by`。  
- 回放一致性字段齐全（或明确 `NOT_AVAILABLE`）。  
- 报告与 YAML 结论一致，无字段漂移。  

---

## 失败处理

| 场景 | 处理 |
|---|---|
| 无 run_id/evidence_ref | 标记 `EVIDENCE_MISSING` 并拒绝 PASS |
| error_code 缺失 | 标记 `FAILURE_NOT_AUDITABLE` |
| at_time 不一致 | 标记 `REPLAY_INCONSISTENT` 并阻断 |
| fetch_pack 缺失 | 标记 `PACK_NOT_FOUND`，可不阻断但需记录 |

