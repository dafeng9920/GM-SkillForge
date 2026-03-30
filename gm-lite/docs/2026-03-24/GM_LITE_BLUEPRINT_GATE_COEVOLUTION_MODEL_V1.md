# GM LITE Blueprint Gate Coevolution Model v1

## 核心结论
- `打勾蓝图` 是逻辑流与状态记忆体
- `近防炮门禁` 是物理执行卡口
- 两者不是并列外挂关系，而是 `共生关系`
- 正确模式是：`过一关，打一勾`

## 默认协作分工

### Python Executor
- 负责物理动作与确定性状态判断
- 负责目录创建、文件移动、文件存在性检查、返回码检查、像素/文件处理
- 负责写入 `manifest.json`
- 负责同步生成或追加 `blueprint.md`
- 负责增量式控制台推送

### LLM Inspector
- 只负责 Python 无法判断的语义审计
- 只在关键节点被 Python 显式唤醒
- 返回 `PASS / FAIL / WARN` 一类审计信号
- 不直接拥有打勾主权

## 事件驱动型打勾机制

### Progressive Push
- 完成一个 step，立即更新一次
- `manifest.json` 实时写状态
- `blueprint.md` 实时追加人眼报告
- 控制台即时推送：
  - `[✅] Gate M6: Noun Anchors Locked.`
  - `[ ] Gate M7: Pending...`

### Checkpointed Resume
- 脚本重启时优先读取 `manifest.json`
- 已完成节点直接跳过
- 从第一个未完成节点继续
- 不允许因重启而重复消耗前序 Token

## 三层夹心模型

### 顶层：Blueprint Orchestrator
- 负责创建档案
- 负责初始化 `manifest.json`
- 负责初始化 `blueprint.md`
- 负责总控回调与 step 级状态推进

### 中层：M-Series Gates
- 每个 Gate 完成后必须回调蓝图控制器
- 回调至少包含：
  - `gate_id`
  - `status`
  - `metadata`
  - `timestamp`
- `M6` 如启用语义相似度审计，默认必须采用三极分支，而非连续模糊分支

### 底层：Mirror Sealer
- 只盯最终 gate 状态
- 仅当完成条件满足时，生成 `.frozen_seal`
- 镜像动作必须晚于蓝图闭环

## BaseGate 默认契约
- 所有子门禁都继承 `BaseGate`
- `BaseGate` 必须内置：
  - `update_checkpoint(task_id, step_name, status, metadata)`
  - `append_blueprint_report(task_id, message, metadata)`
  - `redline_check(task_id, gate_id, metadata)`
  - `execute()` 抽象接口
- `BaseGate` 默认先跑 `redline_check()`，再允许进入 `do_work()`
- Gate 依赖关系必须可被表达为 `DAG`
- `BlueprintOrchestrator` 启动 gate 流前，默认可执行 `topological_sort` 预检
- 如存在环依赖或非法回指，不得推进 gate 打勾

## TaskRunner 默认职责
- 驱动物理执行
- 在每个 step 完成后调用 checkpoint 更新
- 仅在 `needs_semantic_audit(step_id)` 为真时唤醒 LLM
- 维护最小控制台进度图
- 命中红线时立即熔断并停止后续步骤
- 熔断状态必须可写入 `SUSPEND / BLOCKED / CRITICAL_ERROR`
- 熔断后必须进入 `memo -> remediation -> resume` 恢复链，而不是静默停死
- 对 `M6` 的默认推进规则：
  - 绿色直接推进
  - 黄色挂起等待校准
  - 红色物理回滚
- 黄色分支默认允许挂接 `human_in_the_loop CLI`
- 该 CLI 只负责三选一决策，不负责改写主逻辑

## 设计原则
- 打勾主权归 Python，不归 LLM
- 语义审计是补充判断，不是物理状态替身
- 蓝图是状态记忆，不是装饰报告
- 门禁是执行扳机，不是孤立脚本
- 资产封印必须以后验 gate 完成为前提
- 红线高于流程推进，高于打勾完成感
- 恢复必须留下结构化备忘，不能靠口头记忆
- Gate 时间线应支持 `checkpoint hash chain`
- 每一关的结果指纹应可绑定前一关结果，避免后序伪造前序
