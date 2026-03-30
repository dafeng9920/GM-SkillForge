# GM LITE M6 Logic Fuse v1

## 核心结论
- `Retry` 机制如果没有保险丝，迟早会演变成烧钱死循环
- `M6` 必须具备 `最大重试归零` 机制
- 保险丝必须是 `持久化的物理状态`，不能只存在内存里

## 为什么必须有 Logic Fuse
- `M6` 是最容易进入反思递归的位置
- 如果模型连续数次仍无法对齐意图，问题往往不再是“再试一次”
- 继续重试只会：
  - 烧 Token
  - 消耗时间
  - 污染运行日志
  - 稀释主控官注意力

## 默认统计结构

```json
{
  "audit_stats": {
    "m6_retry_count": 0,
    "m6_max_allowed": 3,
    "total_token_burn": 0
  }
}
```

## 默认规则

### Retry Counter
- 每次 `M6` 黄灯后选择 `Retry`
- 必须使：
  - `m6_retry_count += 1`

### Success Reset
- 一旦 `M6` 成功通过
- 必须使：
  - `m6_retry_count = 0`

### Fuse Blow
- 若：
  - `m6_retry_count >= m6_max_allowed`
- 则必须：
  - 停止继续自动重试
  - 置位 `FROZEN_ERROR` 或等价冻结错误态
  - 升级主控官
  - 记录错例
  - 停止继续烧 Token

## 默认阈值
- `m6_max_allowed = 3`

## 为什么是 3
- 第 1 次失败：
  - 可能是模型随机漂移
- 第 2 次失败：
  - 说明需要偏移补偿
- 第 3 次失败：
  - 说明意图、约束或提取目标本身可能有冲突
- 第 4 次：
  - 不再属于工程自愈，而属于资源浪费

## 持久化要求
- `m6_retry_count` 必须写回磁盘中的 `manifest.json`
- 不得只保存在进程内存
- 程序重启后必须能延续真实重试计数

## 与 Token 预算的关系
- `Logic Fuse` 与 `R0 Resource Redline` 联动
- 除重试次数外，建议同时记录：
  - `total_token_burn`
  - 单任务预算阈值
- 如命中预算红线，也可直接触发冻结

## 默认状态机

### 未超限
- `SUSPEND_FOR_REVIEW`
- `RETRY_REQUESTED`
- `OFFSET_COMPENSATION_INJECTED`
- `M6_RETRY_RUNNING`

### 超限
- `FROZEN_ERROR`
- `MEMO_RECORDED`
- `ARCHITECT_ESCALATION_REQUIRED`

## 默认物证要求
- 必须在错误日志中记录：
  - 原始意图
  - 最近一次失败 anchors
  - 最近一次 `semantic_score`
  - 当前 `retry_count`
  - 触发熔断原因

## 设计边界
- 这是 `M6` 专用保险丝
- 不是通用无限重试框架
- 后续若扩展到其他 gate，应单独定义，不默认复用

## 主控官结论
- 一个好的 gate，不只会拦错，也会止损
- `M6 Logic Fuse` 的目标是：
  - 保护账单
  - 保护主控官注意力
  - 保护系统不被无效递归拖入语义深渊
