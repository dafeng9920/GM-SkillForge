# DOC_CLASSIFICATION_MATRIX_v1

## 1. 目的

本文件用于把 2026-03-17 架构文档按系统层级、冻结属性和建议归位路径统一落位。

本文件不改冻结正文，只做：

- 文档分类
- 系统层映射
- 冻结/半冻结/后置标记
- 建议归位路径

---

## 2. 归类矩阵

| 文档 | 分类 | 约束层 | 类型 | 系统层映射 | 建议归位路径 | 是否冻结 | 当前动作 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `《系统宪法》V1.md` | 宪法与冻结规则 | 最高约束 | 冻结规则 | 全系统 | `docs/frozen/constitution/` | 是 | 引用，不改正文 |
| `《模块权限清单 v1》.md` | 宪法与冻结规则 | 权限边界 | 冻结规则 | Kernel / Governance / Packaging / Orchestration | `docs/frozen/governance/` | 是 | 引用，不改正文 |
| `《治理冻结清单 + 生产主线待建清单》v1.md` | 宪法与冻结规则 | 阶段策略 | 冻结规则 | Strategy / Roadmap | `docs/frozen/strategy/` | 是 | 引用，不改正文 |
| `《GM-SkillForge 日终收口检查模板 v1》.md` | 宪法与冻结规则 | 执行制度 | 冻结规则 | Daily Checks | `docs/checks/` | 是 | 引用，不改正文 |
| `《5层创建流程的数据结构清单 v1》.md` | 生产主线 | 对象模型 | 半冻结设计输入 | Production | `docs/production/objects/` | 否 | 后续拆成 schema/model |
| `5层流程.md` | 生产主线 | 流程骨架 | 半冻结设计输入 | Production | `docs/production/flow/` | 否 | 保留主链说明 |
| `架构纠偏文档 v1.md` | 生产主线 | 分层纠偏 | 半冻结设计输入 | Entry / Compiler / Kernel / Ops | `docs/production/architecture/` | 否 | 作为角色归位依据 |
| `skill-creator和五层构建的区别.md` | 包装与交付关系 | 交付边界 | 半冻结设计输入 | Delivery / Packaging | `docs/delivery/` | 否 | 作为边界文档 |
| `skill交付形态.md` | 包装与交付关系 | 交付节奏 | 半冻结设计输入 | Delivery | `docs/delivery/` | 否 | 作为用户侧交付说明 |
| `商用skill的构建流程.md` | 商用扩展层 | 商用后置 | 后置参考 | Commercial Extension | `docs/commercial-extension/` | 否 | 记录，不抢主线 |

---

## 3. 归位原则

### A. 宪法与冻结规则

特点：

- 只引用
- 不重释义
- 不改正文
- 不混进当前创建主线

### B. 生产主线

特点：

- 服务当前唯一受保护主链
- 能落成对象、schema、接口、状态机
- 不得抢审计权

### C. 包装与交付关系

特点：

- 解决 `skill-creator` 与 5 层创建流程的关系
- 解决 Draft / Candidate / Released 的交付节奏
- 不得抢创建前段

### D. 商用扩展层

特点：

- 只记录
- 不抢当前主线
- 作为后续 Commercial-grade 增强参考

---

## 4. 哪些内容可直接转系统对象

### 可直接转对象 / schema 的

- `IntentDraft`
- `ContractBundle`
- `CandidateSkill`
- `BuildValidationReport`
- `DeliveryManifest`
- `RunRecord`
- `ReleaseRecord`

### 可直接转配置 / 接口约束的

- 4 个 handoff 接口
- 正式写口归属
- 模块权限白名单

### 当前应继续保留为文档约束的

- 宪法
- 权限清单
- 治理冻结策略
- 日终收口制度
- `skill-creator` 角色边界

---

## 5. 风险提醒

- 若把 `商用skill的构建流程` 提前塞入当前主线，会造成 5 层与 5+3 混线
- 若把 `skill交付形态` 当成主链路本体，会把用户侧节奏误当工程链路
- 若不先做文档归位，后续对象化会继续依赖聊天结论而不是正式文档
