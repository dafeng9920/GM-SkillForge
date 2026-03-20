# 今日收尾与明日 TODO v1

## 今日收尾

### 今日已完成
- 五层主线对象冻结链已完整闭合：
  - `Bridge Minimal Implementation v0 Frozen`
  - `Governance Intake Minimal Implementation v0 Frozen`
  - `Gate Minimal Implementation Frozen`
  - `Review Minimal Implementation Frozen`
  - `Release Minimal Implementation Frozen`
  - `Audit Minimal Implementation Frozen`
- 五层主线合规检验已完成：
  - [FIVE_LAYER_COMPLIANCE_AUDIT_REPORT_v1.md](/d:/GM-SkillForge/docs/2026-03-19/FIVE_LAYER_COMPLIANCE_AUDIT_REPORT_v1.md)
  - [FIVE_LAYER_COMPLIANCE_CHANGE_REQUIREMENTS_v1.md](/d:/GM-SkillForge/docs/2026-03-19/FIVE_LAYER_COMPLIANCE_CHANGE_REQUIREMENTS_v1.md)

### 今日结论
- 当前五层主线：
  - **结构冻结完成**
  - **边界纪律成立**
  - **对象链闭合**
- 当前五层主线合规状态：
  - **`REQUIRES_CHANGES`**

### 今日阻断结论摘要
- 当前不能把五层主线直接视为“合规闭环完成”。
- 当前最小缺口不是对象层，而是治理桥接层。
- 需要补齐：
  1. 三权分立记录
  2. `permit=VALID` 入口条件
  3. `AuditPack / EvidenceRef` 桥接
  4. “进入系统执行层”改为“有条件进入”

## 明日唯一主线
- 进入：
  - `五层主线合规整改阶段`
- 目标：
  - 先补齐主线合规桥接层，再启动系统执行层准备模块

## 明日 TODO

### T1. 补三权记录
- 目标：
  - 将主控 / 执行 / 验收 三类角色正式挂入五层主线材料
- 要求：
  - 不回改已 frozen 对象
  - 只补治理材料与角色绑定
- 完成标准：
  - 五层主线存在统一可引用的三权分立记录

### T2. 补 `permit=VALID` 入口条件
- 目标：
  - 把后续进入系统执行层的副作用动作前置为 permit 条件
- 要求：
  - 不进入系统执行实现
  - 只定义准入门槛
- 完成标准：
  - 明确写出：无 `permit=VALID` 时不得进入副作用执行

### T3. 补 `AuditPack / EvidenceRef` 桥接
- 目标：
  - 把证据产物与五层主线正式挂接
- 要求：
  - 明确 evidence 放置位置、引用方式、回溯方式
- 完成标准：
  - 五层主线材料能引用 `AuditPack/evidence` 与 `EvidenceRef`

### T4. 把“进入系统执行层”改成“有条件进入”
- 目标：
  - 收紧后续进入系统执行层的文字口径
- 要求：
  - 改成条件式，而不是默认放行式
- 完成标准：
  - 明确写出：
    - 只有当三权记录 + permit + evidence bridge 补齐后，才具备进入系统执行层准备的条件

### T5. 补全旧合规脚本审计范围
- 目标：
  - 扩展 `scripts/run_3day_compliance_review.py`，让它覆盖 2026-03-18 之后的新五层主线，以及仓库里**已存在但尚未写入脚本**的治理与执行相关组件
- 当前已知问题：
  - 该脚本主要覆盖旧治理底座、dispatch、permit、n8n、governance-orchestrator
  - 尚未完整覆盖：
    - `contracts/governance_bridge/...`
    - `contracts/governance_intake/...`
    - `contracts/gate/...`
    - `contracts/review/...`
    - `contracts/release/...`
    - `contracts/audit/...`
    - 对应 frozen / validation / change control 文档
    - 仓库中已存在但尚未写入审计脚本的治理侧组件、证据侧组件、执行侧准备组件
    - 已存在但尚未被正式纳入审计口径的治理端内容
- 完成标准：
  - 脚本能够先做“存在组件盘点”，再做“是否纳入审计范围”比对
  - 脚本能够对五层主线做基础越界/缺口扫描
  - 新旧治理资产都在审计范围内
  - 所有“已存在但未写入”的治理 / 证据 / 执行准备组件都能被列出并判定是否应纳入

### T6. 完成系统执行层准备模块任务包
- 目标：
  - 将 [《系统执行层准备模块任务包 v1》](/d:/GM-SkillForge/docs/2026-03-18/%E3%80%8A%E7%B3%BB%E7%BB%9F%E6%89%A7%E8%A1%8C%E5%B1%82%E5%87%86%E5%A4%87%E6%A8%A1%E5%9D%97%E4%BB%BB%E5%8A%A1%E5%8C%85%20v1%E3%80%8B.md) 纳入明日同一主线并完成
- 前提：
  - 先完成 T1-T4，至少把合规桥接层补齐到可承接状态
- 完成标准：
  - 系统执行层准备模块按任务包要求完成正式产物
  - 不倒灌五层 frozen 对象边界

## 明日执行顺序
1. 先做 T1-T4
2. 再做 T5
3. 最后执行 T6

## 明日禁止项
- 不回改 Bridge / Governance Intake / Gate / Review / Release / Audit 已 frozen 对象
- 不提前进入 workflow / orchestrator / service / handler / api 真实实现
- 不提前进入 runtime
- 不提前进入外部执行与集成层
- 不把合规整改阶段做成系统执行阶段

## 明日补充口径
- `python .\\scripts\\run_3day_compliance_review.py --run-tests` 的整改目标，不只是覆盖五层主线。
- 还必须覆盖：
  - 仓库内已存在的治理端组件
  - 证据链相关组件
  - 系统执行层准备相关组件
  - 当前“存在但未写入审计脚本”的组件集合
- 审计脚本应从“手工硬编码检查点”升级为：
  - `硬规则检查 + 组件盘点 + 覆盖差异报告`

## 收尾状态
- 今日可以收口
- 明日开工入口：
  - `五层主线合规整改阶段`
