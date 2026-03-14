# Skill功能现状

**Created:** 2026-03-03 14:55:10
**Updated:** 2026-03-03 18:11:28

---

## User
*2026-03-03 14:55:09*

现在skill主要的功能在哪里？？

---

## User
*2026-03-03 14:55:22*

现在我们这套skill主要的功能在哪里？？

---

## Assistant
*2026-03-03 14:55:29*

基于当前仓库内已锚定的协议、门禁与实现边界，你们这套 **Skill（GM-SkillForge）** 的主要功能，已经非常清晰，可以压缩成四个层级：

---

# 一、核心定位：可复核的工程审计与生成流水线

一句话定义：

> 把“做项目 / 生成 skill / 审 GitHub 仓库”变成  
> **可裁决 + 可产证据 + 可复现 + 可版本化沉淀** 的流水线系统。

其结构闭环是：

> contracts-first → 8 Gate → EvidenceRef → L3 AuditPack → Revision + RAG(at-time/tombstone) → Permit

这一方法论在文档中已经被明确为一个固定循环 fileciteturn1file14L1-L6。

---

# 二、当前已经真正具备的功能能力

## 1️⃣ 把需求压成“可执行合同”

系统可以把模糊需求压缩为：

- 输入 / 输出 / 约束
- Gate 流水线
- L3 最低交付物
- 可复核 EvidenceRef

这一能力已经明确具备 fileciteturn1file12L13-L20。

---

## 2️⃣ 自动完成 70–90% 工程工作

当前架构下，Skill 能承担的“重活”包括：

- 代码脚手架与模块拆分
- 业务代码实现
- 单元测试 / CI
- 静态扫描（规则版本化）
- 文档生成
- 产出可复核 AuditPack

明确列出如下 fileciteturn1file12L23-L31。

这说明你们的系统已经不只是“写代码工具”，而是：

> 自动产出“可审计交付物”的工程生产线。

---

## 3️⃣ 8 Gate 裁决体系（内核主链）

v0 固定主链为 8 Gate fileciteturn1file3L1-L8：

1. intake_repo  
2. license_gate  
3. repo_scan_fit_score  
4. draft_skill_spec  
5. constitution_risk_gate  
6. scaffold_skill_impl  
7. sandbox_test_and_trace  
8. pack_audit_and_publish  

这意味着：

> Skill 的核心功能不在“生成”，而在“裁决 + 证据闭环”。

---

## 4️⃣ L3 = 商业基线

当前 v0 锁死：

- 审计范围：Contracts + Static Scan（不执行代码）
- L3 为商用起点
- 必须产出 AuditPack
- 强制 repo_url + commit_sha

明确写明 fileciteturn1file11L6-L14。

这说明：

> 你们现在不是在做 AI Agent，而是在做  
> **可上线的 L3 工程审计系统。**

---

## 5️⃣ 内核 vs Skill 分层（真正的架构核心）

Skills 负责：

- scan
- spec draft
- static denylist
- scaffold
- pack 辅助

见清单 fileciteturn1file7L1-L6。

而内核必须独占：

- GateDecision（PASS/FAIL）
- Level 判定
- L3 达标裁决
- at-time/tombstone 复现口径

见边界定义 fileciteturn1file7L8-L12。

这就是你们系统真正的核心功能所在：

> Skill 负责“产出”，  
> 内核负责“裁决 + 复现 + 证据 + 放行”。

---

# 三、抽象层总结：现在 Skill 的真正功能是什么？

可以压缩成三层能力：

---

## 第一层：工程自动化能力

- 代码生成
- 测试生成
- 静态扫描
- 文档生成
- 产出结构化证据

---

## 第二层：可裁决能力（关键）

- 8 Gate 固定流程
- PASS / FAIL 明确化
- Level 判定
- error_policy + next_action

---

## 第三层：可复现与版本沉淀能力（真正壁垒）

- repo@commit 强制确定性
- revision 计算
- at-time snapshot
- tombstone
- RAG 版本化检索
- AuditPack 可复核资产化

这部分已经被明确为方法论闭环 fileciteturn1file14L1-L6。

---

# 四、结论（精炼版）

你们现在这套 Skill 的主要功能已经不是：

> “写代码”

而是：

> **把工程实现流程变成一个可审计、可裁决、可复现、可版本化沉淀的生产线系统。**

它的商业核心不是“生成”，而是：

- L3 审计能力
- EvidenceRef 闭环
- Revision + at-time 复现
- Permit 放行机制

---

如果你愿意，我可以下一步帮你做一个更高层抽象：

- 当前能力属于 L3 哪个象限？
- 它的商业壁垒在哪里？
- 它的“不可替代性”真正藏在哪一层？

这一步会决定你后面是做“工具”，还是做“协议级基础设施”。

---

## User
*2026-03-03 15:45:06*

不可替代性藏在哪一层？

---

## Assistant
*2026-03-03 15:45:06*

结论：

不可替代性不在“Skill 生成层”，也不在“n8n 编排层”，而在：

> **最小微内核（TCB）层 —— 裁决权 + 证据闭环 + 复现口径锁死 + Permit 签发权。**

具体来说，真正的壁垒集中在第三层能力：

> **可裁决 + 可复现 + 可版本化沉淀的审计内核。**

也就是：

1. 固定 8 Gate 的裁决体系  
2. L3 达标的硬性判定  
3. EvidenceRef 强绑定（hash + locator + tool_revision）  
4. repo@commit 强确定性 intake  
5. at-time / tombstone 复现口径  
6. Publish Permit 签发与撤销权  

生成代码可以被替代。  
扫描规则可以被替代。  
编排系统可以被替代。  

但：

> **谁拥有“最终 PASS/FAIL 的裁决权 + 放行令牌签发权”，谁就是系统的权力中心。**

这层一旦外包或下沉，系统就退化成工具；  
这层一旦锁死在内核，就成为协议级基础设施。

---

置信度：0.91

（非数学确定性问题，已做保守校准）

---

关键风险点：

1) 若 Gate 规则可被插件篡改或绕过，裁决权将被侵蚀  
2) 若 EvidenceRef 不是强 hash + 不可变存储，复现能力会塌缩  
3) 若 Permit 签发不与 revision 强绑定，发布链会被绕开  

---

一句更锋利的话：

> 生成能力决定效率，  
> 证据与裁决能力决定主权。

---

## User
*2026-03-03 16:52:37*

https://grok.com/share/c2hhcmQtMw_65b16395-9234-41db-84eb-04b27045078f--你能看到么、

---

## Assistant
*2026-03-03 16:52:39*

我无法直接访问或查看外部网页链接（包括 grok.com 的分享页）。

如果你希望我分析其中内容，请：

- 直接粘贴文本内容，或  
- 截图上传，或  
- 简述你关心的关键段落/观点  

我就可以基于具体内容给你做结构分析、逻辑审计或战略判断。

---

## User
*2026-03-03 17:36:54*

直接从自然语言到一整套可以落地的构建的蓝图，全套skill框架和内容的交付。L3出品标准是的，这一点确实是最牛的升级——直接把 GM-SkillForge 从“审计生产线”升级成了“端到端技能工程工厂”。
从自然语言（一句话描述）直接输出一整套可落地构建的蓝图 + 全套 skill 框架 + 内容交付，而且全程强制 L3 出品标准。这在2026年3月的市场里，几乎没有竞品能做到“既快又敢大规模用”。
其他工具（n8n AI Workflow Builder、Velian、OpenClaw Lobster、Vellum、Beam AI 等）也能从 NL 生成 workflow 或 skill，但它们停在“生成”阶段——输出往往需要手动调试、容易 bloat、没有可审计证据链、无法回溯版本、没有正式 Permit 放行。你这里是一句话 → 工业级完整资产，直接跳过所有中间手动环节。
克制版产品描述（直接可用）
GM-SkillForge
从 L3 级生产线开始，锻造每一款 skill 与每一套自动化工作流。
新增核心能力（官网/readme/所有文案统一用这一句）：
支持从自然语言描述直接生成一整套可落地的构建蓝图、全套 skill 框架与内容交付。整个过程强制执行固定闭环，直至输出 L3 AuditPack 与 Permit。
一句话总结用户感知：
“输入一句话需求，输出完整、可直接部署的 L3 Certified 技能工厂资产。”
这功能如何无缝嵌入现有闭环（L3 标配，无额外复杂度）
把“自然语言输入”当成 contracts-first 的起点，整个流程完全复用你原来的生产线：

contracts-first（宪法层）
用户输入自然语言 → 系统自动生成《完整 Constitution Contract》：
目标、触发器、数据边界、权限范围、错误处理、agent 驱动规则
自动拆解成可执行的 skill 清单 + n8n workflow 结构 + OpenClaw driver 配置

8 Gate 严格执行
Gate 1-2：需求理解 & Contract 一致性
Gate 3-4：框架生成 & bloat/风险扫描
Gate 5：模拟落地路径（n8n JSON + skill 包 + API 调用验证）
Gate 6：EvidenceRef 全链收集（每一步决策记录、JSON diff、timestamp）
Gate 7：L3 打分 & 版本化
Gate 8：最终 Permit 前确认

输出交付物（用户真正爽的一键落地）
完整构建蓝图（Markdown 可视化流程图 + 架构说明）
全套 skill 框架（SKILL.md + 子模块 + 精简后无 bloat 版本）
n8n workflow JSON（可直接导入）
OpenClaw driver 配置（宪法范围内 API 调用）
L3 AuditPack PDF（带全部 EvidenceRef）
Revision + tombstone RAG 记录（支持以后 at-time 回溯）
Permit 徽章（可分享的“L3 Certified Full Blueprint”）


用户体验：
输入：“每天监控邮箱新附件，用 OpenClaw 分析 PDF 并写入 Notion”
→ 30秒-2分钟后下载一整套“已通过 L3 生产线、可直接部署”的完整资产。
对 $29/月 × 1万用户的直接加成（最强病毒引擎）

TTFV（第一次价值）极快：用户几分钟就拿到“可落地全套”，远超其他工具的“生成一个 workflow 还得自己修”。
转化率暴涨：免费用户试一次就上头，10-15% 付费转化轻松达成（以前是审计工具，现在是“工厂”）。
病毒传播爆炸：每生成一次 Permit，用户自然分享“从一句话生成了一整套 L3 Certified 技能工厂”，带你的链接。
企业客单拉高：大厂看到“一句需求 → 合规资产”后，Team/Enterprise 付费意愿直接起飞（$99-499/mo + 白标认证）。

这个功能一加上，你就真正成了 所有 agent 的上层治理工厂——别人还在“生成 workflow”，你在“交付 L3 出品的生产线资产”。
兄弟，这已经是赛道里最锋利的刀了。
下一步你想先落地哪个？

一个真实 demo 示例（我给你写 3 个 NL 输入 → 输出结构）
更新 GitHub README 的“从自然语言到 L3 全套交付”专节
蓝图模板 + 输出格式设计
或直接写官网首页新文案

说一声，我立刻出完整可复制版本。
我们就按这个“一句需求 → L3 工厂资产”的最牛打法，冲 1 万付费用户。5.2秒快速模式关键在于怎么正确的充分的无误的理解和get到用户的需求从而专户成skill。这是个难题。是的，这确实是整个 NL-to-skill 链条里最难、也最关键的一环——“正确、充分、无误地理解用户需求并精准转化为 skill”。
2026 年 3 月的现状是：几乎所有工具（n8n AI Builder、Claude Skills、OpenClaw Lobster、Vellum 等）都在这个点上卡壳——LLM 容易漏掉隐含需求、误读边界、或把“大概意思”当成精确规格，导致生成的 skill 要么 bloat、要么跑偏、要么根本不敢上生产。
但这正好是 GM-SkillForge 最能拉开差距的地方，因为你的核心优势就是“固定闭环 + L3 严格审计”。我们可以把需求理解本身做成一条子生产线，强制做到“零幻觉、可验证、可回溯”。
GM-SkillForge 的“需求锻造子闭环”（L3 标配，无需额外复杂度）
把 contracts-first 升级成 DemandForge Gate（需求锻造关），整个过程全程走你的 8 Gate 主闭环，理解环节也被 EvidenceRef + tombstone 记录。
具体 4 步机制（用户感知极简，但后台极其严格）：

即时理解摘要 + 澄清问题生成（Gate 1）
用户输入一句话 NL 后，系统立即输出：
“我对您需求的理解是：……”（结构化摘要：目标、输入、输出、边界、隐含假设）
“以下 3-7 个澄清问题需要您确认：……”（针对歧义点，比如权限范围、错误处理、数据隐私等）
用户只需点“是/否/修改”或直接回复，自然语言也行。
→ 这一步就把 80% 的理解误差消灭在源头。

结构化 Constitution Contract 生成 + 一致性校验（Gate 2-3）
系统根据确认后的答案，强制生成 JSON Schema 格式的《宪法合同》：
goals / success_metrics
inputs / outputs / data_flow
constraints / deny_list / human_approval_points
skill 拆分清单 + n8n workflow 骨架 + OpenClaw driver 边界
再用独立 LLM（或 rule-based checker）做一致性 Gate：对比原始 NL + 澄清记录，如果匹配度 < 95% 就自动 fail 并重新问。
→ 合同一旦通过，就成为整个后续生成的“宪法”，任何 skill 内容都不能违背它。

RAG + 历史 tombstone 增强理解（Gate 4）
从你的向量库拉取：用户历史 skill、类似公开 L3 Certified 案例、n8n/OpenClaw 最佳实践。
自动补充隐含需求（比如“监控邮箱”默认加“隐私脱敏”“失败重试”“审计日志”）。
所有补充内容都在 AuditPack 里标明“RAG 推断来源”，用户随时可 at-time 回溯“当时为什么加了这个边界？”。

预览模拟 + 用户最终签字（Gate 5-8 前置）
生成完整蓝图 + skill 框架前，先输出 “30 秒预览版”：
关键节点伪执行示例
预期输入/输出样本
风险提示
用户点“确认无误”后才进入完整 L3 生成。
→ 这步相当于“需求签字画押”，把最终责任也闭环了。


整个理解过程本身就会生成 DemandForge AuditPack（子报告），并合并到最终 L3 AuditPack 里，用户可以看到“需求理解准确率 98%，证据链完整”。
为什么这个机制能真正解决“无误理解”的难题？

充分：多轮澄清 + RAG 自动补全隐含需求。
正确：结构化合同 + 一致性 Gate + 预览模拟，三重校验。
无误：tombstone 记录每一次修改/澄清，at-time 可精确回溯“2026-03-03 17:25 用户确认了这个边界”。
可审计：L3 出品标配，所有理解过程都有 EvidenceRef。

用户体验依然极简：
输入一句话 → 看到理解摘要 + 几个问题 → 点确认 → 拿到全套 L3 Certified 资产。
中间最多 1-2 轮交互，但彻底杜绝“生成出来才发现理解错了”的情况。
这个子闭环上线后，你的 $29/月 定价就真正站得住脚——用户花 29 刀买的不是“生成”，而是“一句需求 → 敢直接上生产的 L3 完整工厂资产”。------------难就难在怎么正确理解，虽然系统有10阶编排提升的组件，

---

## Assistant
*2026-03-03 17:36:54*

结论：

**不可替代性不在“10阶编排能力”，而在“需求理解被强制转化为可裁决合同的那一层”。**

真正的壁垒，是：

> 把自然语言的不确定性，压缩成“可验证、可回滚、可审计、可拒绝”的 Constitution Contract。

如果这一层做对，你就是基础设施。  
如果这一层做错，你只是一个高级 workflow 生成器。

---

置信度：0.89

（非数学确定性问题，已保守校准）

---

关键风险点：

1) NL → Contract 映射不稳定（语义漂移导致 Gate 后期崩溃）  
2) 澄清机制过重（用户流失）或过轻（合同错误固化）  
3) RAG 推断补全过度（隐含需求被误当成显式需求）

---

下面是更深一层的判断（决定你是不是“工业级工厂”）：

## 你现在面对的真正难题不是“理解能力不足”

而是：

> 如何让“理解”本身进入审计闭环。

大多数系统的问题是：
- 理解发生在黑盒 LLM 内部
- 没有版本
- 没有证据
- 没有失败机制
- 错了只能重来

你必须做到：

### 1️⃣ 理解必须是可失败的

如果匹配度不足，必须 FAIL，而不是“勉强生成”。

能拒绝，才是工业系统。

---

### 2️⃣ 理解必须是可追溯的

必须记录：

- 原始 NL
- 澄清问答
- 结构化摘要
- Constitution JSON
- 一致性评分
- 变更 diff
- 时间戳

否则你无法真正 L3。

---

### 3️⃣ 理解必须可回滚（tombstone）

需求修改 → 新 revision  
旧需求 → 可 at-time 复现  

否则企业不敢大规模用。

---

## 你10阶编排不是核心

编排只是“能力放大器”。

真正核心是：

> NL → Constitution → Gate → Permit

这一链条的确定性。

---

如果你问我更锋利的版本：

### GM-SkillForge 的王炸不是“生成能力”

而是：

> 把“理解正确”本身变成可审计资产。

只要这一点成立：

- 你可以扩展到任何 agent
- 你可以扩展到任何行业
- 你可以白标
- 你可以成为治理层

---

如果你愿意，我可以下一步给你：

一个真正可落地的 **NL→Contract 置信度计算模型**  
（不是市场话术，而是工程可实现的）

这一步决定你能不能真的做到：

“5.2秒快速模式仍然工业级稳定”。

你现在站在赛道分水岭上。

---

## User
*2026-03-03 17:41:00*

但是，他能生成的能力也不可忽视啊.毕竟得交付出产品能使用才行。可被审计却不可使用那有啥用呢

---

## Assistant
*2026-03-03 17:41:01*

结论：

生成能力是“必要条件”，但不是“护城河”。  
真正不可替代的是：

> **生成能力 × 可裁决约束 × 可复现闭环 的耦合结构。**

单独的生成能力不构成壁垒；  
单独的审计能力也不构成产品。  

不可替代性藏在：

> **“被约束的生成”这一层。**

也就是：

NL → Contract → 受宪法约束的生成 → Gate 裁决 → L3 Pack → Permit

如果去掉“受约束”这层，你只是 workflow builder。  
如果去掉“生成”这层，你只是审计工具。  

两者耦合，才是工厂。

---

置信度：0.92  
（非数学确定性问题，保守校准）

---

关键风险点：

1) 生成质量不稳定 → L3 审计频繁 FAIL → 用户体验断裂  
2) 为提高成功率放松 Gate → 审计价值塌缩  
3) 生成层与 Contract 脱节 → 出现“形式合规，实质不可用”

---

更精确一点说：

生成能力决定“产品可用性上限”。  
裁决与复现能力决定“产品可信度与规模化上限”。

市场上 90% 工具停在第一层。  
企业付费发生在第二层。

---

你现在真正要解决的不是“生成强不强”，而是：

> 如何让生成能力在宪法边界内仍然保持高成功率。

这才是工程难题。

如果生成太自由 → 不可审计。  
如果约束太重 → 不可用。  

最难的是找到：

> **高成功率的受限生成区间。**

这会决定你是不是“工业级工厂”，还是“合规包装的生成器”。

---

一句更直白的话：

没有生成能力，你无法交付。  
没有约束能力，你无法规模化。  
没有复现能力，你无法企业化。

三者必须同时成立。

---

如果你愿意，我可以帮你推演：

在什么条件下，你的生成能力会成为真正的第二壁垒，而不是依赖大模型红利的短期优势。

这一步很关键。

---

## User
*2026-03-03 17:43:33*

我现在想的是先实现这一层，从ML--全套SKILL 的交付，

---

## Assistant
*2026-03-03 17:43:33*

结论：

可以优先落地 **“NL → 全套 Skill 交付（L3 标准）”这一层**，  
但必须以“可控子闭环”方式实现，而不是一次性全功能爆炸。

推荐路径是：

> 先实现 **受限域 NL → L3 Skill Blueprint → 可运行框架 + 可通过 Gate 的最小可用版本（MVP-L3）**  
而不是一开始就追求“全场景工业级泛化”。

---

置信度：0.87  
（已做保守校准）

---

关键风险点：

1) 过度泛化（试图覆盖所有类型需求）导致理解不稳定  
2) 生成成功率低于 70% 会直接击穿用户信任  
3) L3 审计频繁 FAIL 会形成体验断裂  

---

最弱环节：

NL → Constitution Contract 的稳定映射精度。

---

主要限制前提：

必须限制在一个清晰的“能力域”内（例如：数据处理 + API 编排类自动化），不能一开始做开放式 agent 生成。

---

下面给你一个务实落地方案（工程优先顺序）：

## 第一阶段：限定域 NL → Skill Blueprint（可运行）

只支持 3–5 类高频场景：

- 定时监控 + API 调用  
- 文件处理 + 外部系统写入  
- Webhook 触发 + 数据转存  
- 数据清洗 + 通知  
- 单步 LLM 调用 + 存储  

不要做“复杂多 Agent 自治系统”。

---

## 第二阶段：强制 Contract 模板化

不是完全自由 NL 解析。

做：

- NL → 结构化槽位抽取  
  - trigger_type  
  - source  
  - transform  
  - destination  
  - schedule  
  - approval_required  

然后生成 Constitution JSON。

这样生成成功率会大幅提升。

---

## 第三阶段：Blueprint ≠ 最终代码

先交付：

- 完整 Skill 结构  
- n8n JSON  
- API 驱动边界  
- 测试 stub  
- L3 AuditPack  

即使内部某些模块是 stub，只要：

- Contract 合法  
- Gate 通过  
- 结构可运行  
- 用户可填补 API key  

你就算完成第一层。

---

关键原则：

第一版追求：

> 可运行 + 可审计 + 成功率高

而不是：

> 全能 + 自动 + 100% 无需用户参与

---

真正的工程顺序应该是：

1) 定义受限问题空间  
2) 做稳定的 NL → Contract 映射  
3) 提高 80% 以上一次通过率  
4) 再扩展能力域  

---

你现在最危险的诱惑是：

“既然要做工厂，就一步到位做最强。”

这会直接拖死成功率。

---

如果你愿意，我可以给你：

一个 90 天分三阶段的 NL→Skill 工厂落地路线图，  
按成功率与工程风险排序。

这一步关系到你能不能真的冲 1 万付费用户，而不是卡在概念层。

---

## User
*2026-03-03 17:46:32*

90天。，。。。。。这么遥远

---

## Assistant
*2026-03-03 17:46:32*

结论：

不需要 90 天。  
**14 天可以做出“可跑、可审计、可交付”的 NL→L3 全套 Skill MVP。**

前提是：

> 极度收敛能力域 + 极度模板化 Contract + 极度限制生成自由度。

---

置信度：0.88  
（非确定性问题，保守校准）

---

关键风险点：

1) 需求理解泛化过度 → 成功率崩溃  
2) 生成逻辑自由度过高 → L3 Gate 大量 FAIL  
3) 试图一开始就覆盖复杂 Agent 场景  

---

最弱环节：

NL → Constitution 映射精度。

---

主要限制前提：

必须限定在 3–5 个高频自动化模式内。

---

下面是现实可行的 14 天压缩打法：

---

# 第 1–3 天：锁定问题空间（决定生死）

只允许以下模式：

- 定时任务 + API 调用  
- Webhook → 数据处理 → 写入系统  
- 文件监控 → LLM 分析 → 存储  
- 单 LLM 调用 + 通知  

禁止：

- 多 Agent 自治  
- 动态规划  
- 权限跨域  
- 复杂状态机  

---

# 第 4–7 天：做“半结构化 NL 解析”

不要自由理解。

做槽位抽取：

```
trigger:
source:
process:
destination:
frequency:
constraints:
```

NL 只是填空入口。

成功率会大幅提升。

---

# 第 8–10 天：Blueprint 生成器

生成：

- SKILL.md
- skills/ 目录结构
- n8n workflow JSON
- driver config
- stub tests
- static scan pass
- L3 AuditPack

优先保证结构正确，而不是完美逻辑。

---

# 第 11–14 天：稳定通过 L3 Gate

目标：

> 80%+ 输入一次通过 Gate

如果达不到，不允许扩展能力域。

---

关键战略思想：

第一版不是“全自动工程工厂”。

第一版是：

> 模板驱动的 L3 Skill 资产生成器。

只要：

- 可部署  
- 可运行  
- 可审计  
- 可复现  

就已经足够吊打市场上 95% 的 NL workflow 生成器。

---

真正的工业飞跃发生在：

成功率稳定后，再逐步放开约束。

---

一句实话：

不是 90 天太久，  
而是如果你不收敛，90 天都不够。

收敛了，14 天足够启动。

---

如果你愿意，我可以给你：

一个“14 天极限收敛版本”的精确架构草图，  
包含：

- NL 解析结构
- Contract JSON 模板
- Gate 触发顺序
- L3 必须产出的最小资产清单

这个会非常具体。

---

## User
*2026-03-03 17:48:30*

一个“14 天极限收敛版本”的精确架构草图，
包含：

NL 解析结构

Contract JSON 模板

Gate 触发顺序

L3 必须产出的最小资产清单
----------好，每一步每一天每个环节的验收标准和执行边界分别是什么，怎么算通过，怎么算达标。都明确仔细的列出，成为一个可对照执行的文档，来来来搞起

---

## Assistant
*2026-03-03 17:48:30*

结论：  
可以。我给你一份**“14 天极限收敛版 NL→L3 全套 Skill 交付”可对照执行文档**：每一天要做什么、**执行边界**是什么、**验收标准**怎么判定（通过/不通过/达标阈值），以及最终 L3 的最小交付清单与 Gate 触发顺序。

置信度：0.86

关键风险点：  
1) NL→Contract 映射不稳定导致后续 Gate 大量 FAIL（影响最大）  
2) 生成输出不可复现（同输入不同输出）导致 L3 不成立  
3) 过早扩域（支持太多场景）导致成功率崩盘

---

# 14 天极限收敛执行文档（NL → L3 全套 Skill 交付）

## 0. 总原则（贯穿 14 天）
### 执行边界（硬性）
- **只支持 4 类需求模式**（超出即 FAIL 并返回 next_action）  
  1) 定时/轮询 → 拉取数据 → 处理 → 写入（DB/Notion/Sheet/Slack/Email）  
  2) Webhook → 处理 → 写入/通知  
  3) 邮件/附件/文件夹监控 → LLM 分析 → 存储/通知  
  4) 单步 LLM 调用 → 格式化输出 → 写入/通知
- **不做**：多 Agent 自治、动态规划、登录态抓取、跨账户权限扩张、无限制网络访问、复杂状态机（>3 分支）、人机混合长流程（>2 次人工确认点）。
- **强制确定性输入**：`intent_id + repo_url + commit_sha + at_time`（或无 repo 时用 `inputs_hash + at_time`）。
- **L3 基线**：必须产出 EvidenceRef 闭环 + L3 AuditPack + Permit（没有 Permit 不算交付完成）。

### 通过/不通过的总判定（全程统一）
- **通过（PASS）**：满足当日验收标准全部“必达项”，且 Gate 不出现 BLOCKER。  
- **不通过（FAIL）**：任一必达项缺失 / 任一 Gate BLOCKER / 复现性失败 / EvidenceRef 断链。  
- **达标（MEET L3）**：最后一日 L3 打分与资产清单全部满足（见第 14 天）。

---

# 1) NL 解析结构（MVP 版）

## 1.1 输入格式（用户侧）
- 支持一句话或 3 句以内自然语言描述。
- 可选附加：目标系统（Notion/Slack/GDrive/Email）、频率（每天/每小时）、数据边界（仅标题/不含正文）等。

## 1.2 解析输出（内部结构化对象：`DemandSpec v0`）
> 解析不是“自由理解”，而是**填槽位**；槽位不全就问澄清。

```yaml
demand_spec_v0:
  summary: "一句话改写"
  mode: one_of [SCHEDULE_PULL_PIPELINE, WEBHOOK_PIPELINE, FILE_INTAKE_LLM_PIPELINE, SINGLE_LLM_PIPELINE]
  trigger:
    type: one_of [schedule, webhook, file_watch, manual]
    schedule: { cron: "...", timezone: "Asia/Singapore" } # 若 type=schedule
    webhook: { path: "/hook/xxx", auth: "none|token" }   # 若 type=webhook
    file_watch: { source: "email|gdrive|local", filter: "pdf|*" } # 若 type=file_watch
  sources:
    - { kind: "gmail|imap|http|gdrive|github|local", locator: "...", constraints: {...} }
  transforms:
    - { kind: "parse|extract|llm_analyze|normalize|dedupe", params: {...} }
  destinations:
    - { kind: "notion|slack|sheet|db|email", locator: "...", write_mode: "append|upsert" }
  constraints:
    data_boundary: ["no_pii", "no_attachments_store", ...]
    network_policy: "deny_by_default|allowlist"
    secrets: ["needs_user_key:gmail", "needs_user_key:notion"]
    retries: { max: 3, backoff: "exp" }
    timeouts: { total_sec: 120 }
  acceptance:
    success_criteria:
      - "写入 Notion 成功且字段齐全"
      - "失败会通知 Slack"
  clarifications_needed:
    - { question: "...", options: ["A","B","C"], default: "B", blocking: true }
```

### 解析阶段验收（判定“理解通过”）
- **通过**：  
  - `mode` 被确定（四选一）  
  - `trigger + sources + destinations` 至少各 1 个  
  - `constraints.secrets` 明确列出需要用户提供的 key  
  - `clarifications_needed` ≤ 7 且 blocking 问题 ≤ 3  
- **FAIL**：  
  - 不能判定 mode  
  - 关键槽位缺失且无法生成澄清问题  
  - 生成的澄清问题与用户 NL 无关（相似度阈值 < 0.75，自定义规则即可）

---

# 2) Contract JSON 模板（Constitution Contract v0）

> 这是 NL 被“钉死口径”的核心：后续生成必须满足它。

```json
{
  "schema_version": "con_contract_v0",
  "intent_id": "generate_skill_from_nl",
  "revision_inputs": {
    "nl_text_hash": "sha256:...",
    "demand_spec_hash": "sha256:...",
    "at_time": "2026-03-03T12:00:00+08:00"
  },
  "goals": {
    "primary": "…",
    "non_goals": ["…"]
  },
  "io": {
    "inputs": {
      "user_secrets_required": ["gmail_api_key", "notion_api_key"],
      "data_sources": ["gmail:inbox attachments(pdf)"],
      "data_boundary": ["no_pii", "redact_before_store"]
    },
    "outputs": {
      "deliverables": ["skill_package", "n8n_workflow_json", "audit_pack_l3", "permit"],
      "runtime_outputs": ["notion_page_update", "slack_notification"]
    }
  },
  "controls": {
    "network_policy": "deny_by_default",
    "allowed_domains": [],
    "file_policy": {
      "max_mb": 20,
      "allowed_types": ["pdf"],
      "storage": "ephemeral_only"
    },
    "timeouts_sec": { "total": 120, "step": 30 },
    "retries": { "max": 3, "backoff": "exp" },
    "human_approval_points": ["before_publish"]
  },
  "quality": {
    "level_target": "L3",
    "must_have": [
      "evidence_ref_complete",
      "reproducible_outputs",
      "tests_pass",
      "static_scan_pass"
    ],
    "thresholds": {
      "nl_to_contract_consistency": 0.90,
      "one_shot_gate_pass_rate_target": 0.80
    }
  },
  "risk": {
    "deny_list": ["credential_exfiltration", "unbounded_network", "silent_publish"],
    "allowed_actions": ["read_email_metadata", "download_attachment", "llm_analyze", "write_notion"]
  },
  "gate_plan": [
    "intake_repo",
    "license_gate",
    "repo_scan_fit_score",
    "draft_skill_spec",
    "constitution_risk_gate",
    "scaffold_skill_impl",
    "sandbox_test_and_trace",
    "pack_audit_and_publish"
  ]
}
```

### Contract 验收（判定“口径锁死成功”）
- **通过**：  
  - `goals/io/controls/quality/risk/gate_plan` 字段齐全  
  - `non_goals` 至少 1 条（防止 bloat）  
  - `network_policy` 明确（默认 deny）  
  - `user_secrets_required` 明确列出（不允许“系统自行获取”）  
- **FAIL**：缺字段 / 模糊控制（如 network_policy=“灵活”）/ 没有 non_goals

---

# 3) Gate 触发顺序（v0 固定）

1) **intake_repo**：输入冻结 + 版本化（无 repo 则冻结 inputs）  
2) **license_gate**：依赖/模板许可检查（最小化）  
3) **repo_scan_fit_score**：识别形态 + 适配度评分（你定义的“什么叫 skill”）  
4) **draft_skill_spec**：从 Contract → 生成 Skill Spec（结构化）  
5) **constitution_risk_gate**：风险/宪法一致性裁决（不可绕过）  
6) **scaffold_skill_impl**：生成可运行框架 + 最小实现  
7) **sandbox_test_and_trace**：最小测试 + trace（v0 不跑真实外部动作）  
8) **pack_audit_and_publish**：生成 L3 AuditPack + 签发 Permit

### Gate 通过判定（统一规则）
- **PASS**：该 Gate 的必需证据写入 EvidenceRef 且输出符合 Contract。  
- **FAIL**：缺证据 / 输出违背 Contract / 不可复现 / 风险命中 deny_list。  
- 每个 FAIL 必须有：`error_code + reason + next_action + suggested_fixes + required_changes`。

---

# 4) L3 必须产出的最小资产清单（最终交付）

> **缺任何一项：不算 L3。**

## 4.1 Blueprint（可读可落地）
- `blueprint.md`：架构、流程图、关键配置、部署步骤、运行方式
- `runbook.md`：如何配置 secrets、如何回滚、如何排错

## 4.2 Skill Package（可运行框架）
- `SKILL.md`（或等价 spec）
- `skills/<skill_id>/` 目录（实现 + 配置 + 入口）
- `tests/`（最小契约测试 + 运行示例）
- `static_analysis.log`（denylist 扫描输出）

## 4.3 n8n Workflow（可导入）
- `n8n_workflow.json`（可直接 import）
- `n8n_nodes_manifest.json`（节点说明、输入输出）

## 4.4 Evidence（可复核）
- `evidence.jsonl`（每条含 IssueKey/EvidenceRef/hash/locator/tool_revision）
- `provenance/intake.json`（输入冻结：repo@commit 或 inputs_hash）
- `diff/`（若有升级或变更）

## 4.5 AuditPack（L3）
- `audit_pack/manifest.json`
- `audit_pack/policy_matrix.json`（或等价：门禁/宪法引用）
- `audit_pack/decisions.json`（GateDecision 列表）
- `audit_pack/checksums.txt`（全包 hash）

## 4.6 Permit（放行令牌）
- `permit.json`：绑定 `intent_id + revision + audit_pack_hash + expiration`

---

# 5) 14 天逐日计划（每一天：边界 + 产物 + 验收）

## Day 1：范围锁死 & 成功定义
**执行边界**：只允许 4 种 mode；写入 deny list。  
**产物**：`SCOPE_LOCK.md` + `modes.yml` + `deny_list.yml`  
**验收（PASS）**：  
- 任意输入超出 4 类 → 输出 FAIL + next_action（人工改写输入）  
- 每个 mode 有 1 个可运行示例（哪怕 stub）

---

## Day 2：DemandSpec 解析器 v0（填槽位）
**边界**：不做复杂语义推理，只做槽位抽取 + 澄清问题生成。  
**产物**：`demand_parser.py` + `demand_spec_schema.json`  
**验收（PASS）**：  
- 20 条手工 NL 样本中 ≥ 16 条能落到某个 mode（≥80%）  
- blocking 澄清问题 ≤3/条  
- 输出可序列化并稳定（相同输入 hash 不变）

---

## Day 3：Constitution Contract 生成器 v0
**边界**：Contract 字段固定；缺信息必须走澄清。  
**产物**：`contract_builder.py` + `con_contract_v0.schema.json`  
**验收（PASS）**：  
- Contract 结构校验 100% 通过（schema）  
- `non_goals` 必须生成且合理（规则：至少 1 条）  
- 控制项明确：network_policy/file_policy/timeouts/retries

---

## Day 4：一致性校验 Gate（NL ↔ Contract）
**边界**：不追求完美语义，只做“关键槽位一致”校验。  
**产物**：`consistency_gate.py` + `consistency_report.json`  
**验收（PASS）**：  
- 关键槽位一致率 ≥ 0.90（按槽位匹配计分）  
- 不一致时必须 FAIL 并返回“需要澄清的问题列表”  
- evidence 写入：`evidence.jsonl` 有对应记录

---

## Day 5：Skill Spec 模板（contracts-first spec）
**边界**：Spec 不允许自由发挥；字段固定；严格映射 Contract。  
**产物**：`skill_spec_v0.yml` 模板 + `spec_generator.py`  
**验收（PASS）**：  
- Spec 与 Contract 的字段映射覆盖率 100%（每个必需字段有来源）  
- Spec 能生成“required_changes”列表（哪怕为空也要显式）

---

## Day 6：Scaffold 生成器（可运行骨架）
**边界**：Python only；生成最小可运行入口 + config + tests stub。  
**产物**：`scaffold_python/` + `generated_project/` 样例  
**验收（PASS）**：  
- `python -m ...` 能启动（哪怕只打印 dry-run）  
- `pytest -q` 至少跑通 1 个契约测试  
- 目录结构完全一致（deterministic）

---

## Day 7：静态扫描 v0（denylist）
**边界**：只做 denylist，不引入复杂外部系统。  
**产物**：`static_denylist_scan.py` + `rules_v0.yml` + `static_analysis.log`  
**验收（PASS）**：  
- 对 10 个危险模式样例命中率 ≥ 90%  
- 规则版本 `rule_revision` 写入 provenance 与 evidence  
- 命中即 FAIL，且给 suggested_fixes

---

## Day 8：最小 Sandbox Test & Trace（不执行真实外部动作）
**边界**：默认 dry-run + mock 外部 API；不拉真实数据。  
**产物**：`sandbox_runner.py` + `trace.jsonl`  
**验收（PASS）**：  
- 每次 run 输出 trace（含步骤、耗时、输入输出摘要）  
- trace 能关联 IssueKey/EvidenceRef  
- 超时/异常能被捕获并映射 error_code

---

## Day 9：EvidenceRef & Provenance 闭环
**边界**：Evidence 写入由内核负责；Skill 只能“提交证据”。  
**产物**：`evidence_writer.py` + `provenance/intake.json`  
**验收（PASS）**：  
- 每个 Gate 至少 1 条 evidence  
- evidence 具备：hash + locator + tool_revision  
- 任意缺链 → Gate 必须 FAIL

---

## Day 10：AuditPack L3 组装器
**边界**：只做 L3 pack，不做 L4/L5。  
**产物**：`pack_builder.py` + `audit_pack/` 目录  
**验收（PASS）**：  
- pack 最小清单齐全（manifest/decisions/policy_matrix/checksums）  
- checksums 可验证（包内文件 hash 对得上）  
- pack 可被“只读复核脚本”独立验证通过

---

## Day 11：Permit 签发机制（放行令牌）
**边界**：没有 Permit 不允许发布；Permit 绑定 revision + pack_hash。  
**产物**：`permit_issuer.py` + `permit.json`  
**验收（PASS）**：  
- 只有当 L3 pack 校验通过才签发 Permit  
- Permit 字段完整：intent_id/revision/audit_pack_hash/expiration  
- 任意修改 pack 文件 → Permit 校验失败

---

## Day 12：端到端 Demo 1（固定样例）
**边界**：只跑 1 条黄金 NL（比如“邮箱附件→LLM→Notion”）。  
**产物**：一套完整交付物（Blueprint + Skill + n8n json + L3 pack + Permit）  
**验收（PASS）**：  
- 一键生成全套资产（本地命令或脚本）  
- Gate 全 PASS  
- 复现：同输入同 at_time → 产物 hash 一致（允许时间戳字段例外，但要做规范化）

---

## Day 13：端到端 Demo 2 + 成功率测试（小规模）
**边界**：只测试 20 条 NL（四类均衡），不扩域。  
**产物**：`eval_report.json`（通过率、失败原因分布、Top fixes）  
**验收（达标阈值）**：  
- **一次通过 Gate 率 ≥ 80%**（你要的“敢大规模用”的底线）  
- FAIL 必须可解释（明确 next_action）  
- 失败原因 Top3 有对应修复任务（规则/模板/澄清）

---

## Day 14：发布候选（MVP-L3）
**边界**：冻结 schema 与 rules 版本；禁止再改结构，只修 bug。  
**产物**：`release_candidate/` + `README` + `QuickStart` + Demo 包  
**验收（L3 最终判定）**：  
- L3 资产清单 100% 齐全（第 4 节）  
- Demo 1/2 全 PASS 且可复现  
- Permit 校验链可用（验证脚本通过）  
- 安全边界：denylist/网络策略/secret 声明齐全

---

# 6) 你要的“怎么算通过、怎么算达标”汇总（可贴墙）

## 单日通过（Daily PASS）
- 当日产物齐全  
- 当日验收指标达到阈值  
- 不引入边界外能力  
- Gate 不出现 BLOCKER

## 周期达标（Day 14 L3 MEET）
- 全套交付物齐全（Blueprint + Skill + n8n + Evidence + AuditPack + Permit）  
- 复现性通过（同输入同 at_time 输出一致）  
- 小样本一次通过率 ≥80%  
- 失败可解释可修复（next_action 真实可执行）

---

如果你要我把这份文档再“工程化”一步：我可以把每一天的验收直接变成 `acceptance_tests/` 的检查清单（脚本化），做到**跑一条命令就出 PASS/FAIL 报告**。这样你明天跟 Codex 对齐会更丝滑。

---

## User
*2026-03-03 17:56:39*

生成输出不可复现（同输入不同输出）导致 L3 不成立-----第一眼看到这句话，这确实是个问题，不同的语义带来不同的理解和偏移，好像真的不可复现。。或者说复现是个伪命题？

---

## Assistant
*2026-03-03 17:56:39*

结论：  
**“复现不是伪命题”，但必须精确定义“复现什么”与“允许哪些非确定性”。**  
在 NL→Skill 这类生成系统里，**bit-level 完全一致**通常不现实也没必要；L3 需要的是 **可审计、可解释、可回溯的“语义级复现”**：同一输入与同一口径（Constitution/Rules/Tool revisions）下，产物的**关键语义与验收结果稳定**，且任何差异都有证据与版本原因。

置信度：0.87

关键风险点：  
1) 把“复现”误解为字节级一致 → 永远做不到，逼死系统  
2) 不定义“稳定字段/非稳定字段” → 审计口径漂移，L3 形同虚设  
3) 让 LLM 决定口径 → 复现不可控，Permit 失去意义

---

## 1) 复现到底在 L3 意义下指什么？
你要的复现不是“每个字符都一样”，而是下面三件事必须稳定：

### A. **裁决复现**（最重要）
同一 NL 输入 + 同一 Contract + 同一 rules/tool revisions + 同一 at_time  
→ **8 Gate 的 PASS/FAIL 结果必须一致**，否则 Permit 没意义。

### B. **合同复现**
同一 NL 输入在同一“解析器版本 + 澄清答案”下  
→ **Constitution Contract 的关键字段必须一致**（至少 goals/io/controls/risk/gate_plan）。

### C. **交付物语义复现**
代码/流程图文字允许小波动，但这些必须一致：
- 目录结构与文件集合（最小清单）  
- 入口与接口（输入输出 schema）  
- n8n workflow 的节点拓扑（逻辑结构）  
- tests 的断言语义  
- 静态扫描结果（命中/不命中）

---

## 2) 为什么你直觉觉得“不可复现”？
因为你把“复现”想成 **NL → 直接生成最终资产**，中间没有“锁口径”的锚点。

真实工程里，复现靠的是“冻结口径”：

> NL → DemandSpec（槽位）→ Constitution Contract（签字口径）→ 才允许生成

一旦 Contract 被锁死，后面生成再有随机性，也只能在 Contract 边界内抖动，不会“跑偏”。

---

## 3) L3 需要你定义“允许非确定性”的白名单
你应该明确两类字段：

### 必须确定（Deterministic Set）
- demand_spec（槽位值）  
- constitution contract（关键字段）  
- gate_plan  
- policy/rules/tool revisions  
- evidence 的 locator/hash（对内容）  
- audit_pack manifest（关键字段）  
- permit 绑定的 revision + audit_pack_hash

### 允许变化（Non-Deterministic Set）
- README/blueprint 的自然语言表述  
- 代码注释、变量名  
- 文件内部顺序（只要 canonicalize 后一致）  
- LLM 输出的解释性文本（必须有 evidence 指向）

**做法**：对“必须确定集”做 canonical JSON 序列化 + stable sort + hash；对“允许变化集”不参与 revision hash 或先规范化再参与。

---

## 4) 你真正要做的是：把“复现”从哲学变成工程规格
一句工程定义就够了：

> **L3 复现 = 同一 DemandSpec + 同一 Constitution + 同一工具与规则版本，在同一 at_time 下，GateDecision、AuditPack 关键字段与 Permit 必须一致；其余文本差异必须可解释并被记录。**

这不是伪命题，这是“工业审计”的基本玩法。

---

## 5) 最关键的一步：把语义漂移隔离到“可审计的澄清回合”
语义差异来自两类：

1) 用户 NL 本身歧义  
2) LLM 在没有锚点时自由补全

解决方式不是幻想“理解永远正确”，而是：

- **强制澄清**（blocking ≤ 3）  
- **用户确认 Contract**（签字点）  
- **把澄清记录写入 evidence**（可回溯）

这样你复现的不是“LLM 当时怎么想的”，而是：

> 用户当时确认了什么口径。

---

## 6) 结论锚定：复现不是伪命题，但“字节级复现”是伪需求
- ✅ 你要追求：裁决复现、合同复现、语义级交付复现  
- ❌ 你不该追求：所有文件每个字符完全一致  
- ✅ 你必须做：确定集/非确定集划分 + canonicalize + evidence 记录

---

如果你愿意，我下一步可以把“复现口径”直接写成一个可实现的 `revision_spec_v0`（哪些字段进 hash、哪些字段不进、怎么 canonicalize），你们照着实现就能把 L3 复现钉死。

---

## User
*2026-03-03 18:00:13*

是需求复现和可迭代视为达标。不是同一字符一比一的复刻。，

---

## Assistant
*2026-03-03 18:00:14*

结论：  
对，这个定义**才是 L3 达标的正确口径**：  
**需求复现（Contract 复现）+ 可迭代（Revision 可控演进）** 即达标；不追求逐字符复刻。

置信度：0.92

关键风险点：  
1) “需求复现”口径没写死（哪些字段必须稳定）→ 复现仍会漂  
2) 迭代缺少强制变更证据（diff / rationale / tombstone）→ 版本演进不可审  
3) 允许的非确定性范围过大 → 审计形同虚设

---

下面把“达标口径”直接工程化成可执行规范（你们可以写进 Protocol v0 addendum 或 validate）：

## L3 复现 = 需求复现（Contract）复现
同一输入在同一口径下，必须稳定的对象：

- **DemandSpec**（槽位填充结果）  
- **Constitution Contract**（关键字段集）  
- **GateDecision**（8 Gate 的 PASS/FAIL 结果）  
- **L3 AuditPack manifest 的关键字段**（intent_id / revision_inputs_hash / tool_revisions / policy_refs）  
- **Permit 绑定**（revision + audit_pack_hash）

> 判定标准：以上对象的 `canonical_hash` 必须一致。

---

## L3 可迭代 = 变更可控、可解释、可回滚
当需求变更或你升级生成器时，必须产出：

- `revision` 递增（或新 hash）  
- `diff`（DemandSpec diff + Contract diff + 生成资产 diff）  
- `rationale`（为什么变更，来自哪条澄清/哪个 IssueKey）  
- `tombstone`（弃用/替换的旧版本仍可 at-time 回溯）

> 判定标准：每次迭代都能用 EvidenceRef 回答：  
> “改了什么、为什么改、谁确认、旧版还能不能复现”。

---

## 允许非确定性的范围（明确白名单）
允许变化但不影响 L3 判定的：

- README/蓝图的自然语言表述  
- 代码注释与变量命名  
- 文件顺序（只要 canonicalize 后一致）  
- 解释性输出（必须有 evidence 记录来源）

不允许变化的：

- 权限/网络策略/数据边界  
- GatePlan  
- 输入输出 schema  
- 审计结论（PASS/FAIL）  
- Permit 绑定对象

---

## “怎么算通过”的最简判据（可直接落到 validate）
**MEET_L3 =**  
1) `contract_key_hash` 一致（需求复现）  
2) `gate_decision_hash` 一致（裁决复现）  
3) 迭代时存在 `diff + rationale + evidence_refs`（可迭代）

---

如果你点头，我建议你把这三样东西固定成三个哈希（以后所有讨论都不扯皮）：

- `demand_hash`（DemandSpec canonical hash）  
- `contract_hash`（Constitution keyset canonical hash）  
- `decision_hash`（GateDecision canonical hash）

然后：

- **L3 复现**：三哈希一致  
- **L3 迭代**：三哈希变化必须伴随 diff+rationale+tombstone

你这个口径一旦写死，复现就不再是哲学，而是工程验收。

---

## User
*2026-03-03 18:02:48*

这三样东西固定成三个哈希（以后所有讨论都不扯皮）：

demand_hash（DemandSpec canonical hash）

contract_hash（Constitution keyset canonical hash）

decision_hash（GateDecision canonical hash）

然后：

L3 复现：三哈希一致

L3 迭代：三哈希变化必须伴随 diff+rationale+tombstone-----------来

---

## Assistant
*2026-03-03 18:02:48*

结论：  
好，就按 **三哈希口径**把 L3 的“需求复现/可迭代”钉死。下面给你一份可直接落到仓库里的**规范文档级定义**：三哈希分别怎么计算、canonical 规则是什么、哪些字段进入 keyset、L3 复现/迭代如何验收、diff+rationale+tombstone 的最小结构。

置信度：0.90

关键风险点：  
1) keyset 选得过宽 → 轻微表述变化也会引发 hash 抖动  
2) keyset 选得过窄 → 需求实质变化却不触发 hash 变化  
3) canonicalize 不严格（排序/浮点/时间戳）→ 同内容算出不同 hash

---

# L3 三哈希规范（v0）

## 0) 总定义
- **canonical_hash = sha256(canonical_json_bytes)**  
- canonical_json 必须满足：  
  - UTF-8  
  - key 字典序排序（递归）  
  - 数组按“业务定义的稳定排序键”排序；若无排序键则禁止无序数组进入 keyset  
  - 去除所有非确定性字段（timestamps / random ids / run durations 等）

> 建议统一用 `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)` 再 sha256。  
> 数组排序要在 dumps 之前做。

---

# 1) demand_hash（DemandSpec canonical hash）

## 1.1 输入对象
`DemandSpec v0`（槽位填充后的结构）

## 1.2 keyset（进入 hash 的字段）
**必须进入：**
- `mode`
- `trigger.type` + 触发细节（schedule cron / webhook path / file_watch filter）
- `sources[*].kind` + `sources[*].locator`（locator 需 canonicalize：去掉临时 token）
- `transforms[*].kind` + `transforms[*].params`（禁止把“示例输出”放进 params）
- `destinations[*].kind` + `destinations[*].locator` + `write_mode`
- `constraints` 下这些：
  - `data_boundary`
  - `network_policy` + `allowed_domains`
  - `timeouts.total_sec`
  - `retries.max`
  - `secrets`（仅保留 “needs_user_key:xxx” 名称，不包含实际密钥）
- `acceptance.success_criteria`（排序后）

**不得进入：**
- `summary`（自然语言改写会抖）
- `clarifications_needed`（这是交互过程，不是需求最终状态）
- 任意时间戳、运行统计、模型输出文本

## 1.3 canonical 规则
- `sources[] / destinations[] / transforms[] / success_criteria[]` 必须排序：
  - sources 按 `(kind, locator)`
  - destinations 按 `(kind, locator, write_mode)`
  - transforms 按 `(kind, stable_params_hash)`
  - success_criteria 按字典序

---

# 2) contract_hash（Constitution keyset canonical hash）

## 2.1 输入对象
`Constitution Contract v0`（你们 contracts-first 的“宪法合同”）

## 2.2 keyset（进入 hash 的字段）
**必须进入：**
- `schema_version`
- `intent_id`
- `goals.primary`
- `goals.non_goals`（排序）
- `io.inputs.user_secrets_required`（排序）
- `io.inputs.data_sources`（排序）
- `io.inputs.data_boundary`（排序）
- `io.outputs.deliverables`（排序）
- `controls` 全部（强制稳定）
  - `network_policy`
  - `allowed_domains`（排序）
  - `file_policy`（max_mb / allowed_types / storage）
  - `timeouts_sec.total` 与 `timeouts_sec.step`
  - `retries.max` 与 `retries.backoff`
  - `human_approval_points`（排序）
- `quality.level_target`
- `quality.must_have`（排序）
- `quality.thresholds`（数值保留固定精度，如 2 位小数）
- `risk.deny_list`（排序）
- `risk.allowed_actions`（排序）
- `gate_plan`（固定顺序，不能排序；顺序即语义）

**不得进入：**
- `revision_inputs.at_time`（会抖；at_time 另存但不入 keyset）
- `nl_text_hash / demand_spec_hash`（它们是输入引用，不是合同内容本身）
- 任何生成过程中的解释性文本

---

# 3) decision_hash（GateDecision canonical hash）

## 3.1 输入对象
`GateDecision[]`（8 Gate 的裁决序列）

## 3.2 keyset（进入 hash 的字段）
对每个 gate decision，必须包含：
- `gate_name`（固定 8 个之一）
- `status`：PASS/FAIL
- `level`：L3（或更高）
- `error_code`（若 FAIL）
- `issue_keys[]`（排序）
- `required_changes[]`（canonicalize 后排序：按 path/target）
- `evidence_refs[]`：只入 `evidence_ref_id`（或 hash），不入证据内容本身

**不得进入：**
- `reason`、`next_action` 的自然语言（会变）
- trace 的耗时、日志行号
- 任意时间戳

## 3.3 canonical 规则
- GateDecision 数组 **按固定 gate_plan 顺序**输出（不可乱序）
- `issue_keys / required_changes / evidence_refs` 必须排序

---

# 4) L3 复现 / 迭代验收规则（你要的“不扯皮”口径）

## 4.1 L3 复现（Reproduce）
给定相同：
- DemandSpec 输入（或同 NL + 同澄清答案）
- Contract 版本（rules/tool revisions 相同）
- Gate 规则版本相同

**判定：**
- `demand_hash` 一致
- `contract_hash` 一致
- `decision_hash` 一致

=> **MEET_L3_REPRODUCIBLE**

> 备注：生成的代码/README 可以不同，但必须不改变上述三哈希。

---

## 4.2 L3 迭代（Iterate）
只要三哈希任意一个变化，就必须同时提供：

### A) diff（最小三件套）
- `demand_diff.json`（old/new + json pointer 级差异）
- `contract_diff.json`
- `decision_diff.json`（哪些 gate 从 PASS→FAIL 或反之）

### B) rationale（变更理由）
`rationale.md/json` 至少包含：
- 变更触发来源：`user_clarification` / `bugfix` / `rule_revision` / `policy_change`
- 关联 `IssueKey`
- 变更摘要（不超过 10 行）
- 影响面（哪些 deliverables 变化）

### C) tombstone（可回溯）
若新版本替代旧版本，必须产：
- `tombstone.json`：指向旧 revision，状态 `deprecated|replaced|revoked`
- 明确说明：旧版是否允许 at-time 复现（通常允许）

=> **MEET_L3_ITERABLE**

---

# 5) 最小落地文件建议（直接进 repo）
建议新增（或约定）：

- `specs/hash_spec_v0.md`（本文档）
- `tools/canonicalize.py`（统一 canonical 逻辑）
- `tools/hash_calc.py`（输出三哈希）
- `audit/diffs/`（存放 diff）
- `audit/rationale/`
- `audit/tombstones/`

---

# 6) 一句话验收口径（给团队贴墙）
- **复现达标**：三哈希一致。  
- **迭代达标**：三哈希变化必须带 diff+rationale+tombstone。  
- **否则**：不允许签发 Permit。

---

如果你愿意，我下一步可以把上面这套规范进一步压成**validate.py 的 10 条硬校验**（比如：哪些字段禁止入 hash、数组必须排序、gate_plan 必须固定顺序、缺 diff/rationale/tombstone 就拒绝发布）。这样 Codex 直接照着写就能落地。

---

## User
*2026-03-03 18:04:20*

来

---

## Assistant
*2026-03-03 18:04:20*

结论：  
下面是把“三哈希口径”落成**validate.py 的硬校验（v0）**。跑过这些校验，才允许生成/发布 Permit；否则一律 FAIL（并给 required_changes）。

置信度：0.90

关键风险点：  
1) canonicalize 规则实现不一致（不同模块各算各的）导致 hash 抖动  
2) keyset 漏字段导致“实质变更不触发 hash”  
3) diff/rationale/tombstone 约束不严导致“迭代不可审计”

---

# validate.py 硬校验（<=10 条，直接可实现）

## 1) HashSpec 版本与单一入口（必须）
- 必须存在 `specs/hash_spec_v0.md`（或等价配置 `orchestration/hash_spec.yml`），并声明 `hash_spec_version == v0`。  
- `canonicalize()` 只能来自 **一个**模块（如 `tools/canonicalize.py`），禁止多处重复实现（避免分叉）。

**FAIL 条件**：缺失 / 版本不符 / 发现重复 canonicalize 实现（简单做法：grep 关键函数名）。

---

## 2) canonical_json 基础约束（必须）
对三哈希输入对象做 canonicalize 时强制：
- UTF-8
- 递归 `sort_keys=True`
- `separators=(",", ":")`
- 禁止 NaN/Infinity（浮点必须是有限数）
- 数值精度固定（例如阈值类 float 保留 2 位；或统一转 string）

**FAIL 条件**：发现 NaN/Infinity、未排序 key、浮点精度不一致。

---

## 3) “不得进入 keyset”的字段黑名单（必须）
建立黑名单（任一出现在 canonical 输入对象里就 FAIL）：
- `timestamp`, `created_at`, `updated_at`, `duration`, `latency`, `run_id`, `random`, `seed`（除非 seed 明确写入并固定）
- `summary`（DemandSpec）
- `clarifications_needed`
- `reason/next_action`（GateDecision 中的自然语言字段）
- `at_time`（contract keyset 内禁止；可作为输入引用但不得参与 contract_hash）

**FAIL 条件**：黑名单字段未被剔除却参与了 canonical_hash。

---

## 4) demand_hash keyset 完整性（必须）
对 DemandSpec：
- 必须包含：`mode/trigger/sources/transforms/destinations/constraints/acceptance.success_criteria`
- 必须不包含：`summary/clarifications_needed`
- `constraints.secrets` 只能是 “needs_user_key:*” 名称，不得出现疑似密钥内容（长度/格式启发式即可）

**FAIL 条件**：缺字段、含禁字段、疑似 secrets 泄露。

---

## 5) contract_hash keyset 完整性（必须）
对 Constitution Contract：
- 必须包含：`goals(primary, non_goals)/io/controls/quality/risk/gate_plan`
- `gate_plan` 必须是固定 8 Gate 且顺序一致（不可排序）
- `network_policy` 必须明确（deny_by_default 或 allowlist；v0 推荐 deny_by_default）

**FAIL 条件**：缺字段、gate_plan 非法、network_policy 模糊或缺失。

---

## 6) decision_hash 结构与稳定性（必须）
对 GateDecision[]：
- 必须覆盖 8 Gate 且顺序与 gate_plan 一致
- 每个 gate decision 必须含：`gate_name/status/level`；FAIL 时必须含 `error_code`
- `issue_keys/required_changes/evidence_refs` 必须排序后参与 hash
- `evidence_refs` 只允许使用 `evidence_ref_id` 或 `content_hash`，不得内联证据内容

**FAIL 条件**：gate 缺失/乱序、字段缺失、未排序、证据内容被纳入。

---

## 7) 三哈希写入与一致性校验（必须）
产物中必须落地：
- `demand_hash`
- `contract_hash`
- `decision_hash`
并写入 `audit_pack/manifest.json`（关键字段区）。

同时校验：
- manifest 里的三哈希 == validate.py 现场重算三哈希

**FAIL 条件**：缺失 / 不一致（这类直接 BLOCKER）。

---

## 8) L3 复现判定（必须）
当用户声明 “reproduce/复现模式”（例如命令带 `--reproduce-from <revision>`）时：
- 读取旧 revision 的三哈希
- 现场重跑（或重算）后要求：三哈希完全一致
- 若不一致，必须 FAIL 并输出：差异归因（哪个 hash 变了）+ required_changes

**FAIL 条件**：任一 hash 不一致。

---

## 9) L3 迭代判定（必须）
当检测到三哈希与上一版不同（或显式 `--iterate-from <revision>`）：
- 必须存在：`audit/diffs/{revision_from}_to_{revision_to}/`  
  - `demand_diff.json`
  - `contract_diff.json`
  - `decision_diff.json`
- 必须存在：`audit/rationale/{revision_to}.md|json`
- 若替代/撤销旧版：必须存在 `audit/tombstones/{revision_from}.json`

**FAIL 条件**：任一缺失 → 禁止签发 Permit。

---

## 10) Permit 签发前置条件（必须）
Permit 只能在以下都 PASS 后签发：
- L3 AuditPack 最小清单齐全 + checksums 校验通过
- 三哈希写入且可重算一致
- 若迭代：diff+rationale+tombstone 齐全

**FAIL 条件**：任一不满足 → Permit = null（或直接不生成），并返回 error_code（建议用 `SF_PACK_AUDIT_FAILED` / `SF_VALIDATION_ERROR`）。

---

如果你要更进一步“极致不扯皮”，我建议把 **keyset 的字段列表**直接写成机器可读的 `orchestration/hash_keysets.yml`，validate.py 从它生成剔除/包含逻辑，避免未来口径漂移。

---

## User
*2026-03-03 18:07:28*

keyset 的字段列表直接写成机器可读的 orchestration/hash_keysets.yml，validate.py 从它生成剔除/包含逻辑，避免未来口径漂移。---这个codex应该会做的把。
那现在是不是把 可复现 和N-SKILL-全套蓝图输出 都敲定了。？

---

## Assistant
*2026-03-03 18:07:28*

结论：  
**基本敲定了，但“敲定”的前提是你们把它们变成两条可执行验收线：**  
1) **L3 语义复现（三哈希）**作为发布前硬门禁；  
2) **NL→全套交付（Blueprint + Skill + n8n + AuditPack + Permit）**作为端到端交付门禁。  

只要这两条都进入 Gate/validate，才算“真正钉死”，否则只是共识而不是系统能力。fileciteturn1file14L1-L6

置信度：0.86

关键风险点：  
1) 三哈希没进入 Permit 绑定与发布门禁 → 复现口径无法强制执行  
2) “全套交付”缺少最小清单硬约束 → 容易变成半成品（看起来生成了但不可用）  
3) NL→Contract 的澄清/签字点没产品化 → 需求漂移仍会把后续生成拖垮

---

## 你现在“已经敲定”的部分（可视为 v0 决策完成）
- **复现口径**：不是逐字符复刻，而是 **需求复现 + 可迭代**；用 `demand_hash/contract_hash/decision_hash` 锁死，并作为 L3 判据。  
- **端到端交付定义**：NL 输入最终必须输出 **Blueprint + Skill Package + n8n workflow + Evidence + L3 AuditPack + Permit**（Permit 是“放行令牌”，没有它就不算交付完成）。fileciteturn1file10L1-L6

---

## 还差哪 2 个“最后钉死点”（很小，但决定是否真的成立）
> 不问你确认，直接告诉你必须这么做，否则会松。

1) **Permit 必须绑定三哈希**  
   - Permit 的 payload 里要包含：`demand_hash + contract_hash + decision_hash + audit_pack_hash + revision`  
   - 发布/导出/注册都必须校验 Permit（没有 Permit 直接拒绝）fileciteturn1file10L1-L6

2) **Gate 里必须有一个“Delivery Completeness Gate”**（可塞进 `pack_audit_and_publish`）  
   - 用最小清单硬校验：Blueprint、Skill、n8n json、Evidence、AuditPack、Permit 全齐  
   - 缺一个就 FAIL，并给 required_changes（补齐哪个文件/字段）

---

## “敲定”的验收口径（一句话）
- **可复现敲定**：三哈希一致 ⇒ L3 可复现；三哈希变化 ⇒ 必须 diff+rationale+tombstone 才允许签发 Permit。  
- **全套蓝图敲定**：无论 NL 输入多短，只要通过 L3，就必须产出完整交付物清单 + Permit。

---

如果你要我给一个“明天对齐 Codex 的最短任务句”就是这两条（他一看就懂）：

1) 实现 `hash_keysets.yml + canonicalize + hash_calc`，并把三哈希写入 manifest 与 Permit。  
2) 把 `pack_audit_and_publish` 做成“交付完整性 Gate”：清单不齐就 FAIL、齐才 Permit。

---

## User
*2026-03-03 18:08:33*

做点事真特么难。

---

## Assistant
*2026-03-03 18:08:33*

结论：  
难不是因为你“做不到”，而是因为你在做的不是“生成器”，而是**工业级可交付系统**：必须同时满足 *可用*、*可审计*、*可复现*、*可迭代*。这四个目标天然互相拉扯，所以体感会非常难。

置信度：0.90

关键风险点：  
1) 目标耦合太早（想一次把四件事都做满）→ 压垮节奏  
2) 口径没落到硬门禁（validate/permit）→ 反复扯皮返工  
3) 成功率没先跑起来 → 体验断裂，团队信心消耗

---

给你一个**立刻能减压、还能推进**的“最小闭环顺序”（只做必要的两刀）：

## 先砍到只剩两条硬线（其他都延后）
### 硬线 1：三哈希 + Permit 绑定（复现主权）
- demand_hash / contract_hash / decision_hash 计算出来  
- 写入 AuditPack manifest  
- Permit 必须绑定三哈希 + audit_pack_hash  
> 这一步一旦完成，后面所有讨论都不扯皮了。

### 硬线 2：交付完整性清单（可用主权）
- pack_audit_and_publish 里加一个 checklist：Blueprint/Skill/n8n/Evidence/AuditPack/Permit 缺一 FAIL  
> 这一步做完，你的“能用”就被硬约束住了。

---

## 你现在的痛苦点，其实是“没把复杂度外包给规则”
你已经想到把 keyset 写成 `hash_keysets.yml`，这就是正确方向：  
**让规则成为系统的一部分，而不是人的脑子的一部分。**

---

如果你愿意，我建议你明天就让 Codex 只做一个 PR，内容只包含：

1) `orchestration/hash_keysets.yml`  
2) `tools/canonicalize.py` + `tools/hash_calc.py`  
3) validate 增加：三哈希写入+一致性校验 + Permit 绑定校验  
4) pack gate 增加：交付清单检查

其他任何“更高级的 NL 理解、更多技能、更多生态”一律不做。

这一个 PR 合上，你会瞬间感觉：**事情一下子简单了。**

---

## User
*2026-03-03 18:10:48*

没事 幸好有AI ，他来理解和生成指令和执行，最后收口封板冻结，只是需要逐步来落实。还是在三权分立的前提下实现，必然不是那么顺畅。

---

## Assistant
*2026-03-03 18:10:48*

结论：  
你这个判断是对的：在“三权分立”（生成权 / 审核裁决权 / 执行发布权）前提下推进，**不可能顺滑**，但它会带来一个极强的长期收益——系统一旦封板冻结，就能稳定规模化运转；而 AI 的价值正是在中间阶段承担“理解→拆解→生成→执行→产证据”的大头工作量。fileciteturn1file14L1-L6

置信度：0.89

关键风险点：  
1) 三权边界没写成硬门禁（Permit/validate）→ 权力回流、绕过出现  
2) 生成权过强（AI 直接决定裁决）→ 审计失真、L3 失效  
3) 执行权过强（n8n/外部编排可自行发布）→ 治理形同虚设

---

## 你说的“三权分立”在 GM-SkillForge 里最稳的定义
用你们现有术语把它钉死：

1) **生成权（Build/Generate）**  
   - AI/Skills：NL→DemandSpec→Contract→Blueprint→Skill→n8n JSON  
   - 允许快速迭代、允许重跑、允许重写

2) **裁决权（Judge/Govern）**（内核独占）  
   - 8 Gate 的 PASS/FAIL  
   - 三哈希口径  
   - L3 AuditPack 达标检查  
   - 只要不满足就 FAIL

3) **执行/发布权（Run/Publish）**（n8n/外部）  
   - 抓 repo、触发、重试、通知、开 PR、发 Release  
   - 但必须携带 **Permit**，否则不得发布fileciteturn1file10L1-L6

一句话：  
**AI 可以生成一切，但不能放行；n8n 可以干一切，但不能越权。**

---

## “逐步落实”怎么不痛苦：只抓两个冻结点
你现在最该“封板冻结”的不是全系统，而是这两块：

### 冻结点 1：三哈希口径（复现主权）
- demand_hash / contract_hash / decision_hash 计算逻辑写死  
- 写入 AuditPack + Permit  
- 复现与迭代验收只认它（以后不争论）

### 冻结点 2：Permit 门禁（裁决主权）
- 只有内核能签发 Permit  
- 发布必须验 Permit（n8n 也不例外）fileciteturn1file10L1-L6

这两个冻结点一落，剩下的就全是“生成层能力增强”，再怎么迭代都不会把系统搞散。

---

## 你现在的推进节奏建议（非常现实）
- 先让 AI 帮你把“规则写成文件”（hash_keysets.yml、delivery checklist、error policy）  
- 再让 Codex 把规则变成 validate/gate 的硬实现  
- 最后才让 AI 去扩展更多 NL 场景与 skill 模板

这就是把“不顺畅”变成可控工程推进的方式：  
**先冻结裁决与复现，再放开生成与扩展。**

---

如果你想，我可以把“三权分立”再压成一张**系统责任矩阵**（谁能改什么文件、谁能触发什么 Gate、谁能签 Permit、谁能发布），用于你明天对齐时直接当“宪法附件”。

---
