# Retry / Compensation Boundary

## 定位
Retry / Compensation Boundary 是 SkillForge 失败处理后的**建议边界层**，负责分析失败、提供重试策略建议、提供补偿方案建议，**绝不自动执行**。

## 核心原则
1. **只建议，不执行** - 失败后只给出建议，不做自动重试或补偿
2. **只分析，不裁决** - 分析失败原因，不做最终 PASS/FAIL 判定
3. **只引用，不修改** - Frozen 主线的决策结果不可修改
4. **只准备，不运行** - 停留在骨架定义，不进入 runtime

## 目录结构
```
retry_boundary/
├── README.md                    # 本文件
├── RESPONSIBILITIES.md          # 职责定义
├── EXCLUSIONS.md                # 不负责项
├── RUNTIME_EXCLUSION.md         # Runtime 排除边界
├── boundary_interface.py        # 边界接口定义
├── retry_policy.py              # 重试策略（仅骨架）
└── compensation_advisor.py      # 补偿建议（仅骨架）
```

## 与 Frozen 主线的关系
- **只读承接** - 读取 frozen 主线的 GateDecision / Evidence / AuditPack
- **不回写** - 不修改 frozen 主线的任何决策结果
- **不覆盖** - 失败建议不覆盖原有的治理裁决

## 与 system_execution 的关系
- **旁路观察** - 观察 system_execution 的失败事件
- **不做干预** - 不干预 system_execution 的执行流程
- **只提供建议** - 失败后提供建议，由 Governor 决定是否采纳

## 状态
- **阶段**: 准备阶段
- **范围**: 最小骨架定义
- **禁令**: 不得进入 runtime，不得自动执行
