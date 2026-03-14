# T02 任务卡：Canonical JSON 一致性

> **执行者**：vs--cc1 | **审查者**：Antigravity-2 | **合规官**：Kior-C
> **所属 Wave**：Wave 1 | **预计时长**：45 分钟 | **前置依赖**：T01 必须完成

---

## 一、你要做什么

### 背景：为什么需要这个任务？

**问题**：签名是基于内容 hash 的。如果同一份数据每次序列化结果不同，签名就无法验证。

**举例**：
```python
# 这两个 JSON 内容相同，但字符串不同
{"a": 1, "b": 2}
{"b": 2, "a": 1}
# 它们的 hash 会不同 → 签名验证会失败
```

### 具体任务

1. **选定序列化方案**
   - 推荐使用 **JCS (JSON Canonicalization Scheme)**
   - 或者定义自己的规则：键排序、无空格、数字格式统一

2. **实现 canonical_json 函数**
   - 输入：任意 Python dict/list
   - 输出：字符串（保证同一对象每次输出完全一致）

3. **提供测试用例**
   - 相同数据序列化 100 次，hash 必须完全相同
   - 不同顺序的键，输出结果必须相同

---

## 二、产出物

| 文件 | 类型 | 说明 |
|------|------|------|
| `verification/T02_canonical_json_report.md` | 新建 | 实现说明 + 测试结果 |
| `verification/T02_execution_report.yaml` | 新建 | 执行记录 |
| `verification/T02_gate_decision.json` | 新建 | 审查裁决（由 Antigravity-2 填写） |
| `verification/T02_compliance_attestation.json` | 新建 | 合规认证（由 Kior-C 填写） |

---

## 三、参考文件

| 文件 | 用途 |
|------|------|
| `docs/2026-02-26/P0-issues/P0-10-issue-任务清单.md` | 对齐 issue 目标 |
| `docs/2026-02-26/p0-governed-execution/task_dispatch.md` | 对齐依赖与分工 |
| `docs/2026-02-21/架构方向的提问和回复/EXECUTION_GUARD_A_PROPOSAL_SKILL_v1.md` | 治理规则 |
| `docs/EXECUTION_GUARD_B_EXECUTION_SKILL_v1.md` | 执行规范 |

---

## 四、检查清单（执行前）

- [ ] T01 已经完成并 `ALLOW`
- [ ] 已阅读 Guard A/B 文档
- [ ] 已理解"一致性"的含义

---

## 五、验收标准

### 必须通过

| 检查项 | 验证方法 |
|-------|---------|
| 相同数据多次序列化 hash 一致 | 序列化 100 次，hash 全部相同 |
| 键顺序不影响结果 | `{"a":1,"b":2}` 和 `{"b":2,"a":1}` 输出相同 |
| 无 EvidenceRef 不算完成 | 报告中必须引用测试证据 |

### 加分项

- [ ] 支持不同语言实现（Python + JS）结果一致
- [ ] 有性能基准测试

---

## 六、禁止事项

| 禁止 | 原因 |
|------|------|
| 绕过 Compliance PASS 直接执行 | 违反治理流程 |
| 跳过 T01 直接做 T02 | 依赖未满足 |
| 无证据宣称完成 | 无法验证 |
| 修改其他任务的输出文件 | 越权 |

---

## 七、执行流程

```
第 1 步：确认 T01 已 ALLOW
    │
    ▼
第 2 步：实现 canonical_json 函数
    │
    ▼
第 3 步：编写测试用例
    │
    ▼
第 4 步：运行测试，收集证据
    │
    ▼
第 5 步：撰写 T02_canonical_json_report.md
    │   （包含：实现方案、测试代码、运行结果截图/hash）
    │
    ▼
第 6 步：提交 T02_execution_report.yaml
    │
    ▼
第 7 步：等待 Antigravity-2 审查（gate_decision）
    │
    ▼
第 8 步：等待 Kior-C 合规认证（compliance_attestation）
    │
    ▼
第 9 步：收到 ALLOW + PASS → 任务完成
```

---

## 八、报告模板

### T02_canonical_json_report.md

```markdown
# T02 Canonical JSON 实现报告

## 1. 实现方案
- 选定方案：JCS / 自定义
- 核心逻辑：[描述]

## 2. 代码实现
```python
# canonical_json 实现代码
```

## 3. 测试用例
| 输入 | 预期输出 | 实际输出 | 结果 |
|------|---------|---------|------|
| {"b":2,"a":1} | {"a":1,"b":2} | {"a":1,"b":2} | PASS |

## 4. 一致性验证
- 序列化 100 次 hash 结果：[列出前 5 个]
- 结论：全部一致 / 不一致

## 5. EvidenceRef
- 测试代码路径：[路径]
- 运行结果截图：[路径或 hash]
```

### T02_execution_report.yaml

```yaml
task_id: T02
executor: vs--cc1
status: COMPLETED
started_at: 2026-02-26T10:00:00Z
completed_at: 2026-02-26T10:45:00Z
deliverables:
  - path: docs/2026-02-26/p0-governed-execution/verification/T02_canonical_json_report.md
    status: CREATED
evidence_refs:
  - type: TEST_OUTPUT
    path: [测试结果路径]
    hash: [SHA-256]
notes: [任何备注]
```

---

## 九、常见问题

**Q：为什么不能用 Python 的 json.dumps？**
> A：json.dumps 不保证键顺序一致。需要加上 `sort_keys=True` 或使用专门的 canonicalization 库。

**Q：JCS 是什么？**
> A：JSON Canonicalization Scheme，RFC 8785 标准，专门解决 JSON 序列化一致性问题。

**Q：测试要测到什么程度？**
> A：至少证明：相同数据多次序列化 hash 一致；键顺序不影响结果。

---

## 十、联系方式

- **审查者**：Antigravity-2（负责 gate_decision）
- **合规官**：Kior-C（负责 compliance_attestation）
- **有问题**：先查阅 task_dispatch.md，仍有疑问再联系主控官
