# Skill功能现状（执行版）

**Created:** 2026-03-03 14:55:10
**Refactored:** 2026-03-03
**Status:** 执行就绪

---

## 1. TL;DR（10行精要）

GM-SkillForge核心定位：从自然语言到L3级可审计交付物的工业生产线。主要功能分三层：
- **L3层（已达成）**：contracts-first + 8 Gate裁决 + EvidenceRef闭环 + AuditPack + Permit签发
- **L4层（规划中）**：自然语言输入 → 完整Skill交付蓝图（限定域14天MVP）
- **L5层（愿景）**：泛化多Agent自治与生态治理

不可替代性在**裁决权+证据闭环+复现口径锁死**三重约束的生成能力，而非纯生成。

关键决策：采用三哈希（demand_hash/contract_hash/decision_hash）作为复现与迭代判据。

---

## 2. 当前能力地图（L3/L4/L5分层）

### L3层：商用基线（已达成）
**核心能力：**
- contracts-first需求压缩（输入/输出/约束/Gate计划/L3交付物）
- 8 Gate固定主链（intake_repo→license_gate→repo_scan_fit_score→draft_skill_spec→constitution_risk_gate→scaffold_skill_impl→sandbox_test_and_trace→pack_audit_and_publish）
- L3审计标准（Contracts+Static Scan，不执行代码，强制repo_url+commit_sha）
- EvidenceRef闭环（hash+locator+tool_revision）
- AuditPack产出（manifest/policy_matrix/decisions/checksums）
- Permit签发机制（绑定intent_id+revision+audit_pack_hash+expiration）

**内核职责（不可外包）：**
- GateDecision（PASS/FAIL）
- Level判定
- L3达标裁决
- at-time/tombstone复现口径

**Skill职责（可迭代）：**
- scan/spec draft/static denylist/scaffold/pack辅助

### L4层：自然语言到全套交付（14天MVP规划）
**目标：**
限定域NL输入 → 完整可运行Skill框架 + n8n workflow + L3 AuditPack + Permit

**限定4类模式：**
1. 定时轮询 → 拉取数据 → 处理 → 写入系统
2. Webhook → 处理 → 写入/通知
3. 邮件/附件监控 → LLM分析 → 存储/通知
4. 单步LLM调用 → 格式化输出 → 写入/通知

**验收标准：**
- 一次通过Gate率≥80%
- L3资产清单100%齐全
- 复现性验证通过（三哈希一致）

### L5层：泛化生态（愿景）
- 多Agent自治编排
- 动态规划与跨域权限
- 治理层协议基础设施

---

## 3. 已达成共识（12条）

1. **系统定位**：不是"写代码工具"，而是"可审计、可裁决、可复现、可版本化沉淀的工程生产线"

2. **L3为商用起点**：审计范围=Contracts+Static Scan，必须产出AuditPack，强制repo_url+commit_sha

3. **8 Gate固定主链**：v0锁死顺序，不可跳过或重排

4. **内核/Skill分层**：内核独占裁决权（GateDecision/Level判定/Permit签发），Skill负责生成产出

5. **三哈希口径**：demand_hash（需求）、contract_hash（合同）、decision_hash（裁决）作为复现与迭代判据

6. **L3复现定义**：三哈希一致=可复现；不追求逐字符复刻，只要求语义级稳定

7. **L3迭代定义**：三哈希变化必须伴随diff+rationale+tombstone

8. **Permit强制绑定**：无Permit不允许发布；Permit必须绑定三哈希+audit_pack_hash+revision

9. **交付完整性**：必须产出Blueprint+Skill+n8n+Evidence+AuditPack+Permit六项

10. **复现不是伪命题**：通过"冻结口径"（Contract锁死）实现语义级复现

11. **生成能力是必要条件**：但不构成护城河；真正壁垒是"被约束的生成"

12. **三权分立原则**：生成权（AI/Skills）vs裁决权（内核独占）vs执行发布权（n8n/外部，需Permit）

---

## 4. 未决问题（10条）

1. **NL→Contract映射稳定性**：如何保证语义解析的一致性≥90%？

2. **澄清机制平衡**：澄清过重导致流失vs过轻导致合同错误固化的临界点在哪？

3. **RAG推断补全边界**：隐含需求自动补充到什么程度不越界？

4. **生成成功率基线**：70%成功率是否为用户体验断裂阈值？

5. **Gate规则版本管理**：如何防止插件篡改或绕过裁决规则？

6. **EvidenceRef存储策略**：强hash+不可变存储的技术选型未定

7. **受限域扩域时机**：80%成功率稳定后如何逐步放开约束？

8. **需求锻造子闭环**：DemandForge Gate是否需要独立AuditPack？

9. **三哈希计算性能**：canonicalize与hash计算的开销如何优化？

10. **多语言支持边界**：Python only策略是否长期限制能力域？

---

## 5. 决策清单（Decision Log）

| 决策 | 原因 | 影响 |
|------|------|------|
| 采用三哈希口径 | 消除复现定义的哲学争论，转化为工程验收 | 所有L3产出必须包含三哈希，Permit绑定校验 |
| 限定域14天MVP | 避免过度泛化导致成功率崩盘 | 前14天只支持4类自动化模式，不扩域 |
| L3=商用基线 | 企业付费发生在可裁决+可复现层 | 所有发布必须过L3 Gate，签发Permit |
| 8 Gate固定主链 | 裁决权分散会侵蚀系统主权 | v0锁死顺序，禁止跳过或重排 |
| Permit强制绑定 | 无放行令牌会形成治理漏洞 | n8n/外部系统必须验Permit才能发布 |
| 内核独占裁决权 | 生成层与裁决层耦合会导致审计失真 | Skill只能提交证据，内核负责PASS/FAIL |
| 语义级复现定义 | 逐字符复刻不现实也不必要 | 允许注释/变量名/自然语言表述变化 |
| delivery_completeness_gate | 防止半成品发布 | pack_audit_and_publish增加清单硬校验 |
| hash_keysets.yml配置化 | 避免口径漂移，便于版本演进 | validate.py从配置生成校验逻辑 |
| 三权分立架构 | 分权带来长期稳定性和可扩展性 | 明确生成/裁决/执行权边界 |

---

## 6. 明日执行计划（按优先级）

### P0（必须完成）
1. **创建hash_keysets.yml配置**
   - 定义demand_hash/contract_hash/decision_hash的keyset
   - 明确黑名单字段（timestamp/summary等）
   - 路径：`orchestration/hash_keysets.yml`

2. **实现canonicalize.py工具**
   - 统一canonical_json逻辑（UTF-8/sort_keys/separators）
   - 数组稳定排序
   - 路径：`tools/canonicalize.py`

3. **实现hash_calc.py工具**
   - 输出三哈希
   - 与hash_keysets.yml联动
   - 路径：`tools/hash_calc.py`

4. **validate.py增加硬校验**
   - 三哈希写入+一致性校验
   - Permit绑定校验
   - 路径：`skillforge-spec-pack/skillforge/src/orchestration/validate.py`

### P1（重要但可延后）
5. **pack_audit_and_publish增加交付清单检查**
   - Blueprint/Skill/n8n/Evidence/AuditPack/Permit缺一FAIL
   - 路径：`skillforge-spec-pack/skillforge/src/nodes/pack_publish.py`

6. **定义diff/rationale/tombstone结构**
   - 路径：`audit/diffs/`, `audit/rationale/`, `audit/tombstones/`

### P2（规划阶段）
7. **DemandSpec v0 schema定义**
   - 4类mode的槽位结构
   - 路径：`specs/demand_spec_v0.schema.json`

8. **Constitution Contract v0模板**
   - goals/io/controls/quality/risk/gate_plan字段
   - 路径：`specs/con_contract_v0.schema.json`

---

## 7. 风险与应对

| 风险 | 触发条件 | 熔断动作 |
|------|----------|----------|
| NL→Contract映射不稳定 | 一次通过率<70% | 收缩能力域，增加澄清强制度 |
| 三哈希计算不一致 | 发现同输入不同hash | 检查canonicalize实现，强制单一入口 |
| 交付完整性Gate失效 | 发现半成品发布 | 立即回滚Permit，检查清单逻辑 |
| Gate规则被绕过 | 发现跳过Gate的发布路径 | 禁止该路径，强制所有发布过内核 |
| EvidenceRef断链 | 复现验证失败 | 暂停发布，修复证据存储机制 |
| 生成成功率崩盘 | 扩域后成功率<60% | 回滚到上一个稳定版本，停止扩域 |
| RAG推断过度 | 用户投诉隐含需求误加 | 收束RAG置信度阈值，增加人工确认 |
| Permit校验被绕过 | 发现无Permit发布成功 | 立即封堵漏洞，审查所有发布渠道 |
| 三权边界模糊 | 发现Skill直接做裁决 | 强制架构审查，重写边界定义 |
| 14天MVP延期 | 单日验收连续FAIL | 重新评估边界，削减非必要功能 |

---

## 8. 附录：术语表

**DemandHash**
- 定义：DemandSpec canonical hash（需求槽位填充后的结构化哈希）
- 计算对象：mode/trigger/sources/transforms/destinations/constraints/acceptance.success_criteria
- 排除字段：summary/clarifications_needed/所有时间戳
- 用途：需求复现判据

**ContractHash**
- 定义：Constitution keyset canonical hash（宪法合同关键字段哈希）
- 计算对象：goals/io/controls/quality/risk/gate_plan
- 排除字段：at_time/nl_text_hash/解释性文本
- 用途：合同复现判据

**DecisionHash**
- 定义：GateDecision canonical hash（8 Gate裁决序列哈希）
- 计算对象：gate_name/status/level/error_code/issue_keys/required_changes/evidence_refs
- 排除字段：reason/next_action自然语言/耗时/时间戳
- 用途：裁决复现判据

**Permit**
- 定义：放行令牌，绑定intent_id+revision+audit_pack_hash+三哈希+expiration
- 签发权：内核独占
- 校验要求：所有发布必须验Permit

**EvidenceRef**
- 定义：证据引用，包含hash+locator+tool_revision
- 用途：可复核证据链，支持at-time回溯

**AuditPack**
- 定义：L3审计包，包含manifest/policy_matrix/decisions/checksums
- 最低要求：Contracts+Static Scan，不含执行代码

**Tombstone**
- 定义：弃用/替换版本的元数据，指向旧revision
- 用途：支持at-time复现旧版本

**Revision**
- 定义：版本标识，递增或新hash
- 要求：变化必须伴随diff+rationale+tombstone

**at-time**
- 定义：特定时间点的复现能力
- 条件：同输入+同Contract版本+同工具规则版本→三哈希一致

---

## 9. 三个下一步PR建议

### PR#1: 三哈希基础设施
**标题**: feat(l3): implement three-hash foundation for reproducibility

**目标**:
- 建立demand_hash/contract_hash/decision_hash计算基础
- 为L3复现与迭代提供工程判据
- 避免口径漂移

**变更文件列表**:
- `orchestration/hash_keysets.yml`（新增）
- `tools/canonicalize.py`（新增）
- `tools/hash_calc.py`（新增）
- `skillforge-spec-pack/skillforge/src/orchestration/validate.py`（修改）

**验收标准**:
- [ ] hash_keysets.yml定义完整keyset与黑名单
- [ ] canonicalize.py通过JSON schema验证测试
- [ ] hash_calc.py输出三哈希且可重算一致
- [ ] validate.py增加三哈希校验且FAIL条件明确
- [ ] 所有新函数单元测试覆盖率≥80%

---

### PR#2: Permit强制绑定与交付完整性Gate
**标题**: feat(l3): enforce permit binding and delivery completeness gate

**目标**:
- 将Permit绑定三哈希+audit_pack_hash
- 防止半成品发布
- 封死发布门禁

**变更文件列表**:
- `skillforge-spec-pack/skillforge/src/nodes/pack_publish.py`（修改）
- `schemas/permit.schema.json`（新增）
- `skillforge-spec-pack/skillforge/src/orchestration/engine.py`（修改）

**验收标准**:
- [ ] Permit必须包含demand_hash/contract_hash/decision_hash/audit_pack_hash/revision/expiration
- [ ] pack_publish增加六项清单检查（Blueprint/Skill/n8n/Evidence/AuditPack/Permit）
- [ ] 缺任一项必须FAIL并返回required_changes
- [ ] 发布流程强制校验Permit，无Permit直接拒绝
- [ ] 集成测试：完整交付+半成品拒绝各1个case

---

### PR#3: Diff/Rationale/Tombstone结构定义
**标题**: feat(l3): define iteration evidence structure (diff/rationale/tombstone)

**目标**:
- 支持L3可迭代要求
- 每次变更可解释可回溯
- 为未来审计提供证据链

**变更文件列表**:
- `specs/iteration_evidence_v0.md`（新增）
- `audit/diffs/.gitkeep`（新增）
- `audit/rationale/.gitkeep`（新增）
- `audit/tombstones/.gitkeep`（新增）
- `tools/diff_generator.py`（新增）
- `skillforge-spec-pack/skillforge/src/orchestration/validate.py`（修改）

**验收标准**:
- [ ] 迭代证据规范文档定义完整结构
- [ ] diff_generator.py生成demand_diff/contract_diff/decision_diff
- [ ] rationale模板至少包含：触发来源/IssueKey/摘要/影响面
- [ ] tombstone包含：旧revision/状态/复现可用性
- [ ] validate.py增加迭代校验：三哈希变化必须伴随完整证据
- [ ] 端到端测试：一次完整迭代+证据验证

---

**文档版本**: v0
**下一步**: 对齐Codex执行PR#1
**Owner**: GM-SkillForge Team
