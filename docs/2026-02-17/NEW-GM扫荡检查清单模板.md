# NEW-GM 扫荡检查清单模板

> 目的: 在迁移到 GM-SkillForge 前，先冻结“组件意图、边界、依赖、迁移优先级”。
> 原则: 先审计后迁移；Fail-Closed；不可依据猜测补全。

---

## 0. 扫荡元数据

- 扫荡批次ID:
- 扫荡日期:
- 审计人:
- 目标仓库:
- 源仓库:
- 范围说明:
- 排除说明:

---

## 1. 组件清单总表（白名单 / 黑名单）

| 组件ID | 源路径 | 责任边界 | 迁移结论 | 结论依据 | 风险级别 | 备注 |
|---|---|---|---|---|---|---|
| 示例: GATE-ENFORCER | src/services/gates/gate_enforcer.py | 门禁执行 | 白名单 | 属于治理内核，不可替代 | High | |

迁移结论枚举:
- `白名单`: 必须迁移
- `灰名单`: 待验证后决定
- `黑名单`: 不迁移

---

## 2. 白名单组件逐项审计卡

> 每个白名单组件复制一份本卡。

### 2.1 组件识别
- 组件ID:
- 组件名称:
- 源路径:
- 组件类型: `governance | gate | evidence | replay | ssot | adapter | other`
- 负责人(若有):

### 2.2 架构意图冻结
- 组件唯一职责（一句话）:
- 不可改变行为:
- 可调整行为:
- 禁止行为:

### 2.3 输入 / 输出契约
- 输入对象:
- 输出对象:
- 必填字段:
- 错误码语义:

### 2.4 Fail-Closed 条件
- 缺失输入时:
- 版本不一致时:
- 证据完整性失败时:
- 其他拒绝条件:

### 2.5 依赖图
- 直接依赖文件:
- 运行时依赖:
- 配置依赖:
- 环境变量依赖:

### 2.6 迁移方案
- 迁移方式: `copy-only`
- 目标路径:
- 是否需要 stub/mock:
- 是否需要适配层:

### 2.7 验收标准
- 单元验收命令:
- 通过条件:
- 回归用例:

### 2.8 风险登记
- 主要风险:
- 风险等级:
- 缓解动作:

---

## 3. 黑名单组件登记卡

> 黑名单也要登记依据，避免后续反复讨论。

| 组件ID | 源路径 | 不迁移原因 | 触发条件（何时重审） |
|---|---|---|---|
| 示例: N8N-WORKFLOW | archives/deprecated/n8n-nodes-gm/** | 历史/生态耦合，不属于内核 | 若未来需要外部编排再重审 |

---

## 4. SSOT 对齐清单

### 4.1 错误码 SSOT
- 文件:
- 是否唯一来源:
- 是否存在别名/兼容层:
- 冲突项:

### 4.2 契约 SSOT
- Evidence 契约文件:
- Replay 契约文件:
- Gate 契约文件:
- 不一致项:

### 4.3 元数据 SSOT
- trace_id 规范:
- spec_ref 规范:
- decision_hash 规范:

---

## 5. Gate / Evidence / Replay 专项检查

### 5.1 Gate
- Preflight Gate 是否独立可运行:
- Evidence Gate 是否独立可运行:
- Replay Gate 是否独立可运行:
- Gate 是否可被绕过:

### 5.2 Evidence
- 证据写入入口:
- 证据存储路径:
- 完整性校验方式:
- 是否 append-only:

### 5.3 Replay
- 回放输入来源:
- 回放判定逻辑:
- 回放失败返回规范:
- 是否存在“推断补事实”路径:

---

## 6. 迁移优先级与批次计划

| 批次 | 组件列表 | 目标 | 通过门槛 | 状态 |
|---|---|---|---|---|
| Batch-1 | Gate + SSOT | 门禁独立可跑 | Gate 单测全绿 | |
| Batch-2 | Evidence + Replay | 证据回放闭环 | E2E pass/fail可验证 | |
| Batch-3 | 外螺旋契约层 | 接口统一 | 契约审计无阻断项 | |

---

## 7. 审计输出物（必须落盘）

- 组件白名单: `docs/migration/whitelist.md`
- 组件黑名单: `docs/migration/blacklist.md`
- 依赖图: `docs/migration/dependency-map.md`
- 语义冻结: `docs/migration/semantic-freeze.md`
- 迁移批次计划: `docs/migration/migration-batches.md`
- 风险清单: `docs/migration/risk-register.md`

---

## 8. 最终签署

- 审计结论: `可迁移 | 有条件可迁移 | 不可迁移`
- 阻断项:
- 下一步动作:
- 签署人:
- 日期:
