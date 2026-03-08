"""Wave 7 verification: Path A chain + Adapter tests."""
import sys

def test_path_a_chain():
    from skillforge.src.nodes.intent_parser import IntentParser
    from skillforge.src.nodes.source_strategy import SourceStrategy
    from skillforge.src.nodes.skill_composer import SkillComposer
    from skillforge.src.nodes.constitution_gate import ConstitutionGate
    from skillforge.src.nodes.scaffold_impl import ScaffoldImpl
    from skillforge.src.nodes.sandbox_test import SandboxTest
    from skillforge.src.nodes.pack_publish import PackPublish

    artifacts = {"input": {"mode": "nl", "natural_language": "Build a data processing pipeline"}}

    ip = IntentParser()
    assert ip.validate_input(artifacts) == []
    artifacts["intent_parse"] = ip.execute(artifacts)
    assert artifacts["intent_parse"]["intent"]["domain"] == "data_processing"
    print(f"  intent: domain={artifacts['intent_parse']['intent']['domain']}, confidence={artifacts['intent_parse']['confidence']}")

    ss = SourceStrategy()
    assert ss.validate_input(artifacts) == []
    artifacts["source_strategy"] = ss.execute(artifacts)
    assert artifacts["source_strategy"]["strategy"] == "generate"
    print(f"  strategy: {artifacts['source_strategy']['strategy']}")

    sc = SkillComposer()
    assert sc.validate_input(artifacts) == []
    artifacts["skill_compose"] = sc.execute(artifacts)
    assert "skill-data_processing" in artifacts["skill_compose"]["skill_spec"]["name"]
    print(f"  compose: name={artifacts['skill_compose']['skill_spec']['name']}")

    cg = ConstitutionGate()
    assert cg.validate_input(artifacts) == []
    artifacts["constitution_risk_gate"] = cg.execute(artifacts)
    assert artifacts["constitution_risk_gate"]["decision"] == "ALLOW"
    print(f"  constitution: decision={artifacts['constitution_risk_gate']['decision']}")

    si = ScaffoldImpl()
    assert si.validate_input(artifacts) == []
    artifacts["scaffold_skill_impl"] = si.execute(artifacts)
    assert artifacts["scaffold_skill_impl"]["bundle_path"].startswith("/tmp/skillforge")
    print(f"  scaffold: bundle={artifacts['scaffold_skill_impl']['bundle_path']}")

    st = SandboxTest()
    assert st.validate_input(artifacts) == []
    artifacts["sandbox_test_and_trace"] = st.execute(artifacts)
    assert artifacts["sandbox_test_and_trace"]["success"] is True
    print(f"  sandbox: success={artifacts['sandbox_test_and_trace']['success']}")

    pp = PackPublish()
    assert pp.validate_input(artifacts) == []
    artifacts["pack_audit_and_publish"] = pp.execute(artifacts)
    assert artifacts["pack_audit_and_publish"]["publish_result"]["status"] == "published"
    print(f"  publish: status={artifacts['pack_audit_and_publish']['publish_result']['status']}")

    print("  PATH A chain: OK")

def test_adapters():
    from skillforge.src.adapters.github_fetch.adapter import GitHubFetchAdapter
    from skillforge.src.adapters.sandbox_runner.adapter import SandboxRunnerAdapter
    from skillforge.src.adapters.sandbox_runner.types import SandboxConfig
    from skillforge.src.adapters.registry_client.adapter import RegistryClientAdapter

    gf = GitHubFetchAdapter()
    assert gf.health_check() is True
    info = gf.fetch_repo_info("https://github.com/owner/repo")
    assert info.name == "repo" and info.owner == "owner"
    scan = gf.scan_repo_structure("https://github.com/owner/repo")
    assert scan.fit_score == 70
    disc = gf.discover_repos("data pipeline", {}, 3)
    assert len(disc.candidates) == 3
    print(f"  github_fetch: repo={info.name}, scan={scan.fit_score}, candidates={len(disc.candidates)}")

    sr = SandboxRunnerAdapter()
    assert sr.health_check() is True
    result = sr.run_in_sandbox("/tmp/test-bundle", SandboxConfig())
    assert result.success is True and result.test_report["passed"] == 3
    print(f"  sandbox_runner: success={result.success}, passed={result.test_report['passed']}")

    rc = RegistryClientAdapter()
    assert rc.health_check() is True
    assert rc.check_exists("test-skill", "0.1.0") is False
    pub = rc.publish({"skill_id": "test-skill", "version": "0.1.0"})
    assert pub["status"] == "published"
    print(f"  registry_client: exists=False, publish={pub['status']}")

    print("  ADAPTERS: OK")

if __name__ == "__main__":
    print("=== Path A Chain ===")
    test_path_a_chain()
    print("\n=== Adapters ===")
    test_adapters()
    print("\n=== ALL WAVE 7 TESTS PASSED ===")
