# 完整版模块实现 Skill 规范（修订版 v2）

- 项目根目录: `D:\GM-SkillForge`
- 适用范围: `docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts/00_common` 到 `70_read_models`
- 文档状态: 可执行规范（替代旧版污染文档）

---

## 1. 目标与边界

### 1.1 目标
实现 4 个 Skill，用于生成和审计 `00-70` 契约文档体系：
1. `contract-common-builder`
2. `contract-module-builder`
3. `contract-consistency-auditor`
4. `governance-boundary-auditor`

### 1.2 硬边界
1. Skill 只负责文档生成/文档审计，不执行 Gate/Evidence/Replay 内核行为。
2. Fail-Closed: 输入不完整、路径缺失、schema 不合法时必须 `rejected`。
3. 不引入 n8n、外部编排、自动修复、自动重试。

---

## 2. 目录对齐（以当前仓库为准）

### 2.1 必须对齐的现有文件命名
`00_common` 使用以下文件名，不得改为旧命名：
- `envelope_v1.md`
- `error_codes_v1.md`
- `trace_context_v1.md`

### 2.2 模块目录
- `10_input`
- `20_outer_spiral`
- `30_composer`
- `40_skill_artifact`
- `50_governance`
- `60_runtime`
- `70_read_models`

---

## 3. Skill 设计

## 3.1 `contract-common-builder`

### 职责
从源码提取公共契约定义，生成/更新 `00_common` 文档。

### 输入（最小）
```json
{
  "project_root": "D:\\GM-SkillForge",
  "source_paths": ["skillforge/src/**/*.py"],
  "output_dir": "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts/00_common",
  "schema_version": "0.1.0"
}
```

### 输出（最小）
```json
{
  "status": "completed|failed|rejected",
  "generated_files": ["envelope_v1.md", "error_codes_v1.md", "trace_context_v1.md"],
  "provenance": {"skill_id": "contract-common-builder", "run_id": "..."},
  "timestamp": "..."
}
```

### Fail-Closed
- `project_root` 不存在 -> `rejected`
- `source_paths` 空或不存在 -> `rejected`
- `output_dir` 越界 -> `rejected`

---

## 3.2 `contract-module-builder`

### 职责
为 `10-70` 各模块生成契约文档，并引用 `00_common`。

### 输入（最小）
```json
{
  "project_root": "D:\\GM-SkillForge",
  "module_id": "30_composer",
  "node_source_paths": ["skillforge/src/nodes/skill_composer.py"],
  "common_contracts_dir": "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts/00_common",
  "output_dir": "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts/30_composer"
}
```

### 输出（最小）
```json
{
  "status": "completed|failed|rejected",
  "module_id": "30_composer",
  "generated_files": ["composer_request_v1.md", "composer_result_v1.md", "skill_draft_v1.md"],
  "cross_references": ["error_codes_v1.md", "envelope_v1.md"],
  "timestamp": "..."
}
```

### Fail-Closed
- `module_id` 非法 -> `rejected`
- `common_contracts_dir` 缺失 `envelope_v1.md/error_codes_v1.md/trace_context_v1.md` -> `rejected`
- 目标源文件不存在 -> `rejected`

---

## 3.3 `contract-consistency-auditor`

### 职责
只读扫描 `contracts/**`，输出一致性审计报告。

### 检查项
1. 段落完整性（`Purpose/Inputs/Outputs/Constraints/Example`）
2. 字段命名一致性
3. 引用完整性（跨模块引用是否存在）
4. 版本一致性（`_v1` 命名和 schema_version）

### 输出
```json
{
  "status": "pass|fail",
  "summary": {
    "total_files": 0,
    "naming_conflicts": 0,
    "broken_references": 0,
    "missing_sections": 0,
    "version_mismatches": 0
  },
  "findings": []
}
```

---

## 3.4 `governance-boundary-auditor`

### 职责
检查 Skill 源码是否越权调用治理内核行为。

### 禁止模式（示例）
- 直接调用 Gate 执行
- 直接写 Evidence Store
- 直接触发 Replay
- 直接 `subprocess` 执行系统命令

### 输出
```json
{
  "status": "compliant|non_compliant",
  "summary": {"total_violations": 0, "total_warnings": 0},
  "violations": []
}
```

---

## 4. 执行 Runbook

### 4.1 全量执行顺序（固定）
1. `contract-common-builder`
2. `contract-module-builder`（10 -> 70）
3. `contract-consistency-auditor`
4. `governance-boundary-auditor`

### 4.2 增量更新
修改某模块后：
1. 仅重跑该模块 `contract-module-builder`
2. 重新跑 `contract-consistency-auditor`
3. 如涉及 Skill 代码变更，再跑 `governance-boundary-auditor`

---

## 5. 验收标准（量化）

1. 覆盖率
- `contracts` 下目标文件覆盖率 = 100%

2. 一致性
- `naming_conflicts = 0`
- `broken_references = 0`
- `missing_sections = 0`
- `version_mismatches = 0`

3. 边界合规
- `total_violations = 0`

---

## 6. 交付文件（拆分，不混写）

必须拆成 3 个独立文档：
1. `docs/2026-02-16/skill_design_00_70.md`
2. `docs/2026-02-16/skill_runbook_00_70.md`
3. `docs/2026-02-16/skill_acceptance_00_70.md`

本文件仅作为总规范，不替代上述三份文档。

---

## 7. 旧版文档问题说明（保留审计痕迹）

旧版 `完整办模块实现的skill.md` 的已知问题：
1. 渲染污染字符串（`markdownDownloadCopy code` 等）
2. 命名未对齐（使用了 `error_codes.md/shared_types.md/versioning.md`）
3. 交付物混写在单文件，结构不可机审

该文件不再作为执行输入。
