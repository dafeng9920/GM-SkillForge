**SkillForge Stability Architecture**

**四种稳定设计总稿**

*面向 SkillForge / Codex 的系统设计与交付基线*

| **文档目的** | 将“结果稳定、流程稳定、交付稳定、治理稳定”收束为一套可实现、可验收、可交付的系统架构。 |
|--------------|----------------------------------------------------------------------------------------|
| **适用阶段** | L3 主链路收敛后，进入 L4 Continuous Audit / Long-Run Audit 设计阶段。                  |
| **面向对象** | 你本人、后续新账号、Codex、未来审计运行框架的开发与运营。                              |
| **核心结论** | 稳定不是一个指标，而是四类不同目标；必须分层实现、分层验证、分层交付。                 |

**总原则：**
对同一种“稳定”必须给出明确目标、独立模块、独立对象模型、独立验收指标，以及独立交付物；不能用一个模糊总词把它们混在一起。

# 1. 总体框架与总装逻辑

## 1.1 为什么要拆成四种稳定

用户口中的“稳”，实际可能指完全不同的诉求：有的人要同样输入得到同样输出，有的人要流程别卡死，有的人要交付格式一致，有的人要版本、授权、预算与残余风险始终可控。若系统只做一层“稳定性”而不分型，最终只能得到模糊监控，无法形成真正可实现、可收敛、可证明的能力。

## 1.2 四种稳定的定义

**结果稳定：**输出层稳定，关注结果一致性、可预测性、质量回归与关键字段漂移。

**流程稳定：**执行层稳定，关注多步流程、长时间运行、重试、恢复、状态漂移与异常定位。

**交付稳定：**产物层稳定，关注对象模型、证据、结论语言、模板与版本一致性。

**治理稳定：**控制层稳定，关注策略门槛、授权边界、版本治理、升级门槛、预算控制与飞轮蒸馏。

## 1.3 总装架构

**整个系统建议分成四层：**

**Capability Layer：**skill 本体，负责执行具体能力。

**Runtime Stability Layer：**实现结果稳定与流程稳定。

**Assurance Layer：**实现交付稳定。

**Governance Layer：**实现治理稳定。

其中 Capability 负责“做事”，Runtime 负责“做得稳”，Assurance
负责“交得清楚”，Governance 负责“长期不失控”。

# 2. 结果稳定设计

## 2.1 设计目标

保证相近输入在相近条件下得到尽量一致、可验证、可解释的输出。它不是追求绝对一致，而是压缩无意义漂移，并把关键输出锁进可校验契约。

## 2.2 需要控制的五件事

**输入标准化：**清洗、补默认值、统一上下文注入方式。

**能力边界固定：**skill 输入输出契约、风险字段、不可自由漂移字段。

**输出约束：**结构校验、业务规则校验、缺失字段检测、自洽检查。

**回归比较：**同输入多次输出、新旧版本输出差异、关键字段漂移。

**质量评分：**confidence、completeness、consistency、rule pass rate。

## 2.3 核心组件

InputNormalizer、SkillContractValidator、OutputSchemaValidator、ResultConsistencyChecker、RegressionComparator、QualityScorer。

## 2.4 关键数据对象

**NormalizedInput：**记录清洗后的输入、上下文包与标准化版本。

**OutputContract：**记录 skill 的 schema、必填字段、风险字段与版本。

**ResultEvaluation：**记录结构通过率、一致性分数、漂移标记与回归差异。

## 2.5 核心技术动作

必须强制 skill 输出带
schema；高风险字段必须结构化；升级前做回归比较；对相同输入进行抽样重复运行；关键结果必须有验证状态。

## 2.6 验收指标与交付

**验收指标：**结构通过率、高风险字段一致率、同输入偏差率、版本回归通过率、缺失字段率。

**对外交付：**输出一致率、关键字段稳定率、新旧版本差异摘要、规则校验通过比例。

# 3. 流程稳定设计

## 3.1 设计目标

保证多步流程、长时间运行和外部依赖波动条件下，流程仍可执行、可恢复、可观察、可归因。

## 3.2 需要控制的六件事

**状态机化：**明确步骤、状态、转移、失败状态与终止条件。

**错误恢复：**定义可重试错误、重试次数、backoff、checkpoint 与恢复点。

**健康监控：**step latency、error rate、stuck session、retry
storm、资源占用。

**异常分类：**区分 infra、network、dependency、logic、evidence。

**时间治理：**warm-up、steady-state、stress window、closure window。

**恢复标记：**恢复动作必须进入证据与时间线，不可无痕继续。

## 3.3 核心组件

ScenarioStateMachine、RetryPolicyEngine、CheckpointManager、RecoveryController、TelemetryMonitor、IncidentClassifier、TimePhaseController。

## 3.4 关键数据对象

**ScenarioRun：**记录 session、当前步骤、状态、重试次数与终态。

**Checkpoint：**记录关键状态快照与是否可恢复。

**Incident：**记录异常类别、严重度、触发时间、证据引用与恢复动作。

**TimePhase：**记录阶段类型、采样策略与告警阈值。

## 3.5 核心技术动作

必须显式 step 化；关键步骤 checkpoint
化；恢复后证据加标；长时间审计分阶段治理；自动发现 stuck
state；禁止无限重试。

## 3.6 验收指标与交付

**验收指标：**完整流程成功率、中断恢复率、平均恢复时间、长运行存活率、stuck
session 数量、恢复后成功率。

**对外交付：**连续运行曲线、异常恢复能力、关键阻塞点、阶段性异常统计。

# 4. 交付稳定设计

## 4.1 设计目标

让每次审计、每次 skill
评估、每次客户交付都具备统一对象模型、统一证据结构、统一结论语言与统一模板版本。

## 4.2 需要统一的五件事

**对象模型统一：**AuditSession、Finding、EvidenceItem、Incident、CaseVerdict、AuditPack。

**结论语言统一：**Signal、Finding、Reproduced Issue、Confirmed Defect。

**证据结构统一：**时间、环境、条件、证据类型、复现次数、替代解释。

**报告模板统一：**Owner View、Operator View、Client View。

**版本信息统一：**protocol version、template version、environment
profile、evidence level。

## 4.3 核心组件

EvidenceIndexer、VerdictFormatter、ReportComposer、AuditPackBuilder、TemplateVersionManager。

## 4.4 关键数据对象

**EvidenceItem：**证据 ID、时间戳、类型、文件引用、哈希、环境引用。

**Finding：**标题、触发条件、严重度、置信度、证据等级、替代解释、建议动作。

**CaseVerdict：**状态、置信等级、残余风险、结案原因、复测建议。

**AuditPack：**摘要、问题清单、证据索引、环境快照、模板版本与导出包引用。

## 4.5 核心技术动作

每条 finding
使用固定结构；每份报告使用固定模板；所有结论必须能回溯证据；不同角色看不同视图；报告可
diff；模板有版本号。

## 4.6 验收指标与交付

**验收指标：**字段完整率、结论标准化率、finding 与 evidence
关联率、模板一致率、客户驳回率。

**对外交付：**标准 AuditPack、统一裁决卡、可复核证据包、可比较版本报告。

# 5. 治理稳定设计

## 5.1 设计目标

让系统在 skill
数量增加、版本增加、场景增加后仍不失控：知道什么能上、什么要复测、什么不能做、什么要拦截、什么能进入飞轮。

## 5.2 需要控制的六件事

**策略门槛：**什么能上线，什么必须复测，什么必须长时间审计。

**版本治理：**版本号、变更记录、兼容性说明、废弃策略。

**范围控制：**授权目标、禁止动作、允许压力级别、证据保留策略。

**升级治理：**L3 到 L4、finding 到专项都必须过 gate。

**飞轮治理：**只允许蒸馏知识进入 Intelligence Store。

**残余风险管理：**未关闭问题、未排除解释、下一步建议。

## 5.3 核心组件

PolicyEngine、VersionRegistry、ScopeController、EscalationGate、KnowledgeDistiller、ResidualRiskTracker、BudgetGate。

## 5.4 关键数据对象

**ScopePolicy：**授权目标、禁止动作、压力轮廓、保留策略。

**SkillVersion：**版本、changelog、兼容性说明、废弃时间。

**EscalationCaseCard：**来源 finding、问题假设、触发条件、证据目标、stop
rule、out-of-scope、预算上限。

**DistilledPattern：**模式类别、误报提示、证据充分性规则、推荐动作。

**ResidualRisk：**未解决原因、剩余不确定性、是否需要复测。

## 5.5 核心技术动作

版本登记强制化；无授权不执行；高风险改动自动要求复测；升级专项必须有
case card；飞轮只吃裁决后的模式；预算超线可触发降采样或停案建议。

## 5.6 验收指标与交付

**验收指标：**未授权动作拦截率、高风险改动复测覆盖率、升级案件收敛率、残余风险关闭率、预算超限率、版本追踪完整率。

**对外交付：**上线前治理结论、版本与复测治理说明、残余风险说明、预算与范围控制记录。

# 6. 四种稳定的模块映射与实施优先级

## 6.1 模块映射总表

**结果稳定模块：**InputNormalizer、SkillContractValidator、OutputSchemaValidator、ResultConsistencyChecker、RegressionComparator、QualityScorer。

**流程稳定模块：**ScenarioStateMachine、RetryPolicyEngine、CheckpointManager、RecoveryController、TelemetryMonitor、IncidentClassifier、TimePhaseController。

**交付稳定模块：**EvidenceIndexer、VerdictFormatter、ReportComposer、AuditPackBuilder、TemplateVersionManager。

**治理稳定模块：**PolicyEngine、VersionRegistry、ScopeController、EscalationGate、KnowledgeDistiller、ResidualRiskTracker、BudgetGate。

## 6.2 推荐实施顺序

**第一优先：**流程稳定 + 交付稳定。先让系统跑得住、交得出。

**第二优先：**结果稳定。主链路稳定后再压输出漂移。

**第三优先：**治理稳定。补齐长期经营与规模化控制。

## 6.3 最小可行框架

首轮最小闭环建议只落这 8
个件：ScenarioStateMachine、CheckpointManager、RecoveryController、TelemetryMonitor、FindingSchema、EvidenceSchema、CaseVerdict、AuditPackBuilder。先实现流程稳定与交付稳定，再迭代到结果稳定与治理稳定。

# 7. 给 Codex 的落地约束

## 7.1 不要做什么

不要把四种稳定混成一个总模块；不要先做全自动智能治理；不要先追求全场景覆盖；不要让报告靠自由文本发挥。

## 7.2 必须先锁定什么

对象模型、事件时间线、报告模板版本、升级门槛、环境 profile
引用方式、证据索引结构。

## 7.3 第一阶段完成标准

系统可跑单场景审计；可生成结构化 finding；可保存证据索引；可形成
CaseVerdict；可导出最小 AuditPack；可由你本人和我共同完成复核裁决。

# 8. 最终判断

## 8.1 文档主判断

SkillForge
若要从“能跑”升级到“可信、可交付、可治理、可经营”，就必须把稳定拆成四种能力分别建设。对你当前阶段而言，流程稳定与交付稳定优先级最高；结果稳定在主链路稳后跟进；治理稳定在规模化前补齐。

## 8.2 对产品表达的意义

以后对外可以不再笼统地卖“更稳定”，而是分别卖：结果一致性、连续运行稳定性、标准化交付、上线前治理。这样用户更容易理解，你也更容易对应到系统内的真实能力。

# 9. 四种稳定一览矩阵

| **维度**     | **结果稳定**                                        | **流程稳定**                                    | **交付稳定**                                     | **治理稳定**                                                   |
|--------------|-----------------------------------------------------|-------------------------------------------------|--------------------------------------------------|----------------------------------------------------------------|
| **核心问题** | 输出会不会漂                                        | 流程会不会断                                    | 报告会不会乱                                     | 系统会不会失控                                                 |
| **关键模块** | Contract / Validator / Comparator                   | StateMachine / Recovery / Telemetry             | Evidence / Verdict / AuditPack                   | Policy / Scope / Version / Gate                                |
| **核心对象** | NormalizedInput / OutputContract / ResultEvaluation | ScenarioRun / Checkpoint / Incident / TimePhase | Finding / EvidenceItem / CaseVerdict / AuditPack | ScopePolicy / SkillVersion / EscalationCaseCard / ResidualRisk |
| **主要交付** | 一致率 / 回归差异                                   | 存活率 / 恢复率 / 异常曲线                      | 标准 AuditPack / 裁决卡                          | 上线门槛 / 残余风险 / 复测建议                                 |

**建议：** 这份总稿适合作为后续 Codex
实现、架构回看和新账号接手的共同基线；若后续进入代码实现阶段，应继续补接口契约、事件总线格式、数据库表设计与目录约定。
