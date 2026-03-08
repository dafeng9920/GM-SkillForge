```yaml
# 元信息
task_id: "T1"
executor: "vs--cc1"
wave: "Wave 1"
depends_on: []
estimated_minutes: 30

# 输入合同 (Input Contract)
input:
  description: "完成 M0 基线护栏环境注入，与 M2 清除生产环境 AuditPack 样例污染"
  context_files:
    - path: "skillforge/src/storage/audit_pack_store.py"
      purpose: "移除 init 过程中的污染"
  constants:
    env_keys: ["SKILLFORGE_ENV", "REGISTRY_BACKEND", "REGISTRY_DUAL_WRITE", "REGISTRY_SHADOW_READ_COMPARE"]

# 输出合同 (Output Contract)
output:
  deliverables:
    - path: "skillforge/src/storage/audit_pack_store.py"
      type: "修改"
    - path: "skillforge/tests/test_audit_pack_store_init.py"
      type: "新建"
    - path: "config.py" # 假设有一个集中的 config 文件，或者直接在源文件里使用 os.getenv
      type: "修改或新建，用于承载 Feature Flags 的默认值"
  constraints:
    - "SKILLFORGE_ENV 默认值为 prod"
    - "AuditPackStore 在 SKILLFORGE_ENV=prod 时绝对不能生成 dummy 数据"
    - "新增针对三种环境枚举值的初始化测试"
    - "【零例外治理】: 拒绝任何形式的临时放行。缺配置、验签失败必须 BLOCK。"
    - "【零例外治理】: 生产零样例。prod 出现 sample/mock 数据，直接判定验收失败。"
    - "【零例外治理】: 必须保证可回滚。没有 Feature Flag 兜底或者回滚开关，不允许通过。"

# 红线 (Deny List)
deny:
  - "不得引入新依赖"
  - "不得修改验证相关的核心逻辑，只涉及初始化分流"
  - "禁止隐性后门：发现 fallback、兼容性放行、测试特判污染生产路径，直接打回。"

# 质量门禁 (Gate Check)
gate:
  auto_checks:
    - command: "pytest skillforge/tests/test_audit_pack_store_init.py -v"
      expect: "passed"
    - command: "pytest -q"
      expect: "不破坏现有测试"
```
