# 治理承诺内核硬化实施计划（可执行版）

目标：在不牺牲交付节奏的前提下，完成三件 P0 事项：Permit 真验签闭环、生产语义去污染、Registry 从线性文件读升级为可回滚的事务化读写。

## 1. 范围与原则

### In Scope
- Permit Gate 的签名验证从“可降级”升级为“不可绕过”的 Fail-Closed。
- AuditPackStore 在生产环境禁止自动创建 sample 数据。
- RegistryStore 引入 SQLite 索引能力，采用“兼容读 + 双写 + 切读”迁移路径。

### Out of Scope
- 本阶段不改 8-Gate 编排范式，不做全量微内核重构。
- 本阶段不引入新业务能力，仅做治理承诺硬化与存储迁移。

### 强制原则
- 任何异常默认 `BLOCK`，不得返回“绕过验证”的成功态。
- 所有变更必须具备可观测信号（日志、计数器或错误码）。
- 每个里程碑均需可独立回滚，回滚时间目标 < 10 分钟。

## 2. 里程碑总览

| 里程碑 | 时间窗 | 交付物 | 验收门禁 | 回滚触发条件 |
|---|---|---|---|---|
| M0：基线与护栏 | Day 1 | Feature flags、基线测试报告、回滚手册 | 基线测试可复现 | 基线不稳定/无法复现 |
| M1：Permit 硬化 | Day 2-4 | 严格验签逻辑 + 对应测试 | 无 key/坏签名/未知 algo 全部 BLOCK(E003) | 线上误判率突增或 5xx |
| M2：生产去 sample | Day 4-5 | AuditPackStore 环境分流 | `prod` 环境零 sample 注入 | 影响现网读取或初始化失败 |
| M3：Registry 双轨迁移 | Day 6-10 | SQLite backend + 双写 + 一致性校验脚本 | 一致率 100%，读写性能达标 | 一致率<100% 或写失败升高 |
| M4：切主读与收口 | Day 11-14 | 主读切换到 SQLite，保留 JSONL 回退 | 灰度稳定 48h | 灰度期间读延迟/错误异常 |

## 3. Feature Flags（先加再改）

- `SKILLFORGE_ENV=prod|dev|test`
- `REGISTRY_BACKEND=jsonl|sqlite`（默认 `jsonl`）
- `REGISTRY_DUAL_WRITE=0|1`（默认 `0`）
- `REGISTRY_SHADOW_READ_COMPARE=0|1`（默认 `0`）

说明：M3 前不允许直接把默认 backend 改为 sqlite。

## 4. 分阶段实施细则

### M0：基线与护栏
#### 变更
- 增加上述 flags 的配置读取与默认值。
- 固化基线命令与报告路径（便于对比回归）。

#### 验收标准
- 可重复执行以下命令并保存结果：
  - `pytest skillforge/tests/test_gate_permit.py -v`
  - `pytest skillforge/tests/test_registry_store.py -v`
  - `pytest skillforge/tests/test_n8n_orchestration.py -v`
- 产出一份“改动前基线”文档（通过率、失败项、耗时）。

#### 回滚步骤
1. 不发布 M0 代码开关时，停止后续里程碑。
2. 回退到上一稳定 tag。
3. 重新执行基线命令，确认恢复。

### M1：Permit 签名强制闭环
#### 变更
- 文件：`skillforge/src/skills/gates/gate_permit.py`
- 将 `_stub_signature_verifier` 升级为严格验证器：
  - `HS256`：必须存在 `PERMIT_HS256_KEY`，且签名验证通过。
  - `RS256/ES256`：未实现真实公钥验证前一律返回 `False`（由 Gate 输出 `BLOCK/E003`，不得抛 500）。
  - 未知算法：返回 `False`。
- 文件：`skillforge/tests/test_gate_permit.py`
  - 改为测试内构造真实签名或注入 `signature_verifier`，避免依赖全局环境污染。
  - 新增“无 key”“坏签名”“未知 algo”用例。

#### 验收标准
- `pytest skillforge/tests/test_gate_permit.py -v` 全通过。
- 三类负向输入均返回：`gate_decision=BLOCK` 且 `error_code=E003`。
- 运行时不出现未捕获异常（0 个 5xx）。

#### 回滚步骤
1. 立即回退到 M0 稳定 tag。
2. 若必须保持服务可用，临时以“全部 BLOCK”代替“放行”（保持 Fail-Closed）。
3. 重新跑 Permit Gate 测试并恢复发布。

### M2：清除生产语义污染
#### 变更
- 文件：`skillforge/src/storage/audit_pack_store.py`
- `_ensure_initialized()` 中仅在 `SKILLFORGE_ENV in ("dev","test")` 才允许 `_create_sample_packs()`。
- `prod` 默认空库，不生成示例数据。
- 新增/补充测试文件：`skillforge/tests/test_audit_pack_store_init.py`（如不存在则创建）。

#### 验收标准
- 在 `SKILLFORGE_ENV=prod` 下初始化后 sample pack 数量为 0。
- 在 `SKILLFORGE_ENV=test` 下可按需生成 sample pack（用于测试）。
- 不影响 `fetch_pack` 真实数据读取。

#### 回滚步骤
1. 发现生产读取异常时回退到 M1 tag。
2. 清理异常生成的 sample 数据（若有）。
3. 以 `prod` 配置重启并复测。

### M3：Registry 双轨迁移（禁止一步到位切换）
#### 变更
- 文件：`skillforge/src/storage/registry_store.py`
- 引入 SQLite 存储与索引，但保留 JSONL 兼容读写接口。
- 迁移策略：
  1. `REGISTRY_BACKEND=jsonl` + `REGISTRY_DUAL_WRITE=1`（先双写）
  2. 开启 `REGISTRY_SHADOW_READ_COMPARE=1`（对比 jsonl/sqlite 结果）
  3. 一致率 100% 后再切 `REGISTRY_BACKEND=sqlite`
- 新增脚本：
  - `scripts/migrate_registry_jsonl_to_sqlite.py`
  - `scripts/verify_registry_consistency.py`
- 更新测试：`skillforge/tests/test_registry_store.py` 覆盖 jsonl/sqlite/dual-write 三模式。

#### 验收标准
- 双写阶段一致性校验为 100%（按 skill_id + latest_active + revision history）。
- `get_latest_active` 在样本数据下性能优于 JSONL 线性扫描。
- append-only 语义保持（无 update/delete 路径）。

#### 回滚步骤
1. 将 `REGISTRY_BACKEND` 立即切回 `jsonl`，关闭 shadow compare。
2. 保留 SQLite 数据用于排障，不作为主读源。
3. 回退 M3 代码或停留在双写阶段，待修复后重试。

### M4：切主读与收口
#### 变更
- 生产灰度将 `REGISTRY_BACKEND=sqlite`，维持 `REGISTRY_DUAL_WRITE=1` 至少一个发布周期。
- 灰度稳定后再评估关闭 JSONL 双写。

#### 验收标准
- 灰度 48 小时内无一致性告警、无读写错误异常升高。
- 关键 API（run_intent/import_external_skill/fetch_pack）回归通过。

#### 回滚步骤
1. 一键切回 `REGISTRY_BACKEND=jsonl`。
2. 维持双写，保全数据。
3. 复盘并修复后再次灰度。

## 5. 统一验收清单（Definition of Done）

- 安全：Permit 验签不可降级，异常默认 BLOCK。
- 语义：生产环境不生成 sample/mock 数据。
- 性能：Registry 查询不再依赖全文件线性扫描。
- 可回滚：每个里程碑都能在 10 分钟内回到上一稳定状态。
- 可追溯：每次切换有日志、有报告、有对应 commit/tag。
