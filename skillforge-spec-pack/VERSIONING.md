# GM OS Core 版本策略

## Schema 版本号格式

使用 `0.1.x` 格式：
- 主版本: 0 (开发阶段)
- 次版本: 1 (API 基本稳定)
- 修订号: x (向后兼容的修复和增强)

## 版本演进规则

### 向后兼容的变更 (修订号 +1)
- 新增可选字段
- 放宽验证规则
- 新增 enum 值
- 修复 bug

### 破坏性变更 (次版本 +1)
- 删除字段
- 重命名字段
- 收紧验证规则
- 改变必需字段

## 当前版本

| 组件 | 版本 |
|------|------|
| Schemas | 0.1.0 |
| Policies | 0.1.0 |
| Error Codes | 0.1.0 |
| Pipeline | 0.1.0 |

## 版本检查

每个 schema/policy 文件必须包含 `schema_version` 字段：

```json
{
  "schema_version": "0.1.0",
  ...
}
```

```yaml
schema_version: "0.1.0"
...
```

## 升级指南

1. 检查 `schema_version` 变化
2. 阅读变更日志
3. 运行契约测试验证兼容性
4. 更新 examples

## 废弃策略

- 废弃字段保留至少 2 个次版本
- 废弃字段标记 `deprecated: true`
- 在文档中说明替代方案
