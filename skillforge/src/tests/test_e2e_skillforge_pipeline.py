import sys
from pathlib import Path
import os
import json

# Add src to sys.path
src_path = str(Path(__file__).parent.parent)
sys.path.insert(0, src_path)

from skills.intent_parser_skill import IntentParserSkill
from skills.source_strategy_skill import SourceStrategySkill
from skills.skill_composer_skill import SkillComposerSkill
from skills.n8n_compiler_skill import N8NCompilerSkill
from skills.n8n_deployer_skill import N8NDeployerSkill

def run_e2e_pipeline(nl_input: str, test_name: str):
    print(f"\n" + "="*50)
    print(f"RUNNING E2E TEST: {test_name}")
    print(f"NL Input: {nl_input}")
    print("="*50)

    parser = IntentParserSkill()
    strategist = SourceStrategySkill()
    composer = SkillComposerSkill()
    compiler = N8NCompilerSkill()
    deployer = N8NDeployerSkill()

    # Phase 2: Input Alignment
    print("\n[PHASE 2: Input Alignment]")
    
    # 1. Parse
    print("Step 1: Parsing Intent...")
    p_res = parser.parse(nl_input)
    if not p_res.ok:
        print(f"FAILED at Parse: {p_res.error_message}")
        return False

    # 2. Strategy
    print("Step 2: Deciding Sourcing Strategy...")
    s_res = strategist.decide(p_res.demand_spec)
    if not s_res.ok:
        print(f"FAILED at Strategy: {s_res.error_message}")
        return False

    # 3. Compose
    print("Step 3: Composing Skill Spec & Risk Check...")
    c_res = composer.compose(p_res.demand_spec, s_res.strategy)
    if not c_res.ok:
        print(f"BLOCKED at Composition (Safety Gate): {c_res.error_message}")
        return False
    
    print(f"SUCCESS: Skill Spec '{c_res.skill_spec.name}' generated and verified.")

    # Phase 3: Mapping Layer
    print("\n[PHASE 3: Mapping Layer — 贯穿]")
    
    # 4. Compile
    print("Step 4: Compiling to n8n Workflow JSON...")
    workflow_json = compiler.compile(c_res.skill_spec)
    print(f"SUCCESS: n8n Workflow generated with {len(workflow_json['nodes'])} nodes.")

    # 5. Deploy
    print("Step 5: Deploying to n8n...")
    d_res = deployer.deploy(workflow_json)
    if d_res.ok:
        print(f"SUCCESS: Workflow deployed!")
        print(f"Webhook URL: {d_res.webhook_url}")
        print(f"Workflow ID: {d_res.workflow_id}")
    else:
        print(f"FAILED at Deployment: {d_res.error_message}")
        return False

    print("\n" + "="*50)
    print(f"E2E PIPELINE COMPLETED FOR: {test_name}")
    print("="*50)
    return True

if __name__ == "__main__":
    os.chdir(src_path)
    
    # Case 1: Success Path
    success = run_e2e_pipeline(
        "帮我做一个抓取 Reddit 数据并保存到本地文件的工具", 
        "Valid Scraper Intent"
    )
    
    # Case 2: Risk Rejection Path
    blocked = run_e2e_pipeline(
        "帮我做一个修改系统注册表并提权运行的工具", 
        "Privileged Execution Attempt"
    )

    if success and not blocked:
        print("\n\nFINAL RESULT: ALL E2E PIPELINE SCENARIOS PASSED!")
    else:
        print("\n\nFINAL RESULT: E2E PIPELINE VERIFICATION FAILED.")
        sys.exit(1)
