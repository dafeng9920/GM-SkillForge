# 五层主线 AuditPack / EvidenceRef 桥接 v1

## 目的
- 将五层主线与 `AuditPack/evidence`、`EvidenceRef / evidence_ref` 正式挂接。
- 该桥接只补证据口径，不修改既有 frozen 对象。

## 证据位置
- 主证据目录：
  - [AuditPack/evidence](/d:/GM-SkillForge/AuditPack/evidence)

## 证据类型
- 当前五层主线后续应允许引用的证据类型至少包括：
  - frozen 判断证据
  - validation 证据
  - compliance 审计证据
  - permit 入口条件证据
  - 组件盘点 / 覆盖差异证据

## 引用口径

### EvidenceRef
- 用途：
  - 作为主线文档引用具体证据的稳定标识
- 要求：
  - 可定位到证据文件或证据集合
  - 可被主控 / 验收 / 合规记录共同引用

### evidence_ref
- 用途：
  - 作为结构化报告中的字段级证据引用
- 要求：
  - 不得为空
  - 不得只做叙述性描述
  - 必须能回到 `AuditPack/evidence` 或其索引

## 五层主线的桥接方式
- `Bridge`
  - 可引用其 frozen / validation 对应证据
- `Governance Intake`
  - 可引用其 frozen / validation 对应证据
- `Gate`
  - 可引用其 frozen / validation 对应证据
- `Review`
  - 可引用其 frozen / validation 对应证据
- `Release`
  - 可引用其 frozen / validation 对应证据
- `Audit`
  - 可引用其 frozen / validation 对应证据

## 合规要求
- 五层主线若要进入系统执行层准备，必须至少具备：
  - 一条 `AuditPack/evidence` 证据路径
  - 一组 `EvidenceRef / evidence_ref` 引用规则
  - 一份合规审计报告中的证据定位

## 禁止项
- 不得把 `AuditPack/evidence` 当成可有可无的背景目录
- 不得只在仓库存在证据目录，却不在主线材料里引用
- 不得用口头结论替代 `EvidenceRef / evidence_ref`

## 当前桥接结论
- 当前五层主线已存在证据目录：
  - [AuditPack/evidence](/d:/GM-SkillForge/AuditPack/evidence)
- 当前五层主线后续材料应以本桥接文档为准，把证据目录与主线合规结论绑定起来
