# T-FE-02 R1 合规返工说明

> **任务 ID**: T-FE-02
> **返工轮次**: R1
> **执行者**: vs--cc1
> **审查者**: Kior-A
> **合规官**: Kior-B
> **返工触发**: Compliance FAIL
> **返工完成时间**: 2026-03-12 22:45

---

## 一、返工触发原因

Compliance Officer Kior-B 在初次审查中识别出 **6 个问题**，其中：
- **CRITICAL (Blocker)**: 2 个
- **HIGH (Blocker)**: 1 个
- **MEDIUM**: 1 个
- **LOW**: 2 个

核心问题集中在：
1. **机制泄露风险**: 8 Gate Health 和 Evidence Coverage 模块存在暴露规则阈值、权重、探针逻辑的潜在设计入口
2. **未来扩展风险**: 缺少对渐进式机制暴露的约束
3. **语义混淆**: Permit readiness 与 Permit issuance 概念混同
4. **叙事风险**: Forge 导航和空状态 CTA 存在 builder 叙事倾向

---

## 二、返工修复明细

### 2.1 SF_FE02_001 (CRITICAL) - 8 Gate Health 机制泄露

**问题**: 展开项包含"触发规则数"，虽注明"只展示数量"，但没有明确禁止在展开态中暴露规则细节、阈值或权重。

**修复**:
- ✅ 删除"触发规则数"字段
- ✅ 新增"受影响资产数量"字段（纯结果态）
- ✅ 强化"禁止展示"部分，从 4 项扩展至 9 项：
  - 规则阈值 (threshold)
  - 规则权重 (weight)
  - 规则细节或规则表达式 (rule expression)
  - 判定逻辑说明 (decision logic)
  - 触发规则详情 (triggered rule details)
  - 规则与 Gate 的映射关系 (rule-to-gate mapping)
  - 探针代码或探针信息 (probe code/info)
  - 判定路径可视化 (decision path visualization)
- ✅ 新增"允许展示"部分，明确仅允许纯数字统计（不关联具体内容）

**文件位置**: [Section 3.4.2](T-FE-02_dashboard_spec.md:210-243)

---

### 2.2 SF_FE02_002 (CRITICAL) - Evidence Coverage 机制泄露

**问题**: 展示"no evidence/summary-only/sufficient evidence 分布"，可能暴露证据收集机制与判定逻辑。

**修复**:
- ✅ 明确"no evidence/summary-only/sufficient evidence 分布"为"仅结果态分类，不得展示分类依据"
- ✅ 新增 7 项禁止展示项：
  - Evidence 内部内容 (摘要之外)
  - 证据收集方法 (evidence collection method)
  - 证据权重计算方式 (evidence weight calculation)
  - 证据来源探针信息 (evidence source probe info)
  - 证据分类依据 (evidence classification criteria)
  - 证据强度判定逻辑 (evidence strength decision logic)
  - 证据收集路径可视化 (evidence collection path visualization)
- ✅ 新增"允许展示"部分，明确仅允许充分性/完整性层展示

**文件位置**: [Section 3.4.4](T-FE-02_dashboard_spec.md:269-297)

---

### 2.3 SF_FE02_003 (HIGH) - 未来扩展约束缺失

**问题**: Layer 3 禁止列表没有约束未来扩展边界，存在渐进式滑向机制暴露的风险。

**修复**:
- ✅ 新增 Section 3.7.2 "未来扩展约束"
- ✅ 明确 6 类硬约束（以禁止语气，非建议）：
  1. **禁止渐进式机制暴露**: 不得通过"渐进式添加细节"方式逐步暴露机制信息
  2. **规则详情禁止**: 永远不得在 Dashboard 中添加"规则详情"展开或页面
  3. **判定逻辑可视化禁止**: 永远不得在 Dashboard 中添加"判定逻辑"可视化或流程图
  4. **探针过程禁止**: 永远不得在 Dashboard 中添加"探针过程"展示
  5. **权重与阈值禁止**: 永远不得在 Dashboard 中添加"权重"或"阈值"数值展示
  6. **B Guard 复审要求**: 任何新增"详情"展开功能必须先通过 B Guard 复审
- ✅ 提供 4 个违规示例（禁止）和 3 个合规示例（允许）

**文件位置**: [Section 3.7.2](T-FE-02_dashboard_spec.md:432-501)

---

### 2.4 SF_FE02_004 (MEDIUM) - Permit readiness 语义混淆

**问题**: "Ready for Permit" 辅助文案"audit passed, waiting release approval"可能混同 Permit readiness 与 Permit issuance。

**修复**:
- ✅ 将辅助文案从"waiting release approval"改为"eligible for permit issuance"
- ✅ 明确区分：
  - "Ready for Permit" = 资产已通过审计，符合 Permit 申请条件
  - "Permit issuance" = 实际签发 Permit 的动作

**文件位置**: [Section 3.4.1](T-FE-02_dashboard_spec.md:200)

---

### 2.5 SF_FE02_005 (LOW) - Forge 次级入口未明确

**问题**: Top Nav 中 Forge 导航项没有明确标记为次级入口。

**修复**:
- ✅ 新增"导航视觉权重分级"部分
- ✅ 明确 Forge 为"次级视觉权重"
- ✅ UI 层处理要求：Forge 必须在视觉上弱化，不得与三页主链使用同等视觉强调

**文件位置**: [Section 3.9.1](T-FE-02_dashboard_spec.md:520-530)

---

### 2.6 SF_FE02_006 (LOW) - 空状态 CTA builder 叙事风险

**问题**: "Go to Registry" CTA 可能引导用户进入资产创建流程，存在 builder 叙事风险。

**修复**:
- ✅ 主 CTA 保持为"Read Governance Guidelines"
- ✅ 次要 CTA 改为"View Audit Examples"
- ✅ 明确禁止直接引导进入创建流程

**文件位置**: [Section 3.6.1](T-FE-02_dashboard_spec.md:358-367)

---

## 三、返工统计

| 指标 | 数值 |
|-----|------|
| 修复问题总数 | 6 |
| CRITICAL 问题修复 | 2 |
| HIGH 问题修复 | 1 |
| MEDIUM 问题修复 | 1 |
| LOW 问题修复 | 2 |
| 新增 Section | 1 (Section 3.7.2) |
| 新增/修改行数 | 约 180 行 |
| 修改文件数 | 1 (dashboard_spec.md) |

---

## 四、修复验证清单

### 4.1 机制泄露防御验证

| 验证项 | 状态 | 证据 |
|-------|------|------|
| 8 Gate Health 无规则详情入口 | ✅ | Section 3.4.2 禁止展示 9 项 |
| 8 Gate Health 无阈值/权重入口 | ✅ | Section 3.4.2 禁止展示明确 |
| Evidence Coverage 无收集机制入口 | ✅ | Section 3.4.4 禁止展示 7 项 |
| 未来扩展有明确硬约束 | ✅ | Section 3.7.2 禁止渐进式暴露 |

### 4.2 语义清晰度验证

| 验证项 | 状态 | 证据 |
|-------|------|------|
| Permit readiness 与 issuance 分离 | ✅ | Section 3.4.1 辅助文案修订 |
| 空状态 CTA 无 builder 倾向 | ✅ | Section 3.6.1 CTA 修订 |

### 4.3 视觉权重验证

| 验证项 | 状态 | 证据 |
|-------|------|------|
| Forge 为次级入口 | ✅ | Section 3.9.1 视觉权重分级 |

---

## 五、EvidenceRef 清单

| ID | 类型 | 位置 | 描述 |
|----|------|------|------|
| EV-FE02-R1-001 | LINE_REF | :210-243 | Section 3.4.2 R1修订 |
| EV-FE02-R1-002 | LINE_REF | :269-297 | Section 3.4.4 R1修订 |
| EV-FE02-R1-003 | LINE_REF | :432-501 | Section 3.7.2 R1新增 |
| EV-FE02-R1-004 | LINE_REF | :200 | Section 3.4.1 R1修订 |
| EV-FE02-R1-005 | LINE_REF | :520-530 | Section 3.9.1 R1修订 |
| EV-FE02-R1-006 | LINE_REF | :358-367 | Section 3.6.1 R1修订 |
| EV-FE02-R1-007 | LINE_REF | :503-521 | Section 四 R1新增 |

---

## 六、请 Reviewer / Compliance 复核的重点

### 6.1 CRITICAL 问题复核

1. **Section 3.4.2 (8 Gate Health)**: 确认"触发规则数"已删除，禁止展示项已扩展至 9 项，新增"受影响资产数量"为纯结果态字段。

2. **Section 3.4.4 (Evidence Coverage)**: 确认"no evidence/summary-only/sufficient evidence 分布"明确标注为"仅结果态分类，不得展示分类依据"，新增 7 项禁止展示项。

### 6.2 HIGH 问题复核

3. **Section 3.7.2 (未来扩展约束)**: 确认新章节已添加，6 类硬约束以禁止语气（非建议）陈述，包含违规/合规示例。

### 6.3 MEDIUM 问题复核

4. **Section 3.4.1 (Ready for Permit)**: 确认辅助文案已修改为"eligible for permit issuance"，明确区分 readiness 与 issuance。

### 6.4 LOW 问题复核

5. **Section 3.9.1 (Top Nav)**: 确认新增"导航视觉权重分级"，Forge 明确为次级视觉权重。

6. **Section 3.6.1 (空状态)**: 确认 CTA 已修改为"Read Governance Guidelines"，避免引导进入创建流程。

---

## 七、版本信息

**文档版本**: v1.1 (R1 合规返工修订)
**最后更新**: 2026-03-12
**返工执行者**: vs--cc1
**返工触发者**: Kior-B (Compliance)

---

**结论**: 所有 Compliance 指出的 6 个 required_changes 已全部修复，无新增设计范围，无任务边界扩大，未重新引入 builder-first 叙事。
