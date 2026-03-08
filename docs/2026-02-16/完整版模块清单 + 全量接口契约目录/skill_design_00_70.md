# skill_design_00_70

- 项目: `D:\GM-SkillForge`
- 版本: `v1.0`
- 范围: `docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts/00_common` 到 `70_read_models`

## 1. 目标

实现 4 个 Skill，用于 00-70 契约文档体系的生成与审计：
1. `contract-common-builder`
2. `contract-module-builder`
3. `contract-consistency-auditor`
4. `governance-boundary-auditor`

## 2. 非目标

1. 不实现 Gate/Evidence/Replay 执行内核。
2. 不实现外部编排（n8n、webhook、remote executor）。
3. 不实现自动修复，只做生成与审计。

## 3. 目录约束

### 3.1 固定目录
- `contracts/00_common`
- `contracts/10_input`
- `contracts/20_outer_spiral`
- `contracts/30_composer`
- `contracts/40_skill_artifact`
- `contracts/50_governance`
- `contracts/60_runtime`
- `contracts/70_read_models`

### 3.2 00_common 固定文件名
- `envelope_v1.md`
- `error_codes_v1.md`
- `trace_context_v1.md`

## 4. Skill 规格

## 4.1 contract-common-builder

### Purpose
从源码提取公共契约并写入 `00_common`。

### Inputs
- `project_root: string`
- `source_paths: string[]`
- `output_dir: string`
- `schema_version: string`

### Outputs
- `status: completed|failed|rejected`
- `generated_files: string[]`
- `provenance: { skill_id, run_id, skill_version }`
- `timestamp: datetime`

### Constraints
- `output_dir` 必须在 `contracts/00_common`。
- 缺路径、空输入、越界路径必须 `rejected`。

## 4.2 contract-module-builder

### Purpose
按模块生成 `10-70` 契约文件并建立对 `00_common` 的引用。

### Inputs
- `project_root: string`
- `module_id: enum(10_input..70_read_models)`
- `node_source_paths: string[]`
- `common_contracts_dir: string`
- `output_dir: string`

### Outputs
- `status: completed|failed|rejected`
- `module_id: string`
- `generated_files: string[]`
- `cross_references: string[]`
- `timestamp: datetime`

### Constraints
- `common_contracts_dir` 必须包含 `envelope_v1.md/error_codes_v1.md/trace_context_v1.md`。
- 非法 `module_id` 必须 `rejected`。

## 4.3 contract-consistency-auditor

### Purpose
只读扫描 `contracts/**`，输出一致性报告。

### Inputs
- `contracts_root: string`
- `expected_modules?: string[]`

### Outputs
- `status: pass|fail`
- `summary: { total_files, naming_conflicts, broken_references, missing_sections, version_mismatches }`
- `findings: object[]`
- `timestamp: datetime`

### Constraints
- 不修改任何文件。
- 无契约文件时 `fail`。

## 4.4 governance-boundary-auditor

### Purpose
检测 Skill 源码是否越权触发治理内核行为。

### Inputs
- `project_root: string`
- `scan_paths: string[]`
- `forbidden_patterns?: object[]`

### Outputs
- `status: compliant|non_compliant`
- `summary: { total_files, total_violations, total_warnings }`
- `violations: object[]`
- `timestamp: datetime`

### Constraints
- 禁止调用 Gate/Evidence/Replay 执行接口。
- 禁止直接 subprocess 触发外部副作用。

## 5. 数据流

`contract-common-builder -> contract-module-builder(10..70) -> contract-consistency-auditor -> governance-boundary-auditor`

## 6. Fail-Closed 统一规则

1. 输入缺失: `rejected`。
2. 路径不存在: `rejected`。
3. 目录越界: `rejected`。
4. schema 不合法: `failed`。
5. 审计命中违规: `non_compliant`。
