# GM LITE Three Locks Enforcement v1

## 核心结论
- 当前 runtime 必须同时具备三把锁：
  - `Path Guard`
  - `Vector Grinder`
  - `Token Meter`
- 它们分别对应：
  - 空间锁
  - 数学锁
  - 经济锁

## L1: Path Guard

### 目标
- 锁死权威路径
- 防止路径漂移污染

### 默认要求
- 在 `BusManager` / runtime 中优先使用绝对路径
- 路径进入执行前必须做 authority 校验
- `D:\gm-lite` 根校验失败时，必须立刻退出

### 默认动作
- `sys.exit()` 或等价 fail-closed 终止
- 严禁带着错误路径继续运行

## L2: Vector Grinder

### 目标
- 让语义判断服从分值，不服从漂亮解释

### 默认要求
- `M6` 的语义判断以 `semantic_score` 为硬信号
- 分值不到阈值，不得仅凭文字解释通过
- 主控官只在黄灯区拥有 `1/2/3` 决策权

### 默认动作
- `S >= 0.88`：通过
- `0.70 <= S < 0.88`：CLI 决策
- `S < 0.70`：回滚拒绝

## L3: Token Meter

### 目标
- 让每轮反思和重试都有成本记账

### 默认要求
- 在 `manifest.json` 中记录：
  - `retry_count`
  - `total_token_burn`
- 第 3 次失败必须跳闸

### 默认动作
- 超过阈值：
  - `FROZEN_ERROR`
  - 升级主控官
  - 停止继续烧 Token

## 主控官结论
- 这三把锁不是优化项
- 它们是当前闭环继续向前长时的最低止损结构
