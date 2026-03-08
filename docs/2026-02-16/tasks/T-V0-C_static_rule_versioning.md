# T-V0-C: 静态规则版本化 — issue_catalog 版本管理 + validate 扩展

## 背景
`orchestration/issue_catalog.yml` 定义了 20 个 SEO issue key，但没有版本号和生效时间。
v0 需要：
- 每个 issue key 有版本号（规则变更可追溯）
- catalog 整体有 `catalog_version` 和 `effective_from`
- `evidence.jsonl` 中的 issue_key 必须引用有效版本
- validate.py 检查 catalog 版本一致性

## 任务清单

### C1: issue_catalog.yml — 增加版本化字段
**文件**: `orchestration/issue_catalog.yml`

当前格式：
```yaml
issues:
  missing_title_tag:
    severity: high
    category: meta_tags
    description: "..."
    impact: "..."
```

升级为：
```yaml
schema_version: 1
catalog_version: "1.0.0"
effective_from: "2026-02-16T00:00:00Z"

issues:
  missing_title_tag:
    severity: high
    category: meta_tags
    description: "..."
    impact: "..."
    added_in: "1.0.0"          # 首次加入的 catalog 版本
    deprecated_in: ~            # 如果被废弃，填版本号
    rule_source: "semgrep"      # 规则来源
```

### C2: pack_publish.py — 记录 catalog 版本
**文件**: `skillforge/src/nodes/pack_publish.py`

在 `manifest.json` 的 provenance 中增加：
```python
"issue_catalog_version": catalog_version,  # 从 issue_catalog.yml 读取
```

在 `policy_matrix.json` 的每个 finding 中增加：
```python
"rule_version": issue["added_in"],  # 标记该 finding 使用的规则版本
```

### C3: validate.py — 扩展校验
**文件**: `tools/validate.py`

在 `validate_audit_config()` 中增加 3 个检查点：
- CHECK 11: `issue_catalog.yml` 有 `schema_version == 1` 和 `catalog_version`
- CHECK 12: 所有 issue 有 `added_in` 字段
- CHECK 13: `effective_from` 是有效 ISO-8601 时间戳

### C4: test_tech_seo_audit_contract.py — 扩展
**文件**: `contract_tests/test_tech_seo_audit_contract.py`

增加测试：
```python
class TestIssueCatalogVersioning:
    def test_catalog_has_version(self): ...
    def test_all_issues_have_added_in(self): ...
    def test_no_orphan_deprecated_issues(self): ...
    def test_effective_from_valid_iso(self): ...
```

### C5: 存储层集成 — catalog 版本存入 revision
**文件**: `skillforge/src/storage/repository.py`

`append_revision()` 增加可选参数 `catalog_version`，写入 revisions 表的 metadata JSON 字段。
这个让 `get_snapshot(at_time)` 能回溯到"这次审计用的是哪个版本的规则"。

## 验收条件
- `issue_catalog.yml` 有 `schema_version`, `catalog_version`, `effective_from`
- 所有 issue 有 `added_in` 字段
- `python -m pytest contract_tests/test_tech_seo_audit_contract.py -v` 全过
- `python tools/validate.py --audit-config` 不回归

## 关键文件清单
```
orchestration/issue_catalog.yml                    ← 修改
skillforge/src/nodes/pack_publish.py               ← 修改
skillforge/src/storage/repository.py               ← 修改（可选）
tools/validate.py                                  ← 修改
contract_tests/test_tech_seo_audit_contract.py     ← 修改
orchestration/protocol_v0_scope.yml                ← 只读参考
```
