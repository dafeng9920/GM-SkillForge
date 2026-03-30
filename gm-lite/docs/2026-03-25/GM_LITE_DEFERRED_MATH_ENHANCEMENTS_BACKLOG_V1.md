# GM LITE Deferred Math Enhancements Backlog v1

## 目的
- 记录已识别、但当前 **不纳入主线** 的数学/算法增强项
- 防止因为主线聚焦于 `插件外壳 + 手动转递消失` 而遗忘后续高价值增强
- 为未来 `视觉域 / 本地门禁增强 / 资产封印强化 / Studio Backend` 留存清晰入口

## 当前原则
- 这些内容 **不是被否定**
- 只是当前阶段 **后置**
- 后置原因只有一个：
  - 先保障 `作战运行级 1`

## 后置增强清单

### 1. 贝叶斯一致性采样
- 目标：
  - 在终极审计或封印阶段，通过多次采样估计一致性概率
- 候选形式：
  - `P(consistency | sample_runs) > threshold`
- 未来用途：
  - `M9` 终极审计
  - 样板回放的统计一致性证明
  - 镜像封印前的后验置信度判定
- 当前不前置原因：
  - 还没到需要多次采样封印的阶段
  - 当前主线更需要打通产品壳和桥接壳

### 2. 仿射矩阵坐标系统
- 目标：
  - 用 `Affine Matrix` 统一平移、缩放、旋转
- 未来用途：
  - 须弥芥子类微观生成
  - 多层递归切片的坐标对齐
  - gap-free 拼接
  - 视觉分块 / 九宫格 / 81 地块对齐
- 当前不前置原因：
  - 这属于未来视觉域 / Studio Backend
  - 不直接服务当前插件壳与手动转递消失

### 3. Monte Carlo 光比/散射简化模型
- 目标：
  - 让光线、衰减、散射不再纯靠模型猜
- 未来用途：
  - 摄影棚后端
  - 光比计算
  - 物理正确性约束
- 当前不前置原因：
  - 当前主线不是图像生成质量控制

### 4. Hilbert Curve / 空间填充索引
- 目标：
  - 处理高层递归切片时的唯一连续索引
- 未来用途：
  - 分形逻辑
  - 切片地址空间压缩
  - 防止递归路径混乱和索引丢失
- 当前不前置原因：
  - 当前主线还没有进入高层级分形生成 runtime

### 5. 本地语义模型实体化部署
- 候选模型：
  - `paraphrase-MiniLM-L3-v2`
- 未来用途：
  - `semantic_score(a, b)` 的本地实现
  - reverse echo 粗筛
  - noun anchors 语义审计
- 当前不前置原因：
  - 当前先冻结接口，不强绑模型下载和本地模型管理

### 6. 算法 Skill 化
- 目标：
  - 将数学/逻辑核心封装成可调用、可审计、可冻结的标准 Skill
- 候选结构：
  - `logic.py`
  - `manifest.json`
  - `replay_proof.bin`
- 推荐落地路径：
  - `骨架 -> 算法植入 -> 稳定验证 -> Skill 化结晶`
- 未来用途：
  - 语义对齐算法标准件
  - 反思/补偿算法标准件
  - 仿射坐标标准件
  - 光影物理标准件
- 当前不前置原因：
  - 当前主线还在冲插件外壳与手动转递消失
  - 算法资产化更适合在 `GM-LITE -> SkillForge` 汇流阶段启动

## 建议归属的未来主线

### A. 本地门禁增强线
- 候选模块：
  - `qwen_local_gate_integration_preparation_v1`
  - `gm_lite_local_semantic_audit_minimal_implementation_v1`
- 可吸收：
  - 本地语义模型
  - `semantic_score`
  - 轻量贝叶斯/一致性统计
  - 本地 7B 副官的全局建议层

### A2. M5 预审与全局建议线
- 候选模块：
  - `gm_lite_m5_prefight_advisory_preparation_v1`
- 可吸收：
  - 冲突预警
  - 资产复用建议
  - 架构债提醒
  - `summary + current_step` 驱动的全局态势建议

### B. 蓝图/封印增强线
- 候选模块：
  - `gm_lite_blueprint_integrity_hardening_v1`
- 可吸收：
  - 哈希链增强
  - 终极封印一致性证明

### C. Studio / 视觉后端线
- 候选模块：
  - `gm_lite_studio_backend_math_preparation_v1`
  - `gm_lite_fractal_generation_support_v1`
- 可吸收：
  - 仿射矩阵
  - Monte Carlo
  - Hilbert Curve

### D. 算法资产化汇流线
- 候选模块：
  - `gm_lite_algorithmic_skillization_preparation_v1`
  - `skillforge_algorithm_asset_bridge_v1`
- 可吸收：
  - 算法 Skill 化
  - replay proof
  - 算法版本化与冻结

## 与当前主线的关系
- 当前主线：
  - 插件外壳成立
  - 手动转递开始消失
- 后置数学增强：
  - 不插队
  - 不抢主线
  - 只在未来对应能力线成熟时接入

## 主控官结论
- 这些增强都是 `高价值储备`
- 现在先归档，不让它们污染主线节奏
- 等 `作战运行级 1` 打通后，再按能力线逐个接入
