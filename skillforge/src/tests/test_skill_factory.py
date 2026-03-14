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

def test_skill_factory_success():
    print("Testing Skill Factory: Normal Intent...")
    parser = IntentParserSkill()
    strategist = SourceStrategySkill()
    composer = SkillComposerSkill()
    
    nl_input = "帮我做一个抓取 Reddit 数据并保存到本地文件的工具"
    
    # 1. Parse
    p_res = parser.parse(nl_input)
    assert p_res.ok
    
    # 2. Strategy
    s_res = strategist.decide(p_res.demand_spec)
    assert s_res.ok
    
    # 3. Compose (should PASS)
    c_res = composer.compose(p_res.demand_spec, s_res.strategy)
    assert c_res.ok
    assert c_res.gate_decision == "PASSED"
    print(f"SUCCESS: Skill '{c_res.skill_spec.name}' created.")

def test_skill_factory_constitution_violation():
    print("\nTesting Skill Factory: Constitution Violation (Privileged Execution)...")
    parser = IntentParserSkill()
    strategist = SourceStrategySkill()
    composer = SkillComposerSkill()
    
    # Intent that requires prohibited capability
    nl_input = "帮我做一个修改系统注册表并提权运行的工具"
    
    # 1. Parse
    p_res = parser.parse(nl_input)
    # Mocking parser to include a prohibited capability for this test
    p_res.demand_spec.requirements.append("Capability matched: privileged_execution")
    p_res.demand_spec.user_goal = "SYSTEM MODIFICATION PRIVILEGED" # Trigger the mock logic better
    
    # 2. Strategy
    s_res = strategist.decide(p_res.demand_spec)
    
    # 3. Compose (should REJECT)
    # We need to ensure the composer picks up the risk
    # In my current simple composer, I'll manually inject the prohibited capability to test the gate
    p_res.demand_spec.user_goal = "privileged_execution" 
    
    c_res = composer.compose(p_res.demand_spec, s_res.strategy)
    
    # The composer automatically adds 'network' and 'file_write' based on keywords.
    # Let's check how the composer handles risk.
    # I'll update the composer test to force a rejection.
    
    print(f"Composition Result OK: {c_res.ok}")
    print(f"Gate Decision: {c_res.gate_decision}")
    
    if c_res.gate_decision == "REJECTED":
        print("SUCCESS: Prohibited intent correctly REJECTED by Constitution Gate.")
    else:
        print("FAILURE: Prohibited intent was NOT rejected.")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure working directory is src
    os.chdir(src_path)
    
    try:
        test_skill_factory_success()
        test_skill_factory_constitution_violation()
        print("\nAll Skill Factory Phase 2 tests passed!")
    except Exception as e:
        print(f"Tests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
