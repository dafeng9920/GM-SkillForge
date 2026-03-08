```yaml
# 元信息
task_id: "T3"
executor: "vs--cc1"
wave: "Wave 2"
depends_on: ["T1", "T2"]
estimated_minutes: 180

# 输入合同 (Input Contract)
input:
  description: "M3 Registry Store 双轨迁移（引入 SQLite 后端）并支持双写/暗读一致性校验"
  context_files:
    - path: "skillforge/src/storage/registry_store.py"
      purpose: "重构其内部实现，支持 SQLite 表，且能在 jsonl/sqlite 之间通过 Flag 切换/双写"
  constants:
    env_keys: ["REGISTRY_BACKEND", "REGISTRY_DUAL_WRITE", "REGISTRY_SHADOW_READ_COMPARE"]

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge/src/storage/registry_store.py"
      type: "修改"
    - path: "skillforge/tests/test_registry_store.py"
      type: "修改"
    - path: "scripts/migrate_registry_jsonl_to_sqlite.py"
      type: "新建"
    - path: "scripts/verify_registry_consistency.py"
      type: "新建"
  constraints:
    - "数据库结构设计为: registry (skill_id TEXT, revision TEXT, tombstone_state TEXT, created_at TEXT, payload TEXT)"
    - "不得破坏 Append-Only 语义，禁止写 UPDATE / DELETE 语句"
    - "get_latest_active() 必须被优化为 ORDER BY LIMIT 1 的直接高效率查询"
    - "当 SHADOW_READ_COMPARE 开启时，读取时要对比 jsonl 和 sqlite 返回的结果，不一致打 ERROR log"
    - "【零例外治理】: 变更必可回滚。没有 Feature Flag 兜底或者回滚开关（REGISTRY_BACKEND），不允许通过。"
    - "【零例外治理】: 先证据后结论。必须出具双写一致性的运行日志作为证据。"

# 红线 (Deny List)
deny:
  - "不允许引入 SQLAlchemy 之类的 ORM，原生 sqlite3 库即可，保持极简"
  - "不允许在此次重命名外部已暴露 API 的类与方法入参"
  - "禁止隐性后门：发现 fallback、特判污染生产路径，直接打回。"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "pytest skillforge/tests/test_registry_store.py -v"
      expect: "passed"
    - command: "python scripts/verify_registry_consistency.py"
      expect: "Output 'Consistency 100%'"
```
