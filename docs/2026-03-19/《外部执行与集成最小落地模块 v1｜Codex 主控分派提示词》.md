你现在进入同一个项目的下一模块。

你的角色不是主力实现者，而是：

- 主控者
- 拆分者
- 分派者
- 回收者
- 验收者

AI 军团负责具体落实。
你（Codex）负责：
- 冻结模块边界
- 拆分任务
- 分派任务
- 回收结果
- 审查与合规检查
- 最终验收
- 输出模块报告

==================================================
一、模块名称
==================================================

外部执行与集成最小落地模块 v1

==================================================
二、当前前置状态（视为既定前提，不得回退）
==================================================

以下状态已经成立，必须视为冻结前提：

- Production Chain v0 Frozen = true
- Bridge Draft v0 Frozen = true
- Bridge Minimal Implementation v0 Frozen = true
- Governance Intake Minimal Implementation v0 Frozen = true
- Gate Minimal Implementation Frozen = true
- Review Minimal Implementation Frozen = true
- Release Minimal Implementation Frozen = true
- Audit Minimal Implementation Frozen = true
- 系统执行层准备模块 v1 = completed
- 系统执行层最小落地模块 v1 = completed
- 系统执行层 Frozen 判断模块 v1 = completed
- System Execution Minimal Landing Module v1 Frozen = true
- 外部执行与集成准备模块 v1 = completed

说明：
对象主线、治理主线、system_execution 主线、外部执行与集成准备模块，已经完成到当前目标层级。
本模块不是回头修对象层，不是回头做治理主线，不是回头做 system_execution，也不是重做准备模块。

本模块是在已冻结主线与已完成准备模块之上，进入：

- 外部执行与集成最小落地模块 v1

==================================================
三、本模块唯一目标
==================================================

本模块唯一目标只有一个：

- 在不破坏 frozen 主线的前提下，把外部执行与集成层做出“最小可承接、最小可落位、最小可验收”的内部落地骨架

这里的“外部执行与集成层”在本模块内只覆盖以下子面：

1. connector contract
2. integration gateway
3. secrets / credentials boundary
4. external action policy
5. retry / compensation boundary
6. publish / notify / sync boundary

这里的“最小落地”只包括：

- 六子面的最小目录/文件落位
- 六子面的最小职责承接
- frozen 主线产物与 system_execution 的只读承接路径
- permit 在外部动作中的最小承接路径
- Evidence / AuditPack / decision 的不可变承接规则
- 最小接口连接关系
- 最小导入/连接级验收
- 文档、报告、变更控制规则更新

本模块不包括：

- runtime
- 真实外部系统联调
- 真实 webhook / queue / db / registry / slack / email / repo 接入
- 自动重试补偿实现
- 真实发布执行
- 外部 API 调用实装
- 真正业务长链执行
- 反向改写 gate / review / release / audit 的 frozen 边界

==================================================
四、你（Codex）的职责
==================================================

你在本模块中的职责只有以下几项：

1. 冻结本模块边界
2. 拆分子任务
3. 把子任务分派给 AI 军团
4. 跟踪每个子任务的完成状态
5. 回收各子任务产物
6. 做统一结构审查与边界审查
7. 做最终验收
8. 给出“通过 / 局部退回 / 整体退回”结论
9. 生成模块总报告

你不得做的事情：

- 不得默认自己直接写完整模块
- 不得绕过 AI 军团直接吞掉所有实现
- 不得边分派边偷偷扩模块
- 不得让任一子任务越界进入 runtime
- 不得让任一子任务接入真实外部系统
- 不得让任一子任务改写 frozen 主线
- 不得让编排/集成层成为裁决层

如果你发现某个子任务需要你亲自写入，也只能做：
- 极小补丁
- 命名修正
- 导出修正
- 非语义性整合

不得用“整合”名义代替整个子任务的主实现。

==================================================
五、AI 军团职责
==================================================

AI 军团负责具体落实工作。

AI 军团只能在你分配的明确任务边界内推进，负责：

- 目录落位
- 文件骨架
- 最小接口草案
- 最小连接规则草案
- permit 承接骨架
- Evidence / AuditPack 只读承接骨架
- 文档更新
- 模块报告内容起草

AI 军团不得：

- 自行扩模块
- 自行进入 runtime
- 自行接入真实外部系统
- 自行改 frozen 主线
- 自行宣布模块完成
- 自行改变验收标准
- 自行让外部动作绕过 permit
- 自行让外部层修改 Evidence / AuditPack

==================================================
六、本模块边界
==================================================

### 允许进入的范围

只允许进入以下范围：

- connector contract 最小落地
- integration gateway 最小落地
- secrets / credentials boundary 最小落地
- external action policy 最小落地
- retry / compensation boundary 最小落地
- publish / notify / sync boundary 最小落地
- 上述子面与 system_execution 的承接关系
- permit / evidence / audit pack / decision 在外部动作中的只读承接规则
- “外部执行层只能持 permit 行动，不能自行裁决”的规则落地
- “Evidence / AuditPack 由内核生成且不可改写”的规则落地
- 最小目录骨架
- 最小接口骨架
- 最小导入与连接检查

### 禁止进入的范围

本模块一律禁止进入：

- Gate / Review / Release / Audit 对象返修
- system_execution 返修
- runtime 执行层
- 真实外部系统接入
- webhook / queue / registry / db / slack / email / repo 的真实联调
- 真实业务执行逻辑
- 自动重试补偿实现
- 真实发布执行
- 任何会倒灌 frozen 主线边界的改动
- 任何让编排/集成层替代 Governor 裁决的设计

==================================================
七、六个子任务面
==================================================

你必须把本模块拆成以下六个子任务面，并分别交给 AI 军团推进：

### 子任务面 A：connector contract 最小落地
目标：
- 落地 connector contract 子面的最小目录骨架
- 明确外部连接合同只描述输入/输出/约束，不承载裁决
- 明确 connector contract 与 integration gateway 的接口边界
- 明确不接入真实外部系统

必须产出：
- connector contract 子面文件/目录骨架
- connector contract 职责文档
- connector contract 与其余子面的连接说明

### 子任务面 B：integration gateway 最小落地
目标：
- 落地 integration gateway 子面的最小目录骨架
- 明确 gateway 只做外部连接承接与转发，不做裁决
- 明确 gateway 与 system_execution / connector / action policy 的边界
- 明确 gateway 不得成为真实联调实现层

必须产出：
- integration gateway 子面文件/目录骨架
- integration gateway 职责文档
- integration gateway 接口连接说明

### 子任务面 C：secrets / credentials boundary 最小落地
目标：
- 落地 secrets / credentials boundary 子面的最小目录骨架
- 明确 secrets 分层，不与 Evidence / AuditPack 混用
- 明确凭证只作为接入边界说明，不做真实配置接线
- 明确凭证层不改写治理证据

必须产出：
- secrets / credentials boundary 子面文件/目录骨架
- secrets 分层规则文档
- secrets 与其余子面的边界说明

### 子任务面 D：external action policy 最小落地
目标：
- 落地 external action policy 子面的最小目录骨架
- 明确哪些外部动作必须持 permit
- 明确 publish / notify / sync / tombstone 类动作的最小策略边界
- 明确外部动作不能自行判 PASS / FAIL

必须产出：
- external action policy 子面文件/目录骨架
- permit 使用规则文档
- external action policy 边界说明

### 子任务面 E：retry / compensation boundary 最小落地
目标：
- 落地 retry / compensation boundary 子面的最小目录骨架
- 明确这里只做边界与接口，不做真实补偿实现
- 明确 retry / compensation 不得绕过 permit 与 evidence 规则
- 明确后续 runtime 才能真正接管执行策略

必须产出：
- retry / compensation boundary 子面文件/目录骨架
- retry / compensation 边界文档
- 与 runtime 的排除说明

### 子任务面 F：publish / notify / sync boundary 最小落地
目标：
- 落地 publish / notify / sync boundary 子面的最小目录骨架
- 明确发布、通知、同步动作都属于受 permit 约束的外部动作承接层
- 明确这里只做最小承接骨架，不做真实发布
- 明确 publish / notify / sync 不得篡改 AuditPack / Evidence / decision

必须产出：
- publish / notify / sync boundary 子面文件/目录骨架
- publish / notify / sync 职责文档
- 与其余子面的连接说明

==================================================
八、统一约束
==================================================

六个子任务面必须统一遵守以下约束：

1. 只能只读承接 frozen 主线
2. 只能只读承接 system_execution frozen
3. 不得改写 frozen 对象
4. 不得让外部执行层成为裁决层
5. 关键动作必须依赖 permit
6. Evidence / AuditPack 不可被外部执行层改写
7. 不得进入 runtime
8. 不得接入真实外部系统
9. 不得实现真实业务逻辑
10. 所有产物必须可被统一验收

==================================================
九、Codex 的分派动作要求
==================================================

你必须先做任务分派，而不是直接编码。

你必须输出并维护以下内容：

1. 模块任务总表
2. 六个子任务面的负责人/执行单元
3. 每个子任务面的目标
4. 每个子任务面的禁止项
5. 每个子任务面的交付物
6. 每个子任务面的状态：
   - 未开始
   - 进行中
   - 待审查
   - 待合规
   - 待验收
   - 通过
   - 退回

你必须先把任务分出去，再回收结果。

==================================================
十、审查与合规
==================================================

你必须对 AI 军团回收的产物进行两类检查：

### A. 结构审查
检查：
- 目录是否清晰
- 命名是否一致
- 六子面职责是否重叠
- 六子面职责是否断裂
- 接口连接是否自洽
- 文档与骨架是否一致

### B. 边界合规审查
检查：
- 是否倒灌 frozen 主线
- 是否倒灌 system_execution
- 是否提前进入 runtime
- 是否接入真实外部系统
- 是否让外部执行层成为裁决层
- 是否让 permit 规则失效
- 是否让 Evidence / AuditPack 可被改写
- 是否扩大模块范围

==================================================
十一、本模块固定交付物
==================================================

本模块最终必须至少产出以下内容：

### 正式文档
1. EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_SCOPE.md
2. EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_BOUNDARY_RULES.md
3. EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_TASK_BOARD.md
4. EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_ACCEPTANCE.md
5. EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_REPORT.md
6. EXTERNAL_EXECUTION_AND_INTEGRATION_MINIMAL_LANDING_MODULE_V1_CHANGE_CONTROL_RULES.md

### 六个子面最小落地骨架
7. connector contract 子面最小骨架
8. integration gateway 子面最小骨架
9. secrets / credentials boundary 子面最小骨架
10. external action policy 子面最小骨架
11. retry / compensation boundary 子面最小骨架
12. publish / notify / sync boundary 子面最小骨架

### 最小验收
13. 轻量导入/结构级验收结果
14. 子任务级问题清单
15. 模块级通过/退回结论

==================================================
十二、验收标准
==================================================

你必须按以下标准验收，不能主观发挥。

### 通过标准（全部满足才可通过）

1. 六个子任务面都有最小职责定义
2. 六个子任务面都有清晰不负责项
3. 六个子任务面之间关系清晰，无明显重叠/断裂
4. 与 frozen 主线承接关系清晰
5. 与 system_execution 承接关系清晰
6. permit 使用规则清晰
7. Evidence / AuditPack 不可变承接规则清晰
8. 未回改任何 frozen 对象边界
9. 未混入 runtime 语义
10. 未接入真实外部系统
11. 未让集成层成为裁决层
12. 已形成正式文档 1–6
13. 若有目录/文件骨架，则与文档口径一致
14. 无阻断性越界问题

### 退回标准（任一触发即退回）

1. 任一子任务面进入 runtime
2. 任一子任务面接入真实外部系统
3. 任一子任务面要求改写 frozen 对象
4. permit 规则不清或可绕过
5. Evidence / AuditPack 可被改写
6. 六个子任务面职责冲突明显
7. 文档口径与实际骨架不一致
8. 存在阻断性边界问题
9. 交付物不完整

### 局部修正后再审
如果只存在：
- 命名问题
- 注释问题
- 轻微结构不一致
- 文档缺一小节
- 导出链轻微缺口

允许局部修正后再审，不必整体退回。

==================================================
十三、自动暂停条件
==================================================

出现以下任一情况，必须自动暂停，并停止继续推进：

1. 任何一方开始要求修改 frozen 对象
2. 任何一方开始把外部执行层写成裁决层
3. 任何一方开始进入 runtime
4. 任何一方开始接入真实外部系统
5. 任何一方开始实现真实业务逻辑
6. 任何一方开始绕过 permit 规则
7. 任何一方开始让 Evidence / AuditPack 可变
8. 执行单元 / 审查 / 合规发生角色混线
9. Codex 试图绕过分派直接宣布完成

触发暂停时，必须输出：
- 触发了哪条暂停条件
- 哪个子任务面出了问题
- 应退回到哪个边界

==================================================
十四、执行顺序
==================================================

Codex 必须按以下顺序推进：

第一步：
- 读取本任务包
- 冻结模块边界
- 冻结子任务边界
- 冻结验收标准

第二步：
- 输出子任务拆分清单
- 给 AI 军团分派并行任务

第三步：
- 汇总回收结果
- 标注阻断性问题 / 非阻断性问题

第四步：
- 执行必要的局部修正回合（如有）
- 但不得扩模块

第五步：
- 按验收标准做最终判断
- 输出正式文档
- 输出模块报告
- 输出 change control rules

==================================================
十五、最终执行口径
==================================================

你现在不是在做一个小功能。
你现在是在做：

- 外部执行与集成层的第一个最小落地模块

你的目标不是直接把外部执行层做完。
你的目标是：

- 在不破坏 frozen 主线与 system_execution frozen 边界的前提下
- 建立外部执行与集成层的第一块可审查、可并行、可验收的最小落地骨架
- 并为后续模块推进建立稳定的 permit / evidence / audit pack / integration 分层模式

只要超出这个目标，就算越界。

现在开始执行。