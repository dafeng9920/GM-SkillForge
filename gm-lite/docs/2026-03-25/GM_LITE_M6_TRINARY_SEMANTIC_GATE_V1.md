# GM LITE M6 Trinary Semantic Gate v1

## 核心结论
- `M6` 不能拥有无限分支自由度
- `semantic_score` 一旦引入，必须进入 `三极分支`
- 目标是把模糊语义判断压缩成 `确定性漏斗`
- 默认只允许三条路径：
  - `PASS`
  - `SUSPEND_FOR_REVIEW`
  - `ROLLBACK_AND_REJECT`

## 为什么必须三极化
- `M6` 是意图捕获门
- 如果它模糊推进，后面所有 gate 都会建立在不稳定底座上
- 工业级系统最怕 `似乎差不多`
- 因此：
  - 深渊来自于模糊
  - 确定性来自于阈值
- 解释不是通行证，分值才是通行证

## 默认评分区间

### Green Branch
- 条件：
  - `S >= 0.88`
- 语义：
  - 高置信度通过
- 动作：
  - Python 标记 `Gate_M6 = DONE`
  - noun anchors 进入 `Final_Anchors`
  - 允许推进到 `M7`
- 默认日志：
  - `[✅] Gate M6: semantic alignment high ({S})`

### Yellow Branch
- 条件：
  - `0.70 <= S < 0.88`
- 语义：
  - 语义漂移预警
- 动作：
  - 熔断当前自动流
  - 置为 `SUSPEND_FOR_REVIEW`
  - 生成 `original_intent vs extracted_anchors` 对比视图
  - 等待 `human_in_the_loop` 三选一：
    - 强制通过
    - 重新提取
    - 物理熔断
- 默认日志：
  - `[WARN] Gate M6: semantic drift suspected ({S})`
- 若选择 `Retry`，必须采用 `Offset Compensation Protocol`

### Red Branch
- 条件：
  - `S < 0.70`
- 语义：
  - 严重偏离
- 动作：
  - 严禁打勾
  - 执行物理回滚
  - 清理当前 active 临时垃圾
  - 记录到 `_runtime/error_logs`
  - 拒绝进入后续 gate
- 默认日志：
  - `[BLOCKED] Gate M6: severe semantic mismatch ({S})`

## 与现有恢复链的关系
- Green：
  - `DONE`
- Yellow：
  - `SUSPEND -> MEMO_RECORDED -> REMEDIATION_REQUIRED -> READY_TO_RESUME -> RESUMED`
- Red：
  - `ROLLBACK_AND_REJECT`
  - 必须留错例记录，不自动继续

## 默认数据结构建议

```json
{
  "gate_results": {
    "M6": {
      "semantic_score": 0.84,
      "semantic_branch": "SUSPEND_FOR_REVIEW",
      "original_intent_ref": "raw_origin",
      "anchor_result_ref": "noun_anchors",
      "decision": "manual_review_required"
    }
  }
}
```

## Python 执行主权
- 分支判断必须由 Python 基于阈值完成
- LLM / local semantic model 只负责给出分数或候选解释
- `DONE / SUSPEND / ROLLBACK` 的主权不属于模型
- 黄灯分支的人类决策接口也必须由 Python 托管，而不是由模型自由解释

## 默认伪代码

```python
def evaluate_m6_result(score: float) -> str:
    if score >= 0.88:
        return "PASS"
    if score >= 0.70:
        return "SUSPEND_FOR_REVIEW"
    return "ROLLBACK_AND_REJECT"
```

## 当前主线中的地位
- 这是当前 `可直接吸收` 的增强
- 它直接服务：
  - `BaseGate`
  - `BlueprintOrchestrator`
  - `semantic_score(a, b)`
  - redline semantic precheck
- 不属于后置视觉域增强
- 但它必须保持窄边界：
  - 只服务 M6
  - 不演变成开放式自愈循环

## 主控官结论
- `M6` 必须是扳机，不是泥潭
- 一旦启用语义评分，就必须套入固定三极分支
- 不允许出现无限延伸的模糊中间态
