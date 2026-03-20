# 外部执行与集成准备模块 v1 回填追认提示词

## 本轮唯一目标
- 不重做 execution
- 不重做已完成的 review / compliance 判断
- 只把已经实际完成的 review / compliance 结果，补写到标准回收路径

## 主控官速览

### 这轮只补什么
- 只补 `review_report` / `compliance_attestation`
- 不重做 execution
- 不新增判断范围
- 不扩模块边界

### 补完后我看什么
1. 六个子面是否全部具备 `execution / review / compliance`
2. 每份回填文档是否明确写出 `PASS / REQUIRES_CHANGES / FAIL`
3. 每份回填文档是否带最少 `EvidenceRef`
4. 回填后是否能进入 Codex 统一终验

### 缺口总览表

| Task | 缺口类型 | 执行人 | 必须写回 |
|---|---|---|---|
| E1 | Review | Kior-A | `docs/2026-03-19/verification/external_execution_and_integration_preparation/E1_review_report.md` |
| E1 | Compliance | Kior-C | `docs/2026-03-19/verification/external_execution_and_integration_preparation/E1_compliance_attestation.md` |
| E2 | Review | vs--cc3 | `docs/2026-03-19/verification/external_execution_and_integration_preparation/E2_review_report.md` |
| E2 | Compliance | Kior-C | `docs/2026-03-19/verification/external_execution_and_integration_preparation/E2_compliance_attestation.md` |
| E3 | Review | Kior-A | `docs/2026-03-19/verification/external_execution_and_integration_preparation/E3_review_report.md` |
| E3 | Compliance | Kior-C | `docs/2026-03-19/verification/external_execution_and_integration_preparation/E3_compliance_attestation.md` |
| E4 | Compliance | Kior-C | `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_compliance_attestation.md` |
| E5 | Review | Kior-A | `docs/2026-03-19/verification/external_execution_and_integration_preparation/E5_review_report.md` |
| E5 | Compliance | Kior-C | `docs/2026-03-19/verification/external_execution_and_integration_preparation/E5_compliance_attestation.md` |
| E6 | Compliance | Kior-C | `docs/2026-03-19/verification/external_execution_and_integration_preparation/E6_compliance_attestation.md` |

### 主控官一句话判断标准
- 上表 10 项全部补齐，才算“回填完成”
- 少任何 1 项，都不能进入模块终验

## 统一规则
- 必须写入标准路径
- 必须明确写出 `PASS / REQUIRES_CHANGES / FAIL`
- 必须给出 EvidenceRef 或最少证据定位
- 不补写文件就不算回收完成

## 标准回填路径

### E1
- Review:
  - `docs/2026-03-19/verification/external_execution_and_integration_preparation/E1_review_report.md`
- Compliance:
  - `docs/2026-03-19/verification/external_execution_and_integration_preparation/E1_compliance_attestation.md`

### E2
- Review:
  - `docs/2026-03-19/verification/external_execution_and_integration_preparation/E2_review_report.md`
- Compliance:
  - `docs/2026-03-19/verification/external_execution_and_integration_preparation/E2_compliance_attestation.md`

### E3
- Review:
  - `docs/2026-03-19/verification/external_execution_and_integration_preparation/E3_review_report.md`
- Compliance:
  - `docs/2026-03-19/verification/external_execution_and_integration_preparation/E3_compliance_attestation.md`

### E4
- Compliance:
  - `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_compliance_attestation.md`

### E5
- Review:
  - `docs/2026-03-19/verification/external_execution_and_integration_preparation/E5_review_report.md`
- Compliance:
  - `docs/2026-03-19/verification/external_execution_and_integration_preparation/E5_compliance_attestation.md`

### E6
- Compliance:
  - `docs/2026-03-19/verification/external_execution_and_integration_preparation/E6_compliance_attestation.md`

## 发给 Kior-A / vs--cc3 / vs--cc1（Review 回填）

```text
你现在不是重做 review。

你现在只做“回填追认”：
- 把已经完成的 review 结论
- 以标准格式写入指定文档路径

要求：
1. 明确写出 PASS / REQUIRES_CHANGES / FAIL
2. 写明 task_id、reviewer、executor
3. 写明审查重点
4. 给出最少证据定位（文件路径 / 行号 / 文档段落）
5. 不得在本轮新增新的越界判断范围

注意：
- 不重做 execution
- 不扩模块
- 不进入 runtime / 真实外部系统
```

## 发给 Kior-C（Compliance 回填）

```text
你现在不是重做 compliance。

你现在只做“回填追认”：
- 把已经完成的 compliance 结论
- 以标准格式写入指定文档路径

要求：
1. 明确写出 PASS / REQUIRES_CHANGES / FAIL
2. 写明 task_id、compliance_officer、executor、reviewer
3. 写明 Zero Exception Directives 检查结果
4. 给出最少证据定位（文件路径 / 行号 / 文档段落）
5. 不得在本轮扩大模块边界

注意：
- 不重做 execution
- 不新增新的判断对象
- 不把模块外问题写入模块内阻断项
```

## 逐任务回填提示词

### 发给 Kior-A（E1 Review 回填）

```text
你是任务 E1 的审查者 Kior-A。

你现在不是重做 review。
你现在只把已经完成的 E1 review 结论回填到标准文档。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E1_review_report.md`

必须包含：
1. `task_id: E1`
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. connector contract 的审查重点
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

### 发给 Kior-C（E1 Compliance 回填）

```text
你是任务 E1 的合规官 Kior-C。

你现在不是重做 compliance。
你现在只把已经完成的 E1 compliance 结论回填到标准文档。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E1_compliance_attestation.md`

必须包含：
1. `task_id: E1`
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

### 发给 vs--cc3（E2 Review 回填）

```text
你是任务 E2 的审查者 vs--cc3。

你现在不是重做 review。
你现在只把已经完成的 E2 review 结论回填到标准文档。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E2_review_report.md`

必须包含：
1. `task_id: E2`
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. integration gateway 的审查重点
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

### 发给 Kior-C（E2 Compliance 回填）

```text
你是任务 E2 的合规官 Kior-C。

你现在不是重做 compliance。
你现在只把已经完成的 E2 compliance 结论回填到标准文档。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E2_compliance_attestation.md`

必须包含：
1. `task_id: E2`
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

### 发给 Kior-A（E3 Review 回填）

```text
你是任务 E3 的审查者 Kior-A。

你现在不是重做 review。
你现在只把已经完成的 E3 review 结论回填到标准文档。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E3_review_report.md`

必须包含：
1. `task_id: E3`
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. secrets / credentials boundary 的审查重点
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

### 发给 Kior-C（E3 Compliance 回填）

```text
你是任务 E3 的合规官 Kior-C。

你现在不是重做 compliance。
你现在只把已经完成的 E3 compliance 结论回填到标准文档。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E3_compliance_attestation.md`

必须包含：
1. `task_id: E3`
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

### 发给 Kior-C（E4 Compliance 回填）

```text
你是任务 E4 的合规官 Kior-C。

你现在不是重做 compliance。
你现在只把已经完成的 E4 compliance 结论回填到标准文档。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E4_compliance_attestation.md`

必须包含：
1. `task_id: E4`
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

### 发给 Kior-A（E5 Review 回填）

```text
你是任务 E5 的审查者 Kior-A。

你现在不是重做 review。
你现在只把已经完成的 E5 review 结论回填到标准文档。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E5_review_report.md`

必须包含：
1. `task_id: E5`
2. reviewer / executor
3. PASS / REQUIRES_CHANGES / FAIL
4. retry / compensation boundary 的审查重点
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

### 发给 Kior-C（E5 Compliance 回填）

```text
你是任务 E5 的合规官 Kior-C。

你现在不是重做 compliance。
你现在只把已经完成的 E5 compliance 结论回填到标准文档。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E5_compliance_attestation.md`

必须包含：
1. `task_id: E5`
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

### 发给 Kior-C（E6 Compliance 回填）

```text
你是任务 E6 的合规官 Kior-C。

你现在不是重做 compliance。
你现在只把已经完成的 E6 compliance 结论回填到标准文档。

必须写入：
- `docs/2026-03-19/verification/external_execution_and_integration_preparation/E6_compliance_attestation.md`

必须包含：
1. `task_id: E6`
2. compliance_officer / executor / reviewer
3. PASS / REQUIRES_CHANGES / FAIL
4. Zero Exception Directives 检查结果
5. 最少 EvidenceRef（文件路径 / 行号 / 文档段落）
```

## Codex 终验条件
- 以上缺失的 review / compliance 文档全部补齐
- 六个子面都具备 `execution / review / compliance`
- 然后 Codex 统一终验
