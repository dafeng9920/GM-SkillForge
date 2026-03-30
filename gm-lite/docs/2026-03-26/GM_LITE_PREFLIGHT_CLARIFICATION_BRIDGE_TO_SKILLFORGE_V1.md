# GM LITE Preflight Clarification Bridge To SkillForge v1

## 定位
- 本文件用于定义：如何把 `SkillForge` 中已有的前置需求澄清、方案比较、任务拆细能力，合并优化后回挂到 `GM-LITE` 入口端
- 它不是当前主线插队模块
- 它是后置启动的入口增强制度件

## 为什么放在 GM-LITE
- `GM-LITE` 是入口
- `SkillForge` 是后段审计、固化、资产沉淀
- 前置需求澄清天然应放在入口侧
- 后期两者汇成一条主线时，该能力仍然位于前段，不会与 `SkillForge` 后段职责冲突

## 在 SkillForge 中已发现的可吸收素材

### 1. 需求澄清与 intent 合同化
来源：
- [L4.5 启动清单 v2（2026-02-20）.md](/d:/GM-SkillForge/docs/2026-02-20/L4.5%20%E5%90%AF%E5%8A%A8%E6%B8%85%E5%8D%95%20v2%EF%BC%882026-02-20%EF%BC%89.md)

可吸收点：
- 开放窗口中的需求澄清
- intent 合同化
- 从开放输入到蓝图包生成的前置收敛

### 2. 10 阶结构化蓝图
来源：
- [L4.5 启动清单 v2（2026-02-20）.md](/d:/GM-SkillForge/docs/2026-02-20/L4.5%20%E5%90%AF%E5%8A%A8%E6%B8%85%E5%8D%95%20v2%EF%BC%882026-02-20%EF%BC%89.md)

可吸收点：
- 理解
- 拆解
- 计划
- 依赖
- 风险
- 验收

### 3. 方案 A/B/C 比较模板
来源：
- [FRONTEND_REQUIREMENTS_v1.md](/d:/GM-SkillForge/docs/2026-02-20/FRONTEND_REQUIREMENTS_v1.md)

可吸收点：
- 方案比较表
- 推荐度
- 选定方案冻结
- 方案评审模板

### 4. SPEC / TASKS 显式产物意识
来源：
- [L4.5 启动清单 v2（2026-02-20）.md](/d:/GM-SkillForge/docs/2026-02-20/L4.5%20%E5%90%AF%E5%8A%A8%E6%B8%85%E5%8D%95%20v2%EF%BC%882026-02-20%EF%BC%89.md)

可吸收点：
- `SPEC.md`
- `TASKS.md`
- 把前置澄清结果固化为可执行对象

## 来自外部文章、但值得吸收的增强包
- 深度前置需求澄清
- 苏格拉底式递进追问
- 先方案比较，再进实现
- 任务拆到普通执行者也不容易跑偏

## 吸收原则
- 不替换 `GM-LITE` 的 bus / gate / runtime / evidence 主骨架
- 只把前置需求澄清、方案比较、任务拆细作为入口增强层
- 不把 `GM-LITE` 拉回单纯 workflow 插件

## 未来落地方向
- 建议后续单独起：
  - `gm_lite_preflight_clarification_preparation_v1`

## 建议职责
### GM-LITE 前段
- 原始意图澄清
- 边界追问
- A/B/C 方案比较
- SPEC / TASKS 前置固化
- 进入 bus 前的入口整形

### SkillForge 后段
- 深审计
- 固化
- 收编为 Skill 资产
- 版本治理

## 启动条件
- 当前主线优先级：
  - 插件本地安装可用
  - observability 边界与实现
- 上述主线稳定后，再后置启动前置澄清入口增强
