# Connector Contract Runtime 排除边界

## 核心原则
**Connector Contract 停留在接口定义，不进入 runtime 执行。**

## Runtime 边界定义

### 不进入的范围

#### 1. 连接执行
- 不建立真实连接
- 不执行连接握手
- 不处理连接会话
- 不关闭连接

#### 2. 数据传输
- 不发送真实数据
- 不接收真实响应
- 不处理网络错误
- 不重试传输

#### 3. 协议处理
- 不解析协议报文
- 不编码/解码数据
- 不处理协议版本
- 不协商协议参数

#### 4. 状态管理
- 不维护连接状态
- 不跟踪会话状态
- 不更新连接状态
- 不清理连接资源

#### 5. 错误处理
- 不捕获网络错误
- 不处理超时
- 不重试失败操作
- 不回滚事务

## 契约与实现的分界

### Connector Contract（契约层）
```python
# 只定义结构，不实现
@dataclass(frozen=True)
class ExternalConnectionContract:
    request_schema: Dict[str, Any]
    response_schema: Dict[str, Any]
    error_classes: Dict[str, str]
```

### Integration Gateway（实现层，未来）
```python
# 实现 connector 接口（未来）
class GitConnector:
    def connect(self, request: ConnectorRequest) -> ConnectorResult:
        # 真实 Git 连接实现
        pass
```

## 接口定义 vs 实现的示例

### Connector Contract 定义
```python
# 定义 Git 连接的请求 schema
request_schema = {
    "type": "object",
    "properties": {
        "repo_url": {"type": "string"},
        "action": {"type": "string"},
        "payload": {"type": "object"},
    },
}
```

### Integration Gateway 实现（未来）
```python
# 实现 Git 连接（未来）
def execute_git_action(repo_url: str, action: str, payload: dict):
    # 真实 Git 操作
    pass
```

## 骨架代码的限制

### 允许的骨架代码
- 类型定义（dataclass, TypedDict）
- 常量定义
- 文档字符串
- 类型注解

### 禁止的骨架代码
- `raise NotImplementedError()` 之外的实现逻辑
- 网络调用
- 文件 I/O
- 数据库访问
- 外部系统调用

### 接口定义示例
```python
# 允许：接口定义
class ConnectorInterface(Protocol):
    def execute(self, request: ConnectorRequest) -> ConnectorResult:
        """执行 connector 操作"""
        ...

# 允许：类型提示
@dataclass(frozen=True)
class ConnectorRequest:
    connector_type: str
    action: str
    payload: Dict[str, Any]

# 禁止：实现逻辑
class GitConnector:
    def execute(self, request: ConnectorRequest) -> ConnectorResult:
        # 禁止：真实实现
        import git  # 禁止：导入协议库
        repo = git.Repo(request.payload["repo_url"])  # 禁止
        ...
```

## 后续 Runtime 的排除声明

### 当前阶段（准备阶段）
- 只定义接口契约
- 只声明依赖和需求
- 不实现任何执行逻辑

### 下一阶段（实现阶段，未开始）
- 由 Integration Gateway 实现 connector
- 由 Integration Gateway 处理 runtime 逻辑
- Connector Contract 保持不变

### 清晰的边界声明
```python
@dataclass(frozen=True)
class ExternalConnectionContract:
    boundary_note: str = (
        "此契约只定义接口，不实现连接。"
        "真实连接由 Integration Gateway 执行。"
    )
```

## 验证规则

### 自检清单
- [ ] 没有导入外部协议库（git, requests, websocket 等）
- [ ] 没有网络调用代码
- [ ] 没有文件 I/O 代码
- [ ] 没有数据库访问代码
- [ ] 所有 dataclass 都是 frozen=True
- [ ] 所有方法都是接口定义或返回 NotImplementedError
- [ ] 文档明确标注"不实现连接"

### 违规示例
```python
# 违规：真实实现
def push_to_github(repo: str, token: str):
    import requests  # 违规：导入协议库
    requests.post(...)  # 违规：网络调用
```

### 合规示例
```python
# 合规：接口定义
@dataclass(frozen=True)
class GitHubConnectionContract:
    request_schema: Dict[str, Any] = field(default_factory=lambda: {
        "type": "object",
        "properties": {
            "repo": {"type": "string"},
            "action": {"type": "string"},
        },
    })
```
