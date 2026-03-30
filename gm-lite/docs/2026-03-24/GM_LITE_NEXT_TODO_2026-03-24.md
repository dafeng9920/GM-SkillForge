# GM-LITE Next TODO

## 今日收口
- `gm_lite_sample_flow_validation_v1 = completed`
- `gm_lite_blueprint_orchestrator_seed_implementation_v1 = completed`
- `gm_lite_shell_seed_implementation_v1 = completed`
- `gm_lite_environment_bootstrap_v1 = completed`
- `GM-LITE` 当前 smoke test = `PASS`

## 明日续推前必须记住的澄清

### 1. “外壳”的准确含义
- 这里的“外壳”不是目录壳、运行壳、文档壳
- 这里的“外壳”是：**真正的插件外壳**
- 它必须是一个：
  - 可安装
  - 可打开
  - 可作为产品承载体
  - 后续可进入插件市场或至少本地插件形态运行
  的插件壳子

### 2. 下一步的成败条件
下一步不是继续抽象讨论，而是必须开始满足下面两个条件：

#### 条件 A：插件外壳成立
- `GM-LITE` 必须拥有真正的插件壳
- 这个壳子要能承载：
  - 状态查看
  - 操作入口
  - 后续桥接能力

#### 条件 B：手动转递开始被打掉
- 目标不是再生成一堆提示词
- 目标是让插件/桥接壳开始承接：
  - 任务送入
  - 执行脉络挂接
  - 回收入口
- 这是“作战运行级 1”的真正分界线

## 当前真实判断
- 现在的 `GM-LITE` 已经有工程骨架、runtime 骨架、蓝图骨架
- 但还没有形成真正插件形态的承载体
- 也还没有消灭手动转递
- 所以下一阶段必须围绕“插件外壳 + 桥接壳”收缩

## 明天的下一主线
- 候选模块名：
  - `gm_lite_plugin_shell_preparation_v1`

## 明天启动时优先做的事
1. 明确插件宿主形态
- VS Code 扩展壳
- 还是其它编辑器/本地插件壳

2. 明确第一版插件壳的最低能力
- 插件入口
- 状态面板
- 最小操作入口
- 桥接占位

3. 明确“手动转递打掉”的第一刀从哪里落
- chat-output-to-bus bridge
- dispatch packet send hook
- writeback receive hook

## 不可偏离的初心
- 不忘最初目标：让系统真正替人运转
- 不再堆漂亮骨架而忽视作战运行级 `1`
- 后面一切新增模块都必须回答：
  - 是否逼近插件外壳成立？
  - 是否逼近手动转递消失？

## 可直接吸收的数学钢筋
- 当前只吸收三项：
  - `semantic_score(a, b)` 语义相似度接口
  - gate 流 `DAG / topological_sort`
  - checkpoint / seal 的 `hash chain`
- 其余更重的贝叶斯、仿射矩阵、Monte Carlo 先后置，不插队主线
- 后置项已归档：
  - `D:\GM-SkillForge\gm-lite\docs\2026-03-25\GM_LITE_DEFERRED_MATH_ENHANCEMENTS_BACKLOG_V1.md`

## 自动流转后的监控件
- 插件自动流转可用后，应补：
  - 运行区间
  - 完成任务数
  - 代码产出量
  - 状态推进数
  - 手动干预次数
  - Token / 重试 / 错误统计
- 已归档：
  - `D:\GM-SkillForge\gm-lite\docs\2026-03-25\GM_LITE_FLOW_OBSERVABILITY_AND_OUTPUT_REPORTING_V1.md`
