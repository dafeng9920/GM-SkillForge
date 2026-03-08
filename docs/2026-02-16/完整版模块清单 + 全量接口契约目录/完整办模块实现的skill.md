交付物 A: skill_design_00_70.md
markdownDownloadCopy code# Skill Design: 00-70 契约文档体系

文件: docs/2026-02-16/skill_design_00_70.md
生成时间: 2026-02-16T00:00:00Z
作者: 架构工程师(自动生成)

---

## 1. 总体架构

用户输入(源文件路径/模块ID)
│
▼
┌─────────────────────┐
│ contract-common-     │──► contracts/00_common/.md
│ builder              │
└─────────────────────┘
│ 00_common 产物作为后续输入
▼
┌─────────────────────┐
│ contract-module-     │──► contracts/{10..70}_/*.md
│ builder              │
└─────────────────────┘
│ 所有产物就绪后
▼
┌─────────────────────┐
│ contract-consistency-│──► audit_report_consistency.json
│ auditor              │
└─────────────────────┘
│
▼
┌─────────────────────┐
│ governance-boundary- │──► audit_report_boundary.json
│ auditor              │
└─────────────────────┘
数据流方向: 单向，无回路。
每个 Skill 独立运行，无 Skill 间自动触发。

## 2. 目标目录与文件对照表

| 目录前缀 | 模块名 | 职责 | 文件数(最少) |
|----------|--------|------|-------------|
| 00_common | 公共类型 | 错误码、版本号、共用数据类型 | 3 |
| 10_input | 输入层 | intake_repo, intake_nl 输入契约 | 2 |
| 20_outer_spiral | 外螺旋 | intent_parse, source_strategy, github_discover | 3 |
| 30_composer | 编排层 | skill_compose, draft_skill_spec | 2 |
| 40_skill_artifact | 技能产物 | scaffold_impl 产物契约 | 2 |
| 50_governance | 治理层 | license_gate, constitution_risk_gate 契约 | 2 |
| 60_runtime | 运行时 | sandbox_test_and_trace 契约 | 2 |
| 70_read_models | 读模型 | pack_audit_and_publish, registry 契约 | 2 |

最低产出: 18 个 .md 文件。

---

## 3. Skill 1: contract-common-builder

### 3.1 SKILL.md

```yaml
skill_id: contract-common-builder
version: "1.0.0"
description: >
  从项目源码中提取公共类型定义(错误码、schema_version、共用dataclass),
  生成 contracts/00_common/ 下的契约文档。
risk_tier: L0
capabilities:
  network: false
  subprocess: false
  filesystem: read(skillforge/src/**) + write(contracts/00_common/**)

3.2 输入 Schema
jsonDownloadCopy code{
  "\$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ContractCommonBuilderInput",
  "type": "object",
  "required": ["project_root", "source_paths", "output_dir"],
  "additionalProperties": false,
  "properties": {
    "project_root": {
      "type": "string",
      "description": "项目根目录绝对路径"
    },
    "source_paths": {
      "type": "array",
      "minItems": 1,
      "items": { "type": "string" },
      "description": "要扫描的源文件相对路径列表(相对于project_root)"
    },
    "output_dir": {
      "type": "string",
      "description": "输出目录(contracts/00_common)"
    },
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "default": "0.1.0"
    }
  }
}
3.3 输出 Schema
jsonDownloadCopy code{
  "\$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ContractCommonBuilderOutput",
  "type": "object",
  "required": ["status", "generated_files", "provenance", "timestamp"],
  "additionalProperties": false,
  "properties": {
    "status": {
      "type": "string",
      "enum": ["completed", "failed", "rejected"]
    },
    "generated_files": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["path", "source_files", "checksum"],
        "properties": {
          "path": { "type": "string" },
          "source_files": {
            "type": "array",
            "items": { "type": "string" }
          },
          "checksum": { "type": "string" }
        }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["skill_id", "skill_version", "run_id"],
      "properties": {
        "skill_id": { "type": "string" },
        "skill_version": { "type": "string" },
        "run_id": { "type": "string" }
      }
    },
    "timestamp": { "type": "string", "format": "date-time" },
    "rejection_reason": { "type": "string" },
    "missing_fields": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
3.4 执行步骤
步骤1: 输入校验
  - 检查 project_root 是否为合法目录
  - 检查 source_paths 中每个文件是否存在
  - 任何缺失 → status=rejected, 列出 missing_fields

步骤2: 源码扫描
  - 遍历 source_paths, 用 AST 解析提取:
    a. 所有 error_codes.yml 中的错误码定义
    b. 所有 types.py 中的 @dataclass 定义
    c. 所有出现的 schema_version 常量
  - 提取结果存入中间结构 CommonExtract

步骤3: 文档生成
  生成 3 个文件:
  a. 00_common/error_codes.md
     - 表格: 错误码 | 前缀 | 描述 | 定义来源文件:行号
  b. 00_common/shared_types.md
     - 每个 dataclass: 类名 | 字段列表 | 来源文件:行号
  c. 00_common/versioning.md
     - schema_version 值 | 出现位置 | 是否一致

步骤4: 校验和与溯源
  - 为每个生成文件计算 SHA-256
  - 写入 provenance 元数据
  - 返回输出 dict

3.5 Fail-Closed 拒绝条件
条件行为输出project_root 不存在拒绝status=rejected, missing_fields=["project_root"]source_paths 中任何文件不存在拒绝status=rejected, 列出不存在的文件source_paths 为空数组拒绝status=rejected, missing_fields=["source_paths"]output_dir 不在允许的写入路径下拒绝status=rejected, 说明路径越界AST 解析失败(语法错误)失败status=failed, 列出解析失败文件

4. Skill 2: contract-module-builder
4.1 SKILL.md
yamlDownloadCopy codeskill_id: contract-module-builder
version: "1.0.0"
description: >
  为指定模块(10-70)生成接口契约文档。
  从节点源码提取 Input/Output Contract, validate_input/validate_output 规则,
  生成对应 contracts/{prefix}_{module}/ 下的文档。
risk_tier: L0
capabilities:
  network: false
  subprocess: false
  filesystem: read(skillforge/src/**) + read(contracts/00_common/**) + write(contracts/{10..70}_*/**)
4.2 输入 Schema
jsonDownloadCopy code{
  "\$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ContractModuleBuilderInput",
  "type": "object",
  "required": ["project_root", "module_id", "node_source_paths", "common_contracts_dir", "output_dir"],
  "additionalProperties": false,
  "properties": {
    "project_root": {
      "type": "string"
    },
    "module_id": {
      "type": "string",
      "pattern": "^(10_input|20_outer_spiral|30_composer|40_skill_artifact|50_governance|60_runtime|70_read_models)$",
      "description": "目标模块标识"
    },
    "node_source_paths": {
      "type": "array",
      "minItems": 1,
      "items": { "type": "string" },
      "description": "该模块包含的节点源文件路径"
    },
    "common_contracts_dir": {
      "type": "string",
      "description": "00_common 目录路径, 用于交叉引用"
    },
    "output_dir": {
      "type": "string",
      "description": "输出目录(如 contracts/30_composer)"
    },
    "schema_version": {
      "type": "string",
      "default": "0.1.0"
    }
  }
}
4.3 输出 Schema
jsonDownloadCopy code{
  "\$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ContractModuleBuilderOutput",
  "type": "object",
  "required": ["status", "module_id", "generated_files", "cross_references", "provenance", "timestamp"],
  "additionalProperties": false,
  "properties": {
    "status": {
      "type": "string",
      "enum": ["completed", "failed", "rejected"]
    },
    "module_id": { "type": "string" },
    "generated_files": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["path", "node_id", "source_file", "checksum", "sections"],
        "properties": {
          "path": { "type": "string" },
          "node_id": { "type": "string" },
          "source_file": { "type": "string" },
          "checksum": { "type": "string" },
          "sections": {
            "type": "array",
            "items": { "type": "string" },
            "description": "包含的段落标识列表"
          }
        }
      }
    },
    "cross_references": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from_type", "to_type", "location"],
        "properties": {
          "from_type": { "type": "string" },
          "to_type": { "type": "string" },
          "location": { "type": "string" }
        }
      },
      "description": "对 00_common 中类型的引用列表"
    },
    "provenance": {
      "type": "object",
      "required": ["skill_id", "skill_version", "run_id"],
      "properties": {
        "skill_id": { "type": "string" },
        "skill_version": { "type": "string" },
        "run_id": { "type": "string" }
      }
    },
    "timestamp": { "type": "string", "format": "date-time" },
    "rejection_reason": { "type": "string" },
    "missing_fields": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
4.4 执行步骤
步骤1: 输入校验
  - 检查 project_root, common_contracts_dir 目录存在
  - 检查 module_id 在允许的枚举值中
  - 检查 node_source_paths 中每个文件存在
  - 检查 common_contracts_dir 下至少有 error_codes.md, shared_types.md
  - 任何缺失 → rejected

步骤2: 源码解析(每个 node 源文件)
  从 module docstring 中提取:
    a. Input Contract 段: 字段名, 类型, required/optional
    b. Output Contract 段: 字段名, 类型
  从 class body 中提取:
    c. validate_input() 中检查的字段列表和错误条件
    d. validate_output() 中检查的字段列表
    e. execute() 中引用的 artifacts key (前序依赖)
  从 @dataclass 定义中提取:
    f. node_id, stage

步骤3: 交叉引用解析
  - 将 Input/Output 中的类型与 00_common/shared_types.md 比对
  - 记录每个引用: { from_type, to_type, location }
  - 将 error_codes 与 00_common/error_codes.md 比对

步骤4: 文档生成(每个 node 生成 1 个 .md)
  文件名: {node_id}.md
  必须包含的段落(缺一不可):
    ## 节点标识
    - node_id, stage, 所属路径(A/B/AB)

    ## 输入契约
    - 表格: 字段 | 类型 | 必需 | 来源节点 | 说明
    - 来源: module docstring Input Contract + validate_input 逻辑

    ## 输出契约
    - 表格: 字段 | 类型 | 说明
    - 来源: module docstring Output Contract + validate_output 逻辑

    ## 前序依赖
    - 列出 execute() 中读取的 artifacts key
    - 每个 key 标注来源节点

    ## 验证规则
    - validate_input 中所有检查条件
    - validate_output 中所有检查条件
    - 每条规则标注触发时的错误码

    ## 溯源
    - 源文件路径
    - 生成时间
    - 生成 Skill 版本

步骤5: 校验和与输出
  - SHA-256 每个文件
  - 汇总 cross_references
  - 返回输出 dict

4.5 Fail-Closed 拒绝条件
条件行为module_id 不在枚举值内rejectednode_source_paths 中任何文件不存在rejected, 列出缺失文件common_contracts_dir 缺少 error_codes.md 或 shared_types.mdrejected, 要求先运行 contract-common-builder源文件无 module docstring 中的 Input/Output Contract 段failed, 报告该文件缺少契约定义源文件 validate_input 仍为 NotImplementedErrorfailed, 报告该节点未实现

5. Skill 3: contract-consistency-auditor
5.1 SKILL.md
yamlDownloadCopy codeskill_id: contract-consistency-auditor
version: "1.0.0"
description: >
  扫描 contracts/00_common 至 contracts/70_read_models 的全部 .md 文件,
  检测字段命名冲突、引用断裂、版本不一致、缺失必需段落。
  输出审计报告, 不执行任何修复。
risk_tier: L0
capabilities:
  network: false
  subprocess: false
  filesystem: read(contracts/**)
5.2 输入 Schema
jsonDownloadCopy code{
  "\$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ContractConsistencyAuditorInput",
  "type": "object",
  "required": ["contracts_root"],
  "additionalProperties": false,
  "properties": {
    "contracts_root": {
      "type": "string",
      "description": "contracts/ 目录的绝对路径"
    },
    "expected_modules": {
      "type": "array",
      "items": { "type": "string" },
      "default": [
        "00_common", "10_input", "20_outer_spiral", "30_composer",
        "40_skill_artifact", "50_governance", "60_runtime", "70_read_models"
      ]
    },
    "required_sections": {
      "type": "array",
      "items": { "type": "string" },
      "default": [
        "节点标识", "输入契约", "输出契约", "前序依赖", "验证规则", "溯源"
      ],
      "description": "每个非 00_common 的 .md 必须包含的段落"
    }
  }
}
5.3 输出 Schema
jsonDownloadCopy code{
  "\$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ContractConsistencyAuditorOutput",
  "type": "object",
  "required": ["status", "summary", "findings", "files_scanned", "provenance", "timestamp"],
  "additionalProperties": false,
  "properties": {
    "status": {
      "type": "string",
      "enum": ["pass", "fail"]
    },
    "summary": {
      "type": "object",
      "required": [
        "total_files", "naming_conflicts", "broken_references",
        "missing_sections", "version_mismatches"
      ],
      "properties": {
        "total_files": { "type": "integer" },
        "naming_conflicts": { "type": "integer" },
        "broken_references": { "type": "integer" },
        "missing_sections": { "type": "integer" },
        "version_mismatches": { "type": "integer" }
      }
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["finding_id", "category", "severity", "file", "detail"],
        "properties": {
          "finding_id": { "type": "string" },
          "category": {
            "type": "string",
            "enum": [
              "naming_conflict", "broken_reference",
              "missing_section", "version_mismatch",
              "duplicate_field", "type_mismatch"
            ]
          },
          "severity": {
            "type": "string",
            "enum": ["error", "warning"]
          },
          "file": { "type": "string" },
          "detail": { "type": "string" },
          "related_file": { "type": "string" }
        }
      }
    },
    "files_scanned": {
      "type": "array",
      "items": { "type": "string" }
    },
    "provenance": {
      "type": "object",
      "required": ["skill_id", "skill_version", "run_id"],
      "properties": {
        "skill_id": { "type": "string" },
        "skill_version": { "type": "string" },
        "run_id": { "type": "string" }
      }
    },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
5.4 执行步骤
步骤1: 输入校验
  - 检查 contracts_root 存在
  - 检查 expected_modules 中每个子目录存在
  - 缺失子目录 → finding(category=broken_reference, severity=error)

步骤2: 文件发现
  - 递归扫描 contracts_root 下所有 .md 文件
  - 将文件归类到所属模块
  - 记录 files_scanned 列表

步骤3: 段落完整性检查
  对 10-70 的每个 .md 文件:
    - 提取所有 ## 标题
    - 对照 required_sections 列表
    - 缺失段落 → finding(category=missing_section, severity=error)

步骤4: 字段命名一致性检查
  - 从所有"输入契约"和"输出契约"表格中提取字段名
  - 构建全局字段注册表: { field_name → [(file, type, role)] }
  - 同名字段在不同文件中类型不同 → finding(category=naming_conflict)
  - 节点 A 的输出字段名与节点 B 的输入字段名不匹配(声明了依赖但字段名不符)
    → finding(category=type_mismatch)

步骤5: 引用完整性检查
  - 从"前序依赖"段提取引用的 node_id
  - 检查被引用的 node_id 是否存在对应的 .md 文件
  - 不存在 → finding(category=broken_reference, severity=error)

步骤6: 版本一致性检查
  - 从 00_common/versioning.md 获取 schema_version 基准值
  - 从所有 .md 的"溯源"段提取 schema_version
  - 不一致 → finding(category=version_mismatch, severity=warning)

步骤7: 汇总
  - 统计各类 finding 数量
  - naming_conflicts + broken_references + missing_sections > 0 → status=fail
  - 否则 status=pass

5.5 Fail-Closed 拒绝条件
条件行为contracts_root 不存在rejected, 不产出报告contracts_root 下无任何 .md 文件status=fail, finding: "No contract files found".md 文件无法被解析(编码错误等)该文件标记为 finding(error), 继续扫描其余文件
审计器绝不修改任何文件。只读扫描，只写报告。

6. Skill 4: governance-boundary-auditor
6.1 SKILL.md
yamlDownloadCopy codeskill_id: governance-boundary-auditor
version: "1.0.0"
description: >
  检查 Skill 源码是否越权执行了治理行为(Gate执行、Evidence写入、Replay触发)。
  扫描 skillforge/src/nodes/*.py 和 skillforge/src/adapters/**/*.py,
  检测违规模式。输出合规报告。不执行修复。
risk_tier: L0
capabilities:
  network: false
  subprocess: false
  filesystem: read(skillforge/src/**)
6.2 输入 Schema
jsonDownloadCopy code{
  "\$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GovernanceBoundaryAuditorInput",
  "type": "object",
  "required": ["project_root", "scan_paths"],
  "additionalProperties": false,
  "properties": {
    "project_root": {
      "type": "string"
    },
    "scan_paths": {
      "type": "array",
      "minItems": 1,
      "items": { "type": "string" },
      "description": "要扫描的源文件或目录相对路径"
    },
    "forbidden_patterns": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["pattern_id", "regex", "description", "severity"],
        "properties": {
          "pattern_id": { "type": "string" },
          "regex": { "type": "string" },
          "description": { "type": "string" },
          "severity": { "type": "string", "enum": ["violation", "warning"] }
        }
      },
      "default": [
        {
          "pattern_id": "GOV-001",
          "regex": "gate_evaluator\\.enforce|gate\\.execute|gate\\.deny_and_halt",
          "description": "Skill 不得调用 gate 执行方法",
          "severity": "violation"
        },
        {
          "pattern_id": "GOV-002",
          "regex": "evidence_store\\.write|evidence\\.commit|evidence\\.append_record",
          "description": "Skill 不得直接写入 evidence store",
          "severity": "violation"
        },
        {
          "pattern_id": "GOV-003",
          "regex": "replay_engine\\.|replay\\.trigger|replay\\.execute",
          "description": "Skill 不得触发 replay 执行",
          "severity": "violation"
        },
        {
          "pattern_id": "GOV-004",
          "regex": "subprocess\\.(?:run|call|Popen|check_output)",
          "description": "Skill 不得调用子进程",
          "severity": "violation"
        },
        {
          "pattern_id": "GOV-005",
          "regex": "os\\.system|os\\.exec",
          "description": "Skill 不得通过 os 执行系统命令",
          "severity": "violation"
        },
        {
          "pattern_id": "GOV-006",
          "regex": "auto_?fix|auto_?repair|auto_?retry|auto_?correct",
          "description": "Skill 不得包含自动修复逻辑",
          "severity": "warning"
        }
      ]
    }
  }
}
6.3 输出 Schema
jsonDownloadCopy code{
  "\$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GovernanceBoundaryAuditorOutput",
  "type": "object",
  "required": ["status", "summary", "violations", "files_scanned", "provenance", "timestamp"],
  "additionalProperties": false,
  "properties": {
    "status": {
      "type": "string",
      "enum": ["compliant", "non_compliant"]
    },
    "summary": {
      "type": "object",
      "required": ["total_files", "total_violations", "total_warnings"],
      "properties": {
        "total_files": { "type": "integer" },
        "total_violations": { "type": "integer" },
        "total_warnings": { "type": "integer" }
      }
    },
    "violations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["pattern_id", "severity", "file", "line", "matched_text"],
        "properties": {
          "pattern_id": { "type": "string" },
          "severity": { "type": "string" },
          "file": { "type": "string" },
          "line": { "type": "integer" },
          "matched_text": { "type": "string" },
          "context": { "type": "string" }
        }
      }
    },
    "files_scanned": {
      "type": "array",
      "items": { "type": "string" }
    },
    "provenance": {
      "type": "object",
      "required": ["skill_id", "skill_version", "run_id"],
      "properties": {
        "skill_id": { "type": "string" },
        "skill_version": { "type": "string" },
        "run_id": { "type": "string" }
      }
    },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
6.4 执行步骤
步骤1: 输入校验
  - 检查 project_root 存在
  - 检查 scan_paths 中每个路径存在
  - 编译 forbidden_patterns 中每个 regex, 无效正则 → rejected

步骤2: 文件收集
  - 遍历 scan_paths
  - 目录则递归收集 *.py 文件
  - 文件则直接加入
  - 记录 files_scanned

步骤3: 模式扫描
  对每个 .py 文件的每一行:
    - 跳过注释行(以 # 开头)
    - 跳过 docstring 内部行
    - 对每个 forbidden_pattern 执行 regex 搜索
    - 匹配到 → 记录 violation:
      { pattern_id, severity, file, line, matched_text, context(前后各1行) }

步骤4: 汇总
  - total_violations = severity=="violation" 的数量
  - total_warnings = severity=="warning" 的数量
  - total_violations > 0 → status=non_compliant
  - 否则 → status=compliant

6.5 Fail-Closed 拒绝条件
条件行为project_root 不存在rejectedscan_paths 全部不存在rejectedforbidden_patterns 中有无效正则rejected, 列出无效正则.py 文件编码无法读取该文件记录 warning, 继续扫描
审计器绝不修改任何源文件。只读扫描，只写报告。

7. 模块→节点→源文件映射表
此表是 contract-module-builder 的输入参考:
module_idnode_id源文件10_inputintake_reposkillforge/src/nodes/intake_repo.py10_inputintake_nlskillforge/src/nodes/intent_parser.py20_outer_spiralintent_parseskillforge/src/nodes/intent_parser.py20_outer_spiralsource_strategyskillforge/src/nodes/source_strategy.py20_outer_spiralgithub_discoverskillforge/src/nodes/github_discover.py30_composerskill_composeskillforge/src/nodes/skill_composer.py30_composerdraft_skill_specskillforge/src/nodes/draft_spec.py40_skill_artifactscaffold_skill_implskillforge/src/nodes/scaffold_impl.py40_skill_artifact(artifact schema)skillforge/src/adapters/github_fetch/types.py50_governancelicense_gateskillforge/src/nodes/license_gate.py50_governanceconstitution_risk_gateskillforge/src/nodes/constitution_gate.py60_runtimesandbox_test_and_traceskillforge/src/nodes/sandbox_test.py60_runtime(sandbox adapter)skillforge/src/adapters/sandbox_runner/adapter.py70_read_modelspack_audit_and_publishskillforge/src/nodes/pack_publish.py70_read_models(registry adapter)skillforge/src/adapters/registry_client/adapter.py

---

# 交付物 B: skill_runbook_00_70.md

```markdown
# Skill Runbook: 00-70 契约文档体系

文件: docs/2026-02-16/skill_runbook_00_70.md
生成时间: 2026-02-16T00:00:00Z

---

## 1. 前提条件


Python >= 3.11
项目已克隆到 D:\GM-SkillForge
所有节点 .py 文件已实现(无 NotImplementedError)
当前工作目录: D:\GM-SkillForge

## 2. 单个 Skill 调用示例

### 2.1 contract-common-builder

```bash
python -m skillforge.skills.contract_common_builder \
  --input '{
    "project_root": "D:\\GM-SkillForge",
    "source_paths": [
      "skillforge/src/nodes/intake_repo.py",
      "skillforge/src/nodes/license_gate.py",
      "skillforge/src/nodes/intent_parser.py",
      "skillforge/src/nodes/source_strategy.py",
      "skillforge/src/nodes/github_discover.py",
      "skillforge/src/nodes/skill_composer.py",
      "skillforge/src/nodes/draft_spec.py",
      "skillforge/src/nodes/constitution_gate.py",
      "skillforge/src/nodes/scaffold_impl.py",
      "skillforge/src/nodes/sandbox_test.py",
      "skillforge/src/nodes/pack_publish.py",
      "skillforge/src/adapters/github_fetch/types.py",
      "skillforge/src/adapters/sandbox_runner/types.py"
    ],
    "output_dir": "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts/00_common",
    "schema_version": "0.1.0"
  }'

预期输出:
status: completed
generated_files:
  - 00_common/error_codes.md     (SHA-256: ...)
  - 00_common/shared_types.md    (SHA-256: ...)
  - 00_common/versioning.md      (SHA-256: ...)

2.2 contract-module-builder (以 50_governance 为例)
bashDownloadCopy codepython -m skillforge.skills.contract_module_builder \
  --input '{
    "project_root": "D:\\GM-SkillForge",
    "module_id": "50_governance",
    "node_source_paths": [
      "skillforge/src/nodes/license_gate.py",
      "skillforge/src/nodes/constitution_gate.py"
    ],
    "common_contracts_dir": "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts/00_common",
    "output_dir": "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts/50_governance",
    "schema_version": "0.1.0"
  }'
预期输出:
status: completed
module_id: 50_governance
generated_files:
  - 50_governance/license_gate.md         (sections: 6)
  - 50_governance/constitution_risk_gate.md (sections: 6)
cross_references:
  - from: GateDecision → to: 00_common/shared_types.md

2.3 contract-consistency-auditor
bashDownloadCopy codepython -m skillforge.skills.contract_consistency_auditor \
  --input '{
    "contracts_root": "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts"
  }'
预期输出:
status: pass | fail
summary:
  total_files: 18
  naming_conflicts: 0
  broken_references: 0
  missing_sections: 0
  version_mismatches: 0
findings: [...]

2.4 governance-boundary-auditor
bashDownloadCopy codepython -m skillforge.skills.governance_boundary_auditor \
  --input '{
    "project_root": "D:\\GM-SkillForge",
    "scan_paths": [
      "skillforge/src/nodes",
      "skillforge/src/adapters"
    ]
  }'
预期输出:
status: compliant
summary:
  total_files: 14
  total_violations: 0
  total_warnings: 0

3. 全量批量执行方案 (00→70 一次性)
bashDownloadCopy code#!/bin/bash
# run_all_contracts.sh
# 执行顺序固定，不可打乱

set -euo pipefail

PROJECT="D:\\GM-SkillForge"
CONTRACTS="docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts"

echo "=== Phase 1: Common ==="
python -m skillforge.skills.contract_common_builder \
  --input-file config/contract_common_input.json

echo "=== Phase 2: Modules (sequential, 00_common must exist) ==="
for module_config in config/modules/10_input.json \
                     config/modules/20_outer_spiral.json \
                     config/modules/30_composer.json \
                     config/modules/40_skill_artifact.json \
                     config/modules/50_governance.json \
                     config/modules/60_runtime.json \
                     config/modules/70_read_models.json; do
  echo "--- Building: \$module_config ---"
  python -m skillforge.skills.contract_module_builder \
    --input-file "\$module_config"
done

echo "=== Phase 3: Consistency Audit ==="
python -m skillforge.skills.contract_consistency_auditor \
  --input "{\"contracts_root\": \"$PROJECT/\$CONTRACTS\"}" \
  --output audit_report_consistency.json

echo "=== Phase 4: Boundary Audit ==="
python -m skillforge.skills.governance_boundary_auditor \
  --input "{\"project_root\": \"\$PROJECT\", \"scan_paths\": [\"skillforge/src/nodes\", \"skillforge/src/adapters\"]}" \
  --output audit_report_boundary.json

echo "=== Done ==="
echo "Verify: cat audit_report_consistency.json | python -m json.tool"
echo "Verify: cat audit_report_boundary.json | python -m json.tool"
执行顺序的依据:

* Phase 1 必须先于 Phase 2: module-builder 需要读取 00_common 的产物做交叉引用
* Phase 2 各模块之间无依赖，但串行执行避免文件系统竞争
* Phase 3/4 必须在所有文档生成后运行: 审计器需要完整数据集

4. 单文件增量更新方案
场景: 修改了 skillforge/src/nodes/license_gate.py, 需要更新对应契约。
bashDownloadCopy code# 步骤 1: 重新生成该节点所属模块的契约
python -m skillforge.skills.contract_module_builder \
  --input '{
    "project_root": "D:\\GM-SkillForge",
    "module_id": "50_governance",
    "node_source_paths": ["skillforge/src/nodes/license_gate.py"],
    "common_contracts_dir": "docs/.../contracts/00_common",
    "output_dir": "docs/.../contracts/50_governance",
    "schema_version": "0.1.0"
  }'
# 注: 只传入修改的文件路径; 该模块下的其他文件(constitution_gate.md)不会被覆盖

# 步骤 2: 重新跑一致性审计(全量)
python -m skillforge.skills.contract_consistency_auditor \
  --input '{"contracts_root": "docs/.../contracts"}'

# 步骤 3: 检查审计结果
python -c "
import json
with open('audit_report_consistency.json') as f:
    r = json.load(f)
print(f'Status: {r[\"status\"]}')
print(f'Conflicts: {r[\"summary\"][\"naming_conflicts\"]}')
print(f'Broken refs: {r[\"summary\"][\"broken_references\"]}')
"
增量更新时不重新运行 contract-common-builder 的条件:

* 修改的文件中未添加新的 @dataclass 共用类型
* 修改的文件中未添加新的错误码前缀
* 如果不确定 → 重新运行 Phase 1

5. 配置文件模板
每个模块的配置放在 config/modules/ 下:
config/
├── contract_common_input.json
└── modules/
    ├── 10_input.json
    ├── 20_outer_spiral.json
    ├── 30_composer.json
    ├── 40_skill_artifact.json
    ├── 50_governance.json
    ├── 60_runtime.json
    └── 70_read_models.json

示例 config/modules/50_governance.json:
jsonDownloadCopy code{
  "project_root": "D:\\GM-SkillForge",
  "module_id": "50_governance",
  "node_source_paths": [
    "skillforge/src/nodes/license_gate.py",
    "skillforge/src/nodes/constitution_gate.py"
  ],
  "common_contracts_dir": "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts/00_common",
  "output_dir": "docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts/50_governance",
  "schema_version": "0.1.0"
}

---

# 交付物 C: skill_acceptance_00_70.md

```markdown
# Skill Acceptance Criteria: 00-70 契约文档体系

文件: docs/2026-02-16/skill_acceptance_00_70.md
生成时间: 2026-02-16T00:00:00Z

---

## 1. 覆盖率验收

### 1.1 文件覆盖率

指标: contracts/ 下的 .md 文件能覆盖所有已实现节点。

```bash
# 验证命令
python -c "
import os, glob

contracts = 'docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts'
nodes = glob.glob('skillforge/src/nodes/*.py')
node_ids = []
for n in nodes:
    if n.endswith('__init__.py'):
        continue
    with open(n) as f:
        for line in f:
            if 'node_id' in line and '=' in line:
                nid = line.split('=')[1].strip().strip('\"').strip(\"'\")
                node_ids.append(nid)
                break

md_files = []
for root, dirs, files in os.walk(contracts):
    for f in files:
        if f.endswith('.md'):
            md_files.append(os.path.splitext(f)[0])

covered = set(node_ids) & set(md_files)
missing = set(node_ids) - set(md_files)

print(f'Node IDs found:     {len(node_ids)}')
print(f'Contract MDs found: {len(md_files)}')
print(f'Covered:            {len(covered)}')
print(f'Missing:            {missing if missing else \"none\"}')

coverage = len(covered) / len(node_ids) * 100 if node_ids else 0
print(f'Coverage:           {coverage:.1f}%')
assert coverage == 100.0, f'FAIL: coverage {coverage}% < 100%'
print('PASS: 100% node coverage')
"

合格标准: 覆盖率 = 100%。每个 node_id 必须有对应的 .md 文件。
1.2 模块目录覆盖率
bashDownloadCopy codepython -c "
import os

contracts = 'docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts'
expected = [
    '00_common', '10_input', '20_outer_spiral', '30_composer',
    '40_skill_artifact', '50_governance', '60_runtime', '70_read_models'
]
existing = [d for d in os.listdir(contracts) if os.path.isdir(os.path.join(contracts, d))]
missing = set(expected) - set(existing)
print(f'Expected: {len(expected)} directories')
print(f'Found:    {len(existing)} directories')
print(f'Missing:  {missing if missing else \"none\"}')
assert not missing, f'FAIL: missing directories: {missing}'
print('PASS: all 8 module directories exist')
"
合格标准: 8/8 目录存在。
1.3 段落完整性
bashDownloadCopy codepython -c "
import os, re

contracts = 'docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts'
required = ['节点标识', '输入契约', '输出契约', '前序依赖', '验证规则', '溯源']
failures = []

for root, dirs, files in os.walk(contracts):
    if '00_common' in root:
        continue
    for f in files:
        if not f.endswith('.md'):
            continue
        path = os.path.join(root, f)
        with open(path, encoding='utf-8') as fh:
            content = fh.read()
        headings = re.findall(r'^## (.+)$', content, re.MULTILINE)
        for req in required:
            if req not in headings:
                failures.append(f'{path}: missing section \"{req}\"')

print(f'Section check failures: {len(failures)}')
for fail in failures:
    print(f'  - {fail}')
assert len(failures) == 0, f'FAIL: {len(failures)} missing sections'
print('PASS: all required sections present')
"
合格标准: 缺失段落数 = 0。

2. 一致性验收
2.1 字段命名冲突
验证方法: 运行 contract-consistency-auditor, 检查输出。
bashDownloadCopy codepython -c "
import json
with open('audit_report_consistency.json') as f:
    r = json.load(f)
nc = r['summary']['naming_conflicts']
print(f'Naming conflicts: {nc}')
assert nc == 0, f'FAIL: {nc} naming conflicts found'
print('PASS')
"
合格标准: naming_conflicts = 0。
2.2 引用断裂
bashDownloadCopy codepython -c "
import json
with open('audit_report_consistency.json') as f:
    r = json.load(f)
br = r['summary']['broken_references']
print(f'Broken references: {br}')
assert br == 0, f'FAIL: {br} broken references found'
print('PASS')
"
合格标准: broken_references = 0。
2.3 版本一致性
bashDownloadCopy codepython -c "
import json
with open('audit_report_consistency.json') as f:
    r = json.load(f)
vm = r['summary']['version_mismatches']
print(f'Version mismatches: {vm}')
assert vm == 0, f'FAIL: {vm} version mismatches'
print('PASS')
"
合格标准: version_mismatches = 0。

3. 边界合规验收
3.1 治理越权检查
bashDownloadCopy codepython -c "
import json
with open('audit_report_boundary.json') as f:
    r = json.load(f)
tv = r['summary']['total_violations']
print(f'Governance violations: {tv}')
assert tv == 0, f'FAIL: {tv} governance boundary violations'
print('PASS: Skills do not execute governance actions')

# 详细打印每个扫描文件
for f in r['files_scanned']:
    print(f'  scanned: {f}')
"
合格标准: total_violations = 0。
3.2 禁止模式明细
逐条验证 GOV-001 到 GOV-006 的匹配数:
bashDownloadCopy codepython -c "
import json
from collections import Counter

with open('audit_report_boundary.json') as f:
    r = json.load(f)

by_pattern = Counter(v['pattern_id'] for v in r['violations'])
patterns = ['GOV-001','GOV-002','GOV-003','GOV-004','GOV-005','GOV-006']
for p in patterns:
    count = by_pattern.get(p, 0)
    status = 'PASS' if count == 0 else 'FAIL'
    print(f'{p}: {count} matches [{status}]')
"
合格标准: 每个 GOV-* 模式匹配数 = 0。

4. Skill 自身合规验收
4.1 Fail-Closed 行为验证
bashDownloadCopy code# 测试1: 空输入 → 必须 rejected
python -c "
from skillforge.skills.contract_common_builder import run
result = run({})
assert result['status'] == 'rejected', f'Expected rejected, got {result[\"status\"]}'
assert len(result.get('missing_fields', [])) > 0
print('PASS: empty input → rejected with missing_fields')
"

# 测试2: 不存在的路径 → 必须 rejected
python -c "
from skillforge.skills.contract_module_builder import run
result = run({
    'project_root': '/nonexistent',
    'module_id': '50_governance',
    'node_source_paths': ['nonexistent.py'],
    'common_contracts_dir': '/nonexistent',
    'output_dir': '/tmp/out'
})
assert result['status'] == 'rejected'
print('PASS: nonexistent path → rejected')
"

# 测试3: 无效 module_id → 必须 rejected
python -c "
from skillforge.skills.contract_module_builder import run
result = run({
    'project_root': 'D:\\\\GM-SkillForge',
    'module_id': '99_invalid',
    'node_source_paths': ['skillforge/src/nodes/intake_repo.py'],
    'common_contracts_dir': 'docs/.../contracts/00_common',
    'output_dir': '/tmp/out'
})
assert result['status'] == 'rejected'
print('PASS: invalid module_id → rejected')
"
4.2 溯源完整性
bashDownloadCopy codepython -c "
import os, re

contracts = 'docs/2026-02-16/完整版模块清单 + 全量接口契约目录/contracts'
missing_provenance = []

for root, dirs, files in os.walk(contracts):
    if '00_common' in root:
        continue
    for f in files:
        if not f.endswith('.md'):
            continue
        path = os.path.join(root, f)
        with open(path, encoding='utf-8') as fh:
            content = fh.read()
        # 检查溯源段是否包含三个必需字段
        prov_match = re.search(r'## 溯源(.+?)(?=\n## |\Z)', content, re.DOTALL)
        if not prov_match:
            missing_provenance.append(f'{path}: no 溯源 section')
            continue
        prov = prov_match.group(1)
        for field in ['源文件', '生成时间', 'Skill 版本']:
            if field not in prov:
                missing_provenance.append(f'{path}: 溯源 missing \"{field}\"')

print(f'Provenance issues: {len(missing_provenance)}')
for m in missing_provenance:
    print(f'  - {m}')
assert len(missing_provenance) == 0
print('PASS: all provenance fields present')
"
合格标准: 每个非 00_common 的 .md 的溯源段必须包含"源文件""生成时间""Skill 版本"三个字段。

5. 验收汇总检查表
#验收项合格标准验证命令A1节点覆盖率100%1.1 脚本A2目录覆盖率8/81.2 脚本A3段落完整性缺失数=01.3 脚本B1命名冲突02.1 脚本B2引用断裂02.2 脚本B3版本一致02.3 脚本C1治理越权violations=03.1 脚本C2模式明细每个GOV-*=03.2 脚本D1Fail-Closed全部rejected4.1 脚本D2溯源完整缺失数=04.2 脚本
全部 10 项 PASS → 验收通过。
任一项 FAIL → 验收未通过，需修复后重新运行。

6. 已知边界与排除项
本验收范围不包含以下内容(依据硬性约束):
排除项依据Gate 执行逻辑的正确性测试约束 2: Gate 执行不得 Skill 化Evidence 写入的完整性测试约束 2: Evidence 写入不得 Skill 化Replay 回放的功能测试约束 2: Replay 触发不得 Skill 化自动修复被发现的一致性问题约束 4: 不允许自动修复跨 Skill 自动触发链路约束 4: 不允许外部编排审计器修改源文件或契约文件约束 3+5: 只读审计，Fail-Closed
这些排除项通过 governance-boundary-auditor (GOV-001 至 GOV-003) 验证其不存在。