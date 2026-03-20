# Integration Gateway Runtime 排除边界

## 当前阶段
**准备阶段** - 只定义骨架，不进入 runtime

## Runtime 排除边界

### 1. 真实外部系统连接
**排除**:
- 真实 webhook 调用
- 真实 queue 消费
- 真实 db 操作
- 真实 slack 消息
- 真实 email 发送
- 真实 repo 操作

**只做**:
- 定义连接接口
- 定义连接契约
- 定义连接注册表

### 2. 真实业务逻辑执行
**排除**:
- 真实业务流程执行
- 真实数据转换
- 真实错误恢复
- 真实重试补偿

**只做**:
- 定义业务流程接口
- 定义数据转换规则
- 定义错误恢复策略
- 定义重试补偿策略

### 3. 真实状态管理
**排除**:
- 真实连接状态管理
- 真实执行状态跟踪
- 真实资源生命周期管理

**只做**:
- 定义状态模型
- 定义状态转换规则
- 定义生命周期模型

### 4. 真实 Permit 验证
**排除**:
- 真实 permit 验证
- 真实 Governor 通信
- 真实 permit 过期检查

**只做**:
- 定义 permit 验证接口
- 定义 permit 验证规则
- 定义 permit 引用格式

## 骨架定义范围

### 允许定义
1. **接口定义**
   - 类名
   - 方法签名
   - 参数类型
   - 返回类型

2. **数据结构**
   - dataclass 定义
   - 类型注解
   - 文档字符串

3. **配置结构**
   - 配置类定义
   - 配置项定义
   - 默认值

4. **错误类型**
   - 异常类定义
   - 错误码定义
   - 错误消息

### 禁止实现
1. **业务逻辑**
   - 条件判断
   - 循环处理
   - 数据转换

2. **外部调用**
   - HTTP 请求
   - 数据库操作
   - 文件 I/O

3. **状态管理**
   - 状态存储
   - 状态更新
   - 状态查询

## 从准备阶段到 Runtime 的过渡条件

### 过渡条件（仅定义，不触发）
1. Governor 明确授权进入 runtime
2. 所有 permit 验证逻辑已实现
3. 所有连接器已实现并通过测试
4. 所有错误恢复策略已就绪
5. 所有监控告警已配置

### 当前禁令
- **不得**自行决定进入 runtime
- **不得**自行实现 runtime 逻辑
- **不得**绕过 Governor 进入 runtime

## 示例：允许的骨架定义

```python
# 允许：接口定义
class GatewayInterface(ABC):
    @abstractmethod
    def route(self, intent: ExecutionIntent) -> RoutingResult:
        """路由执行意图到连接器"""
        pass

# 允许：数据结构定义
@dataclass
class ExecutionIntent:
    skill_id: str
    action_type: str
    payload: dict
    permit_ref: str

# 允许：错误类型定义
class GatewayError(Exception):
    """网关错误基类"""
    pass
```

## 示例：禁止的 Runtime 实现

```python
# 禁止：真实业务逻辑
def route(self, intent: ExecutionIntent) -> RoutingResult:
    # 禁止：真实判断逻辑
    if intent.action_type == "publish":
        return self._handle_publish(intent)  # 不实现
    # ...

# 禁止：真实外部调用
def send_to_webhook(self, url: str, payload: dict):
    # 禁止：真实 HTTP 调用
    response = requests.post(url, json=payload)  # 不实现
    # ...
```

## 当前状态
- **阶段**: 准备阶段
- **状态**: 骨架定义中
- **禁令**: 不得进入 runtime
- **触发**: 等待 Governor 明确授权
