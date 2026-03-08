选 **A**，而且不需要你再补“范围”——我们前面已经把 **tech_seo_audit + issue_key** 的范围定得很清楚了（canonical / hreflang / structured data / http_fetch 四域，共 20 个 issue_key）。执行者那段报错的本质是：**他们现在这个仓库里还没落盘那套 contracts-first 骨架**，所以 diff 没法应用。

下面我把你缺的 4 个文件 **从零建齐**（外加一个目录占位），你直接让执行者按路径创建即可；创建完后再应用“硬测试”那段 diff 就完全对上了。

---

# 一次性建齐：4 个缺失文件（可直接复制落盘）

## 1) `orchestration/issue_catalog.yml`

```yml
catalog_id: tech_seo_audit_issue_catalog
version: "0.1.0"

defaults:
  evidence_required: true
  suggested_fix_required: true
  message_required: true

suggested_fixes_kind_enum:
  - CONFIG_CHANGE
  - LIMIT_REDUCE
  - RETRY
  - CONTACT_SUPPORT
  - MANUAL_REVIEW

domains:
  - HTTP_FETCH
  - CANONICAL
  - HREFLANG
  - STRUCTURED_DATA

issues:
  # HTTP / Fetch (5)
  - issue_key: HTTP_NON_200
    domain: HTTP_FETCH
    default_severity: FAIL
    title: "HTTP non-200"
    description: "Final response status code is not 200."

  - issue_key: HTTP_REDIRECT_LOOP
    domain: HTTP_FETCH
    default_severity: FAIL
    title: "Redirect loop"
    description: "Redirect chain exceeds max_redirects or repeats."

  - issue_key: FETCH_TIMEOUT
    domain: HTTP_FETCH
    default_severity: FAIL
    title: "Fetch timeout"
    description: "The page did not respond within timeout_seconds."

  - issue_key: FETCH_TOO_LARGE
    domain: HTTP_FETCH
    default_severity: FAIL
    title: "Response too large"
    description: "Downloaded content exceeds max_bytes_download."

  - issue_key: ROBOTS_DISALLOWED
    domain: HTTP_FETCH
    default_severity: FAIL
    title: "Robots blocked"
    description: "robots.txt disallows fetching this URL while respect_robots=true."

  # Canonical (4)
  - issue_key: CANONICAL_MISSING
    domain: CANONICAL
    default_severity: WARN
    title: "Canonical missing"
    description: "No <link rel=canonical> found."

  - issue_key: CANONICAL_MULTIPLE
    domain: CANONICAL
    default_severity: FAIL
    title: "Multiple canonicals"
    description: "More than one canonical tag found."

  - issue_key: CANONICAL_CONFLICT
    domain: CANONICAL
    default_severity: WARN
    title: "Canonical conflict"
    description: "Canonical points to a different URL than expected."

  - issue_key: CANONICAL_RELATIVE_URL
    domain: CANONICAL
    default_severity: WARN
    title: "Canonical is relative"
    description: "Canonical href is a relative URL."

  # Hreflang (5)
  - issue_key: HREFLANG_MISSING
    domain: HREFLANG
    default_severity: WARN
    title: "Hreflang missing"
    description: "No hreflang alternates detected."

  - issue_key: HREFLANG_INVALID_LANG_TAG
    domain: HREFLANG
    default_severity: FAIL
    title: "Invalid hreflang tag"
    description: "hreflang value is not a valid language/region tag."

  - issue_key: HREFLANG_CONFLICT
    domain: HREFLANG
    default_severity: FAIL
    title: "Hreflang conflict"
    description: "Conflicting or inconsistent hreflang references detected."

  - issue_key: HREFLANG_SELF_REFERENCE_MISSING
    domain: HREFLANG
    default_severity: WARN
    title: "Self hreflang missing"
    description: "Page lacks a self-referencing hreflang entry."

  - issue_key: HREFLANG_XDEFAULT_MISSING
    domain: HREFLANG
    default_severity: WARN
    title: "x-default missing"
    description: "Multilingual set lacks x-default."

  # Structured Data (6)
  - issue_key: SD_MISSING
    domain: STRUCTURED_DATA
    default_severity: WARN
    title: "Structured data missing"
    description: "No structured data found (JSON-LD/Microdata/RDFa)."

  - issue_key: SD_INVALID_JSONLD
    domain: STRUCTURED_DATA
    default_severity: FAIL
    title: "Invalid JSON-LD"
    description: "JSON-LD block cannot be parsed as valid JSON."

  - issue_key: SD_REQUIRED_FIELDS_MISSING
    domain: STRUCTURED_DATA
    default_severity: WARN
    title: "Required fields missing"
    description: "Structured data is present but missing required fields for detected types."

  - issue_key: SD_TYPE_UNSUPPORTED
    domain: STRUCTURED_DATA
    default_severity: WARN
    title: "Unsupported type"
    description: "Structured data type is unknown/unsupported by the auditor."

  - issue_key: SD_PARSE_ERROR
    domain: STRUCTURED_DATA
    default_severity: FAIL
    title: "Structured data parse error"
    description: "Structured data exists but parsing/normalization failed."

  - issue_key: SD_MULTIPLE_CONFLICTING_ITEMS
    domain: STRUCTURED_DATA
    default_severity: WARN
    title: "Conflicting items"
    description: "Multiple structured data items appear inconsistent."
```

---

## 2) `schemas/tech_seo_audit.input.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "tech_seo_audit.input.schema.json",
  "title": "tech_seo_audit.v0 input",
  "type": "object",
  "additionalProperties": false,
  "required": ["targets", "checks", "options", "controls"],
  "properties": {
    "targets": {
      "type": "array",
      "minItems": 1,
      "maxItems": 500,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["url"],
        "properties": {
          "url": { "type": "string", "format": "uri", "minLength": 8, "maxLength": 2048 },
          "label": { "type": "string", "minLength": 1, "maxLength": 64 }
        }
      }
    },
    "checks": {
      "type": "object",
      "additionalProperties": false,
      "required": ["structured_data", "canonical", "hreflang"],
      "properties": {
        "structured_data": { "type": "boolean" },
        "canonical": { "type": "boolean" },
        "hreflang": { "type": "boolean" }
      }
    },
    "options": {
      "type": "object",
      "additionalProperties": false,
      "required": ["user_agent", "language_hint", "respect_robots"],
      "properties": {
        "user_agent": { "type": "string", "minLength": 3, "maxLength": 128 },
        "language_hint": { "type": "string", "minLength": 2, "maxLength": 16 },
        "respect_robots": { "type": "boolean", "default": true }
      }
    },
    "controls": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "max_targets",
        "timeout_seconds",
        "max_bytes_download",
        "rate_limit_rps",
        "allow_domains",
        "max_redirects"
      ],
      "properties": {
        "max_targets": { "type": "integer", "minimum": 1, "maximum": 500, "default": 50 },
        "timeout_seconds": { "type": "integer", "minimum": 1, "maximum": 120, "default": 20 },
        "max_bytes_download": { "type": "integer", "minimum": 65536, "maximum": 52428800, "default": 5242880 },
        "rate_limit_rps": { "type": "number", "minimum": 0.1, "maximum": 10, "default": 1 },
        "allow_domains": {
          "type": "array",
          "minItems": 1,
          "maxItems": 64,
          "items": { "type": "string", "minLength": 1, "maxLength": 255 }
        },
        "max_redirects": { "type": "integer", "minimum": 0, "maximum": 10, "default": 5 }
      }
    }
  }
}
```

---

## 3) `schemas/tech_seo_audit.output.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "tech_seo_audit.output.schema.json",
  "title": "tech_seo_audit.v0 output",
  "type": "object",
  "additionalProperties": false,
  "required": ["summary", "results", "evidence", "meta"],
  "properties": {
    "summary": {
      "type": "object",
      "additionalProperties": false,
      "required": ["total", "passed", "warnings", "failed", "top_issues"],
      "properties": {
        "total": { "type": "integer", "minimum": 0 },
        "passed": { "type": "integer", "minimum": 0 },
        "warnings": { "type": "integer", "minimum": 0 },
        "failed": { "type": "integer", "minimum": 0 },
        "top_issues": {
          "type": "array",
          "maxItems": 20,
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": ["issue_key", "count"],
            "properties": {
              "issue_key": { "type": "string", "minLength": 3, "maxLength": 64 },
              "count": { "type": "integer", "minimum": 1 }
            }
          }
        }
      }
    },
    "results": {
      "type": "array",
      "maxItems": 500,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["url", "status", "http", "canonical", "hreflang", "structured_data", "issues"],
        "properties": {
          "url": { "type": "string", "format": "uri" },
          "status": { "type": "string", "enum": ["PASS", "WARN", "FAIL"] },
          "http": {
            "type": "object",
            "additionalProperties": false,
            "required": ["final_url", "status_code", "redirect_chain"],
            "properties": {
              "final_url": { "type": "string", "format": "uri" },
              "status_code": { "type": "integer", "minimum": 100, "maximum": 599 },
              "redirect_chain": { "type": "array", "maxItems": 10, "items": { "type": "string", "format": "uri" } }
            }
          },
          "canonical": {
            "type": "object",
            "additionalProperties": false,
            "required": ["status", "canonical_url", "evidence_ref"],
            "properties": {
              "status": { "type": "string", "enum": ["OK", "MISSING", "MULTIPLE", "CONFLICT"] },
              "canonical_url": { "type": "string" },
              "evidence_ref": { "type": "string", "minLength": 6, "maxLength": 128 }
            }
          },
          "hreflang": {
            "type": "object",
            "additionalProperties": false,
            "required": ["status", "entries", "conflicts", "evidence_ref"],
            "properties": {
              "status": { "type": "string", "enum": ["OK", "MISSING", "INVALID", "CONFLICT"] },
              "entries": {
                "type": "array",
                "maxItems": 200,
                "items": {
                  "type": "object",
                  "additionalProperties": false,
                  "required": ["lang", "href"],
                  "properties": {
                    "lang": { "type": "string", "minLength": 2, "maxLength": 16 },
                    "href": { "type": "string", "format": "uri" }
                  }
                }
              },
              "conflicts": {
                "type": "array",
                "maxItems": 50,
                "items": {
                  "type": "object",
                  "additionalProperties": false,
                  "required": ["type", "detail"],
                  "properties": {
                    "type": { "type": "string", "minLength": 3, "maxLength": 64 },
                    "detail": { "type": "string", "minLength": 1, "maxLength": 500 }
                  }
                }
              },
              "evidence_ref": { "type": "string", "minLength": 6, "maxLength": 128 }
            }
          },
          "structured_data": {
            "type": "object",
            "additionalProperties": false,
            "required": ["status", "items"],
            "properties": {
              "status": { "type": "string", "enum": ["OK", "MISSING", "INVALID", "PARTIAL"] },
              "items": {
                "type": "array",
                "maxItems": 200,
                "items": {
                  "type": "object",
                  "additionalProperties": false,
                  "required": ["format", "@type", "required_fields_missing", "warnings", "evidence_ref"],
                  "properties": {
                    "format": { "type": "string", "enum": ["jsonld", "microdata", "rdfa"] },
                    "@type": {
                      "type": "array",
                      "minItems": 1,
                      "maxItems": 10,
                      "items": { "type": "string", "minLength": 1, "maxLength": 80 }
                    },
                    "required_fields_missing": {
                      "type": "array",
                      "maxItems": 50,
                      "items": { "type": "string", "minLength": 1, "maxLength": 80 }
                    },
                    "warnings": {
                      "type": "array",
                      "maxItems": 50,
                      "items": { "type": "string", "minLength": 1, "maxLength": 120 }
                    },
                    "evidence_ref": { "type": "string", "minLength": 6, "maxLength": 128 }
                  }
                }
              }
            }
          },
          "issues": {
            "type": "array",
            "maxItems": 50,
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": ["severity", "issue_key", "message", "suggested_fix", "evidence_ref"],
              "properties": {
                "severity": { "type": "string", "enum": ["WARN", "FAIL"] },
                "issue_key": { "type": "string", "minLength": 3, "maxLength": 64 },
                "message": { "type": "string", "minLength": 1, "maxLength": 300 },
                "suggested_fix": { "type": "string", "minLength": 0, "maxLength": 500 },
                "evidence_ref": { "type": "string", "minLength": 6, "maxLength": 128 }
              }
            }
          }
        }
      }
    },
    "evidence": {
      "type": "object",
      "additionalProperties": false,
      "required": ["items"],
      "properties": {
        "items": {
          "type": "array",
          "maxItems": 2000,
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": ["evidence_ref", "type", "sha256", "location"],
            "properties": {
              "evidence_ref": { "type": "string", "minLength": 6, "maxLength": 128 },
              "type": { "type": "string", "enum": ["html_snippet", "http_header", "parsed_object"] },
              "sha256": { "type": "string", "pattern": "^[a-fA-F0-9]{64}$" },
              "location": {
                "type": "object",
                "additionalProperties": false,
                "required": ["selector"],
                "properties": { "selector": { "type": "string", "minLength": 1, "maxLength": 300 } }
              }
            }
          }
        }
      }
    },
    "meta": {
      "type": "object",
      "additionalProperties": false,
      "required": ["schema_version", "trace_id", "audit_pack_ref"],
      "properties": {
        "schema_version": { "type": "string", "pattern": "^0\\.1\\.0$" },
        "trace_id": { "type": "string", "minLength": 4, "maxLength": 200 },
        "audit_pack_ref": { "type": "string", "minLength": 4, "maxLength": 200 }
      }
    }
  }
}
```

---

## 4) `contract_tests/test_tech_seo_audit_contract.py`

> 这是“基础合同测试 + 硬测试（examples issue_key 必须存在于 catalog）”的完整文件版。

```python
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def schemas():
    input_schema = _load_json(ROOT / "schemas" / "tech_seo_audit.input.schema.json")
    output_schema = _load_json(ROOT / "schemas" / "tech_seo_audit.output.schema.json")
    Draft202012Validator.check_schema(input_schema)
    Draft202012Validator.check_schema(output_schema)
    return input_schema, output_schema


def test_examples_validate_output_schema(schemas):
    _, output_schema = schemas
    v = Draft202012Validator(output_schema)

    examples_dir = ROOT / "orchestration" / "examples" / "tech_seo_audit"
    assert examples_dir.exists(), f"Missing examples dir: {examples_dir}"

    example_files = sorted(examples_dir.glob("*.json"))
    assert example_files, "No example json files found."

    for f in example_files:
        data = _load_json(f)
        errors = sorted(v.iter_errors(data), key=lambda e: e.path)
        assert not errors, f"{f.name} failed schema: " + "; ".join([e.message for e in errors])


def test_input_schema_minimal_valid(schemas):
    input_schema, _ = schemas
    v = Draft202012Validator(input_schema)

    payload = {
        "targets": [{"url": "https://example.com/page-a"}],
        "checks": {"structured_data": True, "canonical": True, "hreflang": True},
        "options": {"user_agent": "gm-skillforge-bot/1.0", "language_hint": "en", "respect_robots": True},
        "controls": {
            "max_targets": 50,
            "timeout_seconds": 20,
            "max_bytes_download": 5242880,
            "rate_limit_rps": 1,
            "allow_domains": ["example.com"],
            "max_redirects": 5
        }
    }
    errors = list(v.iter_errors(payload))
    assert not errors, "; ".join([e.message for e in errors])


def test_examples_issue_keys_must_exist_in_catalog():
    catalog_path = ROOT / "orchestration" / "issue_catalog.yml"
    assert catalog_path.exists(), f"Missing catalog: {catalog_path}"

    catalog = _load_yaml(catalog_path)
    assert isinstance(catalog, dict) and isinstance(catalog.get("issues"), list), "Invalid issue_catalog.yml structure"

    catalog_keys = set()
    for it in catalog["issues"]:
        assert isinstance(it, dict) and "issue_key" in it, "Invalid issue entry (missing issue_key)"
        k = it["issue_key"]
        assert isinstance(k, str) and k.strip(), "Invalid issue_key in catalog"
        assert k not in catalog_keys, f"Duplicate issue_key in catalog: {k}"
        catalog_keys.add(k)

    examples_dir = ROOT / "orchestration" / "examples" / "tech_seo_audit"
    assert examples_dir.exists(), f"Missing examples dir: {examples_dir}"

    used = set()
    for f in sorted(examples_dir.glob("*.json")):
        data = _load_json(f)
        results = data.get("results", [])
        if not isinstance(results, list):
            continue
        for r in results:
            if not isinstance(r, dict):
                continue
            issues = r.get("issues", [])
            if not isinstance(issues, list):
                continue
            for iss in issues:
                if isinstance(iss, dict) and isinstance(iss.get("issue_key"), str) and iss["issue_key"].strip():
                    used.add(iss["issue_key"])

    missing = sorted(list(used - catalog_keys))
    assert not missing, "Examples reference undefined issue_key(s): " + ", ".join(missing)
```

---

# 你还缺的两个目录占位（执行者必须创建）

因为他们说“搜不到 issue_key 字段”，说明他们连 examples 都没有。你至少要加一个最小 example，否则 pytest 会提示 “No example json files found.”

### 建议你立刻加一个最小示例文件（不是你报错里列的缺失项，但跑通需要）

路径：`orchestration/examples/tech_seo_audit/canonical_missing_warn.json`

```json
{
  "summary": {
    "total": 1,
    "passed": 0,
    "warnings": 1,
    "failed": 0,
    "top_issues": [
      { "issue_key": "CANONICAL_MISSING", "count": 1 }
    ]
  },
  "results": [
    {
      "url": "https://example.com/page-b",
      "status": "WARN",
      "http": {
        "final_url": "https://example.com/page-b",
        "status_code": 200,
        "redirect_chain": []
      },
      "canonical": {
        "status": "MISSING",
        "canonical_url": "",
        "evidence_ref": "ev:html:head:1"
      },
      "hreflang": {
        "status": "OK",
        "entries": [],
        "conflicts": [],
        "evidence_ref": "ev:html:hreflang:0"
      },
      "structured_data": {
        "status": "MISSING",
        "items": []
      },
      "issues": [
        {
          "severity": "WARN",
          "issue_key": "CANONICAL_MISSING",
          "message": "Canonical tag not found.",
          "suggested_fix": "Add <link rel=\"canonical\" href=\"https://example.com/page-b\" /> to <head>.",
          "evidence_ref": "ev:html:head:1"
        }
      ]
    }
  ],
  "evidence": {
    "items": [
      {
        "evidence_ref": "ev:html:head:1",
        "type": "html_snippet",
        "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        "location": { "selector": "head" }
      },
      {
        "evidence_ref": "ev:html:hreflang:0",
        "type": "html_snippet",
        "sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
        "location": { "selector": "head" }
      }
    ]
  },
  "meta": {
    "schema_version": "0.1.0",
    "trace_id": "tr:demo:002",
    "audit_pack_ref": "ap:demo:002"
  }
}
```

> 这一个文件就足够让 “issue_key 硬测试”真正跑起来。

---

# 执行者那段话，你可以怎么回

你可以直接把这句话丢给他：

> 选 A。issue_key 是我们要引入的 contracts-first 新机制。请先按给定路径创建：`schemas/tech_seo_audit.*.json`、`orchestration/issue_catalog.yml`、`contract_tests/test_tech_seo_audit_contract.py`，并至少加入一个 example（canonical_missing_warn.json）。之后再应用 diff / 跑 `pytest -q`。

如果你希望我顺手把 `requirements.txt` 的最小内容也给你（pytest/jsonschema/pyyaml），我也可以直接贴出来。
# requirements.txt (minimal for contracts-first validation)
pytest>=7.4.0
jsonschema>=4.21.0
PyYAML>=6.0.1
