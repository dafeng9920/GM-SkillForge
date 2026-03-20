# 系统执行层最小落地模块变更控制规则 v1

## 允许变更
- 任务卡描述补强
- 文档边界表述收紧
- 非语义性路径修正
- 目录命名建议优化

## 受控变更
- 五子面建议路径调整
- 轻量导入链调整
- 子任务交付物清单细化

## 禁止变更
- 回改 frozen 主线
- 进入 runtime
- 进入外部执行或集成
- 提前实现真实业务逻辑
- 让 workflow / orchestrator 获得裁决权
- 让 service / handler / api 成为完整执行层
- Codex 直接代行全部实现

## Review 规则
- 不得借审查之名新增模块范围。
- 只能给出结构与职责问题。

## Compliance 规则
- 不得代替 Execution 写实现。
- 只能给出 PASS / REQUIRES_CHANGES / DENY 建议。

## Codex 规则
- 不得绕过 AI 军团直接吞掉五子面实现。
- 仅可做极小补丁、路径修正、非语义性整合。
