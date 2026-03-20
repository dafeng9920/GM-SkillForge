# 系统执行层 Frozen 后变更控制规则 v1

## 允许变更
- Frozen 判断任务书补强
- Frozen 验收标准表述收紧
- 非语义性路径修正
- 统一回收路径补充

## 受控变更
- Frozen 范围条目细化
- Change control 分类细化
- 轻量导入/连接级证据补强

## 禁止变更
- 回改 frozen 主线
- 进入 runtime
- 进入外部执行或集成
- 提前实现真实业务逻辑
- 让 workflow / orchestrator 成为裁决层
- 让 service / handler / api 成为真实业务执行层
- Codex 绕过 AI 军团直接下 Frozen 结论

## Frozen 后允许变更
- 文档补强
- 类型注解细化
- 注释完善
- 测试用例新增
- 非语义性路径修正

## Frozen 后受控变更
- 新增路由条目
- 新增转发条目
- 新增 frozen 依赖声明
- 接口方法新增
- 连接关系调整

## Frozen 后禁止变更
- 回改 frozen 主线
- 进入 runtime
- 进入外部执行或集成
- 提前实现真实业务逻辑
- 让 workflow / orchestrator 成为裁决层
- 让 service / handler / api 成为真实业务执行层
- 修改当前五子面的核心接口签名
- 修改当前五子面的目录结构

## 已冻结层保护规则
- Production Chain / Bridge / Governance Intake / Gate / Review / Release / Audit 冻结边界不得倒灌修改
- `system_execution` 五子面冻结骨架不得被反向改写为运行时实现

## 五子面保护规则
- workflow：只保留编排入口与流程连接职责
- orchestrator：只保留内部路由与结构验证职责
- service：只保留内部服务承接与只读 frozen 依赖声明
- handler：只保留输入承接与调用转发职责
- api：只保留接口层承接、请求适配与响应构造职责

## 下一阶段前不得触碰的实现面
- runtime 执行逻辑
- 外部执行与集成
- 真实 webhook / queue / db / registry / slack / email / repo 接入
- 真实业务长链执行
- 自动重试补偿体系
- 外部 API 调用
- 真正的编排引擎控制逻辑
