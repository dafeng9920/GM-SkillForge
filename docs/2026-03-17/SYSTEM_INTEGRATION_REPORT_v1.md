# GM-SkillForge 系统整合报告 v1

## 1. 总结

本次吸收文档包括：

- `codex-prompts/00_read_first.md`
- `codex-prompts/01_codex_system_integration_prompt_v1.md`
- `codex-prompts/02_codex_execution_constraints_appendix_v1.md`
- `skills-generation-architecture/《系统宪法》V1.md`
- `skills-generation-architecture/《模块权限清单 v1》.md`
- `skills-generation-architecture/《治理冻结清单 + 生产主线待建清单》v1.md`
- `skills-generation-architecture/《GM-SkillForge 日终收口检查模板 v1》.md`
- `skills-generation-architecture/《5层创建流程的数据结构清单 v1》.md`
- `skills-generation-architecture/5层流程.md`
- `skills-generation-architecture/架构纠偏文档 v1.md`
- `skills-generation-architecture/skill-creator和五层构建的区别.md`
- `skills-generation-architecture/skill交付形态.md`
- `skills-generation-architecture/商用skill的构建流程.md`

当前系统的整合结论为：

- 已形成 `生成线 + 审计线 + 打包层 + 编排层` 的清晰分层
- 当前唯一受保护的生产主链路成立
- `nl--skill` 应被明确收口为 `Intent Compiler`
- `skill-creator` 只属于后段封装/打包/交付层
- 最终裁决权只属于 `Kernel / Governor / Deterministic Kernel`

本次整合不涉及：

- 冻结文档正文改写
- 主链路顺序变更
- 正式写口改动
- 审计归属变更
- `skill-creator` 角色边界变更

---

## 2. 文档归类矩阵

| 文档名 | 分类 | 约束层 | 角色 | 建议归位路径 | 是否冻结 |
| --- | --- | --- | --- | --- | --- |
| `《系统宪法》V1.md` | 宪法与冻结规则 | 最高约束 | 系统宪法 | `docs/frozen/constitution/` | 是 |
| `《模块权限清单 v1》.md` | 宪法与冻结规则 | 权限边界 | 模块写权/审批权 | `docs/frozen/governance/` | 是 |
| `《治理冻结清单 + 生产主线待建清单》v1.md` | 宪法与冻结规则 | 阶段策略 | 治理冻结/生产主攻 | `docs/frozen/strategy/` | 是 |
| `《GM-SkillForge 日终收口检查模板 v1》.md` | 宪法与冻结规则 | 执行制度 | 日终检查模板 | `docs/checks/` | 是 |
| `《5层创建流程的数据结构清单 v1》.md` | 生产主线 | 对象层 | 五个承重对象 | `docs/production/` | 半冻结 |
| `5层流程.md` | 生产主线 | 流程层 | 主链骨架 | `docs/production/` | 半冻结 |
| `架构纠偏文档 v1.md` | 生产主线 | 架构层 | 角色归位/纠偏 | `docs/production/architecture/` | 半冻结 |
| `skill-creator和五层构建的区别.md` | 包装与交付关系 | 交付层 | 打包层边界 | `docs/delivery/` | 半冻结 |
| `skill交付形态.md` | 包装与交付关系 | 交付层 | Draft/Candidate/Released 交付节奏 | `docs/delivery/` | 半冻结 |
| `商用skill的构建流程.md` | 商用扩展层 | 商用后置 | Commercial-grade 参考 | `docs/commercial-extension/` | 半冻结 |

---

## 3. 冲突与去重结果

### 冲突 1：目录中缺少 `00_index.md`

- 现状：提示词要求优先按 index 顺序读取，但目录下无该文件
- 当前处理：按 `00_read_first.md` 的 fallback 规则改用文件名前缀/字典序读取
- 建议：补一个正式 `00_index.md`
- 不允许丢失的语义：读取顺序必须受控，不允许随意跳读

### 冲突 2：`商用skill的构建流程` 易抢当前主线

- 现状：其内容包含 Deterministic Core、韧性、运维等商用要求
- 风险：若直接纳入当前主链，会把 5 层创建流程与商用扩展混为一体
- 处理建议：明确挂为 `商用扩展层（仅记录，不抢当前主线）`
- 保留版本：当前主链优先，商用扩展后置

### 冲突 3：`nl--skill` 的角色历史漂移

- 旧口径：近似“最终执行系统”
- 新口径：`Intent Compiler`
- 优先版本：`《系统宪法》V1` + `架构纠偏文档 v1`
- 必保语义：AI 只能生成草案/候选，不拥有最终发布权

### 冲突 4：`Build Validation` 与治理验证容易混淆

- 风险：把创建侧自检误写成治理通过
- 处理建议：保留双名，但在所有正式文档中明确：
  - `BuildValidationReport != Governance Validation`
  - `Build Validation` 只服务于 handoff，不服务于最终裁决

---

## 4. 统一术语表

| 术语 | 统一定义 | 备注 |
| --- | --- | --- |
| `IntentDraft` | 需求的结构化意图草案 | 生成线对象 |
| `ContractBundle` | 输入/输出/状态/错误/触发/证据的合同包 | 生成线对象 |
| `CandidateSkill` | 依据合同生成的候选 skill 本体 | 非正式发布物 |
| `BuildValidationReport` | 创建侧最小自检报告 | 不等于治理验证 |
| `DeliveryManifest` | 交给打包层的标准输入物 | 不等于 Release Permit |
| `Draft` | 草案对象 | 可修改，不可发布 |
| `Candidate` | 候选对象 | 可进入验证 |
| `Validated` | 已通过治理验证的对象 | 只能由 `validator` 写入 |
| `Released` | 正式产物 | 只能由 `release-manager` 写入 |
| `Deprecated` | 已弃用 | 生命周期后段状态 |
| `Tombstoned` | 已下线且保留追溯 | 生命周期后段状态 |
| `Kernel / Governor / Deterministic Kernel` | 最终裁决中心 | 语义等价，可保留双名说明 |
| `skill-creator` | 标准 skill 目录封装与打包器 | 非创建引擎、非审计器 |
| `Orchestrator / n8n` | 调度、路由、触发、重试、审批编排层 | 非最终裁决层 |
| `EvidenceRef` | 证据引用对象 | 审计线核心对象 |
| `AuditPack` | 最小审计交付物 | 审计线输出 |
| `Publish Permit / Release Decision` | 内核发布裁决对象 | 不属于打包层 |

---

## 5. 系统主链路对齐结果

当前主链路固定为：

`需求输入 → Intent Draft → Contract Draft → Candidate Skill → Build Validation → Delivery Manifest → skill-creator / 打包层`

正式发布与审计顺序固定为：

`Delivery Manifest → 主审计 / Review / Release Decision / AuditPack`

各步归属如下：

| 步骤 | 归属层 |
| --- | --- |
| 需求输入 | 入口层 |
| Intent Draft | 生成线 |
| Contract Draft | 生成线 |
| Candidate Skill | 生成线 |
| Build Validation | 生成线末端 |
| Delivery Manifest | 生成线 -> 打包层 handoff |
| skill-creator / 打包层 | 打包层 |
| 主审计 / Review / Release / AuditPack | 审计线 |

结论：

- 当前所有有效整合都必须强化这条主链
- 非主链内容只能后置或挂到商用扩展层

---

## 6. 生成线 / 审计线 / 打包层 / 编排层的边界图

### 生成线

负责：

- Intent
- Contract
- Candidate
- Build Validation
- Delivery Handoff

不能做：

- 最终发布
- `released`
- `validated`
- `gate_result`
- 最终审计通过

### 审计线 / 治理线

负责：

- Gate
- Risk Decision
- EvidenceRef
- AuditPack
- Review
- Release
- Revision / Tombstone / At-time

不能做：

- 吞掉生产线主责
- 反向取代 Intent / Contract / Candidate 生产

### 打包层

负责：

- `skill-creator`
- 标准技能包封装
- `skill.zip` 交付

不能做：

- 最终裁决
- 主审计
- 创建流程前段

### 编排层

负责：

- 触发
- 调度
- 路由
- 通知
- 重试
- 人工审批流程编排

不能做：

- 最终发布
- 最终 gate 决策
- 正式 evidence 改写

最终写权：

- 只属于 `Kernel / Governor`

---

## 7. 需要落地成代码或配置的对象

### 已足够落成代码对象 / schema 的

- `IntentDraft`
- `ContractBundle`
- `CandidateSkill`
- `BuildValidationReport`
- `DeliveryManifest`
- `RunRecord`
- `ReleaseRecord`

### 应落成 schema / config 的

- `input_schema`
- `output_schema`
- `state_schema`
- `error_schema`
- `trigger_spec`
- `evidence_spec`
- handoff 输入输出对象

### 应落成保护性配置/约束的

- 正式写口保护规则
- 层级写者白名单
- candidate / validation / review / release handoff 约束

### 保持文档约束即可的

- 宪法
- 治理冻结策略
- 日终收口模板
- `skill-creator` 角色边界

---

## 8. 高风险点

1. `nl--skill` 名义降级但事实性仍越权写正式状态
2. `Build Validation` 与治理审计混线
3. `skill-creator` 被继续误用为主创建引擎或主审计器
4. `n8n / orchestrator` 通过重命名事实性写入正式状态
5. `商用skill的构建流程` 抢当前主链，导致 5 层与 5+3 混合
6. 正式写口未真正收口到授权模块
7. 生产态状态机与治理态状态机未分离
8. 缺少正式 index，后续读取/执行顺序易漂移
9. Draft / Candidate / Released 在文档和代码中命名漂移
10. 文档长期不归位，整合成果停留在聊天结论

---

## 9. 最小整合动作清单（P0 / P1 / P2）

### P0

- 补正式 `00_index.md` 或等价入口
- 产出 `DOC_CLASSIFICATION_MATRIX_v1.md`
- 产出 `TERMINOLOGY_MAP_v1.md`
- 产出 `HANDOFF_INTERFACES_v1.md`
- 把正式写口标红并声明只读/只写归属

### P1

- 将 5 个生产对象落成 schema / model 草案目录
- 明确 candidate / validation / review / release handoff 接口
- 把 `skill交付形态` 定位为交付节奏文档，不抢主链
- 把 `商用skill的构建流程` 定位为商用扩展参考

### P2

- 接上日终收口模板
- 为冻结文档增加只读/冻结标记
- 再决定哪些对象进入 `contracts/`、`orchestration/`、`kernel/`

---

## 10. 最终判定

- 当前是否已经具备“生成与审计双线不耽误”的架构基础  
  - **是。**
- 还差的最短板是什么  
  - **文档归位与对象落位还未形成正式系统文档。**
- 下一步最应该动手整合的 1 件事是什么  
  - **把聊天结论变成正式整合文档，并锁定 4 个 handoff 接口。**
