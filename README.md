# GM-SkillForge (v0) — Repo Refinery & Skill Overlay

This repo builds a **contracts-first refinery** that:
1) scans a GitHub repository (source),
2) identifies gaps (contracts, controls, safety, docs, tests),
3) produces a **GM overlay package** (spec + policies + examples + contract tests),
4) optionally scaffolds an implementation wrapper,
5) outputs an **auditable, bounded, reproducible** skill/tool artifact.

> Goal: Turn “raw repo code” into “production-shaped skill/tool” via stable contracts and gates.

---

## What this project is (Scope)

### We DO
- Create **v0 contracts** (JSON Schemas) for skills/tools
- Define **controls** (limits for time/bytes/rate/domains) and enforce them
- Define **issue catalogs** + consistent `error_code + next_action` semantics
- Ship **examples + contract tests** so CI can prevent drift
- Provide **gap reports** for a target repo: what is missing and how to fix
- Provide a **scaffold** (optional) for a wrapper implementation that conforms to contracts

### We DO NOT (v0)
- Guarantee SEO ranking, legal compliance, or “0.01% error rates”
- Bypass access controls or anti-bot protections
- Rewrite entire upstream projects or claim ownership
- Build a full SaaS platform (website/UI comes later)

---

## The v0 Artifact We Ship

For each refined target (repo or preset), we output a **Refinery Pack**:

- `schemas/`  
  - `<skill>.input.schema.json`  
  - `<skill>.output.schema.json`
- `orchestration/`
  - `profiles/` (default limits & posture)
  - `issue_catalog.yml` (stable issue keys)
  - `examples/<skill>/` (golden examples)
- `contract_tests/` (pytest tests validating schemas/examples)
- `LAUNCH_BLOCKERS.md` (if any)
- `ACCEPTANCE_TESTS_COMMERCIAL_BETA.md` (if enabled for the skill)

This pack is the source-of-truth “mold” that any implementation must fill.

---

## Orchestrator Nodes (Stage 0–7)

These nodes define the production line. Implement them as a callable orchestrator
(or a CLI pipeline) with deterministic outputs.

1. `intake_repo`
   - input: repo URL / local path
   - output: normalized source snapshot + provenance (commit SHA, license)

2. `license_gate`
   - output: allow/deny + required_changes (license risk notes)

3. `repo_scan_fit_score`
   - output: fit score + extraction notes + suspected modules

4. `draft_skill_spec`
   - output: initial spec (schemas, controls, issue keys)

5. `constitution_risk_gate`
   - output: pass/deny + required changes (network posture, unsafe ops bounded)

6. `scaffold_skill_impl` (optional in v0)
   - output: wrapper skeleton matching contracts

7. `sandbox_test_and_trace`
   - output: traces + evidence refs + basic runtime sanity

8. `pack_audit_and_publish`
   - output: refinery pack + audit metadata

---

## v0 Target: Technical SEO Audit Skill

We ship a reference skill first:
- `tech_seo_audit` (canonical / hreflang / structured data)
- contracts + examples + tests are mandatory
- implementation wrapper is optional for v0

Existing files already expected:
- `schemas/tech_seo_audit.input.schema.json`
- `schemas/tech_seo_audit.output.schema.json`
- `orchestration/profiles/toolsite_default_profile.yml`
- `orchestration/issue_catalog.yml`
- `orchestration/examples/tech_seo_audit/*.json`
- `contract_tests/test_tech_seo_audit_contract.py`

---

## Definition of Done (DoD)

A v0 target is DONE when:
- ✅ Schemas validate (Draft 2020-12)
- ✅ Examples validate against output schema
- ✅ Contract tests pass: `pytest -q`
- ✅ Issue keys used in examples exist in `issue_catalog.yml`
- ✅ All FAIL/WARN issues include `evidence_ref + suggested_fix`
- ✅ Controls are required + bounded (max targets/bytes/time/rate/domains)
- ✅ Top-level error envelope is consistent (if used)

---

## How to Run (v0)

```bash
# 1) Install deps
pip install -r requirements.txt

# 2) Run contract tests
pytest -q
```

---

## CI 检查点

### Makefile

```makefile
.PHONY: help install test validate validate-issues ci clean

PYTHON ?= python
PIP ?= pip

help:
	@echo "Targets:"
	@echo "  install          Install Python deps"
	@echo "  test             Run pytest"
	@echo "  validate         Run schema/contract validations (pytest)"
	@echo "  validate-issues  Validate issue_catalog.yml matches examples issue_key usage"
	@echo "  ci               Run all checks (what CI should run)"
	@echo "  clean            Remove caches"

install:
	$(PIP) install -r requirements.txt

test:
	pytest -q

validate: test

validate-issues:
	$(PYTHON) tools/validate_issue_keys.py \
		--catalog orchestration/issue_catalog.yml \
		--examples orchestration/examples

ci: validate-issues test

clean:
	rm -rf .pytest_cache __pycache__ */__pycache__ */*/__pycache__
```

CI 跑 `make ci` 就行：会先校验 issue_key 一致性，再跑 pytest。

### tools/validate_issue_keys.py

```python
#!/usr/bin/env python3
"""
Validate that all issue_key used in orchestration/examples/**.json
exist in orchestration/issue_catalog.yml, and optionally warn on unused catalog keys.

Exit codes:
  0 = OK
  2 = Missing keys in catalog (hard fail)
  3 = Invalid catalog structure / parse errors (hard fail)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Set, Dict, Any

import yaml


def load_catalog(path: Path) -> Set[str]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[FAIL] Cannot parse YAML catalog: {path} :: {e}")
        sys.exit(3)

    if not isinstance(data, dict) or "issues" not in data:
        print(f"[FAIL] Invalid catalog structure: missing top-level 'issues' list in {path}")
        sys.exit(3)

    issues = data["issues"]
    if not isinstance(issues, list):
        print(f"[FAIL] Invalid catalog structure: 'issues' must be a list in {path}")
        sys.exit(3)

    keys: Set[str] = set()
    for i, item in enumerate(issues):
        if not isinstance(item, dict) or "issue_key" not in item:
            print(f"[FAIL] Invalid issue entry at index {i}: must contain 'issue_key'")
            sys.exit(3)
        k = item["issue_key"]
        if not isinstance(k, str) or not k.strip():
            print(f"[FAIL] Invalid issue_key at index {i}: must be non-empty string")
            sys.exit(3)
        if k in keys:
            print(f"[FAIL] Duplicate issue_key '{k}' in catalog")
            sys.exit(3)
        keys.add(k)
    return keys


def collect_example_issue_keys(examples_dir: Path) -> Set[str]:
    keys: Set[str] = set()
    json_files = sorted(examples_dir.rglob("*.json"))

    for f in json_files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[FAIL] Cannot parse JSON example: {f} :: {e}")
            sys.exit(3)

        # Expect v0 output shape: results[].issues[].issue_key
        results = data.get("results", [])
        if isinstance(results, list):
            for r in results:
                if not isinstance(r, dict):
                    continue
                issues = r.get("issues", [])
                if not isinstance(issues, list):
                    continue
                for it in issues:
                    if not isinstance(it, dict):
                        continue
                    k = it.get("issue_key")
                    if isinstance(k, str) and k.strip():
                        keys.add(k)

        # Also allow top-level error envelope to carry error_code
        # (Not necessarily mapped to issue_catalog; skip unless you decide to unify later.)

    return keys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", required=True, help="Path to orchestration/issue_catalog.yml")
    ap.add_argument("--examples", required=True, help="Path to orchestration/examples directory")
    ap.add_argument("--fail-on-unused", action="store_true",
                    help="If set, fail when catalog has keys unused by examples (default: warn only)")
    args = ap.parse_args()

    catalog_path = Path(args.catalog)
    examples_dir = Path(args.examples)

    if not catalog_path.exists():
        print(f"[FAIL] Catalog not found: {catalog_path}")
        return 3
    if not examples_dir.exists():
        print(f"[FAIL] Examples dir not found: {examples_dir}")
        return 3

    catalog_keys = load_catalog(catalog_path)
    used_keys = collect_example_issue_keys(examples_dir)

    missing = sorted(list(used_keys - catalog_keys))
    unused = sorted(list(catalog_keys - used_keys))

    if missing:
        print("[FAIL] Examples reference issue_key not present in issue_catalog.yml:")
        for k in missing:
            print(f"  - {k}")
        return 2

    print(f"[OK] issue_key check passed. Used={len(used_keys)} Catalog={len(catalog_keys)}")

    if unused:
        msg = "[WARN] issue_catalog.yml contains unused issue_key (not referenced in examples yet):"
        if args.fail_on_unused:
            msg = "[FAIL] issue_catalog.yml contains unused issue_key (fail-on-unused enabled):"
        print(msg)
        for k in unused[:50]:
            print(f"  - {k}")
        if len(unused) > 50:
            print(f"  ... ({len(unused) - 50} more)")
        if args.fail_on_unused:
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### requirements.txt

```
pytest
jsonschema
pyyaml
```

### 使用方式

**本地：**
```bash
make ci
```

**CI（GitHub Actions / 任意 CI）：**
```bash
make ci
```

如果你希望 "catalog 里有但 examples 没用到的 key 也算失败"，CI 可以用：
```bash
python tools/validate_issue_keys.py \
    --catalog orchestration/issue_catalog.yml \
    --examples orchestration/examples \
    --fail-on-unused
```
