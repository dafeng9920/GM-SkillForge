"""
NormalizedSkillSpec - Unified skill specification for SkillForge audit pipeline.

This module defines the T2 deliverable: NormalizedSkillSpec.
It provides a standardized representation of skill metadata, dependencies,
and contracts extracted from skill directory structures.

Usage:
    from skillforge.src.contracts.skill_spec import (
        NormalizedSkillSpec,
        SkillParser,
        ParseResult,
        SkillSpecError
    )

    parser = SkillParser()
    result = parser.parse_skill("skillforge/src/skills/quant/")

    if result.is_valid():
        spec = result.spec
        print(f"Skill: {spec.skill_name} v{spec.version}")
        print(f"Dependencies: {spec.dependencies}")
    else:
        print(f"Parse failed: {result.errors}")

Evidence paths:
    - run/<run_id>/normalized_skill_spec.json
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional


# ============================================================================
# Error Codes (T2)
# ============================================================================
class SkillSpecErrorCode:
    """Standard error codes for skill parsing and normalization."""

    # Directory structure errors
    E201_SKILL_DIR_NOT_FOUND = "E201_SKILL_DIR_NOT_FOUND"
    E202_NOT_A_DIRECTORY = "E202_NOT_A_DIRECTORY"
    E203_SKILL_PY_MISSING = "E203_SKILL_PY_MISSING"
    E204_INIT_PY_MISSING = "E204_INIT_PY_MISSING"

    # Manifest errors
    E205_MANIFEST_FILE_MISSING = "E205_MANIFEST_FILE_MISSING"
    E206_MANIFEST_PARSE_FAILED = "E206_MANIFEST_PARSE_FAILED"
    E207_MANIFEST_INVALID_JSON = "E207_MANIFEST_INVALID_JSON"

    # Metadata errors
    E208_SKILL_NAME_MISSING = "E208_SKILL_NAME_MISSING"
    E209_VERSION_MISSING = "E209_VERSION_MISSING"
    E210_VERSION_INVALID_FORMAT = "E210_VERSION_INVALID_FORMAT"

    # Contract errors
    E211_INPUT_CONTRACT_MISSING = "E211_INPUT_CONTRACT_MISSING"
    E212_OUTPUT_CONTRACT_MISSING = "E212_OUTPUT_CONTRACT_MISSING"
    E213_CONTRACT_INVALID_SCHEMA = "E213_CONTRACT_INVALID_SCHEMA"


# ============================================================================
# Exceptions
# ============================================================================
@dataclass(frozen=True)
class SkillSpecError:
    """Structured error for skill parsing failures."""

    code: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "code": self.code,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
        }


class SkillSpecException(Exception):
    """Exception raised when skill parsing fails."""

    def __init__(self, errors: list[SkillSpecError]):
        self.errors = errors
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        return "; ".join([f"{e.code}: {e.message}" for e in self.errors])


# ============================================================================
# Data Classes
# ============================================================================
@dataclass(frozen=True)
class Dependency:
    """A single dependency extracted from skill."""

    name: str
    version: Optional[str] = None
    source: str = "unknown"  # "import", "requirements.txt", "manifest", etc.

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "source": self.source,
        }


@dataclass(frozen=True)
class Contract:
    """Input or output contract for a skill."""

    schema_type: str  # "object", "array", "string", etc.
    properties: dict[str, Any]  # For object types
    required: list[str]
    description: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "schema_type": self.schema_type,
            "properties": self.properties,
            "required": self.required,
            "description": self.description,
        }


@dataclass(frozen=True)
class ManifestSnapshot:
    """Snapshot of skill manifest file."""

    exists: bool
    content_hash: Optional[str] = None
    raw_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "exists": self.exists,
            "content_hash": self.content_hash,
            "raw_data": self.raw_data,
        }


@dataclass(frozen=True)
class DependencyGraph:
    """Dependency graph for a skill."""

    direct_dependencies: list[Dependency]
    transitive_dependencies: list[Dependency]  # T2 MVP: empty list
    dependency_count: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "direct_dependencies": [d.to_dict() for d in self.direct_dependencies],
            "transitive_dependencies": [d.to_dict() for d in self.transitive_dependencies],
            "dependency_count": self.dependency_count,
        }


@dataclass
class NormalizedSkillSpec:
    """
    Normalized Skill Specification (T2 deliverable).

    This is the unified representation of a skill extracted from
    the repository by the SkillParser.

    Fields follow standardized naming conventions (snake_case).
    """

    # Basic metadata
    skill_id: str  # Auto-generated: skill_name-version-hash
    skill_name: str
    version: str
    description: str

    # Structure
    entry_point: str  # Relative path to main skill file
    skill_dir: str  # Absolute path to skill directory
    file_list: list[str]  # All Python files in skill

    # Dependencies and contracts
    dependencies: DependencyGraph
    input_contract: Contract
    output_contract: Contract

    # Manifest
    manifest_snapshot: ManifestSnapshot

    # Metadata
    capabilities: list[str]  # Derived from dependencies/code analysis
    constraints: list[str]  # Constraints extracted from skill

    # Provenance
    parsed_at: str  # ISO-8601 timestamp
    parser_version: str = "1.0.0-t2"

    def compute_spec_hash(self) -> str:
        """Compute SHA-256 hash of the normalized spec (for deduplication)."""
        canonical = json.dumps(
            {
                "skill_name": self.skill_name,
                "version": self.version,
                "entry_point": self.entry_point,
                "input_contract": self.input_contract.to_dict(),
                "output_contract": self.output_contract.to_dict(),
                "dependencies": self.dependencies.to_dict(),
            },
            sort_keys=True,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "version": self.version,
            "description": self.description,
            "entry_point": self.entry_point,
            "skill_dir": self.skill_dir,
            "file_list": self.file_list,
            "dependencies": self.dependencies.to_dict(),
            "input_contract": self.input_contract.to_dict(),
            "output_contract": self.output_contract.to_dict(),
            "manifest_snapshot": self.manifest_snapshot.to_dict(),
            "capabilities": self.capabilities,
            "constraints": self.constraints,
            "parsed_at": self.parsed_at,
            "parser_version": self.parser_version,
            "spec_hash": self.compute_spec_hash(),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, output_path: str | Path) -> None:
        """Save the normalized spec to a JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write atomically via temp file
        temp_path = output_path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(self.to_json())
            temp_path.replace(output_path)
        except OSError as e:
            raise IOError(f"Failed to save normalized skill spec to {output_path}: {e}")


# ============================================================================
# Parse Result
# ============================================================================
@dataclass
class ParseResult:
    """Result of skill parsing."""

    is_valid: bool
    spec: Optional[NormalizedSkillSpec] = None
    errors: list[SkillSpecError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "spec": self.spec.to_dict() if self.spec else None,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": self.warnings,
        }


# ============================================================================
# Skill Parser
# ============================================================================
class SkillParser:
    """
    Parser for extracting NormalizedSkillSpec from skill directory.

    T2 Scope:
    - Parse Python skill directory structure
    - Extract skill metadata from __init__.py and main module
    - Read manifest.json if present
    - Extract dependencies from import statements
    - Extract input/output contracts from docstrings or type hints
    - Normalize field naming

    T2 Hard Constraints:
    - Only Python skills supported (no multi-language framework)
    - No adjudication logic
    - No owner review logic
    - No runtime execution logic
    """

    PATTERNS = {
        "import_statement": re.compile(r"^import\s+([a-zA-Z_][a-zA-Z0-9_]*)"),
        "from_import": re.compile(r"^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import"),
        "skill_name": re.compile(r'SKILL_NAME\s*=\s*["\']([^"\']+)["\']'),
        "skill_version": re.compile(r'SKILL_VERSION\s*=\s*["\']([^"\']+)["\']'),
        "version_semver": re.compile(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$'),
    }

    def __init__(self, fail_on_missing_manifest: bool = False):
        """
        Initialize parser.

        Args:
            fail_on_missing_manifest: If True, missing manifest.json causes parse failure.
                If False, manifest_snapshot.exists will be False but parse succeeds.
        """
        self.fail_on_missing_manifest = fail_on_missing_manifest

    def parse_skill(self, skill_dir: str | Path) -> ParseResult:
        """
        Parse a skill directory and produce NormalizedSkillSpec.

        Args:
            skill_dir: Path to skill directory (e.g., "skillforge/src/skills/quant/")

        Returns:
            ParseResult with NormalizedSkillSpec if successful, or errors if failed.
        """
        errors: list[SkillSpecError] = []
        warnings: list[str] = []

        # Normalize path
        skill_dir = Path(skill_dir).resolve()

        # Step 1: Validate directory structure
        dir_errors = self._validate_directory(skill_dir)
        if dir_errors:
            return ParseResult(is_valid=False, errors=dir_errors)

        # Step 2: Discover Python files
        file_list = self._discover_python_files(skill_dir)

        # Step 3: Find entry point (main .py file or __init__.py)
        entry_point = self._find_entry_point(skill_dir, file_list)
        if entry_point is None:
            errors.append(
                SkillSpecError(
                    code=SkillSpecErrorCode.E203_SKILL_PY_MISSING,
                    message=f"No entry point found in {skill_dir}",
                    file_path=str(skill_dir),
                )
            )
            return ParseResult(is_valid=False, errors=errors)

        # Step 4: Extract metadata from entry point
        metadata = self._extract_metadata(skill_dir / entry_point)
        if not metadata.get("skill_name"):
            errors.append(
                SkillSpecError(
                    code=SkillSpecErrorCode.E208_SKILL_NAME_MISSING,
                    message="SKILL_NAME not found in entry point",
                    file_path=str(skill_dir / entry_point),
                )
            )
        if not metadata.get("version"):
            errors.append(
                SkillSpecError(
                    code=SkillSpecErrorCode.E209_VERSION_MISSING,
                    message="SKILL_VERSION not found in entry point",
                    file_path=str(skill_dir / entry_point),
                )
            )

        if any(e.code.startswith("E20") for e in errors):
            return ParseResult(is_valid=False, errors=errors)

        # Step 5: Read manifest if present
        manifest_snapshot = self._read_manifest(skill_dir)
        if not manifest_snapshot.exists and self.fail_on_missing_manifest:
            errors.append(
                SkillSpecError(
                    code=SkillSpecErrorCode.E205_MANIFEST_FILE_MISSING,
                    message=f"manifest.json not found in {skill_dir}",
                    file_path=str(skill_dir / "manifest.json"),
                )
            )
            return ParseResult(is_valid=False, errors=errors)

        # Step 6: Extract dependencies
        dependencies = self._extract_dependencies(skill_dir, file_list)

        # Step 7: Extract input/output contracts
        contract_result = self._extract_contracts(skill_dir, entry_point, metadata)
        input_contract = contract_result["input"]
        output_contract = contract_result["output"]
        manifest_capabilities = contract_result.get("capabilities", [])
        manifest_constraints = contract_result.get("constraints", [])
        if contract_result.get("errors"):
            errors.extend(contract_result["errors"])

        # Step 8: Generate skill_id
        spec_hash_input = f"{metadata['skill_name']}-{metadata['version']}-{entry_point}"
        skill_id = f"{metadata['skill_name']}-{metadata['version']}-{hashlib.sha256(spec_hash_input.encode()).hexdigest()[:8]}"

        # Step 9: Build NormalizedSkillSpec
        spec = NormalizedSkillSpec(
            skill_id=skill_id,
            skill_name=metadata["skill_name"],
            version=metadata["version"],
            description=metadata.get("description", ""),
            entry_point=entry_point,
            skill_dir=str(skill_dir),
            file_list=file_list,
            dependencies=dependencies,
            input_contract=input_contract,
            output_contract=output_contract,
            manifest_snapshot=manifest_snapshot,
            capabilities=manifest_capabilities,
            constraints=manifest_constraints,
            parsed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        # Step 10: Fail on critical contract errors
        critical_errors = [e for e in errors if e.code in [
            SkillSpecErrorCode.E211_INPUT_CONTRACT_MISSING,
            SkillSpecErrorCode.E212_OUTPUT_CONTRACT_MISSING,
        ]]
        if critical_errors:
            return ParseResult(is_valid=False, errors=errors)

        return ParseResult(is_valid=True, spec=spec, errors=errors, warnings=warnings)

    # ========================================================================
    # Private Methods
    # ========================================================================

    def _validate_directory(self, skill_dir: Path) -> list[SkillSpecError]:
        """Validate that skill_dir is a valid directory."""
        if not skill_dir.exists():
            return [
                SkillSpecError(
                    code=SkillSpecErrorCode.E201_SKILL_DIR_NOT_FOUND,
                    message=f"Skill directory not found: {skill_dir}",
                    file_path=str(skill_dir),
                )
            ]
        if not skill_dir.is_dir():
            return [
                SkillSpecError(
                    code=SkillSpecErrorCode.E202_NOT_A_DIRECTORY,
                    message=f"Path is not a directory: {skill_dir}",
                    file_path=str(skill_dir),
                )
            ]
        return []

    def _discover_python_files(self, skill_dir: Path) -> list[str]:
        """Discover all Python files in skill directory."""
        files = []
        for py_file in skill_dir.rglob("*.py"):
            # Get relative path from skill_dir
            rel_path = py_file.relative_to(skill_dir)
            files.append(str(rel_path))
        return sorted(files)

    def _find_entry_point(self, skill_dir: Path, file_list: list[str]) -> Optional[str]:
        """Find the main entry point for the skill."""
        # Priority 1: Look for files matching skill name pattern
        for f in file_list:
            if f.endswith("_skill.py"):
                return f

        # Priority 2: Look for execute.py, run.py, main.py
        for name in ["execute.py", "run.py", "main.py", "handler.py"]:
            if name in file_list:
                return name

        # Priority 3: Look for any .py file that has SKILL_NAME
        for f in file_list:
            file_path = skill_dir / f
            try:
                with open(file_path, "r", encoding="utf-8") as fp:
                    content = fp.read(2000)  # Read first 2000 chars
                    if "SKILL_NAME" in content:
                        return f
            except OSError:
                continue

        # Priority 4: Use __init__.py if it exists
        if "__init__.py" in file_list:
            return "__init__.py"

        # Priority 5: First .py file
        if file_list:
            return file_list[0]

        return None

    def _extract_metadata(self, entry_point_path: Path) -> dict[str, Any]:
        """Extract metadata from skill entry point file."""
        metadata = {
            "skill_name": None,
            "version": None,
            "description": "",
            "capabilities": [],
            "constraints": [],
        }

        try:
            with open(entry_point_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract SKILL_NAME
            name_match = self.PATTERNS["skill_name"].search(content)
            if name_match:
                metadata["skill_name"] = name_match.group(1)

            # Extract SKILL_VERSION
            version_match = self.PATTERNS["skill_version"].search(content)
            if version_match:
                version = version_match.group(1)
                if self.PATTERNS["version_semver"].match(version):
                    metadata["version"] = version

            # Extract docstring as description
            lines = content.split("\n")
            in_docstring = False
            docstring_lines = []
            for line in lines:
                stripped = line.strip()
                if '"""' in stripped or "'''" in stripped:
                    if in_docstring:
                        break
                    in_docstring = True
                    # Remove the quotes and continue
                    cleaned = stripped.replace('"""', "").replace("'''", "").strip()
                    if cleaned:
                        docstring_lines.append(cleaned)
                    continue
                if in_docstring:
                    docstring_lines.append(stripped)
            if docstring_lines and not metadata.get("description"):
                metadata["description"] = " ".join(docstring_lines[:3])  # First 3 lines

        except OSError as e:
            pass  # Metadata will be incomplete, handled by caller

        return metadata

    def _read_manifest(self, skill_dir: Path) -> ManifestSnapshot:
        """Read manifest.json if present."""
        manifest_path = skill_dir / "manifest.json"

        if not manifest_path.exists():
            return ManifestSnapshot(exists=False)

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()

            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            raw_data = json.loads(content)

            return ManifestSnapshot(
                exists=True,
                content_hash=content_hash,
                raw_data=raw_data,
            )
        except json.JSONDecodeError:
            return ManifestSnapshot(
                exists=True,
                content_hash=None,
                raw_data={"_parse_error": "Invalid JSON"},
            )
        except OSError:
            return ManifestSnapshot(exists=False)

    def _extract_dependencies(
        self, skill_dir: Path, file_list: list[str]
    ) -> DependencyGraph:
        """Extract dependencies from Python files."""
        dependencies: list[Dependency] = []

        for rel_path in file_list:
            file_path = skill_dir / rel_path
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()

                        # Skip comments and empty lines
                        if not line or line.startswith("#"):
                            continue

                        # Match "import xxx" or "from xxx import"
                        import_match = self.PATTERNS["import_statement"].match(line)
                        from_match = self.PATTERNS["from_import"].match(line)

                        if import_match:
                            dep_name = import_match.group(1)
                            # Skip stdlib and local imports
                            if not self._is_stdlib(dep_name) and not dep_name.startswith("skills."):
                                dependencies.append(
                                    Dependency(name=dep_name, source="import")
                                )
                        elif from_match:
                            dep_name = from_match.group(1)
                            # Skip stdlib and local imports
                            if not self._is_stdlib(dep_name) and not dep_name.startswith("skills."):
                                dependencies.append(
                                    Dependency(name=dep_name, source="from_import")
                                )

            except OSError:
                continue

        # Deduplicate
        seen = {}
        for dep in dependencies:
            if dep.name not in seen:
                seen[dep.name] = dep

        unique_deps = list(seen.values())

        return DependencyGraph(
            direct_dependencies=unique_deps,
            transitive_dependencies=[],  # T2 MVP
            dependency_count=len(unique_deps),
        )

    def _is_stdlib(self, module_name: str) -> bool:
        """Check if module is Python standard library."""
        stdlib_modules = {
            "os", "sys", "re", "json", "datetime", "pathlib", "typing",
            "dataclasses", "hashlib", "time", "logging", "collections",
            "itertools", "functools", "copy", "enum", "uuid", "random",
            "math", "io", "textwrap", "argparse", "subprocess", "tempfile",
            "inspect", "importlib", "warnings", "contextlib", "abc",
        }
        base_name = module_name.split(".")[0]
        return base_name in stdlib_modules

    def _extract_contracts(
        self, skill_dir: Path, entry_point: str, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract input/output contracts from skill."""
        errors: list[SkillSpecError] = []

        # Default contracts (minimal)
        default_input = Contract(
            schema_type="object",
            properties={},
            required=[],
            description="No input contract defined",
        )

        default_output = Contract(
            schema_type="object",
            properties={
                "result": {"type": "string", "description": "Operation result"},
            },
            required=["result"],
            description="Default output contract",
        )

        # Try to extract from manifest
        manifest = self._read_manifest(skill_dir)
        if manifest.exists and manifest.raw_data:
            input_spec = manifest.raw_data.get("input_schema", {})
            output_spec = manifest.raw_data.get("output_schema", {})

            input_contract = self._schema_to_contract(input_spec, "input")
            output_contract = self._schema_to_contract(output_spec, "output")

            # Extract capabilities and constraints from manifest
            capabilities = manifest.raw_data.get("capabilities", [])
            constraints = manifest.raw_data.get("constraints", [])

            return {
                "input": input_contract or default_input,
                "output": output_contract or default_output,
                "capabilities": capabilities,
                "constraints": constraints,
                "errors": [],
            }

        # No manifest: return defaults
        return {
            "input": default_input,
            "output": default_output,
            "capabilities": [],
            "constraints": [],
            "errors": [],
        }

    def _schema_to_contract(self, schema: dict[str, Any], contract_type: str) -> Optional[Contract]:
        """Convert JSON schema to Contract object."""
        if not schema or not isinstance(schema, dict):
            return None

        schema_type = schema.get("type", "object")
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        description = schema.get("description", f"{contract_type} contract")

        return Contract(
            schema_type=schema_type,
            properties=properties,
            required=required,
            description=description,
        )


# ============================================================================
# Convenience Functions
# ============================================================================
def parse_skill_directory(
    skill_dir: str | Path,
    fail_on_missing_manifest: bool = False,
) -> ParseResult:
    """
    Parse a skill directory and produce NormalizedSkillSpec.

    Args:
        skill_dir: Path to skill directory.
        fail_on_missing_manifest: If True, missing manifest.json causes failure.

    Returns:
        ParseResult with NormalizedSkillSpec if successful.

    Raises:
        SkillSpecException: If parsing fails and fail_on_missing_manifest=True.
    """
    parser = SkillParser(fail_on_missing_manifest=fail_on_missing_manifest)
    result = parser.parse_skill(skill_dir)

    if not result.is_valid:
        raise SkillSpecException(result.errors)

    return result


def create_normalized_skill_spec(
    skill_name: str,
    version: str,
    description: str,
    entry_point: str,
    skill_dir: str,
    file_list: list[str],
    dependencies: list[Dependency],
    input_contract: Contract,
    output_contract: Contract,
    capabilities: list[str] | None = None,
    constraints: list[str] | None = None,
) -> NormalizedSkillSpec:
    """
    Create a NormalizedSkillSpec from extracted data.

    Args:
        skill_name: Name of the skill.
        version: Semantic version string.
        description: Human-readable description.
        entry_point: Relative path to main skill file.
        skill_dir: Absolute path to skill directory.
        file_list: List of Python files in skill.
        dependencies: List of direct dependencies.
        input_contract: Input contract.
        output_contract: Output contract.
        capabilities: Optional list of capabilities.
        constraints: Optional list of constraints.

    Returns:
        NormalizedSkillSpec instance.
    """
    spec_hash_input = f"{skill_name}-{version}-{entry_point}"
    skill_id = f"{skill_name}-{version}-{hashlib.sha256(spec_hash_input.encode()).hexdigest()[:8]}"

    return NormalizedSkillSpec(
        skill_id=skill_id,
        skill_name=skill_name,
        version=version,
        description=description,
        entry_point=entry_point,
        skill_dir=skill_dir,
        file_list=file_list,
        dependencies=DependencyGraph(
            direct_dependencies=dependencies,
            transitive_dependencies=[],
            dependency_count=len(dependencies),
        ),
        input_contract=input_contract,
        output_contract=output_contract,
        manifest_snapshot=ManifestSnapshot(exists=False),
        capabilities=capabilities or [],
        constraints=constraints or [],
        parsed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


# ============================================================================
# CLI Entry Point
# ============================================================================
def main():
    """CLI entry point for skill parsing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse skill directory and generate normalized_skill_spec.json"
    )
    parser.add_argument(
        "skill_dir",
        help="Path to skill directory (e.g., skillforge/src/skills/quant/)",
    )
    parser.add_argument(
        "--output",
        default="run/latest/normalized_skill_spec.json",
        help="Output path for normalized_skill_spec.json",
    )
    parser.add_argument(
        "--fail-on-missing-manifest",
        action="store_true",
        help="Fail if manifest.json is not present",
    )
    args = parser.parse_args()

    # Parse skill
    try:
        result = parse_skill_directory(
            args.skill_dir,
            fail_on_missing_manifest=args.fail_on_missing_manifest,
        )
    except SkillSpecException as e:
        print(f"Parse failed: {e}", file=sys.stderr)
        for err in e.errors:
            print(f"  - {err.code}: {err.message}", file=sys.stderr)
        sys.exit(1)

    # Save
    try:
        result.spec.save(args.output)
        print(f"Normalized skill spec saved to: {args.output}")
        print(f"  Skill ID: {result.spec.skill_id}")
        print(f"  Skill Name: {result.spec.skill_name}")
        print(f"  Version: {result.spec.version}")
        print(f"  Dependencies: {result.spec.dependencies.dependency_count}")
        if result.spec.manifest_snapshot.exists:
            print(f"  Manifest Hash: {result.spec.manifest_snapshot.content_hash}")
        else:
            print(f"  Manifest: Not found (snapshot created)")
    except IOError as e:
        print(f"Failed to save: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
