# Connector Contract 职责定义

## 负责事项

### 1. 契约定义 (Contract Definition)
- 定义外部连接接口的数据结构
- 定义请求/响应的 schema 规范
- 定义错误分类规范
- 使用 frozen dataclass 确保契约不可变

### 2. 依赖声明 (Dependency Declaration)
- 声明对 frozen 主线的只读依赖
- 声明访问模式（read/reference/query）
- 声明依赖用途
- 禁止隐式依赖

### 3. Permit 需求声明 (Permit Requirement Declaration)
- 声明连接所需的 permit 类型
- 声明 permit 使用场景
- 不生成 permit
- 不验证 permit

### 4. Evidence 引用声明 (Evidence Reference Declaration)
- 声明 Evidence 引用类型
- 声明访问模式（read/upload/notify）
- 声明引用用途
- 不修改 Evidence

### 5. 接口分类 (Interface Classification)
- 按连接类型分类（git/webhook/api/registry/storage/notification）
- 按协议无关性定义通用接口
- 为 Integration Gateway 提供路由依据

## 不负责事项
详见 [EXCLUSIONS.md](./EXCLUSIONS.md)

## 接口关系
详见 [CONNECTIONS.md](./CONNECTIONS.md)

## Permit 规则
详见 [PERMIT_RULES.md](./PERMIT_RULES.md)

## Runtime 边界
详见 [RUNTIME_BOUNDARY.md](./RUNTIME_BOUNDARY.md)
