"""
L4 LLM Client Tests - Unit tests for the LLM integration.

Tests cover:
- Configuration loading and missing config errors
- Prompt building
- Mock response generation
- LLM response parsing
- Error handling (fail-closed)
"""
import os
import sys
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ============================================================================
# Test Fixtures
# ============================================================================

MOCK_LLM_CONFIG = {
    "LLM_PROVIDER": "mock",
    "LLM_MODEL": "mock-model",
    "OPENAI_API_KEY": "test-mock-key",
}

VALID_LLM_CONFIG = {
    "LLM_PROVIDER": "openai",
    "LLM_MODEL": "gpt-4o-mini",
    "OPENAI_API_KEY": "sk-test-key-12345",
}


def set_env_vars(config: dict) -> None:
    """Set environment variables from config dict."""
    for key, value in config.items():
        os.environ[key] = value


def clear_env_vars(keys: list) -> None:
    """Clear specified environment variables."""
    for key in keys:
        os.environ.pop(key, None)


# ============================================================================
# Test Cases
# ============================================================================

class TestLLMConfig(unittest.TestCase):
    """Tests for LLM configuration loading."""

    def setUp(self):
        """Clear relevant env vars before each test."""
        self.env_keys = ["LLM_PROVIDER", "LLM_MODEL", "OPENAI_API_KEY",
                         "CLOUD_LLM_MODEL", "CLOUD_LLM_API_KEY", "OPENAI_BASE_URL",
                         "CLOUD_LLM_BASE_URL"]
        clear_env_vars(self.env_keys)

    def tearDown(self):
        """Clean up env vars after each test."""
        clear_env_vars(self.env_keys)

    def test_config_missing_api_key_raises_error(self):
        """Missing OPENAI_API_KEY should raise LLMConfigError."""
        from llm.client import load_llm_config, LLMConfigError

        # Set provider and model but not API key
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ["LLM_MODEL"] = "gpt-4o-mini"

        with self.assertRaises(LLMConfigError) as ctx:
            load_llm_config()

        self.assertIn("OPENAI_API_KEY", ctx.exception.message)
        self.assertIn("OPENAI_API_KEY", ctx.exception.missing_keys)

    def test_config_with_all_required_keys(self):
        """Complete config should load successfully."""
        from llm.client import load_llm_config

        set_env_vars(VALID_LLM_CONFIG)
        config = load_llm_config()

        self.assertEqual(config["provider"], "openai")
        self.assertEqual(config["model"], "gpt-4o-mini")
        self.assertEqual(config["api_key"], "sk-test-key-12345")

    def test_config_uses_cloud_llm_aliases(self):
        """Config should fall back to CLOUD_LLM_* aliases."""
        from llm.client import load_llm_config

        os.environ["CLOUD_LLM_MODEL"] = "gpt-4"
        os.environ["CLOUD_LLM_API_KEY"] = "sk-alias-key"
        os.environ["CLOUD_LLM_BASE_URL"] = "https://custom.api/v1"

        config = load_llm_config()

        self.assertEqual(config["model"], "gpt-4")
        self.assertEqual(config["api_key"], "sk-alias-key")
        self.assertEqual(config["base_url"], "https://custom.api/v1")

    def test_config_defaults_to_openai_provider(self):
        """Provider should default to 'openai' if not specified."""
        from llm.client import load_llm_config

        os.environ["OPENAI_API_KEY"] = "sk-test-key"

        config = load_llm_config()

        self.assertEqual(config["provider"], "openai")


class TestPromptBuilding(unittest.TestCase):
    """Tests for prompt construction."""

    def test_build_10d_prompt_includes_input(self):
        """Prompt should include the user input."""
        from llm.client import build_10d_prompt

        user_input = "Test commit message"
        prompt = build_10d_prompt(user_input)

        self.assertIn("Test commit message", prompt)
        self.assertIn("10-dimensional", prompt)

    def test_build_10d_prompt_includes_context(self):
        """Prompt should include context information."""
        from llm.client import build_10d_prompt

        user_input = "Test input"
        context = {
            "repo_url": "https://github.com/test/repo",
            "commit_sha": "abc123",
            "requester_id": "user-001",
        }
        prompt = build_10d_prompt(user_input, context)

        self.assertIn("https://github.com/test/repo", prompt)
        self.assertIn("abc123", prompt)
        self.assertIn("user-001", prompt)

    def test_build_10d_prompt_includes_all_dimensions(self):
        """Prompt should mention all 10 dimensions."""
        from llm.client import build_10d_prompt

        prompt = build_10d_prompt("test")

        dimensions = ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10"]
        for dim in dimensions:
            self.assertIn(dim, prompt)


class TestMockGeneration(unittest.TestCase):
    """Tests for mock response generation."""

    def setUp(self):
        """Set up mock config."""
        self.env_keys = ["LLM_PROVIDER", "LLM_MODEL", "OPENAI_API_KEY"]
        clear_env_vars(self.env_keys)
        set_env_vars(MOCK_LLM_CONFIG)

    def tearDown(self):
        """Clean up env vars."""
        clear_env_vars(self.env_keys)

    def test_mock_generate_returns_10_dimensions(self):
        """Mock generation should return exactly 10 dimensions."""
        from llm.client import generate_10d

        result = generate_10d("test input", use_mock=True)

        self.assertIn("dimensions", result)
        self.assertEqual(len(result["dimensions"]), 10)

    def test_mock_generate_dimensions_have_required_fields(self):
        """Each dimension should have required fields."""
        from llm.client import generate_10d

        result = generate_10d("test input", use_mock=True)

        for dim in result["dimensions"]:
            self.assertIn("dim_id", dim)
            self.assertIn("name", dim)
            self.assertIn("summary", dim)
            self.assertIn("score", dim)
            self.assertIn("evidence_hint", dim)

    def test_mock_generate_returns_metadata(self):
        """Mock generation should return metadata."""
        from llm.client import generate_10d

        result = generate_10d("test input", use_mock=True)

        self.assertIn("model", result)
        self.assertIn("provider", result)
        self.assertIn("latency_ms", result)
        self.assertIn("trace_id", result)

    def test_mock_generate_scores_in_valid_range(self):
        """Scores should be between 0 and 100."""
        from llm.client import generate_10d

        result = generate_10d("test input", use_mock=True)

        for dim in result["dimensions"]:
            self.assertGreaterEqual(dim["score"], 0)
            self.assertLessEqual(dim["score"], 100)

    def test_mock_provider_uses_mock_automatically(self):
        """Setting LLM_PROVIDER=mock should use mock generation."""
        from llm.client import generate_10d

        # LLM_PROVIDER is set to "mock" in setUp
        result = generate_10d("test input", use_mock=False)

        self.assertEqual(result["provider"], "mock")
        self.assertEqual(result["model"], "mock")


class TestResponseParsing(unittest.TestCase):
    """Tests for LLM response parsing."""

    def test_parse_valid_json_response(self):
        """Valid JSON response should parse correctly."""
        from llm.client import _parse_llm_response

        response = '''{
            "dimensions": [
                {"dim_id": "L1", "name": "Fact Extraction", "summary": "Good", "score": 85, "evidence_hint": "test"},
                {"dim_id": "L2", "name": "Concept Abstraction", "summary": "Good", "score": 80, "evidence_hint": "test"},
                {"dim_id": "L3", "name": "Causal Reasoning", "summary": "Good", "score": 75, "evidence_hint": "test"},
                {"dim_id": "L4", "name": "Structural Decomposition", "summary": "Good", "score": 70, "evidence_hint": "test"},
                {"dim_id": "L5", "name": "Risk Perception", "summary": "Good", "score": 88, "evidence_hint": "test"},
                {"dim_id": "L6", "name": "Temporal Modeling", "summary": "Good", "score": 65, "evidence_hint": "test"},
                {"dim_id": "L7", "name": "Cross-Domain Association", "summary": "Good", "score": 72, "evidence_hint": "test"},
                {"dim_id": "L8", "name": "Uncertainty Annotation", "summary": "Good", "score": 78, "evidence_hint": "test"},
                {"dim_id": "L9", "name": "Recommendation Feasibility", "summary": "Good", "score": 82, "evidence_hint": "test"},
                {"dim_id": "L10", "name": "Narrative Coherence", "summary": "Good", "score": 90, "evidence_hint": "test"}
            ]
        }'''

        dimensions = _parse_llm_response(response)

        self.assertEqual(len(dimensions), 10)
        self.assertEqual(dimensions[0]["dim_id"], "L1")
        self.assertEqual(dimensions[0]["score"], 85)

    def test_parse_response_with_markdown_code_block(self):
        """Response wrapped in markdown code block should parse."""
        from llm.client import _parse_llm_response, LLMCallError

        response = '''```json
        {
            "dimensions": [
                {"dim_id": "L1", "name": "D1", "score": 50, "evidence_hint": "e1"},
                {"dim_id": "L2", "name": "D2", "score": 50, "evidence_hint": "e2"},
                {"dim_id": "L3", "name": "D3", "score": 50, "evidence_hint": "e3"},
                {"dim_id": "L4", "name": "D4", "score": 50, "evidence_hint": "e4"},
                {"dim_id": "L5", "name": "D5", "score": 50, "evidence_hint": "e5"},
                {"dim_id": "L6", "name": "D6", "score": 50, "evidence_hint": "e6"},
                {"dim_id": "L7", "name": "D7", "score": 50, "evidence_hint": "e7"},
                {"dim_id": "L8", "name": "D8", "score": 50, "evidence_hint": "e8"},
                {"dim_id": "L9", "name": "D9", "score": 50, "evidence_hint": "e9"},
                {"dim_id": "L10", "name": "D10", "score": 50, "evidence_hint": "e10"}
            ]
        }
        ```'''

        dimensions = _parse_llm_response(response)
        self.assertEqual(len(dimensions), 10)

    def test_parse_invalid_json_raises_error(self):
        """Invalid JSON should raise LLMCallError."""
        from llm.client import _parse_llm_response, LLMCallError

        response = "This is not valid JSON"

        with self.assertRaises(LLMCallError):
            _parse_llm_response(response)

    def test_parse_missing_dimensions_raises_error(self):
        """Response without dimensions key should raise LLMCallError."""
        from llm.client import _parse_llm_response, LLMCallError

        response = '{"other_key": []}'

        with self.assertRaises(LLMCallError):
            _parse_llm_response(response)

    def test_parse_wrong_dimension_count_raises_error(self):
        """Response with wrong number of dimensions should raise LLMCallError."""
        from llm.client import _parse_llm_response, LLMCallError

        response = '{"dimensions": [{"dim_id": "L1", "name": "Only one", "score": 50}]}'

        with self.assertRaises(LLMCallError):
            _parse_llm_response(response)


class TestCheckLLMConfig(unittest.TestCase):
    """Tests for configuration checking utility."""

    def setUp(self):
        """Clear env vars."""
        self.env_keys = ["LLM_PROVIDER", "LLM_MODEL", "OPENAI_API_KEY"]
        clear_env_vars(self.env_keys)

    def tearDown(self):
        """Clean up."""
        clear_env_vars(self.env_keys)

    def test_check_config_when_missing(self):
        """check_llm_config should report missing config."""
        from llm.client import check_llm_config

        result = check_llm_config()

        self.assertFalse(result["configured"])
        self.assertIn("OPENAI_API_KEY", result["missing_keys"])

    def test_check_config_when_present(self):
        """check_llm_config should report valid config."""
        from llm.client import check_llm_config

        set_env_vars(VALID_LLM_CONFIG)
        result = check_llm_config()

        self.assertTrue(result["configured"])
        self.assertTrue(result["has_api_key"])


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
