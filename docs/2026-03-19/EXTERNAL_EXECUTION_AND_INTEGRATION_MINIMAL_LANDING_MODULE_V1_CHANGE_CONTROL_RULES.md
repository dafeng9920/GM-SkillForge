# 外部执行与集成最小落地模块 v1 Change Control Rules

## 本阶段允许变更范围
- 六个子面内的最小目录与文件骨架
- 最小接口占位
- 最小连接规则说明
- permit / evidence / audit pack 的只读承接说明
- 模块级文档、任务板、报告

## 本阶段禁止变更范围
- frozen 主线对象与文档
- `system_execution` frozen 资产
- runtime
- 真实外部系统接入
- 自动重试补偿实现
- 真实发布执行
- 任何裁决逻辑

## 已冻结层保护规则
- Production Chain / Bridge / Governance Intake / Gate / Review / Release / Audit 全部只读
- `system_execution` 全部只读

## 六子面变更控制规则
- connector contract / integration gateway / secrets / action policy / retry boundary / publish boundary 只能做最小落地
- 任何新增逻辑不得越过 permit
- 任何新增结构不得使 Evidence / AuditPack 可变

## 下一阶段前不得触碰的实现面
- runtime 调度
- 真实 API / webhook / queue / db / repo / slack / email 联调
- 真实业务副作用动作

