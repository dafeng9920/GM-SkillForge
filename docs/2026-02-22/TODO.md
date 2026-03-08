# GM-SkillForge TODO 看板（2026-02-22）

目标：把“临时可跑”推进为“系统原生可复现”，并补齐前端落地断点。  
状态枚举：`已完成` | `进行中` | `待完成` | `待确认`

## P0 - 审计系统化落地（必须完成）

| 项目 | 负责人 | 状态 | 核心交付物 | 验收标准 | 证据/备注 |
|---|---|---|---|---|---|
| P0-1 审计入口产品化（CLI/命令） | Codex | 已完成 | 统一命令入口（目标：`skillforge audit run --profile l5-static --domains finance,legal --top-n 10 --output-dir reports/skill-audit`） | 非脚本作者可单命令复跑 | 已补 `pyproject.toml` console script + `scripts` 包化；`skillforge audit run --help` 验证通过 |
| P0-2 审计策略配置化与版本化 | Codex | 已完成 | `configs/audit_policy_v1.json`；报告写入 `policy_version` | 改阈值无需改代码 | 已落盘并被审计脚本读取 |
| P0-3 证据链标准输出 | Codex | 已完成 | 输出 `run_id`、`evidence_ref`、输入/结果哈希；落盘到 `reports/skill-audit/runs/<run_id>/` | 结果可追溯输入与规则版本 | `reports/skill-audit/runs/*/run_meta.json` 已存在 |
| P0-4 CI 门禁（最小可用） | Codex | 已完成 | CI Job 执行 `l5-static` smoke，失败即拦截 | 审计破坏可被 CI 拦截 | `.github/workflows/l5-gate.yml` |

## P1 - 前端落地（必须有可演示页面）

| 项目 | 负责人 | 状态 | 核心交付物 | 验收标准 | 证据/备注 |
|---|---|---|---|---|---|
| P1-1 审计结果页 MVP | Codex | 已完成 | 总览卡、明细表（可排序）、结论限制区块；读取 `reports/skill-audit/*.json` | 桌面/移动可浏览 | `ui/app/src/pages/audit/SkillAuditPage.tsx`，路由已接入 |
| P1-2 前后端数据契约对齐 | Codex | 已完成 | 前端消费 schema + 加载前 JSON 校验 + 错误提示 | 字段缺失不静默失败 | `schemas/skill_audit_report.schema.json` + 页面内校验逻辑 |
| P1-3 Demo 脚本 | Codex | 已完成 | `docs/2026-02-22/DEMO_STEPS.md` | 5 分钟内可重复演示 | 文档已落盘 |

## 后续任务（对齐既定文档）

> 仅保留 `docs/2026-02-22/L4.5.MD` 与 `docs/2026-02-22/系统状态审讯报告.md` 明确提出的后续项。

| 项目 | 负责人 | 状态 | 目标 |
|---|---|---|---|
| N1 n8n production endpoints | 待分配 | 待完成 | 将 n8n 从 `NOT_IMPLEMENTED` 升级到 `VERIFIED` |
| N2 P2 证据包冻结 | 待分配 | 待完成 | 生成并固化 `P2_CLOSING_FREEZE.md`/索引口径 |
| N3 远端 CI/PR 验证 | 待分配 | 待完成 | 触发并留存主干可追溯执行证据 |

## 当前未完成清单（可直接盯办）

| 项目 | 负责人 | 状态 | 下一动作 |
|---|---|---|---|
| N1 n8n production endpoints | 待分配 | 待完成 | 从 Mock 验证态切换到真实后端端点并补验证证据 |
| N2 P2 证据包冻结 | 待分配 | 待完成 | 按当前事实源生成冻结文档并记录 hash |
| N3 远端 CI/PR 验证 | 待分配 | 待完成 | 执行一次远端流水线并归档运行证据 |

## Backlog（不纳入当前主线验收）

| 项目 | 负责人 | 状态 | 目标 | 备注 |
|---|---|---|---|---|
| B1 Token 计数升级 | 待分配 | 待完成 | 从估算升级为模型 tokenizer 实测 | 提升成本与质量评估精度 |
| B2 A/B 回归样例 | 待分配 | 待完成 | 增加压缩前后 A/B 回归样例（2 个 skill） | 用于长期回归基线 |
| B3 证据链详情抽屉 | 待分配 | 待完成 | 前端展示 run_id/evidence_ref/hash 详情抽屉 | 提升运营与复盘效率 |

## Definition of Done（明日收工口径）

1. 审计能力不再依赖临时脚本调用路径，进入系统命令入口。
2. 审计输出具备 run_id + evidence_ref + policy_version。
3. 前端可展示本次 `finance+legal top10` 报告并可排序筛选。
4. CI 至少覆盖 1 条审计 smoke gate。
5. 形成一页可对外复述的“方法-结果-限制”说明。

## 建议执行顺序（减少返工）

1. 优先推进 N1（n8n 生产端点），这是当前唯一明确开放风险。
2. 完成 N2（P2 冻结）与 N3（远端 CI/PR 证据）做收口。

## 明后天推进任务（优先级）

| 优先级 | 任务 | 目标产物 | 状态 |
|---|---|---|---|
| 1 | N1 n8n production endpoints | n8n 从 Mock 升级为可用生产端点实现 | 待完成 |
| 2 | N1 完成后端到端验证并补证据 | `docs/2026-02-22/verification/n8n_probe_report.json` 升级为 `VERIFIED` | 待完成 |
| 3 | N2 P2 证据包冻结 | `P2_CLOSING_FREEZE.md` + 冻结索引/hash 更新 | 待完成 |
| 4 | N3 远端 CI/PR 验证 | 一次远端流水线成功记录 + 证据落盘 | 待完成 |
| 5 | 更新系统状态审讯报告口径 | `docs/2026-02-22/系统状态审讯报告.md` 与最新事实一致 | 待完成 |
| 6 | Backlog 顺序推进（不纳入主线验收） | 按 B2 -> B1 -> B3 逐项推进 | 待完成 |

> 执行总计划直达：`docs/2026-02-22/L5-L6_EXECUTION_PLAN.md`
