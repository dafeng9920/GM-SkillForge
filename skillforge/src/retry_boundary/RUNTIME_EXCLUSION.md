# Retry / Compensation Boundary Runtime 排除边界

## 当前阶段
**准备阶段** - 只定义骨架，不进入 runtime

## Runtime 排除边界

### 1. 真实重试执行
**排除**:
- 真实重试触发
- 真实重试逻辑执行
- 真实重试状态管理
- 真实重试结果跟踪

**只做**:
- 定义重试策略接口
- 定义重试建议结构
- 定义重试次数限制规则

### 2. 真实补偿执行
**排除**:
- 真实补偿触发
- 真实补偿逻辑执行
- 真实补偿状态管理
- 真实补偿结果跟踪

**只做**:
- 定义补偿方案接口
- 定义补偿建议结构
- 定义补偿类型规则

### 3. 真实失败分析
**排除**:
- 真实失败类型判定
- 真实失败原因分析
- 真实失败影响评估
- 真实失败恢复

**只做**:
- 定义失败分析接口
- 定义失败类型枚举
- 定义失败原因分类

### 4. 真实 Permit 验证
**排除**:
- 真实 permit 验证
- 真实 Governor 通信
- 真实 permit 过期检查
- 真实 permit 范围验证

**只做**:
- 定义 permit 验证接口
- 定义 permit 验证规则
- 定义 permit 引用格式

### 5. 真实决策修改
**排除**:
- 真实 GateDecision 修改
- 真实 AuditPack 修改
- 真实 Evidence 覆盖
- 真实 frozen 主线修改

**只做**:
- 定义决策覆盖接口（仅限 Governor 使用）
- 定义覆盖理由格式
- 定义覆盖限制规则

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

5. **建议结构**
   - 建议类型定义
   - 建议字段定义
   - 建议优先级定义

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

4. **自动执行**
   - 自动重试触发
   - 自动补偿触发
   - 自动决策修改

## 从准备阶段到 Runtime 的过渡条件

### 过渡条件（仅定义，不触发）
1. Governor 明确授权进入 runtime
2. 所有 permit 验证逻辑已实现
3. 所有重试策略已实现并通过测试
4. 所有补偿方案已实现并通过测试
5. 所有失败分析逻辑已实现
6. 所有监控告警已配置
7. 所有决策覆盖限制已生效

### 当前禁令
- **不得**自行决定进入 runtime
- **不得**自行实现 runtime 逻辑
- **不得**绕过 Governor 进入 runtime
- **不得**在无 permit 的情况下执行重试/补偿

## 示例：允许的骨架定义

```python
# 允许：接口定义
class BoundaryInterface(ABC):
    @abstractmethod
    def analyze_failure(self, event: FailureEvent) -> FailureAnalysis:
        """分析失败事件"""
        pass

# 允许：数据结构定义
@dataclass
class RetryAdvice:
    """重试建议"""
    retry_type: str
    retry_interval: int
    max_retries: int
    required_permit_type: str

# 允许：错误类型定义
class BoundaryError(Exception):
    """边界错误基类"""
    pass
```

## 示例：禁止的 Runtime 实现

```python
# 禁止：真实重试逻辑
def retry_execution(self, execution_id: str) -> RetryResult:
    # 禁止：真实重试触发
    if self.should_retry(execution_id):
        return self._do_retry(execution_id)  # 不实现
    # ...

# 禁止：真实补偿逻辑
def compensate_failure(self, failure_id: str) -> CompensationResult:
    # 禁止：真实补偿触发
    if self.should_compensate(failure_id):
        return self._do_compensate(failure_id)  # 不实现
    # ...
```

## 当前状态
- **阶段**: 准备阶段
- **状态**: 骨架定义中
- **禁令**: 不得进入 runtime，不得自动执行
- **触发**: 等待 Governor 明确授权
