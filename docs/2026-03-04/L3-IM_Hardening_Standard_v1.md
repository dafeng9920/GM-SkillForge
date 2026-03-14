# L3-IM Hardening Standard (L3-IM-S) v1.0
*Standard for AI Agents in High-Exposure Messaging Environments (Discord, Slack, Feishu, Teams)*

## 1. The Core Objective
To protect AI Agent instances (e.g., The Lobster) from hostile social engineering, prompt injection, and accidental data exfiltration in public or collaborative chat environments.

## 2. Pillar 1: Causal Intent Isolation (Non-Inferred Execution)
- **Rule**: No user message in a chat environment shall be treated as an "Execution Command" without passing through a **Non-Inferred Interpreter**.
- **Requirement**: The Agent must map a user's natural language to a pre-defined **Audit-Contract (JSON)**. If the intent cannot be explicitly mapped to a signed contract, the execution must be blocked (**Fail-Closed**).

## 3. Pillar 2: The "Group Chat" Data Filter (DLP-IM)
- **Output Masking**: All responses destined for a public/group channel must pass through a `Lore-Scrubber`.
- **Blocked Data**: Hashes, Internal File Paths, Environment Variables, and Task Metadata must be stripped from public view.
- **Evidence Reference**: Provide a unique `Evidence_ID` instead of dumping execution logs into the chat.

## 4. Pillar 3: Tactical Rate Limiting (Anti-Burst)
- **Protection**: Every IM-accessible instance must have a hardware-level or middleware-level **Command Budget** (e.g., max 5 execution commands per user per hour).
- **Graceful Throttle**: When the budget is exceeded, the Agent must transition to a "Passive Listening" mode, refusing all logic-heavy tasks.

## 5. Pillar 4: The "Bystander" Sandbox
- **Risk**: An unauthorized user "overhearing" the Agent and hijacking the context.
- **Defense**: Strict **Context Locking** to the specific User ID that initiated the Permit. All other "Bystander" messages in the same channel must be treated as untrusted noise.

## 6. Pillar 5: Immutable Registry
- The Agent's local configuration and the `SHC Hardening Pack` itself must be made **Immutable** to IM-originated commands. No `/set_config` or `/update_key` commands shall be allowed from the messaging interface.

---
*Status: DRAFT v1.0 | Authored by: Antigravity-3 (GM-SkillForge)*
