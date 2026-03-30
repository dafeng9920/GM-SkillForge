# GM LITE Executor Inspector Arbiter Allocation v1

## 核心结论
- `GM-LITE` 的默认分工不是“全让大模型做”，而是：
  - `Python Executor`
  - `7B Inspector`
  - `Controller Arbiter`
- 分工原则是：
  - 能由 Python/规则完成的，绝不交给 LLM
  - 能由 7B 完成的，不升级主控官
  - 只有高价值歧义判断，才交给主控官/强模型

## 三层分工

### 1. Python Executor
- 负责路径创建、文件创建/移动、返回码检查、物理状态判断
- 负责 `manifest.json` / `blueprint.md` 更新
- 负责 checkpoint 打勾
- 负责 redline 预检与物理熔断
- 负责 `.frozen_seal` 生成
- 负责 replay / runtime 索引

### 2. 7B Inspector
- 负责 noun anchors 提取
- 负责 tag cloud / forbidden noun drift / 轻量 reverse echo
- 负责语义红线与轻量 drift 初筛
- 负责“是否升级强模型”的预判
- 后续可扩展承担：
  - 意图压缩
  - 冲突检测
  - 100 字内全局风险摘要
  - 资产复用建议的低成本粗筛

### 3. Controller Arbiter
- 负责 Spec/Contract 生成与修正
- 负责高歧义意图裁决
- 负责 remediation 方案裁决
- 负责 release judgment
- 负责跨模块冲突与架构升级判断

## 成本优先级
- `Python`：默认主执行层，承担大部分流程劳动
- `7B`：默认质检层，承担高频低成本语义判断
- `Controller`：默认最终裁决层，只做高价值判断

## 默认路由
1. Python 先跑
2. 7B 再审
3. 分歧 / 高风险 / 高价值歧义时升级主控官

## 分层防火墙补充
- `L1 物理层`：
  - Python Executor 主导
- `L2 过滤层`：
  - 本地轻量模型 / 20MB 语义模型 / 7B Inspector 主导
- `L3 进化层`：
  - 7B 提建议，Controller 做裁决

## Blueprint Runtime 映射

### Python 完成
- `BO1` 绝大部分
- `BaseGate.update_checkpoint`
- `manifest / blueprint` 双写
- `SUSPEND / MEMO / RESUME`
- `MirrorSealer` 条件检查
- 控制台进度推送

### 7B 完成
- `M6` noun anchors 粗提取
- 逻辑红线禁词检查
- 轻量 semantic drift 检查
- 是否触发 `R5 / R5A` 的初筛

### 主控官完成
- RAW -> ENRICHED 的复杂补完
- “Spec 是否丢了灵魂” 的最终裁决
- remediation 方向判定
- 是否允许恢复推进
- 最终冻结/发布判断
