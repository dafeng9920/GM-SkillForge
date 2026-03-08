SkillForge 实现层架构设计 + 接口合同 (v2)
修订说明: 根据原始产品愿景补全了"生成层"——即 NL(自然语言) → Skill 的完整路径。 原始愿景文档明确定义了三层架构：聚合层 + 生成层 + 可信层。

产品定位（来自原始愿景）
"利用 gm os 的编排能力，做一个专门写 skill 的网站，
 再把 github 的网站下载，整合成一个 skill 的专业生成网站"
三层拆解：

聚合层 — GitHub skill/模板发现、归档、可搜索
生成层 — 用 GM OS 编排，把"需求 → skill"自动生成 ← ⚠️ 之前的架构遗漏了这层
可信层 — 门禁、审计、trace、合约验收
总体架构（双路径）
路径A: 从零生成
路径B: GitHub优化
路径A+B: 混合
用户自然语言'我需要一个SEO审计工具'
用户提供 GitHub URLgithub.com/user/repo
IntentParser意图理解 + 结构化
SourceStrategy路径决策器
SkillComposerSpec + 实现 生成
intake_repoStage 0
GitHubDiscovery搜索匹配repo
constitution_risk_gateStage 4
license_gateStage 1
repo_scan_fit_scoreStage 2
draft_skill_specStage 3
scaffold_skill_implStage 5
sandbox_test_and_traceStage 6
pack_audit_and_publishStage 7
路径说明
路径	入口	流程	MVP 优先级
A: NL → Skill	自然语言描述	Intent → Spec → Scaffold → Gate → Test → Publish	P1
B: GitHub → Skill	repo URL	Intake → License → Scan → Draft → Gate → Test → Publish	P1
A+B: 混合	自然语言 + 自动搜索 GitHub	Intent → Discovery → Intake → ... → Publish	P2
新增模块（之前架构遗漏的）
1. IntentParser（意图解析器）
[NEW] 
intent_parser.py
class IntentParser(NodeHandler):
    node_id = "intent_parse"
    def execute(self, input_data: dict) -> dict:
        """
        Input:  { "natural_language": "我需要一个能分析网页SEO的工具",
                  "context": { "user_id": "...", "preferences": {...} } }
        Output: { "intent": {
                    "skill_name": "tech_seo_audit",
                    "description": "分析网页的技术SEO指标",
                    "capabilities_needed": ["network", "html_parse"],
                    "input_hints": {"url": "string"},
                    "output_hints": {"report": "object"},
                    "risk_estimate": "L1",
                    "suggested_sources": ["github", "generate"]
                  }}
        """
2. SourceStrategy（路径决策器）
[NEW] 
source_strategy.py
class SourceStrategy(NodeHandler):
    node_id = "source_strategy"
    def execute(self, input_data: dict) -> dict:
        """
        Input:  { "intent": {...}, "repo_url": null | "https://..." }
        Output: { "path": "A" | "B" | "AB",
                  "reason": "用户已提供 repo URL，走 GitHub 优化路径",
                  "github_search_query": "technical SEO python tool" | null,
                  "repo_url": "https://..." | null }
        """
3. GitHubDiscovery（GitHub 搜索）
[NEW] 
github_discover.py
class GitHubDiscovery(NodeHandler):
    node_id = "github_discover"
    def execute(self, input_data: dict) -> dict:
        """
        Input:  { "search_query": "technical SEO python tool",
                  "intent": {...}, "max_results": 5 }
        Output: { "candidates": [
                    { "repo_url": "...", "stars": 200, "license": "MIT",
                      "fit_score_estimate": 78, "match_reason": "..." }
                  ],
                  "selected": { "repo_url": "...", "reason": "..." } | null }
        """
4. SkillComposer（路径 A 专用：从零生成 Skill）
[NEW] 
skill_composer.py
class SkillComposer(NodeHandler):
    node_id = "skill_compose"
    def execute(self, input_data: dict) -> dict:
        """
        路径 A 专用：直接从意图生成完整 Skill Spec + 实现骨架
        跳过 Stage 0-3（不需要 GitHub 扫描）
        Input:  { "intent": {...} }
        Output: { "SKILL.md": "...",
                  "schemas": { "input": {...}, "output": {...} },
                  "capabilities": [...],
                  "scaffold_bundle": { ... },
                  "provenance": { "source_type": "generated", ... } }
        """
更新后的 Pipeline 节点清单
#	node_id	Stage	路径	模块
—	intent_parse	Pre-0	A, A+B	nodes/intent_parser.py
—	source_strategy	Pre-0	A, A+B	nodes/source_strategy.py
—	github_discover	Pre-0	A+B	nodes/github_discover.py
—	skill_compose	A-only	A	nodes/skill_composer.py
0	intake_repo	0	B, A+B	nodes/intake_repo.py
1	license_gate	1	B, A+B	nodes/license_gate.py
2	repo_scan_fit_score	2	B, A+B	nodes/repo_scan.py
3	draft_skill_spec	3	B, A+B	nodes/draft_spec.py
4	constitution_risk_gate	4	ALL	nodes/constitution_gate.py
5	scaffold_skill_impl	5	ALL	nodes/scaffold_impl.py
6	sandbox_test_and_trace	6	ALL	nodes/sandbox_test.py
7	pack_audit_and_publish	7	ALL	nodes/pack_publish.py
Stage 4-7 是所有路径共享的后半段（可信层）

完整文件结构
skillforge/src/
├── __init__.py
├── cli.py                          # CLI 入口
├── protocols.py                    # NodeHandler / GateEvaluator / Adapter
├── adapters/
│   ├── __init__.py
│   ├── github_fetch/               # GitHub API 调用
│   │   ├── __init__.py
│   │   ├── adapter.py              # fetch + scan + discover
│   │   └── types.py
│   ├── sandbox_runner/             # 沙箱执行
│   │   ├── __init__.py
│   │   ├── adapter.py
│   │   └── types.py
│   └── registry_client/            # Registry 发布
│       ├── __init__.py
│       └── adapter.py
├── orchestration/
│   ├── __init__.py
│   ├── engine.py                   # PipelineEngine（双路径编排）
│   ├── node_runner.py              # NodeRunner（trace + timeout + retry）
│   └── gate_engine.py              # GateEngine
└── nodes/
    ├── __init__.py
    ├── intent_parser.py            # [NEW] NL 意图解析
    ├── source_strategy.py          # [NEW] 路径决策
    ├── github_discover.py          # [NEW] GitHub 搜索
    ├── skill_composer.py           # [NEW] 从零生成 Skill
    ├── intake_repo.py              # Stage 0
    ├── license_gate.py             # Stage 1
    ├── repo_scan.py                # Stage 2
    ├── draft_spec.py               # Stage 3
    ├── constitution_gate.py        # Stage 4
    ├── scaffold_impl.py            # Stage 5
    ├── sandbox_test.py             # Stage 6
    └── pack_publish.py             # Stage 7
~25 新文件，0 修改已有文件。

Engine Input Contract（更新版）
{
  "mode": "nl | github | auto",
  "natural_language": "我需要一个SEO审计工具",
  "repo_url": "https://github.com/user/repo",
  "branch": "main",
  "options": {
    "target_environment": "python",
    "intended_use": "web",
    "visibility": "public",
    "sandbox_mode": "strict"
  }
}
mode: "nl" → 路径 A（用户只给自然语言，从零生成）
mode: "github" → 路径 B（用户给 URL，GitHub 优化）
mode: "auto" → 路径 A+B（NL 解析意图 → 搜索 GitHub → 有则优化，无则生成）
Verification Plan
Automated Tests
pytest -q                        # 现有合同测试不受影响
python tools/validate.py --all   # 现有示例校验不受影响
pytest skillforge/tests/ -v      # 新增 Protocol + Engine 测试
E2E Smoke Test（MVP 完成后）
# 路径 A
skillforge refine --mode nl "一个能分析网页SEO的Python工具"
# 路径 B
skillforge refine --mode github https://github.com/nichochar/tech-seo-tool
# 路径 A+B
skillforge refine --mode auto "一个能分析网页SEO的Python工具"

Comment
Ctrl+Alt+M
