# HANDOFF_IMPLEMENTATION_READINESS_v1

## 1. 目的

本文件用于定义 4 个 handoff 在“最小实现阶段”前的准备口径。

当前只做：

- 类型占位准备
- payload 结构准备
- 输入输出接口定义准备
- 错误对象定义准备

当前不做：

- handoff 执行代码
- 治理实现
- 发布实现

---

## 2. Candidate Handoff

### 当前是否进入最小实现阶段

- 是

### 当前只需要

- 类型占位
- payload 结构
- 输入输出接口定义
- 错误对象定义

### 当前不进入代码的部分

- 真实治理接管逻辑
- 下游 validator 调用

### 未来允许接入的调用方

- 生成线末端交付服务
- `state-manager`（仅运行态记录）

### 明确禁止接入的调用方

- `nl--skill`
- `skill-creator`
- `n8n / orchestrator`

---

## 3. Validation Handoff

### 当前是否进入最小实现阶段

- 是

### 当前只需要

- 类型占位
- payload 结构
- 输入输出接口定义
- 错误对象定义

### 当前不进入代码的部分

- 真实 validator 执行
- 治理通过/失败写口

### 未来允许接入的调用方

- `validator`

### 明确禁止接入的调用方

- `nl--skill`
- `skill-compiler`
- `skill-creator`
- `n8n / orchestrator`

---

## 4. Review Handoff

### 当前是否进入最小实现阶段

- 否，本轮只做接口准备

### 当前只需要

- payload 结构
- 输入输出接口定义
- 错误对象定义

### 当前不进入代码的部分

- Review 对象实现
- 人工审批逻辑
- Review record 实现

### 未来允许接入的调用方

- `admin-review-console`

### 明确禁止接入的调用方

- `nl--skill`
- `skill-creator`
- `n8n / orchestrator`

---

## 5. Release/Audit Handoff

### 当前是否进入最小实现阶段

- 否，本轮只做接口准备

### 当前只需要

- payload 结构
- 输入输出接口定义
- 错误对象定义

### 当前不进入代码的部分

- ReleaseDecision 实现
- AuditPack 实现
- 发布写口实现

### 未来允许接入的调用方

- `release-manager`
- `evidence-collector`
- `revision-manager`（特定生命周期场景）

### 明确禁止接入的调用方

- `nl--skill`
- `skill-creator`
- `n8n / orchestrator`

---

## 6. 当前结论

在最小实现阶段：

- `candidate handoff` 与 `validation handoff` 可进入类型占位准备
- `review handoff` 与 `release/audit handoff` 只保留接口准备，不进入对象实现
