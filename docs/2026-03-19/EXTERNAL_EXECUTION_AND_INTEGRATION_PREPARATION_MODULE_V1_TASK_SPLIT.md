# 外部执行与集成准备模块 v1 任务拆分

## 模块结构
- 一个模块
- 六个子面
- 统一验收

## 子任务清单

### E1 connector contract
- 目标：定义 connector contract 的最小职责、接口承接、permit/evidence 的引用规则
- 执行者：`vs--cc1`
- 审查者：`Kior-A`
- 合规官：`Kior-C`
- 执行关系：`并行`

### E2 integration gateway
- 目标：定义 integration gateway 的最小职责、与 `system_execution` 的连接边界、不得裁决规则
- 执行者：`Antigravity-1`
- 审查者：`vs--cc3`
- 合规官：`Kior-C`
- 执行关系：`并行`

### E3 secrets / credentials boundary
- 目标：定义 secrets / credentials 的最小分层、最小承接、最小泄露防护边界
- 执行者：`Antigravity-2`
- 审查者：`Kior-A`
- 合规官：`Kior-C`
- 执行关系：`并行`

### E4 external action policy
- 目标：定义外部动作分类、permit 使用条件、Evidence/AuditPack 引用规则
- 执行者：`Kior-B`
- 审查者：`vs--cc1`
- 合规官：`Kior-C`
- 执行关系：`串行，依赖 E1/E2/E3 输出`

### E5 retry / compensation boundary
- 目标：定义 retry / compensation 只停留在边界说明，不进入真实补偿实现
- 执行者：`vs--cc3`
- 审查者：`Kior-A`
- 合规官：`Kior-C`
- 执行关系：`串行，依赖 E2/E4 输出`

### E6 publish / notify / sync boundary
- 目标：定义 publish / notify / sync 的最小边界，明确必须持 permit，且不得触发真实动作
- 执行者：`Antigravity-1`
- 审查者：`vs--cc1`
- 合规官：`Kior-C`
- 执行关系：`串行，依赖 E4/E5 输出`

## 并行 / 串行规则

### 第一波并行
- E1 connector contract
- E2 integration gateway
- E3 secrets / credentials boundary

### 第二波串行
- E4 external action policy
  - 依赖：E1 + E2 + E3

### 第三波串行
- E5 retry / compensation boundary
  - 依赖：E2 + E4
- E6 publish / notify / sync boundary
  - 依赖：E4 + E5

## 统一回收要求
- 六个子面都必须回收到 `execution / review / compliance`
- Codex 只在六个子面回收完成后做统一终验
