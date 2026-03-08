"""
T3 Test Suite: Incremental Delta Artifacts Enforcement

Tests for:
1. Incremental requests must produce new version or sub-skill
2. Output must contain UpdatedGraph field
3. Output must contain ReleaseManifest field with rollback support
"""
import pytest
from unittest.mock import MagicMock, patch

from skillforge.src.nodes.skill_composer import SkillComposer
from skillforge.src.nodes.pack_publish import PackPublish


class TestIncrementalVersionEnforcement:
    """Test that incremental requests produce version evolution."""

    def setup_method(self):
        self.composer = SkillComposer()

    def test_new_skill_creates_initial_version(self):
        """New skill should start at version 0.1.0."""
        input_data = {
            "intent_parse": {
                "intent": {"goal": "test skill", "domain": "test"},
                "confidence": 0.8
            }
        }

        result = self.composer.execute(input_data)

        assert result["skill_spec"]["version"] == "0.1.0"
        assert result["delta_info"]["is_incremental"] is False
        assert result["delta_info"]["change_type"] == "new"

    def test_incremental_request_bumps_minor_version(self):
        """Incremental request should bump version."""
        input_data = {
            "intent_parse": {
                "intent": {"goal": "updated skill", "domain": "test"},
                "confidence": 0.8
            },
            "existing_skill": {
                "skill_spec": {
                    "name": "skill-test-example",
                    "version": "1.2.3",
                    "description": "Existing skill"
                }
            },
            "change_request": {
                "scope": "minor",
                "description": "Add new feature"
            }
        }

        result = self.composer.execute(input_data)

        assert result["delta_info"]["is_incremental"] is True
        assert result["delta_info"]["base_version"] == "1.2.3"
        assert result["skill_spec"]["version"] == "1.3.0"
        assert result["delta_info"]["change_type"] == "update"

    def test_breaking_change_bumps_major_version(self):
        """Breaking change should bump major version."""
        input_data = {
            "intent_parse": {
                "intent": {"goal": "breaking update", "domain": "test"},
                "confidence": 0.8
            },
            "existing_skill": {
                "skill_spec": {
                    "name": "skill-test-example",
                    "version": "1.2.3",
                    "description": "Existing skill"
                }
            },
            "change_request": {
                "scope": "major",
                "description": "Remove old API - breaking change"
            }
        }

        result = self.composer.execute(input_data)

        assert result["delta_info"]["version_bump"] == "major"
        assert result["skill_spec"]["version"] == "2.0.0"

    def test_divergent_change_creates_subskill(self):
        """Divergent change should create sub-skill."""
        input_data = {
            "intent_parse": {
                "intent": {"goal": "variant feature", "domain": "test"},
                "confidence": 0.8
            },
            "existing_skill": {
                "skill_spec": {
                    "name": "skill-test-example",
                    "version": "1.2.3",
                    "description": "Existing skill"
                }
            },
            "change_request": {
                "scope": "subskill",
                "description": "Fork for alternative use case"
            }
        }

        result = self.composer.execute(input_data)

        assert result["delta_info"]["change_type"] == "subskill"
        assert result["skill_spec"]["parent_skill"] == "skill-test-example"
        assert result["skill_spec"]["name"].startswith("skill-test-example-")

    def test_delta_info_required_in_output(self):
        """delta_info must be present in output."""
        input_data = {
            "intent_parse": {
                "intent": {"goal": "test", "domain": "test"},
                "confidence": 0.8
            }
        }

        result = self.composer.execute(input_data)

        assert "delta_info" in result
        errors = self.composer.validate_output(result)
        assert not any("delta_info" in e for e in errors)


class TestUpdatedGraphField:
    """Test UpdatedGraph field in publish output."""

    def setup_method(self):
        self.publisher = PackPublish()

    def test_updated_graph_present_in_output(self):
        """updated_graph must be present in publish output."""
        input_data = {
            "scaffold_skill_impl": {"impl_path": "/tmp/test"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {},
                "trace_events": []
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "version": "1.0.0",
                    "description": "Test"
                }
            }
        }

        result = self.publisher.execute(input_data)

        assert "updated_graph" in result
        assert isinstance(result["updated_graph"], dict)

    def test_updated_graph_contains_required_fields(self):
        """updated_graph must contain required fields."""
        input_data = {
            "scaffold_skill_impl": {"impl_path": "/tmp/test"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {},
                "trace_events": []
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "version": "1.0.0",
                    "description": "Test"
                }
            }
        }

        result = self.publisher.execute(input_data)
        graph = result["updated_graph"]

        assert "skill_id" in graph
        assert "version" in graph
        assert "graph_hash" in graph
        assert "nodes_added" in graph
        assert "nodes_modified" in graph

    def test_new_skill_adds_node_to_graph(self):
        """New skill should add node to graph."""
        input_data = {
            "scaffold_skill_impl": {"impl_path": "/tmp/test"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {},
                "trace_events": []
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "new-skill",
                    "version": "0.1.0",
                    "description": "New"
                },
                "delta_info": {
                    "is_incremental": False,
                    "change_type": "new"
                }
            }
        }

        result = self.publisher.execute(input_data)
        graph = result["updated_graph"]

        assert graph["change_type"] == "new"
        assert "new-skill" in graph["nodes_added"]
        assert graph["is_incremental"] is False

    def test_update_skill_modifies_graph_node(self):
        """Update should mark node as modified."""
        input_data = {
            "scaffold_skill_impl": {"impl_path": "/tmp/test"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {},
                "trace_events": []
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "existing-skill",
                    "version": "1.1.0",
                    "description": "Updated"
                },
                "delta_info": {
                    "is_incremental": True,
                    "change_type": "update",
                    "base_version": "1.0.0"
                }
            }
        }

        result = self.publisher.execute(input_data)
        graph = result["updated_graph"]

        assert graph["change_type"] == "update"
        assert "existing-skill" in graph["nodes_modified"]
        assert graph["is_incremental"] is True

    def test_subskill_adds_edge_to_parent(self):
        """Sub-skill should add edge to parent."""
        input_data = {
            "scaffold_skill_impl": {"impl_path": "/tmp/test"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {},
                "trace_events": []
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "parent-skill-variant",
                    "version": "0.1.0",
                    "description": "Variant"
                },
                "delta_info": {
                    "is_incremental": True,
                    "change_type": "subskill",
                    "parent_skill": "parent-skill",
                    "base_version": "1.0.0"
                }
            }
        }

        result = self.publisher.execute(input_data)
        graph = result["updated_graph"]

        assert graph["change_type"] == "subskill"
        assert graph["parent_ref"] == "parent-skill"
        assert len(graph["edges_added"]) > 0
        assert graph["edges_added"][0]["from"] == "parent-skill"


class TestReleaseManifestField:
    """Test ReleaseManifest field with rollback support."""

    def setup_method(self):
        self.publisher = PackPublish()

    def test_release_manifest_present_in_output(self):
        """release_manifest must be present in publish output."""
        input_data = {
            "scaffold_skill_impl": {"impl_path": "/tmp/test"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {},
                "trace_events": []
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "version": "1.0.0",
                    "description": "Test"
                }
            }
        }

        result = self.publisher.execute(input_data)

        assert "release_manifest" in result
        assert isinstance(result["release_manifest"], dict)

    def test_release_manifest_contains_required_fields(self):
        """release_manifest must contain required fields."""
        input_data = {
            "scaffold_skill_impl": {"impl_path": "/tmp/test"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {},
                "trace_events": []
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "version": "1.0.0",
                    "description": "Test"
                }
            }
        }

        result = self.publisher.execute(input_data)
        manifest = result["release_manifest"]

        assert "release_id" in manifest
        assert "skill_id" in manifest
        assert "version" in manifest
        assert "change_type" in manifest
        assert "rollback" in manifest
        assert "artifacts" in manifest

    def test_rollback_not_supported_for_new_skill(self):
        """New skill should have rollback.supported = False."""
        input_data = {
            "scaffold_skill_impl": {"impl_path": "/tmp/test"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {},
                "trace_events": []
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "new-skill",
                    "version": "0.1.0",
                    "description": "New"
                },
                "delta_info": {
                    "is_incremental": False,
                    "change_type": "new"
                }
            }
        }

        result = self.publisher.execute(input_data)
        manifest = result["release_manifest"]

        assert manifest["rollback"]["supported"] is False
        assert manifest["rollback"]["rollback_version"] is None

    def test_rollback_supported_for_update(self):
        """Update should have rollback support with previous version."""
        input_data = {
            "scaffold_skill_impl": {"impl_path": "/tmp/test"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {},
                "trace_events": []
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "existing-skill",
                    "version": "1.1.0",
                    "description": "Updated"
                },
                "delta_info": {
                    "is_incremental": True,
                    "change_type": "update",
                    "base_version": "1.0.0"
                }
            }
        }

        result = self.publisher.execute(input_data)
        manifest = result["release_manifest"]

        assert manifest["rollback"]["supported"] is True
        assert manifest["rollback"]["rollback_version"] == "1.0.0"
        assert manifest["previous_version"] == "1.0.0"

    def test_release_manifest_includes_artifact_list(self):
        """release_manifest should include L3 artifact list."""
        input_data = {
            "scaffold_skill_impl": {"impl_path": "/tmp/test"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {},
                "trace_events": []
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "test-skill",
                    "version": "1.0.0",
                    "description": "Test"
                }
            }
        }

        result = self.publisher.execute(input_data)
        manifest = result["release_manifest"]

        assert "manifest.json" in manifest["artifacts"]
        assert "policy_matrix.json" in manifest["artifacts"]
        assert "evidence.jsonl" in manifest["artifacts"]

    def test_delta_summary_included_for_incremental(self):
        """Incremental update should include delta_summary."""
        input_data = {
            "scaffold_skill_impl": {"impl_path": "/tmp/test"},
            "sandbox_test_and_trace": {
                "success": True,
                "test_report": {},
                "trace_events": []
            },
            "skill_compose": {
                "skill_spec": {
                    "name": "existing-skill",
                    "version": "1.1.0",
                    "description": "Updated"
                },
                "delta_info": {
                    "is_incremental": True,
                    "change_type": "update",
                    "base_version": "1.0.0",
                    "version_bump": "minor"
                }
            }
        }

        result = self.publisher.execute(input_data)
        manifest = result["release_manifest"]

        assert "delta_summary" in manifest
        assert manifest["delta_summary"]["base_version"] == "1.0.0"
        assert manifest["delta_summary"]["version_bump"] == "minor"


class TestOutputValidation:
    """Test output validation for T3 requirements."""

    def setup_method(self):
        self.publisher = PackPublish()
        self.composer = SkillComposer()

    def test_publish_output_validates_updated_graph(self):
        """Validation should catch missing updated_graph."""
        output = {
            "schema_version": "1.0.0",
            "audit_pack": {"audit_id": "test", "skill_id": "test", "version": "1.0", "quality_level": "L3"},
            "publish_result": {"status": "published"},
            "release_manifest": {}
        }

        errors = self.publisher.validate_output(output)

        assert any("updated_graph" in e for e in errors)

    def test_publish_output_validates_release_manifest(self):
        """Validation should catch missing release_manifest."""
        output = {
            "schema_version": "1.0.0",
            "audit_pack": {"audit_id": "test", "skill_id": "test", "version": "1.0", "quality_level": "L3"},
            "publish_result": {"status": "published"},
            "updated_graph": {}
        }

        errors = self.publisher.validate_output(output)

        assert any("release_manifest" in e for e in errors)

    def test_composer_output_validates_delta_info(self):
        """Validation should catch missing delta_info."""
        output = {
            "schema_version": "0.1.0",
            "skill_spec": {"name": "test", "version": "1.0", "description": "test"},
            "source": "generated",
            "confidence": 0.8
        }

        errors = self.composer.validate_output(output)

        assert any("delta_info" in e for e in errors)

    def test_updated_graph_validates_required_fields(self):
        """Validation should catch missing required fields in updated_graph."""
        output = {
            "schema_version": "1.0.0",
            "audit_pack": {"audit_id": "test", "skill_id": "test", "version": "1.0", "quality_level": "L3"},
            "publish_result": {"status": "published"},
            "updated_graph": {"skill_id": "test"},  # Missing version, graph_hash
            "release_manifest": {"release_id": "test", "skill_id": "test", "version": "1.0", "change_type": "new", "rollback": {"supported": False}}
        }

        errors = self.publisher.validate_output(output)

        assert any("updated_graph.version" in e or "updated_graph.graph_hash" in e for e in errors)

    def test_release_manifest_validates_rollback_structure(self):
        """Validation should catch missing rollback.supported."""
        output = {
            "schema_version": "1.0.0",
            "audit_pack": {"audit_id": "test", "skill_id": "test", "version": "1.0", "quality_level": "L3"},
            "publish_result": {"status": "published"},
            "updated_graph": {"skill_id": "test", "version": "1.0", "graph_hash": "abc123"},
            "release_manifest": {"release_id": "test", "skill_id": "test", "version": "1.0", "change_type": "new", "rollback": {}}  # Missing supported
        }

        errors = self.publisher.validate_output(output)

        assert any("rollback.supported" in e for e in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
