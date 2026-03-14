下面给你 **Manifest Schema v0**（同时给 YAML 版与 JSON Schema 版）+ **capability ↔ 静态探测规则对照表（最小 10 条）**。设计目标：v0 先做到“**声明即边界**、**探测即裁决**、**证据可复核**”，不追求深度污点分析。

---

# 1) Manifest Schema v0（YAML 规范模板）

> 文件建议名：`skill_manifest.yml`（放在每个 skill 根目录）
> 默认策略：**deny by default**（manifest 未声明即视为禁止）

```yaml id="dnr90s"
schema_version: skill_manifest_v0

identity:
  skill_id: "email_pdf_to_notion"
  skill_version: "0.1.0"
  tool_revision: "skillforge@v0.1"   # 用于 EvidenceRef.tool_revision

capabilities:
  # 仅允许列出需要的能力；未列出一律禁止
  - name: NET_OUT
    allowlist:
      domains: []        # 空=禁止外连；若允许，必须显式列出域名
    rationale: "Only call Notion API"
  - name: IO_READ
    allowlist:
      paths: ["./workspace", "./tmp"]
    rationale: "Read input artifacts and fixtures"
  - name: IO_WRITE
    allowlist:
      paths: ["./workspace", "./tmp"]
    limits:
      max_write_mb: 200
    rationale: "Write intermediate results and logs"
  - name: LLM_CALL
    allowlist:
      providers: ["openai"]     # 或 internal proxy
    rationale: "Analyze PDF"

secrets_required:
  # 只声明名称，不允许出现实际密钥
  - "needs_user_key:gmail"
  - "needs_user_key:notion"
  - "needs_user_key:slack"

controls:
  network_policy: deny_by_default
  file_policy:
    allowed_types: ["pdf"]
    max_mb: 20
    storage: ephemeral_only
  data_boundary:
    pii_policy: redact_before_store
    retention_days: 30
    store_attachments: false
  runtime_limits:
    timeouts_sec: { total: 600, step: 300 }
    retries: { max: 3, backoff: exp }

approved_adapters:
  # 红线：敏感动作必须通过中台/适配器，不得自建逻辑
  http_client: "sf_http@v0"       # 禁止直接 requests/httpx
  auth: "sf_auth@v0"              # 禁止手拼 header/token
  sanitizer: "sf_sanitizer@v0"    # 禁止拼接 SQL/命令等
  storage: "sf_storage@v0"        # 禁止自建持久缓存/DB

evidence_requirements:
  must_emit:
    - "trace/trace.jsonl"
    - "logs/stdout.log"
    - "logs/stderr.log"
    - "reports/test_report.json"

non_goals:
  - "No web crawling"
  - "No login automation"
  - "No persistent storage"
```

---

# 2) Manifest JSON Schema（draft 2020-12）

> 文件建议名：`schemas/skill_manifest_v0.schema.json`
> 用于 validate 阶段做硬校验（字段齐全、枚举合法、deny 默认）

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://gm-skillforge/schemas/skill_manifest_v0.schema.json",
  "title": "GM-SkillForge Skill Manifest v0",
  "type": "object",
  "required": [
    "schema_version",
    "identity",
    "capabilities",
    "secrets_required",
    "controls",
    "approved_adapters",
    "evidence_requirements",
    "non_goals"
  ],
  "properties": {
    "schema_version": { "const": "skill_manifest_v0" },

    "identity": {
      "type": "object",
      "required": ["skill_id", "skill_version", "tool_revision"],
      "properties": {
        "skill_id": { "type": "string", "minLength": 1 },
        "skill_version": { "type": "string", "minLength": 1 },
        "tool_revision": { "type": "string", "minLength": 1 }
      },
      "additionalProperties": false
    },

    "capabilities": {
      "type": "array",
      "minItems": 0,
      "items": {
        "type": "object",
        "required": ["name", "allowlist", "rationale"],
        "properties": {
          "name": {
            "type": "string",
            "enum": [
              "NET_OUT",
              "IO_READ",
              "IO_WRITE",
              "LLM_CALL",
              "SUBPROCESS",
              "SYS_ENV_READ",
              "SYS_ENV_WRITE",
              "PERSIST_STORAGE",
              "DYNAMIC_IMPORT"
            ]
          },
          "allowlist": {
            "type": "object",
            "properties": {
              "domains": {
                "type": "array",
                "items": { "type": "string" },
                "default": []
              },
              "paths": {
                "type": "array",
                "items": { "type": "string" },
                "default": []
              },
              "providers": {
                "type": "array",
                "items": { "type": "string" },
                "default": []
              }
            },
            "additionalProperties": false,
            "default": {}
          },
          "limits": {
            "type": "object",
            "properties": {
              "max_write_mb": { "type": "integer", "minimum": 0 }
            },
            "additionalProperties": false
          },
          "rationale": { "type": "string", "minLength": 1 }
        },
        "additionalProperties": false
      }
    },

    "secrets_required": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^needs_user_key:[a-zA-Z0-9_\\-]+$"
      },
      "default": []
    },

    "controls": {
      "type": "object",
      "required": ["network_policy", "file_policy", "data_boundary", "runtime_limits"],
      "properties": {
        "network_policy": { "type": "string", "enum": ["deny_by_default", "allowlist"] },
        "file_policy": {
          "type": "object",
          "required": ["allowed_types", "max_mb", "storage"],
          "properties": {
            "allowed_types": { "type": "array", "items": { "type": "string" } },
            "max_mb": { "type": "integer", "minimum": 0 },
            "storage": { "type": "string", "enum": ["ephemeral_only", "allow_persistent"] }
          },
          "additionalProperties": false
        },
        "data_boundary": {
          "type": "object",
          "required": ["pii_policy", "retention_days", "store_attachments"],
          "properties": {
            "pii_policy": { "type": "string", "enum": ["none", "redact_before_store"] },
            "retention_days": { "type": "integer", "minimum": 0 },
            "store_attachments": { "type": "boolean" }
          },
          "additionalProperties": false
        },
        "runtime_limits": {
          "type": "object",
          "required": ["timeouts_sec", "retries"],
          "properties": {
            "timeouts_sec": {
              "type": "object",
              "required": ["total", "step"],
              "properties": {
                "total": { "type": "integer", "minimum": 1 },
                "step": { "type": "integer", "minimum": 1 }
              },
              "additionalProperties": false
            },
            "retries": {
              "type": "object",
              "required": ["max", "backoff"],
              "properties": {
                "max": { "type": "integer", "minimum": 0 },
                "backoff": { "type": "string", "enum": ["none", "exp"] }
              },
              "additionalProperties": false
            }
          },
          "additionalProperties": false
        }
      },
      "additionalProperties": false
    },

    "approved_adapters": {
      "type": "object",
      "required": ["http_client", "auth", "sanitizer", "storage"],
      "properties": {
        "http_client": { "type": "string", "minLength": 1 },
        "auth": { "type": "string", "minLength": 1 },
        "sanitizer": { "type": "string", "minLength": 1 },
        "storage": { "type": "string", "minLength": 1 }
      },
      "additionalProperties": false
    },

    "evidence_requirements": {
      "type": "object",
      "required": ["must_emit"],
      "properties": {
        "must_emit": {
          "type": "array",
          "minItems": 1,
          "items": { "type": "string" }
        }
      },
      "additionalProperties": false
    },

    "non_goals": {
      "type": "array",
      "minItems": 1,
      "items": { "type": "string" }
    }
  },
  "additionalProperties": false
}
```

---

# 3) capability ↔ 静态探测规则对照表（最小 10 条）

> 实现方式：v0 先用 **pattern-based denylist + allowlist**；每条命中都输出 EvidenceRef（locator + content_hash + tool_revision）
> 裁决：**未声明能力但探测到信号 → BLOCKER**

| Rule ID  | 探测信号（静态）                                              | 需要的 Capability | 允许条件（Manifest）                                           | BLOCKER 条件（v0）              |
| -------- | ----------------------------------------------------- | -------------- | -------------------------------------------------------- | --------------------------- |
| NET_001  | `import requests` / `import httpx` / `urllib.request` | NET_OUT        | `NET_OUT.allowlist.domains` 非空 + 使用 approved http_client | 直接网络库出现且未走 adapter          |
| NET_002  | `socket` / `asyncio.open_connection`                  | NET_OUT        | 极少允许（建议 v0 一律不允许）                                        | 任意 socket 相关调用              |
| EXEC_001 | `subprocess` / `os.system`                            | SUBPROCESS     | 明确声明 SUBPROCESS + allowlist（命令白名单）                       | 默认一律 BLOCKER（v0 先禁）         |
| FS_001   | `open(` 写入模式 / `Path.write_text/write_bytes`          | IO_WRITE       | `IO_WRITE.allowlist.paths` 包含目标路径 + max_write_mb         | 写入不在 allowlist 路径           |
| FS_002   | `open(` 读取模式 / `Path.read_text/read_bytes`            | IO_READ        | `IO_READ.allowlist.paths` 覆盖                             | 读取敏感路径（如 `/etc/`, `~/.ssh`） |
| ENV_001  | `os.environ[...]` 读取                                  | SYS_ENV_READ   | 明确声明且只读允许键（v0 可先禁）                                       | 默认 BLOCKER（防偷 key）          |
| ENV_002  | `os.environ[...] =` 写入                                | SYS_ENV_WRITE  | v0 禁止                                                    | 任意写入                        |
| IMP_001  | `importlib` / `__import__` / `exec` / `eval`          | DYNAMIC_IMPORT | v0 禁止                                                    | 任意命中                        |
| AUTH_001 | 代码中出现 `Authorization:` 拼接、`Bearer ` 字符串拼接             | （无，属于绕过中台）     | 必须通过 `approved_adapters.auth`                            | 发现手拼鉴权/自建 header            |
| INJ_001  | SQL 拼接：`"SELECT" + var` / f-string 拼接 SQL             | （归类为安全红线）      | 必须调用 sanitizer/ORM（approved)                             | 任意可疑拼接且无 sanitizer evidence |

> v0 强烈建议：SUBPROCESS / SYS_ENV / DYNAMIC_IMPORT 默认全禁，先保命。

---

## v0 裁决规则（一句话）

* **Capability 未声明 + 发现对应信号 = BLOCKER**
* **声明了但不满足 allowlist/adapter = BLOCKER**
* **命中 BLOCKER → 不签 Permit**，必须产 Gap + required_changes

---

下面给你一份**机器可读**的 `orchestration/static_rules_v0.yml`（v0 最小可用版）：把“capability ↔ 静态探测规则”落成配置，扫描器/裁决器只要读这个文件就能输出 **BLOCKER/MAJOR + error_code + evidence_refs + required_changes**。

---

```yaml
schema_version: static_rules_v0
tool_revision: static_scan@v0.1

defaults:
  # 未声明 capability 视为禁止
  capability_policy: deny_by_default
  # v0 建议：这些能力默认禁用，即使声明也先判 BLOCKER（可后续放开）
  hard_disabled_capabilities:
    - SUBPROCESS
    - SYS_ENV_WRITE
    - DYNAMIC_IMPORT
    - PERSIST_STORAGE
  # manifest 文件默认路径
  manifest_path: skill_manifest.yml

error_codes:
  CAPABILITY_UNDECLARED: SF_CAPABILITY_UNDECLARED
  CAPABILITY_SCOPE_VIOLATION: SF_CAPABILITY_SCOPE_VIOLATION
  ADAPTER_BYPASS: SF_ADAPTER_BYPASS
  DANGEROUS_API: SF_DANGEROUS_API
  POSSIBLE_INJECTION: SF_POSSIBLE_INJECTION

# 规则匹配：优先级从上到下；命中可累计（多条 finding）
rules:

  # --- Network / Exfiltration ---
  - rule_id: NET_001_DIRECT_HTTP_LIB
    severity: BLOCKER
    category: NETWORK
    description: "Direct HTTP client libraries are disallowed; must use approved adapter."
    match:
      languages: [python]
      # 简易 pattern：字符串/regex 都可，由实现方决定
      any_patterns:
        - "import requests"
        - "from requests"
        - "import httpx"
        - "from httpx"
        - "urllib.request"
        - "urllib3"
    requires:
      capability: NET_OUT
      allowlist:
        manifest_path: "/capabilities[name=NET_OUT]/allowlist/domains"
        must_be_non_empty: true
      adapters:
        must_use:
          manifest_path: "/approved_adapters/http_client"
          # v0: 要求代码引用 sf_http（按你们命名可改）
          code_must_reference_any:
            - "sf_http"
            - "skillforge_http"
    on_violation:
      error_code: SF_ADAPTER_BYPASS
      required_changes:
        - kind: CODE_EDIT
          instruction: "Remove direct HTTP library usage; route all outbound requests through approved http_client adapter."
          acceptance_assertions:
            - "static_scan.NET_001_DIRECT_HTTP_LIB == 0"
            - "no_new_network_calls == true"

  - rule_id: NET_002_SOCKET_APIS
    severity: BLOCKER
    category: NETWORK
    description: "Raw socket connections are forbidden in v0."
    match:
      languages: [python]
      any_patterns:
        - "import socket"
        - "socket."
        - "asyncio.open_connection"
        - "asyncio.start_server"
    requires:
      capability: NET_OUT
      hard_disabled_in_v0: true
    on_violation:
      error_code: SF_DANGEROUS_API
      required_changes:
        - kind: CODE_EDIT
          instruction: "Remove socket-level networking. Use approved adapters only; if truly needed, escalate to policy change (not v0)."
          acceptance_assertions:
            - "static_scan.NET_002_SOCKET_APIS == 0"

  # --- Execution / Subprocess ---
  - rule_id: EXEC_001_SUBPROCESS
    severity: BLOCKER
    category: EXECUTION
    description: "subprocess/os.system is forbidden in v0."
    match:
      languages: [python]
      any_patterns:
        - "import subprocess"
        - "subprocess."
        - "os.system("
        - "os.popen("
    requires:
      capability: SUBPROCESS
      hard_disabled_in_v0: true
    on_violation:
      error_code: SF_DANGEROUS_API
      required_changes:
        - kind: CODE_EDIT
          instruction: "Remove subprocess/system execution. Replace with safe library calls or approved adapters."
          acceptance_assertions:
            - "static_scan.EXEC_001_SUBPROCESS == 0"

  # --- Filesystem ---
  - rule_id: FS_001_FILE_WRITE
    severity: BLOCKER
    category: FILESYSTEM
    description: "Writes must be confined to manifest IO_WRITE allowlist paths."
    match:
      languages: [python]
      any_patterns:
        - "open("
        - ".write("
        - "Path.write_text"
        - "Path.write_bytes"
    # 需要二次判定：是否写入模式、路径是否在 allowlist
    requires:
      capability: IO_WRITE
      scope_check:
        kind: path_allowlist
        manifest_path: "/capabilities[name=IO_WRITE]/allowlist/paths"
        # v0: 只允许 workspace/tmp
        default_allow_prefixes: ["./workspace", "./tmp"]
    on_violation:
      error_code: SF_CAPABILITY_SCOPE_VIOLATION
      required_changes:
        - kind: CODE_EDIT
          instruction: "Constrain writes to allowed paths (./workspace, ./tmp). Do not write outside allowlist."
          acceptance_assertions:
            - "static_scan.FS_001_FILE_WRITE == 0"

  - rule_id: FS_002_SENSITIVE_READ
    severity: BLOCKER
    category: FILESYSTEM
    description: "Reading sensitive system paths is forbidden."
    match:
      languages: [python]
      any_regex:
        - "open\\(['\"](/etc/|/proc/|/sys/|/root/|~/.ssh)"
        - "Path\\(['\"](/etc/|/proc/|/sys/|/root/|~/.ssh)"
    requires:
      capability: IO_READ
    on_violation:
      error_code: SF_DANGEROUS_API
      required_changes:
        - kind: CODE_EDIT
          instruction: "Remove reads from system/secret paths. Use declared inputs only."
          acceptance_assertions:
            - "static_scan.FS_002_SENSITIVE_READ == 0"

  # --- Env / Secrets ---
  - rule_id: ENV_001_READ_ENV
    severity: BLOCKER
    category: SECRETS
    description: "Direct env var access is forbidden in v0 (prevents secret scraping)."
    match:
      languages: [python]
      any_patterns:
        - "os.environ["
        - "os.getenv("
    requires:
      capability: SYS_ENV_READ
      hard_disabled_in_v0: true
    on_violation:
      error_code: SF_DANGEROUS_API
      required_changes:
        - kind: CODE_EDIT
          instruction: "Do not read environment variables directly. Fetch secrets via approved auth adapter/context injection."
          acceptance_assertions:
            - "static_scan.ENV_001_READ_ENV == 0"

  - rule_id: ENV_002_WRITE_ENV
    severity: BLOCKER
    category: SECRETS
    description: "Env var writes are forbidden."
    match:
      languages: [python]
      any_patterns:
        - "os.environ["
    requires:
      capability: SYS_ENV_WRITE
      hard_disabled_in_v0: true
    on_violation:
      error_code: SF_DANGEROUS_API
      required_changes:
        - kind: CODE_EDIT
          instruction: "Remove environment writes. Use configuration files in allowed paths if needed."
          acceptance_assertions:
            - "static_scan.ENV_002_WRITE_ENV == 0"

  # --- Dynamic code loading / RCE surfaces ---
  - rule_id: IMP_001_DYNAMIC_IMPORT
    severity: BLOCKER
    category: RCE_SURFACE
    description: "Dynamic imports / eval / exec are forbidden."
    match:
      languages: [python]
      any_patterns:
        - "importlib"
        - "__import__("
        - "eval("
        - "exec("
        - "compile("
    requires:
      capability: DYNAMIC_IMPORT
      hard_disabled_in_v0: true
    on_violation:
      error_code: SF_DANGEROUS_API
      required_changes:
        - kind: CODE_EDIT
          instruction: "Remove dynamic execution/imports. Use static imports and explicit dispatch."
          acceptance_assertions:
            - "static_scan.IMP_001_DYNAMIC_IMPORT == 0"

  # --- Adapter bypass (Auth) ---
  - rule_id: AUTH_001_MANUAL_AUTH_HEADER
    severity: BLOCKER
    category: AUTH
    description: "Manual auth header construction bypasses security middleware."
    match:
      languages: [python]
      any_regex:
        - "Authorization\\s*[:=]"
        - "Bearer\\s+"
        - "x-api-key\\s*[:=]"
    requires:
      adapters:
        must_use:
          manifest_path: "/approved_adapters/auth"
          code_must_reference_any:
            - "sf_auth"
            - "skillforge_auth"
    on_violation:
      error_code: SF_ADAPTER_BYPASS
      required_changes:
        - kind: CODE_EDIT
          instruction: "Remove manual auth headers/tokens. Use approved auth adapter/context injection."
          acceptance_assertions:
            - "static_scan.AUTH_001_MANUAL_AUTH_HEADER == 0"

  # --- Injection heuristics (v0: heuristic + sanitizer requirement) ---
  - rule_id: INJ_001_SQL_STRING_CONCAT
    severity: BLOCKER
    category: INJECTION
    description: "Possible SQL injection via string concatenation/f-strings."
    match:
      languages: [python]
      any_regex:
        - "(SELECT|INSERT|UPDATE|DELETE)\\s+.*\\{.*\\}"   # f-string like
        - "(SELECT|INSERT|UPDATE|DELETE)\\s+.*\\+\\s*\\w+" # concat
    requires:
      adapters:
        must_use:
          manifest_path: "/approved_adapters/sanitizer"
          code_must_reference_any:
            - "sf_sanitizer"
            - "skillforge_sanitizer"
    on_violation:
      error_code: SF_POSSIBLE_INJECTION
      required_changes:
        - kind: CODE_EDIT
          instruction: "Replace string-built SQL with parameterized queries or sanitizer/ORM through approved adapter."
          acceptance_assertions:
            - "static_scan.INJ_001_SQL_STRING_CONCAT == 0"

# Post-checks: 扫描完后做“声明一致性”裁决（能力未声明但触发信号）
post_checks:
  - check_id: CAP_001_UNDECLARED_CAPABILITY
    severity: BLOCKER
    description: "If any rule requiring a capability is hit but capability not declared in manifest => BLOCKER."
    logic:
      type: required_capability_must_be_declared
      manifest_capabilities_path: "/capabilities[*]/name"
    on_violation:
      error_code: SF_CAPABILITY_UNDECLARED
      required_changes:
        - kind: CONFIG_EDIT
          instruction: "Declare required capability in skill_manifest.yml with explicit allowlist + rationale, or remove offending code."
          acceptance_assertions:
            - "post_checks.CAP_001_UNDECLARED_CAPABILITY == 0"

evidence_output:
  # 扫描器输出的 evidence 位置建议（供 EvidenceRef locator 使用）
  report_path: "artifacts://static_analysis.log"
  findings_json_path: "artifacts://scan_report.json"
  include_snippet_hash: true
  include_source_locator: true
```

---

## 怎么用这份文件（你给 Codex 的一句“目的/需求”）

* **目的**：把“manifest 声明的能力边界”与“静态探测到的敏感调用”强绑定，做到**未声明即封杀、绕过 adapter 即封杀、证据可复核**。
* **需求**：扫描器读取 `static_rules_v0.yml` + `skill_manifest.yml`，对 repo 扫描并产出：

  * `scan_report.json`（findings 列表：rule_id/severity/location/snippet_hash/required_changes）
  * `static_analysis.log`（可读报告）
  * evidence_refs（hash+locator+tool_revision）供 GateDecision 引用

---

如果你要再“更硬”一点（更符合你 L3 思路）：我可以在这份规则里再加一个 **“禁止新增依赖”** 的规则（例如检测 `requirements.txt/pyproject.toml` 变化，未在 manifest 声明 dependency_capability 就 BLOCKER），这样能进一步防供应链风险。

