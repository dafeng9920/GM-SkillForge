# GM LITE M6 Offset Compensation Protocol v1

## 核心结论
- `Retry` 不能等于机械重试
- `M6` 黄灯分支一旦选择 `Retry`，必须进入 `偏移补偿协议`
- 目标不是让模型“再说一遍”，而是让它基于失败现场进行 `受约束的反思重提取`

## 为什么需要偏移补偿
- 如果只是原样重试，模型大概率复读上一次错误
- `semantic_score` 已经给出了一个明确的失败信号
- 工业化系统必须把：
  - 失败提取结果
  - 失败分值
  - 当前阈值
  - 关键遗漏方向
  作为结构化反馈重新注入

## 触发条件
- 仅当 `M6` 进入黄色分支，且主控官在 CLI 中选择：
  - `Retry`

## 协议目标
- 将“失败现场”转化为下次提取的约束输入
- 收敛模型的自由度
- 迫使它补回遗漏的锚点，而不是输出解释性废话

## 反馈注入的最小字段
- `raw_intent`
- `failed_anchors`
- `semantic_score`
- `required_focus`
- `threshold_target`

## required_focus 默认方向
- `空间感`
  - 方位
  - 层级
  - 视角
  - 焦距
- `时间感`
  - 顺序
  - 流程位置
  - 关键前置条件
- `价值感`
  - 哪些锚点是后续镜像资产纯度的决定因素

## 默认重试提示词约束
- 必须包含：
  - 上次失败结果
  - 上次失败分值
  - 当前阈值目标
  - 重新提取任务
- 必须禁止：
  - 冗长解释
  - 道歉文本
  - 与名词提取无关的扩展发挥

## 推荐输出要求
- 只输出：
  - 重新校准后的名词锚点序列
- 不输出解释，不输出分析散文

## 默认伪模板

```text
### Audit Feedback
Previous extraction did not pass Gate M6.

[Raw Intent]: "{raw_intent}"
[Failed Anchors]: "{failed_anchors}"
[Semantic Score]: {score} (below threshold)

### Reflection Task
Your extraction shows semantic drift.
1. Identify what physical detail or anchor is missing.
2. Re-anchor space / time / value boundaries.
3. Re-extract a tighter set of explicit noun anchors.

### Output Requirement
Do not explain.
Only output corrected noun anchors.
```

## 与 CLI 的关系
- `CLI` 负责让主控官选择：
  - `Force Pass`
  - `Retry`
  - `Abort`
- `Offset Compensation Protocol` 只在 `Retry` 被选中时生效
- 也就是说：
  - CLI 是火控决策口
  - Offset Compensation 是重试弹药装填规则

## 与现有状态机的关系
- `SUSPEND_FOR_REVIEW`
  - 若选 `Retry`
  - 进入：
    - `MEMO_RECORDED`
    - `RETRY_REQUESTED`
    - `OFFSET_COMPENSATION_INJECTED`
    - `M6_RETRY_RUNNING`
- `Retry` 不得无限递归
- 必须受 `Logic Fuse` 约束

## 设计边界
- 这不是通用自愈系统
- 只针对 `M6 noun anchor extraction`
- 不允许在当前阶段演变成无限递归反思链
- 默认应限制最大重试次数

## 默认建议
- `max_retry_attempts = 2`
- 当前统一改为：
  - `m6_max_allowed = 3`
- 超限后不得继续自动重试
- 必须冻结任务并升级主控官

## 主控官结论
- `Retry` 必须有代价，也必须有方向
- 数值失败信号是最好的补偿入口
- M6 的正确重试，不是重播，而是带偏差校正的重新提取
