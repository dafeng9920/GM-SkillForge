# Execution Guard A: Proposal Skill v1

> 最新版单一事实源 (Single Source of Truth)

## 1. 核心护栏理念 (The Core Philosophy)
任何未受强约束的执行方案，都是对系统架构完整性的潜在破坏。
本提案规范（Proposal Skill）强制主控官（Commander）与执行者（Executor）在分派及回放方案时，必须严格遵循一种 **“防御导向（Defensive-First）”** 的三段式报告结构。凡是不符合此基本结构要求的任务建议，一律作废打回。

## 2. 三段式结构 (The Mandatory 3-Part Structure)

所有执行方案/计划表必须包含、且仅包含以下结构：

### 1) PreflightChecklist (起飞前检查单)
在接触代码和系统状态前，必须明确当前护栏：
- **Fail-Closed 风险枚举**：这项变动可能在什么边缘条件下绕过默认拒绝规则？
- **依赖环境 (Env/Flags)**：涉及哪些 Feature Flags 以及环境变量（需明确给出各环境下的默认挂载值）。
- **历史债务扫描**：代码库中该路径周边现存的 `fallback`（降级放行）或“容错跳过”逻辑是什么？

### 2) ExecutionContract (执行契约)
锁定改动范围，禁止执行特权外渗。
- **Input Constraints**：可以碰哪些文件，绝对不可碰/绕过哪些文件。
- **Output Definition**：交付物形态，且必须明文附带 **回滚（Rollback）方案**。如果不能回滚，不允许变更。
- **Gate / Acceptance Check**：确切的自动化验收命令与准出判断标准。

### 3) RequiredChanges (确切改动点)
拒绝抽象与空泛，提供精确改动蓝图。
- 必须精确定位到修改的文件名与类/方法名。
- 必须明确具体的防腐层调整。例如，不能仅说“去掉 mock”，必须表述为“当验签失败或 key 缺失时，立即抛出附带 EvidenceRef 的 `E003` 错误并阻断流程”。
