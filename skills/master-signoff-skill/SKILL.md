# master-signoff-skill

> 版本: v0.1.0  
> 适用阶段: 主控签核（如 T34/Txx Master-Control）

---

## 触发词

- `主控签核`
- `Master-Control 签发`
- `READY_FOR_AUTORUN 判定`
- `最终 gate 决策`
- `签核收口`

---

## 输入

```yaml
input:
  gate_decision_file: string      # 例如 docs/.../T33_gate_decision.json
  summary_file: string            # 各小队汇总文档
  signoff_file: string            # 主控签核文档
  expected_ready_key: string      # 例如 ready_for_p2_autorun
  signer: string                  # 默认 Master-Control
```

---

## 步骤

1. 读取 `gate_decision_file`，校验 `gate_decision=ALLOW`。  
2. 校验三判定 `implementation_ready/regression_ready/baseline_ready` 均为 `YES`。  
3. 校验 `expected_ready_key=YES`。  
4. 更新 `signoff_file`：写入 `decision/decision_value/signer/timestamp`。  
5. 更新 `summary_file` 的 Txx 状态与最终判定区块。  

---

## DoD

- 前置条件满足才允许签发 `READY_FOR_*_AUTORUN=YES`。  
- 签核文档与汇总文档状态一致，无互相冲突字段。  
- 输出引用了源证据路径（gate_decision json/yaml）。  

---

## 失败处理

| 场景 | 处理 |
|---|---|
| gate_decision 非 ALLOW | 拒绝签核，输出 `BLOCKED_BY_GATE_DECISION` |
| 三判定缺失或非 YES | 拒绝签核，输出缺失项 |
| 汇总文档冲突 | 暂停写入，先对齐事实来源再更新 |
| 签核文件不存在 | 自动新建模板并标记 `DRAFT` |

