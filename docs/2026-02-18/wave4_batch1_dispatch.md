# ⚔️ Wave 4 Batch 1: 军团行动指令 (Commander's Orders)

> **指挥官**: Gemini
> **任务**: 7 Gate 并行突击
> **状态**: 🟢 Ready to Launch

请将以下指令分别分发给 3 个 AI Agent。

---

## 🟢 Squad A (先锋队) 指令
**负责 Gate**: `intake_repo`, `repo_scan_fit_score`

> **Prompt to Agent-1:**
>
> 你是 **Squad A (先锋队)**。你的任务是守住入口，根据 `contracts/gates/gate_interface_v1.yaml` 实现以下两个 Gate：
>
> **1. G1: intake_repo**
> - **Input**: `repo_url`, `commit_sha`
> - **Logic**: 校验输入完整性。如果 `commit_sha` 为空，直接 `REJECTED`。
> - **Evidence**: 生成 `intake_manifest.json`。
>
> **2. G2: repo_scan_fit_score**
> - **Input**: Repo 文件路径。
> - **Logic**: 扫描目录结构（如 `README.md`, `LICENSE`）。
> - **Score**: 计算适配分（0-100）。低于 60 分 `REJECTED`。
> - **Evidence**: 生成 `scan_report.json`。
>
> **行动**: 请在 `skillforge/src/gates/squad_a/` 下创建实现代码，并产出测试结果。

---

## 🔵 Squad B (参谋部) 指令
**负责 Gate**: `draft_skill_spec`, `constitution_risk_gate`

> **Prompt to Agent-2:**
>
> 你是 **Squad B (参谋部)**。你的任务是制定作战计划，根据 `contracts/gates/gate_interface_v1.yaml` 实现以下两个 Gate：
>
> **1. G3: draft_skill_spec**
> - **Input**: 来自 Squad A 的 `scan_report.json`。
> - **Logic**: 根据扫描结果，草拟 `skill_spec.yaml`（定义 skill 的输入输出契约）。
> - **Evidence**: 产出 `skill_spec.yaml`。
>
> **2. G4: constitution_risk_gate**
> - **Input**: `skill_spec.yaml`。
> - **Logic**: 审查 Spec 是否包含违宪关键词（如 "override_governance"）。
> - **Fail-Closed**: 发现任何风险，立即 `REJECTED`。
> - **Evidence**: 生成 `risk_assessment.json`。
>
> **行动**: 请在 `skillforge/src/gates/squad_b/` 下创建实现代码。

---

## 🟡 Squad C (工程兵) 指令
**负责 Gate**: `scaffold_skill_impl`, `sandbox_test`, `publish`

> **Prompt to Agent-3:**
>
> 你是 **Squad C (工程兵)**。你的任务是落地与发布，根据 `contracts/gates/gate_interface_v1.yaml` 实现以下三个 Gate：
>
> **1. G5: scaffold_skill_impl**
> - **Input**: 经过风险审查的 `skill_spec.yaml`。
> - **Logic**: 生成 Python 源码骨架 `skills/*.py`。
> - **Evidence**: 源码文件本身。
>
> **2. G6: sandbox_test_and_trace**
> - **Input**: 源码。
> - **Logic**: 在沙箱中运行并在 `at_time` 下进行 Trace 验证。
> - **Evidence**: `test_results.json`, `trace_log.json`。
>
> **3. G7: pack_audit_and_publish**
> - **Input**: G1-G6 的所有 Evidence。
> - **Logic**: 验证哈希链，打包为 L3 AuditPack。
> - **Evidence**: `audit_pack_manifest.json`。
>
> **行动**: 请在 `skillforge/src/gates/squad_c/` 下创建实现代码。
