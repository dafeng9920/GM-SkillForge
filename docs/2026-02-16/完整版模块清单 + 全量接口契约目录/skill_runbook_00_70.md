# skill_runbook_00_70

- 项目根目录: `D:\GM-SkillForge`
- 执行环境: `Python 3.11+`
- 工作目录: `D:\GM-SkillForge`

## 1. 前置检查

1. 确认目录存在：
- `docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts`
- `skillforge/src`

2. 确认 00_common 文件存在：
- `envelope_v1.md`
- `error_codes_v1.md`
- `trace_context_v1.md`

## 2. 执行顺序（固定）

1. `contract-common-builder`
2. `contract-module-builder`（10 到 70）
3. `contract-consistency-auditor`
4. `governance-boundary-auditor`

## 3. 命令模板

### 3.1 contract-common-builder
```bash
python -m skillforge.skills.contract_common_builder --input-file config/contract_common_input.json
```

### 3.2 contract-module-builder
```bash
python -m skillforge.skills.contract_module_builder --input-file config/modules/10_input.json
python -m skillforge.skills.contract_module_builder --input-file config/modules/20_outer_spiral.json
python -m skillforge.skills.contract_module_builder --input-file config/modules/30_composer.json
python -m skillforge.skills.contract_module_builder --input-file config/modules/40_skill_artifact.json
python -m skillforge.skills.contract_module_builder --input-file config/modules/50_governance.json
python -m skillforge.skills.contract_module_builder --input-file config/modules/60_runtime.json
python -m skillforge.skills.contract_module_builder --input-file config/modules/70_read_models.json
```

### 3.3 contract-consistency-auditor
```bash
python -m skillforge.skills.contract_consistency_auditor --input '{"contracts_root":"docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts"}' --output audit_report_consistency.json
```

### 3.4 governance-boundary-auditor
```bash
python -m skillforge.skills.governance_boundary_auditor --input '{"project_root":"D:\\GM-SkillForge","scan_paths":["skillforge/src/nodes","skillforge/src/adapters"]}' --output audit_report_boundary.json
```

## 4. 增量更新流程

当单模块源码发生变化：
1. 只重跑该模块对应 `contract-module-builder`。
2. 重跑 `contract-consistency-auditor`。
3. 如涉及 skill runtime/adapter 逻辑，重跑 `governance-boundary-auditor`。

## 5. 常见失败与处理

1. `status=rejected` 且 `missing_fields` 非空
- 处理: 补齐输入字段，不允许默认猜测。

2. `broken_references > 0`
- 处理: 修复前序依赖引用或补齐目标契约文件。

3. `total_violations > 0`
- 处理: 删除越权调用，禁止在 Skill 层执行治理动作。

## 6. 运行产物

- `audit_report_consistency.json`
- `audit_report_boundary.json`
- 各模块更新后的 `*_v1.md` 文档
