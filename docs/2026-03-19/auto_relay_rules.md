# Auto Relay Rules v1

## 目标
- 让任务在 execution -> review -> compliance -> final gate 之间按规则自动接力。

## 核心原则
- 自动接力只负责“生成下一跳任务”
- 自动接力不负责裁决
- 自动接力不改写任务内容

## 规则 1：Execution 完成后触发 Review

### 前提
- `execution_report` 已写回标准路径
- execution_report 最小字段齐全

### 动作
1. 校验 execution_report 是否存在
2. 生成同 task_id 的 review envelope
3. 继承：
   - task_id
   - module
   - source_of_truth
   - writeback 路径
   - hard_constraints
4. 将 `role` 设为 `review`
5. 将 `next_hop` 设为 `compliance`

## 规则 2：Review 完成后触发 Compliance

### 前提
- `review_report` 已写回标准路径
- review verdict 已明确

### 动作
1. 校验 review_report 是否存在
2. 生成同 task_id 的 compliance envelope
3. 继承：
   - task_id
   - module
   - source_of_truth
   - writeback 路径
   - hard_constraints
4. 将 `role` 设为 `compliance`
5. 将 `next_hop` 设为 `final_gate`

## 规则 3：Compliance 完成后触发 Final Gate 通知

### 前提
- `compliance_attestation` 已写回标准路径
- execution / review / compliance 三件齐全

### 动作
1. 聚合同 task_id 的三件回收件
2. 标记任务状态为 `GATE_READY`
3. 将任务加入主控终验池
4. 通知 Codex 可终验

## 规则 4：幂等性
- 目标 writeback 文件已存在时，不重复生成相同下一跳
- 已处于更后状态的任务，不允许回退重触发

## 规则 5：异常转升级
- 若 relay 发现缺件、字段缺失、依赖未满足、状态超时，则不继续接力
- 直接走 escalation protocol

