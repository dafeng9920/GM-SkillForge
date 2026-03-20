# 系统执行层准备模块任务拆分 v1

## 模式
- `mode = strict`
- 执行顺序：
  - `Review -> Compliance -> Execution`
- Codex 角色：
  - 任务分发者
  - 汇总者
  - 最终验收者

## 三权角色记录
- Execution Wing：`5.4-mini / AI 执行军团`
- Review Wing：`结构与职责审查`
- Compliance Wing：`边界与 fail-closed 合规检查`
- Final Gate：`Codex`

## 统一验收基线
- 五子面必须全部有：
  - 职责定义
  - 不负责项
  - frozen 主线承接点
  - 与其他四子面的接口关系
  - 禁止越界点
  - 建议目录/文件骨架

## 子任务拆分表

| Wave | Task | Scope | Execution | Review | Compliance | Depends On | 状态 |
|---|---|---|---|---|---|---|---|
| Wave 1 | T1 | workflow 面职责与骨架 | Execution Wing | Review Wing | Compliance Wing | - | completed |
| Wave 1 | T2 | orchestrator 面职责与骨架 | Execution Wing | Review Wing | Compliance Wing | - | completed |
| Wave 1 | T3 | service 面职责与骨架 | Execution Wing | Review Wing | Compliance Wing | - | completed |
| Wave 1 | T4 | handler 面职责与骨架 | Execution Wing | Review Wing | Compliance Wing | - | completed |
| Wave 1 | T5 | api 面职责与骨架 | Execution Wing | Review Wing | Compliance Wing | - | completed |
| Wave 2 | T6 | 模块文档、边界、验收、变更控制汇总 | Execution Wing | Review Wing | Compliance Wing | T1,T2,T3,T4,T5 | completed |

## Execution Wing 输出要求
- 形成五子面 skeleton。
- 形成 scope / boundary / acceptance / report / change-control 初稿。
- 不得进入运行时逻辑。

## Review Wing 审查要点
- 目录、命名、分层是否一致。
- 五子面职责是否重叠或断裂。
- 文档与 skeleton 是否对齐。
- 阻断性问题是否存在。

## Compliance Wing 审查要点
- 是否出现 frozen 主线倒灌。
- 是否混入 runtime / external integration。
- 是否让 workflow / orchestrator 变成裁决者。
- 是否让 service / handler / api 变成真实执行层。

## Codex 最终验收口径
- 三权记录完整。
- 五子面全部交付。
- 无阻断性越界。
- 文档与 skeleton 一致。
