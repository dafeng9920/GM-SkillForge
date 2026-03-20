# Publish / Notify / Sync Boundary 职责定义

## 负责事项

### 1. Publish Boundary (发布边界)
- 定义发布动作的边界规则
- 验证发布动作的 permit 有效性（仅定义接口）
- 定义发布请求的数据结构
- 定义发布结果的数据结构

### 2. Notify Boundary (通知边界)
- 定义通知动作的边界规则
- 验证通知动作的 permit 有效性（仅定义接口）
- 定义通知请求的数据结构
- 定义通知结果的数据结构

### 3. Sync Boundary (同步边界)
- 定义同步动作的边界规则
- 验证同步动作的 permit 有效性（仅定义接口）
- 定义同步请求的数据结构
- 定义同步结果的数据结构

### 4. Permit 前置检查
- 定义 permit 前置检查接口
- 定义 permit 类型映射规则
- 定义 permit 错误处理结构

### 5. Action Policy 协作
- 与 E4 External Action Policy 协作
- 使用 E4 定义的关键动作列表
- 使用 E4 定义的 permit 校验规则

## 与 E4 (External Action Policy) 的关系

### E4 提供
- 关键动作列表 (CRITICAL_ACTIONS)
- Permit 校验接口 (PermitCheckResult)
- 动作分类 (ActionCategory)

### E6 使用
- 检查动作是否在 CRITICAL_ACTIONS 中
- 调用 permit 校验接口
- 根据 ActionCategory 决定 permit 类型

## 与 E5 (Retry / Compensation Boundary) 的关系

### E5 提供
- 失败事件观察
- 重试建议 (RetryAdvice)
- 补偿建议 (CompensationAdvice)

### E6 使用
- 接收失败事件
- 根据建议重新执行动作（仅定义接口）
- 需要新的 permit 才能重新执行

## 不负责事项
详见 [EXCLUSIONS.md](./EXCLUSIONS.md)

## Permit 规则
详见 [PERMIT_RULES.md](./PERMIT_RULES.md)

## Runtime 边界
详见 [RUNTIME_BOUNDARY.md](./RUNTIME_BOUNDARY.md)
