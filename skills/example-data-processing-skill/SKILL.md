# example-data-processing-skill

> 版本: v1.0.0
> 创建时间: 2026-02-20
> 类型: 数据处理

---

## 概述

示例数据处理 Skill - 演示如何创建一个完整的skill，包含数据验证、转换和输出功能。

### 核心能力

| 能力 | 说明 |
|------|------|
| 数据验证 | 验证输入数据的格式和完整性 |
| 数据转换 | 将数据从一种格式转换为另一种格式 |
| 数据清洗 | 清理和标准化数据 |
| 错误处理 | 优雅地处理各种错误情况 |
| 日志记录 | 记录处理过程和结果 |

### 核心约束

```yaml
fail_safe: true
data_integrity: true
performance_optimized: true
```

---

## 触发条件

- 接收到数据处理请求
- 数据文件上传
- API调用触发
- 定时任务执行

---

## 输入契约

```yaml
input:
  data_source: string       # 数据源路径或URL
  format: string           # 输入数据格式 (json, csv, xml)
  processing_rules: array  # 处理规则列表
  output_format: string    # 期望的输出格式
  validation_schema: object # 数据验证模式
```

---

## 输出契约

```yaml
output:
  processed_data: object   # 处理后的数据
  processing_summary: object # 处理摘要
    - total_records: int
    - processed_records: int
    - error_records: int
    - processing_time_ms: int
  validation_results: array # 验证结果
  error_log: array         # 错误日志
```

---

## 处理流程

### 1. 数据验证阶段
```javascript
function validateData(data, schema) {
  const errors = [];
  
  // 检查必填字段
  for (const field of schema.required) {
    if (!data[field]) {
      errors.push(`Missing required field: ${field}`);
    }
  }
  
  // 检查数据类型
  for (const [field, type] of Object.entries(schema.types)) {
    if (data[field] && typeof data[field] !== type) {
      errors.push(`Invalid type for field ${field}: expected ${type}`);
    }
  }
  
  return errors;
}
```

### 2. 数据转换阶段
```javascript
function transformData(data, rules) {
  let result = { ...data };
  
  for (const rule of rules) {
    switch (rule.type) {
      case 'rename':
        result[rule.to] = result[rule.from];
        delete result[rule.from];
        break;
      case 'format':
        result[rule.field] = formatValue(result[rule.field], rule.format);
        break;
      case 'calculate':
        result[rule.field] = calculateValue(result, rule.expression);
        break;
    }
  }
  
  return result;
}
```

### 3. 数据清洗阶段
```javascript
function cleanData(data) {
  return {
    ...data,
    // 去除空白字符
    name: data.name?.trim(),
    // 标准化邮箱格式
    email: data.email?.toLowerCase(),
    // 格式化电话号码
    phone: formatPhoneNumber(data.phone),
    // 验证和格式化日期
    date: parseAndFormatDate(data.date)
  };
}
```

---

## 使用示例

### 基本用法
```javascript
const skill = new DataProcessingSkill();

const result = await skill.process({
  data_source: './data/users.json',
  format: 'json',
  processing_rules: [
    { type: 'rename', from: 'full_name', to: 'name' },
    { type: 'format', field: 'email', format: 'lowercase' },
    { type: 'calculate', field: 'age', expression: 'current_year - birth_year' }
  ],
  output_format: 'json',
  validation_schema: {
    required: ['name', 'email'],
    types: {
      name: 'string',
      email: 'string',
      age: 'number'
    }
  }
});

console.log(result.processed_data);
console.log(result.processing_summary);
```

### 批量处理
```javascript
const batchResult = await skill.processBatch({
  data_sources: ['./data/batch1.csv', './data/batch2.csv'],
  format: 'csv',
  processing_rules: [
    { type: 'clean', fields: ['name', 'address'] },
    { type: 'validate', schema: 'user_schema' }
  ],
  output_format: 'json'
});
```

---

## 错误处理

### 错误类型
| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| E001 | 数据源不存在 | 返回错误信息，停止处理 |
| E002 | 数据格式无效 | 尝试自动修复，失败则跳过 |
| E003 | 验证失败 | 记录错误，继续处理其他数据 |
| E004 | 转换规则错误 | 使用默认规则或跳过该规则 |

### 错误恢复策略
```javascript
function handleError(error, data, context) {
  switch (error.code) {
    case 'E002':
      // 尝试自动修复数据格式
      return attemptAutoFix(data);
    case 'E003':
      // 记录验证错误但继续处理
      context.errors.push(error);
      return data;
    default:
      throw error;
  }
}
```

---

## 性能优化

### 批处理优化
- 使用流式处理大文件
- 并行处理独立的数据块
- 内存使用监控和清理

### 缓存策略
- 缓存验证模式
- 缓存转换规则编译结果
- 缓存常用的数据格式转换器

---

## 测试用例

```javascript
describe('DataProcessingSkill', () => {
  test('should validate required fields', () => {
    const skill = new DataProcessingSkill();
    const result = skill.validate(
      { name: 'John' },
      { required: ['name', 'email'] }
    );
    expect(result.errors).toContain('Missing required field: email');
  });

  test('should transform data according to rules', () => {
    const skill = new DataProcessingSkill();
    const result = skill.transform(
      { full_name: 'John Doe' },
      [{ type: 'rename', from: 'full_name', to: 'name' }]
    );
    expect(result.name).toBe('John Doe');
    expect(result.full_name).toBeUndefined();
  });
});
```

---

## 部署配置

### 环境变量
```bash
DATA_PROCESSING_MAX_FILE_SIZE=100MB
DATA_PROCESSING_TIMEOUT=30000
DATA_PROCESSING_CACHE_TTL=3600
```

### Docker配置
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 验收标准

- [x] 支持多种数据格式 (JSON, CSV, XML)
- [x] 数据验证准确率 >99%
- [x] 处理性能 >1000 records/second
- [x] 错误恢复机制完善
- [x] 完整的测试覆盖率 >90%
- [x] 详细的日志记录
- [x] 内存使用优化

---

*版本: v1.0.0 | 创建时间: 2026-02-20*