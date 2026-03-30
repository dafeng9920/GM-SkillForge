# GM-LITE 隐性依赖发现模型 V1

## 1. 核心问题

工业化 AI 生产里，最危险的不是“已知的未知”，而是：

> 不召唤就不出现、但不出现系统就跑不满血的隐性依赖。  

也就是：

- A 表面上是一个独立任务
- 实际上依赖 B 的数据引擎
- 依赖 C 的过滤逻辑
- 遵循 D 的规则
- 最终还要喂给 E 做回测或下游消费

如果只把 A 单独交给模型，模型极容易生成一个“孤岛版 A”。

---

## 2. 总体原则

GM-LITE 必须把“召唤隐藏依赖”这件事从偶然行为，升级成制度行为。

也就是同时依靠：

1. 静态雷达
2. 强迫质询
3. 宪法锚点
4. 运行时探测

---

## 3. 语义雷达：Global Scan

### 3.1 目标

在 `RAW -> ENRICHED` 之前，不只盯着当前任务 A 看，而要自动扫描：

- `SkillForge` 资产库
- `.gm-lite/skills/`
- 现有代码库
- 现有 Spec / Contract

### 3.2 最小做法

BusManager 或其前置入口执行一次：

- `global_scan`

输入：

- `raw_intent`
- `explicit_nouns`
- `goal_statement`

输出：

- 与现有组件、Skill、Spec 的关联候选

建议字段：

- `global_scan_matches`
- `related_skill_refs`
- `related_spec_refs`
- `related_interface_refs`

### 3.3 作用

如果系统发现：

- A 与 B 的接口高度相关
- A 与 C 的过滤逻辑高度相关

则应自动把这些对象的接口规范或合同摘要注入任务包，作为：

- `shadow_context_refs`

而不是让 A 在真空里生长。

---

## 3.4 Intent Resonance Radar

`global_scan` 在后续增强版中，可以升级为：

- `intent_resonance_radar`

它的目标不是只做一次静态检索，而是对任务 A 周边的“电子云”做 360° 语义扫描。

### 四个扫描维度

#### 1. 静态资产扫描 `Static Asset Ping`

问题：

- “我的邻居是谁？”

动作：

- 扫描 `.gm-lite/skills/`
- 扫描现有代码库
- 扫描已有 Spec / Contract / Interface 资产

如果 A 提到：

- `K线`

则系统应锁定所有带相关标签、接口或逻辑骨架的旧 Skill / Spec。

建议字段：

- `neighbor_skill_refs`
- `neighbor_spec_refs`
- `neighbor_constraint_refs`

#### 2. 负向空间质询 `Negative Space Inquiry`

问题：

- “我缺了什么？”

动作：

- 强制围绕边缘场景发问

典型质询方向：

- 左舷：输入数据断流怎么办？
- 右舷：输出目标满载怎么办？
- 上方：全局配置变化怎么办？
- 下方：底层系统报错怎么办？

建议字段：

- `negative_space_questions`
- `negative_space_findings`

#### 3. 影子拓扑预测 `Shadow Topology Prediction`

问题：

- “我未来会遇到谁？”

动作：

- 根据现有 SkillForge 全局拓扑、接口模式和组件关系，预测 A 的下游耦合对象

如果 A 是：

- `清洗逻辑`

则系统应预测它大概率会遇到：

- 存储逻辑
- 可视化逻辑
- 回测逻辑

建议字段：

- `predicted_downstream_refs`
- `predicted_interface_hooks`

#### 4. 上下文注入确认 `Context Injection Confirmation`

问题：

- “我是否真的把 BCDEFG 纳入考虑了？”

动作：

- 将雷达扫描出的邻居、缺口、未来耦合对象注入任务包
- 再让上游模型确认已感知这些对象

建议字段：

- `context_environment`
- `context_injection_confirmed`

---

## 4. 强迫式全局质询

### 4.1 目标

利用一个“挑刺型角色”在 `ENRICHED` 生成前逼模型交代：

- 数据从哪里来
- 错误由谁接
- 结果写到哪里
- 依赖谁的协议

### 4.2 角色建议

可定义一个预研型角色：

- `global_interrogator`

它的职责只有一个：

- 列出当前任务的隐藏依赖清单

### 4.3 最低要求

若任务复杂度中等及以上，`global_interrogator` 至少必须提出：

- 3 个隐藏依赖问题

如果上游模型答不上来，则：

- 状态锁死在 `RAW`
- 不允许推进到 `ENRICHED`

建议字段：

- `hidden_dependency_questions`
- `hidden_dependency_answers`
- `hidden_dependency_gaps`

---

## 5. 宪法级显性锚点

### 5.1 目标

对于某些类型的任务，不能等模型“想起来”它依赖什么，而应由宪法强制声明：

- A 类任务必须显式引用 B 框架
- A 类任务必须显式遵循 C 规则

### 5.2 实现方式

在：

- `constitution/`
- `rules/`

中定义：

- `base_layer_declaration`

建议字段：

- `mandatory_base_layers`
- `required_global_contracts`

### 5.3 效果

当 A 类任务生成元数据时，BusManager 自动检查：

- 是否包含这些必选隐藏项

若没有：

- 自动补全
- 或打回要求上游模型重写

---

## 6. 动态发现：运行时探测针

### 6.1 目标

利用 Python/脚本层验证的红利，在运行时把隐藏依赖从“潜伏”状态拉出来。

### 6.2 最小做法

在验证执行过程中挂一个最小探测器：

- `runtime_dependency_trace`

捕获：

- 未定义变量
- 缺失环境配置
- 缺失依赖模块
- 缺失接口协议
- 未声明外部资源访问

### 6.3 回流规则

一旦发现 Missing Link：

- 不只是修代码
- 必须回写到元数据层

建议字段：

- `runtime_missing_links`
- `dependency_trace_log`
- `metadata_patch_required`

---

## 7. 与 M6 / M7 的关系

### M6：入口防火墙

应新增一个：

- `global_scan`

让系统在 `RAW -> ENRICHED` 之前先扫现有资产与接口邻居。

### M7：分级路由

应能根据 `global_scan` 和 `hidden_dependency_gaps` 的结果决定：

- 直接驳回
- 先补元数据
- 还是进入执行层

也就是说：

> 不是所有 RAW 都有资格直接进入昂贵齐射。  

---

## 8. 对 BusManager 的直接约束

后续 `gm_bus_manager_seed_implementation_v1` 或其后续增强中，至少应预留以下字段：

- `global_scan_matches`
- `related_skill_refs`
- `related_spec_refs`
- `related_interface_refs`
- `shadow_context_refs`
- `neighbor_skill_refs`
- `neighbor_spec_refs`
- `neighbor_constraint_refs`
- `hidden_dependency_questions`
- `hidden_dependency_answers`
- `hidden_dependency_gaps`
- `negative_space_questions`
- `negative_space_findings`
- `mandatory_base_layers`
- `required_global_contracts`
- `predicted_downstream_refs`
- `predicted_interface_hooks`
- `context_environment`
- `context_injection_confirmed`
- `runtime_missing_links`
- `dependency_trace_log`
- `metadata_patch_required`

---

## 9. 当前结论

本文件正式冻结以下判断：

1. 隐性依赖发现必须成为系统能力，而不是靠模型偶然想起
2. `global_scan` 应成为 `RAW -> ENRICHED` 前的建议性默认步骤
3. `global_interrogator` 适合作为强迫式全局质询角色
4. 宪法层应允许声明某类任务的强制底座依赖
5. 运行时 Missing Link 必须回流到元数据层，而不是只在代码层修补
6. `intent_resonance_radar` 是 `global_scan` 的增强版，可作为后续 M6 入口预处理序列
