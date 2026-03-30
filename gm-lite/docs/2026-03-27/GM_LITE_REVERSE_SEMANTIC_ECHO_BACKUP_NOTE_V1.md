# GM LITE Reverse Semantic Echo Backup Note v1

## 目的
- 将“反向语义回声”作为后续增强方向留档
- 当前不插入主线，不打断 marketplace readiness 路径
- 作为入口增强层与插件可见反馈层的后备制度件

## 核心定义
“反向语义回声”指系统在接收用户意图后，以**低泄露、可审计、可见状态**的方式反向输出：
- 系统当前理解成了什么
- 当前偏差或不确定性是什么
- 下一步准备怎么做
- 哪些点需要人工确认

## 目标边界
### In Scope
- 意图回声
- 偏差回声
- 阻塞回声
- 下一跳回声
- 插件侧可见反馈面

### Out Of Scope
- 暴露完整思维链
- 暴露核心 prompt / skill 内核
- 泄露私有调度逻辑
- 取代现有 gate / review / compliance

## 推荐落点
### 1. GM-LITE 入口层
- 作为 preflight clarification 的增强层
- 在 execution 前给出结构化回声

### 2. 插件侧可见层
- 在 sidebar / status / run report 中给出最小语义回声面
- 让用户看到状态，不看到核心资产

## 推荐输出形态
- `Intent Echo`
- `Drift Echo`
- `Block Echo`
- `Next-Hop Echo`
- `Need-Confirm Echo`

## 与当前系统关系
- 当前系统已有近似能力：
  - state feedback
  - observability
  - report
  - preflight clarification bridge
- 但“反向语义回声”尚未被单独制度化

## 当前处理原则
- 仅留档
- 不抢占当前 marketplace readiness 主线
- 后续如需启动，可立项为：
  - `gm_lite_reverse_semantic_echo_preparation_v1`
