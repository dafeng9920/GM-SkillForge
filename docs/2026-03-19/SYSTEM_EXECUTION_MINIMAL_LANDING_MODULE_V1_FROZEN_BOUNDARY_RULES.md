# 系统执行层 Frozen 判断模块 v1 边界规则

## 主控规则
- Codex 只负责冻结边界、拆分任务、分派任务、回收结果、统一审查与最终验收。
- Codex 不直接重写最小落地模块，不绕过 AI 军团直接宣布 Frozen 成立。

## Frozen 判断边界
- 只判断 `workflow / orchestrator / service / handler / api`
- 只判断目录、骨架、职责、边界、导入/连接级验收
- 不进入 runtime / 外部执行 / 集成 / 真实业务逻辑

## 三权分立规则
- Execution：整理冻结依据、核对骨架与文档、起草规则草案
- Review：检查结构、命名、职责和文档一致性
- Compliance：按 B Guard 做边界硬审，有一票否决权
- Codex：只做统一终验与最终结论

## 自动暂停条件
- 任一方要求修改 frozen 主线
- 任一方要求补 runtime
- 任一方要求补外部执行 / 集成
- 任一方把 workflow / orchestrator 写成裁决层
- 任一方把 service / handler / api 写成真实业务执行层
- Codex 试图绕过 AI 军团直接拍板

## 阻断条件
- 五子面缺失任一核心子面
- 五子面职责冲突明显
- 文档与骨架口径不一致
- frozen 主线被倒灌
- runtime 语义混入
- 外部执行 / 集成语义混入
- 轻量导入/连接级验收与现状不一致
- Frozen 范围无法明确列举
- Frozen 后变更控制规则无法明确
