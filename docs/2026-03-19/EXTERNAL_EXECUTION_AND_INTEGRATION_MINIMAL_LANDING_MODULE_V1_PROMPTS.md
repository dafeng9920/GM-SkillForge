# 外部执行与集成最小落地模块 v1 分派提示词

## 主控官速览

### 第一波并行
- X1 connector contract
- X2 integration gateway
- X3 secrets / credentials boundary

### 第二波串行
- X4 external action policy
- 依赖：X1 / X2 / X3

### 第三波串行
- X5 retry / compensation boundary
- 依赖：X2 / X4
- X6 publish / notify / sync boundary
- 依赖：X4 / X5

### 统一回收路径
- `docs/2026-03-19/verification/external_execution_and_integration_minimal_landing/`

### 主控官一句话判断标准
- 六个子面都具备 `execution / review / compliance` 后，才允许终验

