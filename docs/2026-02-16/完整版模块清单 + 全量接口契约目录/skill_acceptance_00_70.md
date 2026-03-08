# skill_acceptance_00_70

- 验收范围: `00_common` 到 `70_read_models`
- 验收模式: 量化指标 + 审计报告

## 1. 覆盖率

### A1 模块目录覆盖
- 标准: 8/8 模块目录存在
- 通过条件: `00_common,10_input,20_outer_spiral,30_composer,40_skill_artifact,50_governance,60_runtime,70_read_models` 全部存在

### A2 文档覆盖
- 标准: 目标契约文件覆盖率 100%
- 通过条件: 清单内文件全部存在，无遗漏

## 2. 一致性

### B1 命名冲突
- 指标: `naming_conflicts`
- 通过条件: `0`

### B2 引用断裂
- 指标: `broken_references`
- 通过条件: `0`

### B3 必要段落缺失
- 指标: `missing_sections`
- 通过条件: `0`

### B4 版本不一致
- 指标: `version_mismatches`
- 通过条件: `0`

## 3. 边界合规

### C1 治理越权
- 指标: `total_violations`
- 通过条件: `0`

### C2 告警控制
- 指标: `total_warnings`
- 通过条件: `<= 允许阈值（默认0）`

## 4. Fail-Closed 行为

### D1 输入缺失
- 测试: 必填字段为空
- 通过条件: 返回 `rejected`，包含 `missing_fields`

### D2 路径非法
- 测试: 不存在路径或越界路径
- 通过条件: 返回 `rejected`

### D3 schema 违规
- 测试: module_id 非法或输入对象结构错误
- 通过条件: 返回 `rejected|failed`，不得继续执行

## 5. 验收结论模板

- 覆盖率: `PASS|FAIL`
- 一致性: `PASS|FAIL`
- 边界合规: `PASS|FAIL`
- Fail-Closed: `PASS|FAIL`
- 最终结论: `ACCEPTED|REJECTED`
- 阻断项:
- 备注:
