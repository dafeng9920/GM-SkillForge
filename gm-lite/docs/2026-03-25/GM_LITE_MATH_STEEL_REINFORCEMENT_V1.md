# GM LITE Math Steel Reinforcement v1

## 核心结论
- 三大支柱可以接受 `数学/算法钢筋` 加固
- 但当前主线只吸收三类 `直接增强当前 runtime` 的内容：
  - `语义相似度接口`
  - `DAG / topological_sort`
  - `哈希链式 checkpoint / seal`
- 其余更重的数学机制先记为后置增强，不插队主线

## 为什么是选择性吸收
- `GM-LITE` 当前的成败线是 `作战运行级 1`
- 当前最优先的是：
  - 插件外壳作为产品承载体
  - 手动转递开始消失
  - 执行脉络与执行条件真正接上
- 因此数学增强必须服务这条主线，而不是把系统提前做成研究平台

## 支柱 1：空间感

### 当前采纳
- 保留 `坐标锚点` 作为未来视觉/分形模块的标准术语
- 允许在后续涉及切片、拼接、微观生成时采用 `Affine Matrix` 思路

### 当前不前置实现
- 不在当前 plugin shell / blueprint runtime 主线里强绑仿射矩阵实现
- 不把 `81 地块 gap-free` 这种视觉域目标提前塞入当前 runtime

### 理由
- 这条更偏未来 `视觉 / 分形 / Studio Backend` 能力
- 对当前“插件外壳 + 手动转递消失”不是第一优先级

## 支柱 2：时间感

### DAG 约束
- `BlueprintOrchestrator` 的 gate 流必须可被表达为 `DAG`
- 默认 gate 主链至少满足：
  - `M6 -> M7 -> M8 -> M9`
- 必须支持 `topological_sort`
- 如出现环依赖、回指、非法越级，必须拒绝执行

### Hash Chain 约束
- 每个 gate checkpoint 的指纹应包含前一 gate 的指纹
- 目标不是上链，而是建立 `不可逆逻辑时间轴`
- 这直接服务：
  - `manifest.json`
  - `blueprint.md`
  - `.frozen_seal`
  - 样板回放证明

### 直接收益
- 无法在没有 `M6` 的情况下伪造 `M7`
- 无法在中途静默改写早期 gate 而不影响后续 seal
- 打勾蓝图从“状态表”升级为“带顺序证明的证据链”

## 支柱 3：价值感

### 当前采纳
- 允许引入 `semantic_score(a, b)` 作为候选语义审计接口
- 推荐用途：
  - `M6` 原始意图 vs noun anchors 的语义一致性粗检
  - reverse echo 前置分流
  - redline 里的语义侧预检

### 当前接口优先
- 先冻结函数位和阈值位
- 不把具体模型实现绑死在 v1 主线
- 推荐接口：

```python
def semantic_score(text_a: str, text_b: str) -> float:
    ...
```

### 候选阈值
- `score < 0.85`：
  - 不允许直接打勾
  - 进入 `WARN / SUSPEND / escalate` 路径

### 当前不前置实现
- 不把 `3 次采样 + P > 0.95` 的贝叶斯封印条件提前做成当前强制门
- 不在当前主线中强绑本地 `sentence-transformers` 模型下载流程

### 理由
- 现阶段先要保证壳、路由、状态、转递脉络成立
- 统计审计适合在后续 local gate integration 后再增强

## 当前应被正式吸收的三条钢筋

### 1. Semantic Similarity Interface
- 类型：轻量语义质检接口
- 所属层：
  - `7B / local inspector`
  - `redline semantic precheck`
  - `M6 noun anchor validation`

### 2. DAG Topology Validation
- 类型：流程合法性校验
- 所属层：
  - `BlueprintOrchestrator`
  - `BaseGate dependency validation`
  - runtime 启动前预检

### 3. Checkpoint Hash Chain
- 类型：证据链与封印增强
- 所属层：
  - `manifest.json`
  - `blueprint seal`
  - `MirrorSealer`
  - replay / audit proof

## 后置增强清单
- 贝叶斯一致性采样
- 仿射矩阵驱动的视觉拼接/缩放/旋转
- Monte Carlo 光比/散射推演
- 视觉分形索引与 Hilbert Curve 等更重的递归路径算法

## 主控官结论
- 数学可以是 `GM-LITE` 的钢筋
- 但钢筋必须先服务当前活主干
- 当前最该落地的是：
  - 语义相似度接口
  - DAG 拓扑合法性
  - 哈希链式 checkpoint / seal
- 其余重数学增强在未来视觉域和本地门禁增强阶段再接入
