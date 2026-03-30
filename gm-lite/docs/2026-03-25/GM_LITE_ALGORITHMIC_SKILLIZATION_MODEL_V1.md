# GM LITE Algorithmic Skillization Model v1

## 核心结论
- `算法 Skill 化` 是 `GM-LITE -> SkillForge` 这条路上非常关键的一层
- 普通 Skill 更像手脚，算法 Skill 更像可复用的 `大脑插件`
- 它的意义不是多一个文件夹，而是把散落的数学逻辑升级为：
  - 可调用
  - 可审计
  - 可版本化
  - 可冻结
  - 可回放
  的工业标准件

## 为什么必须 Skill 化

### 1. 空间维度：原子化
- 余弦相似度
- 仿射矩阵
- 哈希链
- 贝叶斯一致性判断
- 各种算法若散落在代码里，就只是脆弱逻辑片段
- 一旦封装成 Skill，就成为标准化原子部件

### 2. 时间维度：版本化
- `Skill_Reflection_v1`
- `Skill_Reflection_v2`
- `Skill_Math_VectorAlign_v1`
- `Skill_Light_Physics_v1`
- 算法可以独立演进、独立回滚，不必把整条主线一起推翻

### 3. 价值维度：冻结
- 一个算法一旦通过大量 replay 验证，就不应只存在于脚本里
- 它应被视为 `确定性资产`
- 只有被封存为标准 Skill，后续项目才能真正复利调用

## 与 SkillForge 的关系
- `GM-LITE` 负责：
  - 生成
  - 验证
  - 打勾
  - 门禁
  - 最小运行脉络
- `SkillForge` 负责：
  - 算法资产化
  - L3 五层审计
  - 工业级封装
  - 长期复用与沉淀

因此：

> `算法 Skill 化` 是 `GM-LITE` 输出能力向 `SkillForge` 资产体系沉积的关键接口层。

## 推荐落地路径：骨架 -> 算法 -> Skill

### 第一阶段：骨架搭建
- 先在现有 gate / runtime 骨架里写最小可跑逻辑
- 例如：
  - `if-else`
  - 字符串匹配
  - 简单阈值判断
- 目标：
  - 跑通权威树
  - 跑通状态推进
  - 跑通 CLI / checkpoint / redline / recovery
- 这一步优先确保：
  - 空间感成立
  - 时间感成立

### 第二阶段：算法植入与测试
- 在 gate 内部直接植入算法原型
- 例如先在 `M6` 内部直接接入：
  - `semantic_score`
  - 向量比对
  - 黄灯分支
  - 偏移补偿
  - 逻辑保险丝
- 目标：
  - 观察算法在真实意图上的表现
  - 通过 `1/2/3` CLI 做压力测试
  - 找到稳定阈值和稳定行为
- 这一步优先确保：
  - 准心成立
  - 阈值可信
  - 自愈不失控

### 第三阶段：Skill 化结晶
- 当算法在足够多的样板测试中稳定后，再从具体 gate 中剥离
- 形成标准算法 Skill：
  - `logic.py`
  - `manifest.json`
  - `replay_proof.bin`
- 目标：
  - 解耦
  - 复用
  - 版本化
  - 资产冻结
- 这一步优先确保：
  - 价值感成立
  - 资产可沉淀

## 为什么不能一开始就直接写 Skill
- 容易过度封装
- 容易在真实 gate 行为没稳定前就冻结错误抽象
- 容易把本该靠样板链验证的东西提前做成“看起来很完整”的资产

因此：

> 正确路径不是“先 Skill 后验证”，
> 而是“先在骨架里打样，再通过炮火验证，最后结晶成 Skill”。

## 物理结构建议

### logic.py
- 角色：
  - 算法内核
- 内容：
  - 纯数学或纯逻辑实现
- 要求：
  - 尽量无副作用
  - 可单测
  - 可独立 replay

### manifest.json
- 角色：
  - 输入输出协议
- 内容：
  - 输入类型
  - 输出类型
  - 维度约束
  - 版本
  - 依赖
  - 阈值
  - replay 要求

### replay_proof.bin
- 角色：
  - 确定性证据
- 内容：
  - 标准数据集回放指纹
  - 哈希摘要
  - 一致性证明

## 候选算法 Skill 样式

### Skill_Math_VectorAlign
- 用途：
  - 余弦相似度
  - 向量对齐
  - 语义偏移检测
- 典型来源：
  - `M6` 语义对齐打样成熟后剥离

### Skill_Reflection
- 用途：
  - 偏移补偿
  - 重试反思注入
  - 失败现场重构

### Skill_Affine_Transform
- 用途：
  - 平移
  - 缩放
  - 旋转
  - 坐标锚点一致性

### Skill_Light_Physics
- 用途：
  - 光比估计
  - 衰减近似
  - 散射近似

## 进入 Skill 化前的最低门槛
- 已经有明确 `logic.py`
- 已经有结构化 `manifest.json`
- 已经有最小 replay 样板
- 已经通过至少一轮样板回放或 deterministic smoke
- 不依赖主控官临时解释才能运行

## 当前主线中的定位
- 这不是当前 `插件外壳 + 手动转递消失` 主线里的插队项
- 它更适合被定义为：
  - `后续资产化主线`
  - `GM-LITE 与 SkillForge 汇流主线`

## 当前样板锚点
- `M6` 是第一块最适合进行算法 Skill 化打样的样板位
- 推荐演进顺序：
  1. `M6` 内部先跑通阈值与 CLI
  2. 在真实样板中做若干轮验证
  3. 稳定后再剥离为 `Skill_VectorAlign`

## 建议归属的未来主线
- `gm_lite_algorithmic_skillization_preparation_v1`
- 或：
  - `skillforge_algorithm_asset_bridge_v1`

## 主控官结论
- 算法 Skill 化不是可有可无的美化
- 它是从“代码可跑”迈向“资产可沉淀”的关键台阶
- 当前先归档为未来主线，不插队当前插件壳战线
