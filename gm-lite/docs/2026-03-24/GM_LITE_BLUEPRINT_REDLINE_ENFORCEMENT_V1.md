# GM LITE Blueprint Redline Enforcement v1

## 核心结论
- 打勾蓝图必须自带 `不可逾越红线`
- 红线不是提示语，而是 `熔断条件`
- 一旦触发红线，系统必须停止推进、拒绝打勾、升级主控官
- 红线必须被写入 `manifest.json` 的 `constraints.redlines` 中，由 Python 执行体强制拦截

## 红线存在的目的
- 为复杂项目建立确定性边界
- 防止 AI 以“继续推进”为名越界扩展
- 防止错误产物在蓝图中被误标为通过
- 防止 `manifest.json` 与 `blueprint.md` 失真

## Redline 分类

### R0. Resource Redline
- 必须支持 Token / 调用次数 / 预算 / 频率上限
- 如果下一步执行会超出预算或频率上限，必须置为 `CRITICAL_ERROR` 或 `SUSPEND`
- AI 不得绕过 Python 执行体继续消耗资源
- `M6` 的重试次数上限与 `total_token_burn` 统计也应视为资源红线的一部分

### R1. 权威路径红线
- 不得把权威写回落到镜像树
- `D:\gm-lite` 是唯一权威项目树
- 如写回路径落到 `D:\GM-SkillForge\gm-lite`，立即熔断

### R2. Frozen Contract 红线
- 不得改写已冻结的 contract / spec / manifest 基线
- 不得让执行体回写污染 `FROZEN` 物件

### R3. Runtime Scope 红线
- 在 seed 阶段不得偷跑完整 watcher、auto-send、timeout/retry、direct-connect
- 出现这些实现迹象，立即熔断

### R4. False Checkmark 红线
- 未经物理状态确认，不得打勾
- LLM 不得代替 Python 直接打勾
- 无文件、无返回码、无证据，不得置为 `DONE`

### R5. Semantic Drift 红线
- M6/M7 等关键 gate 如发现 noun anchors 丢失、意图原件被改写、关键元数据缺失，立即熔断
- 允许通过 `semantic_score(a, b)` 作为辅助预检信号
- 如原始意图与提取结果语义相似度显著偏低，不得直接置为 `DONE`
- 对 `M6` 默认适用三极阈值分支：
  - `S >= 0.88`：可通过
  - `0.70 <= S < 0.88`：挂起重审
  - `S < 0.70`：回滚拒绝

### R5A. Logic Redline
- 必须支持禁改核心名词 / 禁词 / 禁止逻辑方向
- 如 `M6` 已锁定核心名词，后续 gate 不得出现与之冲突的禁词或方向漂移
- 一旦触发负向语义越界，必须打勾失败并回滚

### R6. Mirror Seal 红线
- 未完成封印条件，不得执行镜像资产复制
- 未生成或未验证 `.frozen_seal`，不得宣称资产固化完成

### R7. Physical Redline
- 只允许向授权 active 路径写入
- 执行体不得向权威 active 目录之外写入任意字节
- 镜像树默认只读，除封印动作外不得写入

## 默认熔断动作
- 当前 Gate 状态置为 `ERROR` 或 `BLOCKED`
- 必要时置为 `SUSPEND`
- 在 `manifest.json` 中记录 redline code / metadata
- 在 `blueprint.md` 追加红线事件
- 控制台输出红线警报
- 强制升级主控官

## 标准恢复闭环
- 红线的目标不只是“挂起”，而是形成 `悬崖勒马 -> 留痕备忘 -> 纠偏修正 -> 重新启动` 的标准恢复链
- 默认恢复链：
  - `SUSPEND`
  - `MEMO_RECORDED`
  - `REMEDIATION_REQUIRED`
  - `READY_TO_RESUME`
  - `RESUMED`

### SUSPEND
- 当前 Gate 停止推进
- 后续 Gate 全部暂停

### MEMO_RECORDED
- 必须写入一条结构化备忘
- 至少包含：
  - `redline_code`
  - `trigger_gate`
  - `failed_condition`
  - `physical_evidence_ref`
  - `recommended_remediation`

### REMEDIATION_REQUIRED
- 问题未修复前，不得恢复推进
- 允许主控官或指定修复角色补齐缺失项

### READY_TO_RESUME
- 红线问题已被纠偏
- 已具备重新进入当前 Gate 的条件

### RESUMED
- 任务从最近合法 checkpoint 重新进入
- 不得重跑已稳定通过的历史步骤

## Manifest 默认约束结构
```json
{
  "constraints": {
    "redlines": [
      {
        "code": "R0",
        "type": "resource",
        "status": "ACTIVE"
      },
      {
        "code": "R5A",
        "type": "logic",
        "status": "ACTIVE"
      },
      {
        "code": "R7",
        "type": "physical",
        "status": "ACTIVE"
      }
    ]
  }
}
```

## Manifest 默认恢复字段
```json
{
  "recovery": {
    "recovery_status": "SUSPEND",
    "memo_log": [
      {
        "redline_code": "R5A",
        "trigger_gate": "M6",
        "failed_condition": "forbidden noun drift",
        "physical_evidence_ref": "active/<intent_trace_id>/audit.log",
        "recommended_remediation": "restore noun anchors and rerun gate"
      }
    ]
  }
}
```

## BaseGate 默认要求
- 每个 Gate 必须有 `redline_check()` 逻辑
- `execute()` 之前和之后都可触发红线检查
- `update_checkpoint()` 不得绕过红线判断
- 如启用语义相似度审计，默认由 `Inspector` 提供评分，由 Python 负责熔断或挂起
- Yellow 分支不得伪装成通过，只能进入 `SUSPEND` 路径
- Red 分支不得进入后续 gate，只能回滚并记错

## Seal 与时间线增强
- `manifest.json` 的 checkpoint 记录建议支持 `hash chain`
- 后一关 checkpoint 的哈希应包含前一关哈希、当前 gate_id、当前 gate 结果摘要
- `.frozen_seal` 建议绑定最终 checkpoint hash，确保镜像资产与逻辑时间线一致

## 最小控制台格式
- `[BLOCKED] Redline R1: authority path conflict`
- `[BLOCKED] Redline R4: physical evidence missing`
- `[BLOCKED] Redline R5: noun anchors lost`
