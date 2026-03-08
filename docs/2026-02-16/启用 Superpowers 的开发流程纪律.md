它的目标只有一个：**启用 Superpowers 的开发流程纪律，但所有“产品真相/合同真相”仍以 SkillForge 仓库的 contracts 为准**，两套体系绝不混在一起。

> 参考：Superpowers 官方 README/安装文档的定位是“给 coding agents 的完整开发工作流 + 可组合 skills”，并且在 OpenCode 等环境里通过 `.opencode/plugins` + skills 目录来加载。 ([GitHub][1])

---

## 开工令补丁（直接复制）

```text
# PATCH: Superpowers Workflow Enabled, SkillForge Contracts Are Canon

You MUST use Superpowers-style workflow discipline (brainstorm → plan → implement → verify)
to avoid skipping steps. However:

CANON OF TRUTH:
- The ONLY source of truth for product behavior is THIS repository’s contracts and gates:
  - schemas/**
  - orchestration/** (issue_catalog.yml, controls catalogs, profiles, policies)
  - contract_tests/**
  - tools/validate.py --all
  - Makefile targets (make ci)
- Superpowers is ONLY a development workflow helper. It must NOT redefine our schemas,
  issue_key taxonomy, error_code semantics, directory layout, or naming conventions.

NON-NEGOTIABLE RULES:
1) Never implement or refactor without first running:
   - python tools/validate.py --all
   - pytest -q
   (or simply: make ci)
2) Any new feature/change must include:
   - contract updates (schemas, catalogs, policies) if needed
   - at least 1 example JSON updated/added
   - contract test updates when required
   - tools/validate.py stays green
3) Do NOT introduce new “frameworks” or reorganize directories unless explicitly asked.
4) Keep work small and verifiable: commit in thin slices with passing CI.

WORKFLOW DISCIPLINE (Superpowers-style):
A) Brainstorm:
   - Restate the goal and constraints in 5 bullets max.
   - Identify the minimal contract changes needed.
B) Plan:
   - Write a short task plan with acceptance checks for each step.
C) Execute:
   - Implement the smallest change that makes one acceptance check pass.
D) Verify:
   - Run: python tools/validate.py --all && pytest -q
   - If failing: fix, re-run, never hand-wave.
E) Report:
   - Summarize what changed (files touched) and what tests were run.

OUTPUT FORMAT FOR EACH WORK SESSION:
- What I changed:
  - file list
- Commands I ran:
  - exact commands + results
- What is now passing:
  - validations/tests
- Next small step:
  - one step only
```

---

## 你可以再加一句“安装/启用提示”（可选）

如果你们的 Codex 环境确实接得上 Superpowers（比如 OpenCode / Codex adapter），再追加这一句即可（不强依赖）：

```text
If Superpowers integration is available in this environment, enable it.
If not available, still follow the workflow discipline above manually.
```

---

## 为什么这补丁能防“体系搅在一起”

* Superpowers 负责 **过程纪律**（不跳步、TDD、计划、验证）([GitHub][1])
* SkillForge 负责 **产物真相**（schemas / issue_catalog / validate.py / contract_tests）
* 两者用“CANON OF TRUTH”一刀切开，Codex 很难跑偏。

如果你还想更狠一点，我可以再给你一个“惩罚条款”：**任何 PR 如果没跑 `make ci` 就直接判定无效**（写进开工令）。

[1]: https://github.com/obra/superpowers/blob/main/README.md?utm_source=chatgpt.com "superpowers/README.md at main · obra/superpowers · GitHub"
