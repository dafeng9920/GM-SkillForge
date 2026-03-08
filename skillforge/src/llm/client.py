"""
LLM Client - Unified LLM Adapter for SkillForge L4 API.

Provides a unified interface for generating 10-dimensional cognition assessments
using various LLM providers (OpenAI, OpenAI-compatible APIs).

Environment Variables:
    LLM_PROVIDER: Provider name (e.g., "openai", "azure")
    LLM_MODEL: Model identifier (e.g., "gpt-4o-mini", "gpt-4")
    OPENAI_API_KEY: API key for OpenAI or compatible services
    OPENAI_BASE_URL: Optional base URL for OpenAI-compatible APIs

Compatible Aliases:
    CLOUD_LLM_API_KEY -> OPENAI_API_KEY
    CLOUD_LLM_BASE_URL -> OPENAI_BASE_URL
    CLOUD_LLM_MODEL -> LLM_MODEL
"""
from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional


# ============================================================================
# Custom Exceptions
# ============================================================================

class LLMConfigError(Exception):
    """Raised when LLM configuration is missing or invalid."""

    def __init__(self, message: str, missing_keys: Optional[list[str]] = None):
        self.message = message
        self.missing_keys = missing_keys or []
        super().__init__(self.message)


class LLMCallError(Exception):
    """Raised when LLM API call fails."""

    def __init__(self, message: str, provider: Optional[str] = None,
                 original_error: Optional[Exception] = None):
        self.message = message
        self.provider = provider
        self.original_error = original_error
        super().__init__(self.message)


# ============================================================================
# Configuration Loading
# ============================================================================

def _load_dotenv_if_exists() -> None:
    """
    Load .env file if it exists and we're in a development environment.

    This supports two startup modes:
    A. Process-injected environment variables (production) - takes precedence
    B. Local .env file (development) - loaded as fallback
    """
    # Check if dotenv is available
    try:
        from dotenv import load_dotenv
    except ImportError:
        # dotenv not installed, skip .env loading
        return

    # Find .env file - check multiple locations
    possible_paths = [
        # skillforge/.env
        os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"),
        # project root .env
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env"),
    ]

    for env_path in possible_paths:
        if os.path.exists(env_path):
            # override=False means process env vars take precedence
            load_dotenv(env_path, override=False)
            break


def load_llm_config() -> dict[str, Any]:
    """
    Load LLM configuration from environment variables.

    Returns:
        dict with keys: provider, model, api_key, base_url (optional)

    Raises:
        LLMConfigError: If required configuration is missing
    """
    # Attempt to load .env file (only if not already loaded)
    _load_dotenv_if_exists()

    missing_keys = []

    # Provider configuration
    provider = os.getenv("LLM_PROVIDER")
    if not provider:
        # Default to openai if not specified
        provider = "openai"

    # Model configuration (with alias fallback)
    model = os.getenv("LLM_MODEL") or os.getenv("CLOUD_LLM_MODEL")
    if not model:
        missing_keys.append("LLM_MODEL")
        model = "gpt-4o-mini"  # Default fallback

    # API key (with alias fallback)
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("CLOUD_LLM_API_KEY")
    if not api_key:
        missing_keys.append("OPENAI_API_KEY")

    # Base URL (optional, with alias fallback)
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("CLOUD_LLM_BASE_URL")

    config = {
        "provider": provider,
        "model": model,
        "api_key": api_key,
        "base_url": base_url,
    }

    # Check for missing critical keys
    if "OPENAI_API_KEY" in missing_keys:
        raise LLMConfigError(
            f"LLM configuration incomplete. Missing required environment variable: OPENAI_API_KEY",
            missing_keys=missing_keys
        )

    return config


# ============================================================================
# Prompt Building
# ============================================================================

def build_10d_prompt(user_input: str, context: Optional[dict] = None) -> str:
    """
    Build the prompt for 10-dimensional cognition assessment.

    Args:
        user_input: The main input text (e.g., commit message, code description)
        context: Optional context information (repo_url, commit_sha, etc.)

    Returns:
        Formatted prompt string for the LLM
    """
    context_str = ""
    if context:
        context_items = []
        if "repo_url" in context:
            context_items.append(f"Repository: {context['repo_url']}")
        if "commit_sha" in context:
            context_items.append(f"Commit: {context['commit_sha']}")
        if "requester_id" in context:
            context_items.append(f"Requester: {context['requester_id']}")
        if context_items:
            context_str = "\n".join(context_items) + "\n\n"

    prompt = f"""You are a governance assessment AI. Analyze the following input and produce a 10-dimensional cognition assessment.

{context_str}INPUT TO ANALYZE:
{user_input}

Respond with a JSON object containing exactly 10 dimensions with this structure:
{{
  "dimensions": [
    {{
      "dim_id": "L1",
      "name": "Fact Extraction",
      "summary": "Brief assessment of fact extraction capability",
      "score": <0-100>,
      "evidence_hint": "Key evidence or reasoning for this score"
    }},
    ... (L2-L10)
  ]
}}

The 10 dimensions are:
L1: Fact Extraction (事实提取) - Ability to extract accurate facts
L2: Concept Abstraction (概念抽象) - Ability to form abstract concepts
L3: Causal Reasoning (因果推理) - Understanding cause-effect relationships
L4: Structural Decomposition (结构解构) - Breaking down complex structures
L5: Risk Perception (风险感知) - Identifying potential risks
L6: Temporal Modeling (时序建模) - Understanding time-based patterns
L7: Cross-Domain Association (跨域关联) - Connecting concepts across domains
L8: Uncertainty Annotation (不确定性标注) - Recognizing and marking uncertainties
L9: Recommendation Feasibility (建议可行性) - Practicality of recommendations
L10: Narrative Coherence (叙事连贯性) - Overall logical consistency

Scoring guidelines:
- 0-40: Poor/Failed
- 41-60: Marginal
- 61-80: Good
- 81-100: Excellent

Provide concise, actionable summaries and evidence hints.
Return ONLY the JSON object, no additional text."""
    return prompt


# ============================================================================
# LLM Response Parsing
# ============================================================================

def _parse_llm_response(response_text: str) -> dict[str, Any]:
    """
    Parse LLM response text into structured 10D result.

    Args:
        response_text: Raw response text from LLM

    Returns:
        Parsed dimensions list

    Raises:
        LLMCallError: If parsing fails
    """
    try:
        # Try to extract JSON from the response
        text = response_text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last line if they're code block markers
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        parsed = json.loads(text)

        if "dimensions" not in parsed:
            raise LLMCallError("LLM response missing 'dimensions' key")

        dimensions = parsed["dimensions"]

        if not isinstance(dimensions, list) or len(dimensions) != 10:
            raise LLMCallError(f"Expected 10 dimensions, got {len(dimensions) if isinstance(dimensions, list) else 'non-list'}")

        # Validate and normalize each dimension
        normalized = []
        for i, dim in enumerate(dimensions):
            normalized.append({
                "dim_id": dim.get("dim_id", f"L{i+1}"),
                "name": dim.get("name", f"Dimension {i+1}"),
                "summary": dim.get("summary", ""),
                "score": min(100, max(0, int(dim.get("score", 50)))),
                "evidence_hint": dim.get("evidence_hint", ""),
            })

        return normalized

    except json.JSONDecodeError as e:
        raise LLMCallError(f"Failed to parse LLM response as JSON: {str(e)}")


# ============================================================================
# Mock LLM Client (for testing)
# ============================================================================

def _mock_generate_10d(user_input: str, context: Optional[dict] = None) -> dict[str, Any]:
    """
    Generate mock 10D result for testing purposes.

    This is used when LLM_PROVIDER=mock or when testing without real API calls.
    """
    # Generate deterministic but varied scores based on input hash
    input_hash = hash(user_input) % 100

    dim_labels = [
        ("L1", "Fact Extraction", "事实提取"),
        ("L2", "Concept Abstraction", "概念抽象"),
        ("L3", "Causal Reasoning", "因果推理"),
        ("L4", "Structural Decomposition", "结构解构"),
        ("L5", "Risk Perception", "风险感知"),
        ("L6", "Temporal Modeling", "时序建模"),
        ("L7", "Cross-Domain Association", "跨域关联"),
        ("L8", "Uncertainty Annotation", "不确定性标注"),
        ("L9", "Recommendation Feasibility", "建议可行性"),
        ("L10", "Narrative Coherence", "叙事连贯性"),
    ]

    dimensions = []
    for i, (dim_id, name_en, name_cn) in enumerate(dim_labels):
        # Generate varied but reasonable scores
        base_score = 70 + (input_hash + i * 7) % 25
        score = min(100, max(50, base_score))

        dimensions.append({
            "dim_id": dim_id,
            "name": name_en,
            "summary": f"Mock assessment for {name_en} ({name_cn})",
            "score": score,
            "evidence_hint": f"Mock evidence hint for {dim_id} based on input analysis",
        })

    return dimensions


# ============================================================================
# Main Generation Function
# ============================================================================

def generate_10d(user_input: str, context: Optional[dict] = None,
                 use_mock: bool = False) -> dict[str, Any]:
    """
    Generate a 10-dimensional cognition assessment using LLM.

    Args:
        user_input: The main input text to analyze
        context: Optional context (repo_url, commit_sha, requester_id, etc.)
        use_mock: If True, use mock response instead of real LLM call

    Returns:
        dict with structure:
        {
            "dimensions": [
                {
                    "dim_id": "L1",
                    "name": "...",
                    "summary": "...",
                    "score": 0-100,
                    "evidence_hint": "..."
                },
                ... (10 dimensions total)
            ],
            "model": "...",
            "provider": "...",
            "latency_ms": ...,
            "trace_id": "..."
        }

    Raises:
        LLMConfigError: If LLM configuration is missing
        LLMCallError: If LLM API call fails
    """
    trace_id = f"LLM-{int(time.time())}-{uuid.uuid4().hex[:8].upper()}"

    # If explicit mock requested, skip config check entirely
    if use_mock:
        start_time = time.time()
        dimensions = _mock_generate_10d(user_input, context)
        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "dimensions": dimensions,
            "model": "mock",
            "provider": "mock",
            "latency_ms": latency_ms,
            "trace_id": trace_id,
        }

    # Load configuration
    try:
        config = load_llm_config()
    except LLMConfigError:
        raise

    provider = config["provider"]
    model = config["model"]

    # Use mock if provider is "mock"
    if provider.lower() == "mock":
        start_time = time.time()
        dimensions = _mock_generate_10d(user_input, context)
        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "dimensions": dimensions,
            "model": "mock",
            "provider": "mock",
            "latency_ms": latency_ms,
            "trace_id": trace_id,
        }

    # Build prompt
    prompt = build_10d_prompt(user_input, context)

    # Call LLM API
    start_time = time.time()

    try:
        import openai

        client_kwargs = {"api_key": config["api_key"]}
        if config["base_url"]:
            client_kwargs["base_url"] = config["base_url"]

        client = openai.OpenAI(**client_kwargs)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a governance assessment AI that responds only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        response_text = response.choices[0].message.content
        latency_ms = int((time.time() - start_time) * 1000)

        # Parse response
        dimensions = _parse_llm_response(response_text)

        return {
            "dimensions": dimensions,
            "model": model,
            "provider": provider,
            "latency_ms": latency_ms,
            "trace_id": trace_id,
        }

    except LLMCallError:
        raise
    except Exception as e:
        raise LLMCallError(
            f"LLM API call failed: {str(e)}",
            provider=provider,
            original_error=e
        )


# ============================================================================
# Configuration Check Utility
# ============================================================================

def check_llm_config() -> dict[str, Any]:
    """
    Check if LLM configuration is available.

    Returns:
        dict with keys: configured (bool), provider, model, has_api_key
    """
    try:
        config = load_llm_config()
        return {
            "configured": True,
            "provider": config["provider"],
            "model": config["model"],
            "has_api_key": bool(config["api_key"]),
        }
    except LLMConfigError as e:
        return {
            "configured": False,
            "provider": None,
            "model": None,
            "has_api_key": False,
            "missing_keys": e.missing_keys,
        }
