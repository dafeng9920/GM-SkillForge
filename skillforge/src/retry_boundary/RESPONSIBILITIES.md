# Retry / Compensation Boundary 职责定义

## 负责事项

### 1. 失败分析 (Failure Analysis)
- 分析失败类型（连接失败 / 业务失败 / 治理失败）
- 分析失败原因（网络错误 / 资源不足 / 权限不足）
- 分析失败影响范围（单点 / 批量 / 级联）

### 2. 重试策略建议 (Retry Strategy Advice)
- 提供重试类型建议（立即重试 / 延迟重试 / 不重试）
- 提供重试间隔建议（指数退避 / 固定间隔）
- 提供重试次数建议（最多 3 次 / 最多 5 次）

### 3. 补偿方案建议 (Compensation Plan Advice)
- 提供补偿类型建议（回滚 / 重做 / 人工介入）
- 提供补偿范围建议（单点补偿 / 批量补偿）
- 提供补偿优先级建议（高优先 / 中优先 / 低优先）

### 4. Permit 引用建议 (Permit Reference Advice)
- 说明重试需要的 permit 类型
- 说明补偿需要的 permit 类型
- 说明 permit 获取路径

## 不负责事项
详见 [EXCLUSIONS.md](./EXCLUSIONS.md)

## Runtime 边界
详见 [RUNTIME_EXCLUSION.md](./RUNTIME_EXCLUSION.md)
