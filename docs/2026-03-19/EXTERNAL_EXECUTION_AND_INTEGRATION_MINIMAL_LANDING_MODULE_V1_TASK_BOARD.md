# 外部执行与集成最小落地模块 v1 任务总表

| Task | Scope | Execution | Review | Compliance | 并行/串行 | 目标 | 状态 |
|---|---|---|---|---|---|---|---|
| X1 | connector contract | vs--cc1 | Kior-A | Kior-C | 并行（第一波） | 建立 connector contract 最小骨架与只读合同边界 | 通过 |
|X2|integration gateway|Antigravity-1|vs--cc3|Kior-C|并行（第一波）|建立 integration gateway 最小骨架与转发边界| 通过 |
|X3|secrets / credentials boundary|Antigravity-2|Kior-A|Kior-C|并行（第一波）|建立 secrets 分层与 credentials 只读边界| 通过 |
|X4|external action policy|Kior-B|vs--cc1|Kior-C|串行（第二波，依赖 X1/X2/X3）|建立 permit / evidence 驱动的 external action policy 骨架| 通过 |
|X5|retry / compensation boundary|vs--cc3|Kior-A|Kior-C|串行（第三波，依赖 X2/X4）|建立 retry / compensation 最小边界，不进入实现| 通过 |
|X6|publish / notify / sync boundary|Antigravity-1|vs--cc1|Kior-C|串行（第三波，依赖 X4/X5）|建立 publish / notify / sync 最小承接骨架| 通过 |

## 统一回收路径
- `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/`

## Codex 回收规则
- X1/X2/X3 先并行回收
- X4 只有在 X1/X2/X3 回收后才放行
- X5/X6 只有在 X4 回收后才放行
- 六个子面都完成 `execution / review / compliance` 后，Codex 才做统一终验

## 当前主控裁决
- 当前模块状态：`模块级终验通过`
- 当前主控结论：`X1-X6 三件套齐全，外部执行与集成最小落地模块 v1 正式通过`

