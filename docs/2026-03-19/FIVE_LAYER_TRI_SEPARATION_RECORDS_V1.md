# 五层主线三权记录 v1

## 目的
- 将五层主线的治理推进正式绑定到三权分立口径。
- 该记录只补治理桥接，不回改任何已 frozen 对象。

## 适用范围
- `Bridge Minimal Implementation v0 Frozen`
- `Governance Intake Minimal Implementation v0 Frozen`
- `Gate Minimal Implementation Frozen`
- `Review Minimal Implementation Frozen`
- `Release Minimal Implementation Frozen`
- `Audit Minimal Implementation Frozen`

## 三权角色

### 主控权
- 角色：
  - `Codex / 主控官`
- 职责：
  - 定阶段
  - 定唯一目标
  - 定允许项 / 禁止项
  - 汇总执行结果
  - 做最终验收与冻结判断
- 不得：
  - 绕过三权分立直接把执行结果当作验收结果
  - 未经合规核验直接宣布进入系统执行层

### 执行权
- 角色：
  - `Execution Wing`
- 职责：
  - 在已冻结边界内生成 typed object / payload / schema / interface
  - 生成阶段文档草稿
  - 生成最小实现与最小校验产物
- 不得：
  - 擅自扩边界
  - 擅自给出冻结结论
  - 擅自把对象层推进到执行层

### 验收权
- 角色：
  - `Review Wing`
- 职责：
  - 核对结构一致性
  - 核对上下游承接口径
  - 标记阻断性 / 非阻断性问题
- 不得：
  - 直接改执行产物
  - 直接宣布合规放行

### 合规权
- 角色：
  - `Compliance Wing`
- 职责：
  - 检查 fail-closed
  - 检查 compat / source status 是否主化
  - 检查是否提前混入系统执行层 / 外部执行层
  - 检查是否触发 permit 约束
- 不得：
  - 替代执行权或验收权
  - 未经证据链就直接做放行裁决

## 五层主线中的三权绑定
- `Bridge / Governance Intake / Gate / Review / Release / Audit`
  - 都属于对象与治理主线
  - 只能被执行权创建或整理
  - 只能被验收权做结构审查
  - 只能被合规权做边界与证据审查
  - 只能由主控权做最终阶段结论

## 当前结论
- 五层主线后续进入系统执行层前，必须保留：
  - 主控权
  - 执行权
  - 验收权
  - 合规权
- 四者记录必须可追溯，不允许角色混线。

## 进入系统执行层前的三权要求
- 至少要有：
  - 一份执行记录
  - 一份结构验收记录
  - 一份合规审计记录
  - 一份主控裁决记录
- 若任一记录缺失：
  - 不得解释为“已具备进入系统执行层准备条件”
