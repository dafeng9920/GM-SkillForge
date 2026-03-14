# PR1: 三哈希基础设施（v0）

## 目标

把 L3 复现口径落成可执行工具链：
- `demand_hash`
- `contract_hash`
- `decision_hash`

口径来源：`orchestration/hash_keysets.yml`

## 新增文件

- `orchestration/hash_keysets.yml`
- `scripts/hash_calc.py`
- `scripts/validate_three_hashes.py`

## 使用方法

### 1) 计算三哈希并生成 manifest

```powershell
python scripts/hash_calc.py `
  --demand <demand.json> `
  --contract <contract.json> `
  --decision <decision.json> `
  --out <three_hash_manifest.json>
```

输出：
- `hash_spec_version`
- `demand_hash`
- `contract_hash`
- `decision_hash`
- `canonical_inputs`（用于审计回溯）

### 2) 验证 manifest 与当前输入一致

```powershell
python scripts/validate_three_hashes.py `
  --demand <demand.json> `
  --contract <contract.json> `
  --decision <decision.json> `
  --manifest <three_hash_manifest.json>
```

通过输出：
- `PASS`

失败输出：
- `FAIL` + mismatch 明细

## 当前口径（v0）

- 全局排除字段（时间/随机等非确定性）
- Demand 排除：`summary`, `clarifications_needed`
- Contract 排除：`at_time`
- Decision 按固定 8 Gate 顺序归一

说明：v0 先保证“可运行 + 可复现”，后续在 PR2/PR3 增强 Permit 绑定与迭代证据链。

## 本地冒烟结果

已在 `.tmp/pr1_smoke/` 完成冒烟：
- `hash_calc.py` => PASS
- `validate_three_hashes.py` => PASS

### 冒烟命令与输出

```powershell
# 验证 manifest
python scripts/validate_three_hashes.py `
  --demand .tmp/pr1_smoke/demand.json `
  --contract .tmp/pr1_smoke/contract.json `
  --decision .tmp/pr1_smoke/decision.json `
  --manifest .tmp/pr1_smoke/three_hash_manifest.json
```

**输出:**
```
PASS
- hash_spec_version: v0
- demand_hash: 0aadae06454b317fbefc9c997e63336128752993552909090ead5ccfd8039429
- contract_hash: cf9436bed520a4d6edd0e084ab3da4df1b3cf7a6c540a571daf8503a20465f8a
- decision_hash: 80bbb0b07dc13e01e32a93f8c405686f0f011bae172749b8a3e39db3f7d51e2a
```

## 下一步（PR2）

- Permit 绑定三哈希
- Delivery Completeness Gate（Blueprint/Skill/n8n/Evidence/AuditPack/Permit 缺一 FAIL）
