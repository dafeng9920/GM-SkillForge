# GM LITE M6 Human In The Loop CLI v1

## 核心结论
- `M6` 的黄灯分支不能悬空
- 当 `0.70 <= semantic_score < 0.88` 时，系统需要一个 `human_in_the_loop` 决策终端
- 这个 CLI 的职责不是接管逻辑，而是接管 `最终决策`
- 它必须运行在权威树 `D:\gm-lite` 上，并与蓝图、红线、恢复链一致

## 设计目标
- 不干扰主逻辑
- 不替代 Python 执行主权
- 只在黄色预警区出现
- 给主控官一个极简明确的 `1/2/3` 决策口

## 触发条件
- 仅当 `M6` 进入黄色分支时触发：
  - `0.70 <= S < 0.88`

## CLI 决策协议

### 选项 1：Force Pass
- 返回：
  - `PASS`
- 含义：
  - 主控官人工确认当前提取结果可接受
- 后果：
  - 可强制置位 `Gate_M6 = DONE`
  - 必须在 `manifest.json` 中记录这是 `human_override`

### 选项 2：Retry
- 返回：
  - `RETRY`
- 含义：
  - 语义不达标，但值得再试一次
- 后果：
  - 不打勾
  - 进入重新提取路径
  - 默认必须注入 `Offset Compensation Protocol`
  - 默认必须增加 `m6_retry_count`
  - 需记录重试次数和重试理由

### 选项 3：Abort
- 返回：
  - `ABORT`
- 含义：
  - 判定意图当前不可接受
- 后果：
  - 进入 `ROLLBACK_AND_REJECT`
  - 执行物理回滚
  - 记录到 `_runtime/error_logs`

## 最小界面要求
- 必须展示：
  - `RAW INTENT`
  - `AI ANCHORS`
  - `semantic_score`
  - `1/2/3` 三选项
- 必须阻塞等待输入
- 输入非法时必须重新提示，不得静默继续

## 与现有状态机的映射

### Force Pass
- `SUSPEND_FOR_REVIEW -> human_override -> DONE`

### Retry
- `SUSPEND_FOR_REVIEW -> MEMO_RECORDED -> REMEDIATION_REQUIRED -> RETRY_REQUESTED`

### Abort
- `SUSPEND_FOR_REVIEW -> ROLLBACK_AND_REJECT`

## Manifest 建议字段

```json
{
  "gate_results": {
    "M6": {
      "semantic_score": 0.76,
      "semantic_branch": "SUSPEND_FOR_REVIEW",
      "human_decision": "RETRY",
      "human_decision_ts": "2026-03-25T00:00:00Z",
      "human_decision_reason": "anchor too generic"
    }
  }
}
```

## 设计边界
- 该 CLI 只服务黄灯分支
- 绿色分支不应弹窗
- 红色分支不应给“模糊挽救”机会，默认直接回滚拒绝
- 该 CLI 不属于完整插件 UI，只是当前 `闭环 1` 和 `Blueprint runtime` 的最小人机火控协议

## 主控官结论
- 这不是普通交互组件
- 这是 `M6` 黄灯分支的 `火控协议`
- 它让主控官只在真正需要的时候介入，并以确定性的三选一方式介入
- 一旦选择 `Retry`，系统不得原样重试，而必须进行偏移补偿
- 一旦超过 `Logic Fuse` 阈值，CLI 不得继续放行重试
