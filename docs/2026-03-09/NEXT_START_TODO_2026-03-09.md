# 明日启动 TODO（2026-03-09）

## 一、优先收口

- [x] 已产出 `REAL-TASK-002` 合规审查口径：
  - `docs/2026-03-09/REAL-TASK-002_合规审查口径_2026-03-09.md`
- [x] 已起草 `REAL-TASK-002` 冻结结论草案：
  - `docs/2026-03-09/REAL-TASK-002_冻结结论_草案_2026-03-09.md`
- [x] 已整理 `REAL-TASK-001 / REAL-TASK-002` 首批真实闭环样本对照：
  - `docs/2026-03-09/REAL-TASK-001_REAL-TASK-002_首批真实闭环样本对照_2026-03-09.md`
- [x] 已完成 `REAL-TASK-002` 正式 `Compliance` 审查并固化结果：
  - `docs/2026-03-09/REAL-TASK-002_合规审查口径_2026-03-09.md`
- [x] 已将 `REAL-TASK-002` 冻结结论升级为正式版：
  - `docs/2026-03-09/REAL-TASK-002_冻结结论_2026-03-09.md`
- [x] 已产出 `REAL-TASK-003-R1` 冻结结论：
  - `docs/2026-03-10/REAL-TASK-003-R1_冻结结论_2026-03-10.md`
- [x] 已将样本对照扩展为 `REAL-TASK-001 / 002 / 003 / 003-R1`：
  - `docs/2026-03-09/REAL-TASK-001_REAL-TASK-002_首批真实闭环样本对照_2026-03-09.md`
- [x] 已将首批样本标记为“首批真实受控任务样本板”：
  - 统一口径：`patch_proposal_only`
  - 统一状态：`not absorbed`
  - 统一状态：`not final accepted`
  - 仅 `REAL-TASK-003-R1` 可写 `ABSORB_READY (proposal only)`

## 二、治理与统计补强

- [ ] 将 `execution-runtime-telemetry-skill` 正式拆分为：
  - `execution-time-telemetry-skill`
  - `execution-workload-telemetry-skill`
- [ ] 定义两者与 `governance-telemetry-skill` 的汇总关系
- [ ] 检查云端后续任务包是否统一产出：
  - `execution_runtime_report.json`
  - `execution_runtime_summary.md`
  - `execution_runtime_moments.md`

## 三、环境一致性治理

- [ ] 记录并审查两套云端执行环境差异：
  - `/root/openclaw-box/...`
  - `/home/node/.openclaw/...`
- [ ] 明确哪一套是后续主执行环境
- [ ] 把环境分叉纳入治理遥测报告

## 四、小龙虾加量前检查

- [x] 已基于 `REAL-TASK-002` 产出“小龙虾加量策略”：
  - `docs/2026-03-09/小龙虾加量策略_2026-03-09.md`
- [x] 已明确下一单继续给小龙虾：
  - `docs/2026-03-09/REAL-TASK-003_首版任务定义_2026-03-09.md`
- [x] 已明确当前仍限制为：
  - 单模块
  - 低风险
  - 文档/报告/规范化类
- [x] `REAL-TASK-003` 已完成独立合规审查：
  - 结论：`Compliance FAIL`
  - 原因：执行边界破坏、`completion_record` 口径污染
- [x] 已完成 `REAL-TASK-003-R1` remediation 收口冻结：
  - 已修复为真正的 `dropzone-only proposal`
  - 已修正 `completion_record` 状态口径
  - 已形成修复成功样本冻结结论
- [x] remediation 完成后，小龙虾当前仍维持 `Level A`：
  - 不加量
  - 不扩域

## 五、下一阶段准备

- [x] 已开启 `REAL-TASK-003` 准备：
  - `docs/2026-03-09/REAL-TASK-003_首版任务定义_2026-03-09.md`
- [x] `REAL-TASK-003` 已完成 `Phase 0` 冻结：
  - target_files
  - change_type
  - expected_diff_scope
- [ ] 继续保持：
  - Payload-First
  - Host Absorb Manual
  - Local Accept
- [ ] 固化“执行者分工规则”：
  - 云端 Codex：首单流程验证、底盘修复、治理/桥接/脚本/skill 安装类任务
  - 小龙虾：低风险、强约束、重复性高的执行任务

## 六、v0 差距清单（待封板项）

- [ ] 将“三哈希”正式并入每单主链：
  - `demand_hash`
  - `contract_hash`
  - `decision_hash`
- [ ] 将 Permit / 放行固化为唯一不可绕过入口
- [ ] 固化最小运行接口：
  - `RunRequest`
  - `RunResult`
  - `ArtifactManifest`
- [ ] 将 `dropzone -> pre_absorb_check -> absorb -> local accept` 固化为标准运行链
- [ ] 将运输层从“手工中继”提升为“制度化 payload transport”

## 七、v1 跃迁路线图（进入条件与建设方向）

- [ ] 统一任务接口与请求标识：
  - `request_id`
  - 幂等语义
  - 基本额度/配额字段
- [ ] 补齐自动 Gap / `required_changes` 产出
- [ ] 建立批量成功率统计与升级阈值
- [ ] 推动云端桥接从手工中继升级到半自动化
- [ ] 让 `execution-time-telemetry` 与 `execution-workload-telemetry` 拆分落地
- [ ] 将 `governance-telemetry` 抬升为升级裁判层

## 八、阶段判断（执行时参考）

- [ ] 当前定位：`v0 late stage`
- [ ] 当前原则：先封 v0，再进 v1
- [x] 首批真实受控任务样本板已封板：
  - `REAL-TASK-001`：冻结样本
  - `REAL-TASK-002`：冻结样本
  - `REAL-TASK-003`：`Compliance FAIL` 失败样本
  - `REAL-TASK-003-R1`：修复成功样本，`ABSORB_READY (proposal only)`
- [ ] 当前禁忌：
  - 不因局部成功样本而误判 v0 已彻底封板
  - 不在运输层未稳前直接追求批量化
  - 不在 Permit / 三哈希未固化前过早开放更大自动化
