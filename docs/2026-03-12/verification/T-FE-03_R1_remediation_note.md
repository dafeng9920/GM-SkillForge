# T-FE-03 R1 返工修订说明

> **任务 ID**: T-FE-03
> **返工轮次**: R1
> **执行者**: Antigravity-1
> **审查者**: vs--cc2
> **合规官**: Kior-C
> **日期**: 2026-03-12

---

## 一、返工背景

### Review 决策
- **decision**: REQUIRES_CHANGES
- **reviewer**: vs--cc2
- **reviewed_at**: 2026-03-12T20:00:00Z

### Compliance 决策
- **decision**: PASS
- **compliance_officer**: Kior-C
- **reviewed_at**: 2026-03-12T20:30:00Z

**说明**: Review 发现的问题属于规格完善问题，不触及 B Guard Zero Exception Directives，因此 Compliance 保持 PASS。

---

## 二、Review 发现的问题

### FE03-002 (HIGH)
- **位置**: Section 3.3 模块详细规格
- **问题**: 页面骨架中引用了 `Contract / Control Snapshot` 模块，但规格书中缺少对该模块的详细定义
- **参考**: 线框图 L719-735 定义了该模块应包含的内容

### FE03-001 (MEDIUM)
- **位置**: Section 2.1 Input Constraints
- **问题**: 引用了不存在的文件 `docs/2026-03-12/T-FE-03_三权分发提示词.md`
- **说明**: 该文件在 R1 阶段已存在，但原始提交时可能因时间差导致引用失效

---

## 三、R1 修复措施

### 修复 FE03-002 (HIGH)

**新增内容**: Section 3.3 [7.5] Contract / Control Snapshot

**包含字段**:
- Contract Summary (合同摘要)
- Constitution Version (宪法版本号)
- Rule Pack Version (规则包版本号)
- ControlSpec Version (控制规格版本号)
- Linked Manifest (关联清单 ID)
- Audit Scope (审计范围说明)

**与其他模块的关系**:
- 与 Decision Summary: Decision Summary 说明裁决结果，Contract/Control Snapshot 说明裁决依据
- 与 8 Gate Details: 8 Gate 说明具体哪道门被阻断，Contract/Control Snapshot 说明这些门的规则版本
- 与 Hash & Reproducibility: Hash 说明裁决的唯一性，Contract/Control Snapshot 说明裁决的治理框架

**禁止事项**:
- ❌ 不得展示规则具体内容（Rule 规则细节属于 Layer 3）
- ❌ 不得展示判定阈值和权重（属于 Layer 3）
- ❌ 不得展示内部模块拓扑（属于 Layer 3）

**文件位置**: `docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md:478-550`

### 修复 FE03-001 (MEDIUM)

**更新内容**: Section 2.1 Input Constraints

**新增引用**:
- `docs/2026-03-12/verification/T-FE-03_gate_decision.json` (R1 复审)
- `docs/2026-03-12/verification/T-FE-03_compliance_attestation.json` (R1 复审)

**文件位置**: `docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md:44-56`

---

## 四、未改变的合规边界

R1 返工未破坏以下已通过 Compliance 的约束:

1. ✅ 仍然维持"结论 → 原因 → 证据 → 修复"不可逆顺序
2. ✅ Evidence/Rule/Gate/Gap 仍然分离呈现
3. ✅ Layer 3 绝对禁止前端呈现区定义完整
4. ✅ EvidenceRef visible/summary-only/restricted 三级可见性保留
5. ✅ Red Lines 与 Fixable Gaps 仍然左右分栏，语义未混淆
6. ✅ 三权分立边界仍然通过 Power Boundary 显式展示
7. ✅ Hash / Revision / Decision binding 仍然完整
8. ✅ API 层裁剪责任明确，禁止前端裁剪

---

## 五、交付物更新

### 更新的文件
1. `docs/2026-03-12/verification/T-FE-03_audit_detail_spec.md`
   - 新增 85 行（Section 3.3 [7.5] Contract / Control Snapshot）
   - 更新 Section 2.1 Input Constraints
   - 更新交付物验收清单（新增第 13 项）
   - 更新文档版本为 v1.1 (R1)

2. `docs/2026-03-12/verification/T-FE-03_execution_report.yaml`
   - 更新状态为 "R1 返工完成"
   - 记录 R1 返工修复点
   - 新增 R1 相关 EvidenceRef

3. `docs/2026-03-12/verification/T-FE-03_R1_remediation_note.md` (本文件)
   - R1 返工说明文档

### 新增 EvidenceRef
- EV-TFE03-R1-001: Contract / Control Snapshot 模块规格
- EV-TFE03-R1-002: 线框图 L719-735 参考
- EV-TFE03-R1-003: gate_decision.json 参考
- EV-TFE03-R1-004: compliance_attestation.json 参考

---

## 六、请 Reviewer 复核的重点

1. **R1 新增的 [7.5] Contract / Control Snapshot 模块规格是否完整**
   - 字段定义是否齐全
   - 与其他模块的关系是否明确
   - 禁止事项是否清晰

2. **Contract / Control Snapshot 是否触及 Layer 3 禁止区**
   - 是否只展示版本号和摘要
   - 是否未展开规则细节
   - 是否未暴露判定阈值和权重

3. **Input Constraints 文件引用是否已修正**
   - 是否增加了 gate_decision 和 compliance_attestation 引用
   - 引用路径是否正确

4. **原有合规边界是否保持完整**
   - 结论先行是否仍然维持
   - 红线与可修复项分离是否仍然明确
   - EvidenceRef 可见性级别是否仍然保留

---

**R1 返工完成时间**: 2026-03-12T21:00:00Z
