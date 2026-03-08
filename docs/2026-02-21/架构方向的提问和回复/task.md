# 治理承诺内核硬化任务分解（可执行版）

说明：该任务单与 `implementation_plan.md` 对齐，按 M0-M4 顺序执行。未完成当前里程碑验收前，不得进入下一里程碑。

## M0 基线与护栏（Day 1）

- [ ] 新增配置开关（默认安全值）：
  - [ ] `SKILLFORGE_ENV`（默认 `prod`）
  - [ ] `REGISTRY_BACKEND`（默认 `jsonl`）
  - [ ] `REGISTRY_DUAL_WRITE`（默认 `0`）
  - [ ] `REGISTRY_SHADOW_READ_COMPARE`（默认 `0`）
- [ ] 记录改动前基线结果（通过率/耗时/失败项）：
  - [ ] `pytest skillforge/tests/test_gate_permit.py -v`
  - [ ] `pytest skillforge/tests/test_registry_store.py -v`
  - [ ] `pytest skillforge/tests/test_n8n_orchestration.py -v`

### M0 验收标准
- [ ] 基线结果可复现，且报告已归档到 docs。

### M0 回滚步骤
- [ ] 回退到上一个稳定 tag。
- [ ] 重新执行三条基线命令确认恢复。

## M1 Permit 验签硬化（Day 2-4）

- [ ] 修改 `skillforge/src/skills/gates/gate_permit.py`：
  - [ ] `HS256` 无 `PERMIT_HS256_KEY` 必须失败。
  - [ ] `HS256` 验签失败必须失败。
  - [ ] `RS256/ES256` 在未实现真实公钥验签前一律失败。
  - [ ] 所有失败路径统一输出 `BLOCK + E003`，不得抛 500。
- [ ] 更新 `skillforge/tests/test_gate_permit.py`：
  - [ ] 用测试内签名构造/注入验证器替代脆弱 fixture。
  - [ ] 新增无 key、坏签名、未知 algo 的负向测试。

### M1 验收标准
- [ ] `pytest skillforge/tests/test_gate_permit.py -v` 全通过。
- [ ] 负向场景均返回 `gate_decision=BLOCK` 且 `error_code=E003`。
- [ ] 服务日志无未捕获异常。

### M1 回滚步骤
- [ ] 回退 M1 代码到 M0 稳定 tag。
- [ ] 紧急兜底只能“全部 BLOCK”，禁止“放行降级”。
- [ ] 复跑 Permit 测试确认恢复。

## M2 清除生产语义污染（Day 4-5）

- [ ] 修改 `skillforge/src/storage/audit_pack_store.py`：
  - [ ] `_create_sample_packs()` 仅允许在 `dev/test` 环境触发。
  - [ ] `prod` 环境初始化不得生成 sample pack。
- [ ] 新增或补齐测试（如不存在则创建）：
  - [ ] `skillforge/tests/test_audit_pack_store_init.py`
  - [ ] 覆盖 `prod/dev/test` 三环境行为。

### M2 验收标准
- [ ] `SKILLFORGE_ENV=prod` 时 sample 数量为 0。
- [ ] `SKILLFORGE_ENV=test` 时可按预期生成 sample（仅测试用途）。
- [ ] `fetch_pack` 真实数据读取路径不回归。

### M2 回滚步骤
- [ ] 回退到 M1 稳定 tag。
- [ ] 清理异常 sample 数据。
- [ ] 复测初始化与读取路径。

## M3 Registry 双轨迁移（Day 6-10）

- [ ] 改造 `skillforge/src/storage/registry_store.py` 支持 SQLite backend：
  - [ ] 保留 JSONL 兼容能力。
  - [ ] 增加双写路径（`REGISTRY_DUAL_WRITE=1`）。
  - [ ] 增加 shadow read compare（`REGISTRY_SHADOW_READ_COMPARE=1`）。
- [ ] 新增迁移与核对脚本：
  - [ ] `scripts/migrate_registry_jsonl_to_sqlite.py`
  - [ ] `scripts/verify_registry_consistency.py`
- [ ] 更新 `skillforge/tests/test_registry_store.py`：
  - [ ] 覆盖 `jsonl/sqlite/dual-write` 三模式。
  - [ ] 验证 append-only 语义未破坏。

### M3 验收标准
- [ ] 一致性核对报告 100% 通过。
- [ ] `get_latest_active` 性能显著优于 JSONL 线性扫描。
- [ ] 无 update/delete 破坏 append-only 语义。

### M3 回滚步骤
- [ ] 立即设置 `REGISTRY_BACKEND=jsonl`。
- [ ] 关闭 shadow compare，必要时关闭 dual-write。
- [ ] 保留 SQLite 数据用于排障，不作为主读源。

## M4 切主读与收口（Day 11-14）

- [ ] 灰度切换：`REGISTRY_BACKEND=sqlite`，保留 `REGISTRY_DUAL_WRITE=1` 一个发布周期。
- [ ] 灰度观察窗口：48 小时（错误率、延迟、一致性）。
- [ ] 灰度通过后，提交收口报告与后续优化清单。

### M4 验收标准
- [ ] 48 小时内无 P0/P1 告警。
- [ ] run_intent/import_external_skill/fetch_pack 回归通过。
- [ ] 可回滚演练成功（切回 jsonl < 10 分钟）。

### M4 回滚步骤
- [ ] 一键切回 `REGISTRY_BACKEND=jsonl`。
- [ ] 保持 dual-write，防止数据缺口。
- [ ] 复盘后再发起下一次灰度。

## 全局质量门（每阶段都要过）

- [ ] 安全门：Fail-Closed 不可降级，不得出现“验签失败但放行”。
- [ ] 语义门：生产环境无 sample/mock 数据注入。
- [ ] 回滚门：任何阶段都可在 10 分钟内恢复。
- [ ] 证据门：每次发布有测试报告、变更记录、回滚记录。
