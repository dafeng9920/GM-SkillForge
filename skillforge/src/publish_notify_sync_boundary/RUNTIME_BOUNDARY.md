# Publish / Notify / Sync Boundary Runtime 排除边界

## 当前阶段
**准备阶段** - 只定义骨架，不进入 runtime

## Runtime 排除边界

### 1. 真实发布动作
**排除**:
- 真实 PUBLISH_LISTING 发布
- 真实 UPGRADE_REPLACE_ACTIVE 替换
- 真实 repo 推送
- 真实 registry 更新

**只做**:
- 定义发布接口
- 定义发布契约
- 定义发布边界规则

### 2. 真实通知动作
**排除**:
- 真实 slack 消息发送
- 真实 email 发送
- 真实 webhook 调用
- 真实 SMS 发送

**只做**:
- 定义通知接口
- 定义通知契约
- 定义通知边界规则

### 3. 真实同步动作
**排除**:
- 真实状态同步到外部系统
- 真实配置同步
- 真实数据同步

**只做**:
- 定义同步接口
- 定义同步契约
- 定义同步边界规则

### 4. 真实 Permit 验证
**排除**:
- 真实 permit 验证
- 真实 Governor 通信
- 真实 permit 过期检查

**只做**:
- 定义 permit 验证接口
- 定义 permit 验证规则（委托给 E4）
- 定义 permit 引用格式

### 5. 真实外部系统连接
**排除**:
- 真实 connector 调用
- 真实 API 请求
- 真实数据传输

**只做**:
- 定义 connector 接口
- 定义 connector 契约
- 定义 connector 请求/响应结构

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

5. **协作接口**
   - 与 E4 的协作接口
   - 与 E5 的协作接口
   - 与 system_execution 的协作接口

### 禁止实现
1. **业务逻辑**
   - 条件判断
   - 循环处理
   - 数据转换

2. **外部调用**
   - HTTP 请求
   - 数据库操作
   - 文件 I/O
   - API 调用

3. **状态管理**
   - 状态存储
   - 状态更新
   - 状态查询

4. **执行逻辑**
   - 发布执行
   - 通知发送
   - 同步执行

## 从准备阶段到 Runtime 的过渡条件

### 过渡条件（仅定义，不触发）
1. Governor 明确授权进入 runtime
2. E4 permit 校验逻辑已实现
3. E5 重试/补偿建议已就绪
4. 所有 connector 已实现并通过测试
5. 所有错误恢复策略已就绪
6. 所有监控告警已配置
7. 所有边界规则已生效

### 当前禁令
- **不得**自行决定进入 runtime
- **不得**自行实现 runtime 逻辑
- **不得**绕过 Governor 进入 runtime
- **不得**在无 permit 的情况下执行任何动作

## 示例：允许的骨架定义

```python
# 允许：接口定义
class BoundaryInterface(ABC):
    @abstractmethod
    def check_publish_boundary(self, request: PublishRequest) -> BoundaryCheckResult:
        """检查发布边界"""
        pass

# 允许：数据结构定义
@dataclass
class PublishRequest:
    skill_id: str
    target_system: str
    payload: dict
    permit_ref: str

@dataclass
class BoundaryCheckResult:
    allowed: bool
    block_reason: str | None
    permit_check_result: PermitCheckResult | None

# 允许：错误类型定义
class BoundaryError(Exception):
    """边界错误基类"""
    pass
```

## 示例：禁止的 Runtime 实现

```python
# 禁止：真实发布逻辑
def check_publish_boundary(self, request: PublishRequest) -> BoundaryCheckResult:
    # 禁止：真实判断逻辑
    if request.target_system == "github":
        return self._publish_to_github(request)  # 不实现
    # ...

# 禁止：真实通知发送
def send_notification(self, request: NotifyRequest) -> NotifyResult:
    # 禁止：真实 API 调用
    slack_client.send_message(request.message)  # 不实现
    # ...

# 禁止：真实同步执行
def sync_state(self, request: SyncRequest) -> SyncResult:
    # 禁止：真实同步
    external_api.sync(request.state)  # 不实现
    # ...
```

## 三类边界的具体排除规则

### Publish Boundary 排除
- 不实现真实发布
- 不调用 repo API
- 不更新 registry
- 不执行 git push

### Notify Boundary 排除
- 不实现真实通知
- 不调用 slack API
- 不调用 email API
- 不调用 webhook

### Sync Boundary 排除
- 不实现真实同步
- 不调用外部同步 API
- 不更新外部状态
- 不执行数据传输

## 当前状态
- **阶段**: 准备阶段
- **状态**: 骨架定义中
- **禁令**: 不得进入 runtime
- **触发**: 等待 Governor 明确授权
