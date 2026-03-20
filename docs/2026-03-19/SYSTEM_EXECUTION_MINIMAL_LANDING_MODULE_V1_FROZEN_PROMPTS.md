# 系统执行层 Frozen 判断模块 v1 分派提示词

## 发给 vs--cc1（F1 Execution）

```text
你是任务 F1 的执行者 vs--cc1。

目标：
- 核对 workflow / orchestrator / service / handler / api 五子面的目录、最小骨架、导入链、目录与文档一致性

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F1_execution_report.md`

硬约束：
- 只核对，不修改代码
- 不进入 runtime / 外部执行 / 集成
- 不改 frozen 主线
```

## 发给 Kior-A（F1 Review）

```text
你是任务 F1 的审查者 Kior-A。

你不做执行，只做结构审查。

审查目标：
1. 五子面目录是否齐全
2. 五子面最小骨架是否齐全
3. 导入链说明与实际骨架是否一致
4. 目录与文档口径是否一致

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F1_review_report.md`

必须明确给出：
- PASS / REQUIRES_CHANGES / FAIL
- 证据文件与行号
```

## 发给 Kior-C（F1 Compliance）

```text
你是任务 F1 的合规官 Kior-C。

本轮只做 B Guard 式硬审，不做执行，不做普通质量审查。

本轮只检查：
1. 结构核对是否试图越权修改 frozen 主线
2. 结构核对是否借机扩大到 runtime
3. 结构核对是否借机扩大到外部执行 / 集成
4. 结构核对是否把目录问题扩写成新实现任务

Zero Exception Directives：
- 只要要求修改 frozen 主线，直接 FAIL
- 只要要求补 runtime / external integration，直接 FAIL
- 只要借核对扩模块，直接 FAIL

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F1_compliance_attestation.md`
- 必须明确写出 PASS / FAIL
```

## 发给 Antigravity-1（F2 Execution）

```text
你是任务 F2 的执行者 Antigravity-1。

目标：
- 核对 workflow / orchestrator / service / handler / api 的职责边界、不负责项、相互关系与职责吞并风险

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F2_execution_report.md`

硬约束：
- 只做职责冻结核对
- 不给出 Frozen 最终结论
- 不补 runtime / 外部执行 / 集成
```

## 发给 vs--cc3（F2 Review）

```text
你是任务 F2 的审查者 vs--cc3。

你不做执行，只做职责审查。

审查目标：
1. workflow / orchestrator / service / handler / api 职责边界是否清晰
2. 五子面不负责项是否清晰
3. 相互关系是否清晰
4. 是否出现职责吞并、职责断裂或职责重叠

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F2_review_report.md`

必须明确给出：
- PASS / REQUIRES_CHANGES / FAIL
- 证据文件与行号
```

## 发给 Kior-C（F2 Compliance）

```text
你是任务 F2 的合规官 Kior-C。

本轮只做 B Guard 式硬审。

本轮只检查：
1. 职责冻结核对是否把 workflow / orchestrator 推成裁决层
2. 是否把 service / handler / api 推成真实业务执行层
3. 是否借职责核对引入 runtime / 外部集成
4. 是否借职责核对倒灌 frozen 主线

Zero Exception Directives：
- 只要 workflow / orchestrator 被主化为裁决层，直接 FAIL
- 只要 service / handler / api 被主化为真实执行层，直接 FAIL
- 只要出现 runtime / external integration，直接 FAIL

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F2_compliance_attestation.md`
- 必须明确写出 PASS / FAIL
```

## 发给 Antigravity-2（F3 Execution）

```text
你是任务 F3 的执行者 Antigravity-2。

目标：
- 核对 frozen 主线是否被倒灌
- 核对 runtime 是否混入
- 核对外部执行 / 集成是否混入
- 核对 workflow / orchestrator / service / handler / api 是否越权

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F3_execution_report.md`

硬约束：
- 只核对边界与合规
- 不修改任何实现
- 发现阻断项只记录，不修复
```

## 发给 Kior-A（F3 Review）

```text
你是任务 F3 的审查者 Kior-A。

你不做执行，只做边界审查。

审查目标：
1. frozen 主线倒灌判断是否有证据
2. runtime / 外部执行 / 集成混入判断是否有证据
3. workflow / orchestrator / service / handler / api 越权判断是否有证据
4. 阻断项与非阻断项分类是否清晰

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F3_review_report.md`

必须明确给出：
- PASS / REQUIRES_CHANGES / FAIL
- 证据文件与行号
```

## 发给 Kior-C（F3 Compliance）

```text
你是任务 F3 的合规官 Kior-C。

本轮只做 B Guard 式硬审。

本轮只检查：
1. 是否存在 frozen 主线倒灌
2. 是否存在 runtime 混入
3. 是否存在外部执行 / 集成混入
4. 是否存在编排层兼裁决层的主化风险

Zero Exception Directives：
- 只要出现 frozen 主线倒灌，直接 FAIL
- 只要出现 runtime / external integration，直接 FAIL
- 只要执行层兼裁决层，直接 FAIL

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F3_compliance_attestation.md`
- 必须明确写出 PASS / FAIL
```

## 发给 Kior-B（F4 Execution）

```text
你是任务 F4 的执行者 Kior-B。

目标：
- 起草 Frozen 范围清单
- 起草 Frozen 后允许变更 / 受控变更 / 禁止变更
- 起草下一阶段前不得触碰的实现面

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F4_execution_report.md`

硬约束：
- 只起草规则草案
- 不改代码
- 不越权宣布 Frozen 成立
```

## 发给 vs--cc1（F4 Review）

```text
你是任务 F4 的审查者 vs--cc1。

你不做执行，只做规则草案审查。

审查目标：
1. Frozen 范围条目是否完整
2. 允许变更 / 受控变更 / 禁止变更是否自洽
3. 下一阶段前不得触碰的实现面是否清晰
4. 规则草案是否与现有模块事实一致

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F4_review_report.md`

必须明确给出：
- PASS / REQUIRES_CHANGES / FAIL
- 证据文件与行号
```

## 发给 Kior-C（F4 Compliance）

```text
你是任务 F4 的合规官 Kior-C。

本轮只做 B Guard 式硬审。

本轮只检查：
1. 规则草案是否偷渡 runtime / 外部执行 / 集成
2. 是否偷渡治理裁决语义
3. 是否扩大系统执行层模块范围
4. 是否越权宣布 Frozen 成立

Zero Exception Directives：
- 只要规则草案偷渡 runtime / external integration，直接 FAIL
- 只要规则草案把执行层写成裁决层，直接 FAIL
- 只要越权宣布 Frozen 成立，直接 FAIL

输出：
- `docs/2026-03-19/verification/system_execution_frozen/F4_compliance_attestation.md`
- 必须明确写出 PASS / FAIL
```

## Codex 终验条件
- F1/F2/F3/F4 的 execution / review / compliance 全部回收
- 无阻断性越界问题
- Frozen 范围与 change control rules 可固化
- 才允许输出 Frozen 结论
