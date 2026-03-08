# Wave 0 Gate Decisions

## T-W0-A: constitution_ref 嵌入 manifest → `ALLOW` ✅

**执行者**: vs--cc1

| 检查项 | 结果 |
|---|---|
| 交付物齐全 | ✅ `utils/__init__.py`, `utils/constitution.py`, `pack_publish.py` |
| Gate Check 全绿 | ✅ 95/95 passed |
| constitution_ref 在 provenance | ✅ L405 |
| constitution_hash 在 provenance | ✅ L406 |
| MISSING → rejected | ✅ L443-445 |
| 红线遵守 | ✅ 未越权 |

**Decision: `ALLOW`**

---

## T-W0-B: constitution_gate 版本对齐 → `ALLOW` ✅

**执行者**: vs--cc2

| 检查项 | 结果 |
|---|---|
| 交付物齐全 | ✅ `constitution_gate.py` |
| 导入 load_constitution | ✅ 从 utils 导入,未重复实现 |
| MISSING → DENY | ✅ L78-93 |
| 硬编码 "0.1.0" 消除 | ✅ 使用 constitution_ref |
| constitution_hash 在 details | ✅ |
| 红线遵守 | ✅ 未越权 |

**Decision: `ALLOW`**

---

## T-W0-C: validate.py CHECK 16-17 → `ALLOW` ✅

**执行者**: Kior-C

| 检查项 | 结果 |
|---|---|
| 交付物齐全 | ✅ `validate.py` |
| CHECK 16 CONSTITUTION_EXISTS | ✅ L481-490 |
| CHECK 17 CONSTRAINTS_EXISTS | ✅ L492-500 |
| 17-Point 标题 | ✅ L511 |
| validate --audit-config 17/17 | ✅ 全绿 |
| 红线遵守 | ✅ 未修改 CHECK 1-15 |

**Decision: `ALLOW`**

---

## T-W0-D: 宪法强制测试 → `ALLOW` ✅

**执行者**: Kior-A

| 检查项 | 结果 |
|---|---|
| 交付物齐全 | ✅ `test_constitution_enforcement.py` (311行, 5个测试) |
| 5/5 tests passed | ✅ |
| REJECTED 路径覆盖 | ✅ test_gate_deny + test_pack_rejected |
| V1-Prove §6.4 满足 | ✅ 可追溯 REJECTED |
| 使用 fixtures 隔离 | ✅ monkeypatch, tmp_path |
| 红线遵守 | ✅ 未越权 |

**Decision: `ALLOW`**

---

## T-W0-E: v3 引用替换清单 → `ALLOW` ✅

**执行者**: 主控官

| 检查项 | 结果 |
|---|---|
| 扫描完成 | ✅ 1 个旧文件需标注废弃 |
| 0 处代码需改 | ✅ |

**Decision: `ALLOW`**

---

## 遗留问题记录

| 问题 | 影响面 | 与 Wave 0 关系 |
|---|---|---|
| `test_protocols.py` 12 个 `test_execute_raises_not_implemented` 失败 | 期待 `execute()` 抛 `NotImplementedError`，但所有 12 个 node 已有真实实现 | ❌ 无关，历史遗留 |
