# OpenClaw + SkillForge: The "Safety Bridle" Architecture

## Goal
To transform OpenClaw from a high-risk autonomous agent into a **Governed Intelligence**. By integrating it with SkillForge, we implement the four pillars of AI safety described in the recent security report: **Isolation, Human-in-the-Loop, Real-time Monitoring, and Least Privilege.**

## User Review Required
> [!IMPORTANT]
> **Active Interception Strategy**: We will move from passive logging to **Active Interception**. This means OpenClaw will be incapable of executing high-risk shell/file commands without an encrypted "Permit Token" issued by the SkillForge G9 Gate.

## Proposed Governance Gates
Based on the AI Safety article, we will implement these specific "Reins":
1.  **G6 (Sandbox/Isolation)**: OpenClaw will remain isolated in its Docker container, unable to access the Windows Host files except through SkillForge-monitored mount points.
2.  **G9 (Permit/Human-in-the-loop)**: Any command involving `rm`, `mv`, or API calls exceeding a specific cost threshold will trigger a **Lock** on the session until a human teammate approves it in the SkillForge dashboard.
3.  **G7 (Audit/Real-time Monitoring)**: Every agent "Thought" (Reasoning) and "Action" will be serialized into a signed **AuditPack** for forensic review.

### [Component] OpenClaw (WSL2/Docker)
#### [NEW] `openclaw-skillforge-adapter`
*   A custom middleware/skill for OpenClaw that intercepts actions.
*   Maps OpenClaw action requests to SkillForge `requested_action` formats.

### [Component] SkillForge Backend (Python)
#### [MODIFY] [registry_store.py](file:///d:/GM-SkillForge/skillforge/src/storage/registry_store.py)
*   Add support for `OPENCLAW` source type in skill registration.

#### [NEW] `openclaw_runtime_adapter.py`
*   Translates OpenClaw trace events into SkillForge `AuditPack` evidence.
*   Connects to G6 (Sandbox) for automated verification of OpenClaw agent policies.

#### [MODIFY] [gate_permit.py](file:///d:/GM-SkillForge/skillforge/src/skills/gates/gate_permit.py)
*   Ensure `subject` mapping correctly handles OpenClaw instance IDs.

## Phase 3: Discord Integration

We will bridge the OpenClaw agent to Discord so you can interact with it outside of the local dashboard.

### Provider: Discord
- **Method**: Discord Bot via Bot Token.
- **Requirements**:
  1. Create a Discord App on the [Developer Portal](https://discord.com/developers/applications).
  2. Create a **Bot** and copy its **Token**.
  3. Enable **Message Content Intent** in the Bot settings.
  4. Use the OAuth2 URL Generator to invite the bot to your server (Permissions: `Send Messages`, `Read Message History`, `View Channels`).

## Proposed Changes

### OpenClaw Gateway
- **Action**: Add Discord channel account via CLI.
- **Command**: `openclaw channels add --channel discord --token <YOUR_BOT_TOKEN>`

## Verification Plan

### Automated Tests
1.  **Direct G5 -> G6 -> G9 Chain**:
    *   Simulate an OpenClaw action request.
    *   Run `gate_permit.py` checks.
    *   Verify `ALLOW/BLOCK` decision correctly reflects in the dummy OpenClaw log.

### Manual Verification
- Send a direct message to the bot on Discord or mention it in a server.
- Verify the bot replies using the GLM-5 brain.
- Check `openclaw channels status` for Discord connectivity.
1.  **"Halt the Hydra" Test**:
    *   Start OpenClaw in WSL2.
    *   Attempt an action (e.g., "Create a file").
    *   SkillForge (Windows side) detects the intent and prompts for Manual Approval (or auto-rejects based on policy).
    *   Verify OpenClaw execution stops or proceeds based on the decision.

## Phase 5: Operational Recovery (Fixing Bootstrap Loop) 🔧

### [MODIFY] [docker-compose.yml](file:///d:/GM-SkillForge/openclaw-box/docker-compose.yml)
- **Action**: Optimize the `command` to avoid recursive `npm install` failures. 
- **Change**: Separate installation from execution. Only update if the binary is missing or requested.

### Verification
1.  Verify container status is `Up` (not looping).
2.  Access `localhost:18789` and verify the Control UI loads.

## Phase 6: Skill Standardization (Knowledge Assetization) 🧠

### [NEW] [SKILL.md](file:///d:/GM-SkillForge/.agents/skills/governance_protocol/SKILL.md)
- **Action**: Formalize the governance logic as a standard Antigravity Skill.
- **Content**: Detailed instructions on PreflightChecklist, ExecutionContract, and RequiredChanges for governance tasks.

### Verification
1.  Confirm the IDE discovers the `governance_protocol` skill.
2.  Perform a test "Audit Request" using the new skill guidelines.

## Phase 7: Productization Strategy (IP Protection & Monetization) 🛡️💰

### Implementation Concept: Commercial Governance API
- **Black-Box Enforcement**: Move all reasoning-heavy `Permit Gate` logic to a hosted SkillForge Cloud.
- **API Key Required**: Skill-stubs in the client workspace must include a valid `SkillForge_API_KEY`.
- **Result-Only Delivery**: The client only receives signed `ALLOW/DENY` tokens and high-level audit summaries. Core logic (the "how") stays in the vault.

### Verification
1.  Verify the "GaaS Stub" can successfully call a dummy remote API.
2.  Ensure that deleting the local stub doesn't expose the remote gate logic.

## Phase 9: Intelligence Orchestration (Knowledge Base) 🧠📡

### [NEW] `monitor_config.json`
- **Location**: `/root/.openclaw/monitor_config.json` (mapped to host `./openclaw-box/.openclaw/`).
- **Purpose**: Serve as the SSOT (Single Source of Truth) for all monitoring targets across all platforms.

### Cross-Platform Logic
1.  **X (Browser)**: Use Playwright to scrape latest posts according to the Tier-1 schedule.
2.  **YouTube (RSS/Scrape)**: Extract captions and summarize key insights.
3.  **Governance Check**: All automated scrapes must pass through the `GOVERNANCE_PROTOCOL` to ensure no illegal data gathering or unauthorized API usage.

### Verification
1.  Verify OpenClaw can parse the JSON file.
2.  Trigger a test briefing for "Tier 1 Foundation" via Discord.

## Phase 10: Niche Site Automation (Revenue Pilot: pSEO Matrix) 📈💰

> [!IMPORTANT]
> **Revenue Analysis**: The **pSEO Universal Tool Matrix** is identified as "Closest to the Money" because its direct output is a monetization-ready web asset. While UES and Memory Swap are critical infrastructure, the pSEO Matrix acts as the "Printing Press" for niche sites.

### Core Strategy: ROI-First Automation
1.  **Mining (Zero-Volume Intent)**: Prioritize "how-to" and "tool-needed" complaints for file processing, data transformation, and niche generators.
2.  **Building (The pSEO Matrix)**: 
    -   **Generic Core**: A single Python/Node skill that handles a class of problems (e.g., Conversion, Analysis, Generation).
    -   **Matrix Expansion**: Automatically generate 10-100 unique landing pages targeting specific long-tail keywords (e.g., "CSV to Shopify JSON", "Markdown to LinkedIn Post").
2.  **Validation (Capability Sniffer)**: 
    -   Check GitHub/ClawHub/MCP-directory for existing solutions.
    -   **Trigger Build IF**: Demand is high/recent but no clean Skill or MCP server exists.
3.  **Building (Skill Scaffolding)**: 
    -   Feed the requirement into the `skill_creator` tool.
    -   Generate a standard Antigravity Skill or MCP server repository automatically.

### [NEW] `ecosystem_sniffer_skill`
- **Logic**: Implements the "Skill Demand" detection. Scans community threads for unanswered "How do I..." or "Agent can't..." queries.
- **Decision Engine**: Validates technical feasibility and existing market saturation.

### Verification
1.  Verify the Sniffer can find a specific "Unmet Tooling Need" in the Antigravity or MCP reddit.
2.  Automate the generation of a `.pen` file or Skill folder for the identified need.

## Phase 11: Intelligence Factory Automation (Fixed Reusable Mode) 🦞⚙️

### [NEW] `intelligence_factory` Skill
- **Logic**: A meta-skill that reads `monitor_config.json` and executes the `TREND_SNIFFER` ritual for each target.
- **Output**: Generates a consolidated "Opportunity Report" in `/root/.openclaw/intelligence/latest_briefing.json`.

### Automation: The Daily Briefing
- **Cron Job**: `openclaw cron add --schedule "0 9 * * *" --task "run-intelligence-factory"`
- **Prompt**: "Execute the intelligence_factory skill and send the high-ROI findings to the Discord #intel channel."

### Verification
1.  Manually trigger the `run-intelligence-factory` task via CLI.
2.  Verify the report is generated and the Discord message is sent.
3.  **Audit (2026-02-24)**: Verified that the agent autonomously created `ads-intel` skill and memory. Successfully synced to local docs.

## Phase 12: AI Search Checker MVP Development 🚀🔍

### Product Focus: "Perplexity-First AIO Checker"
- **Problem**: Zero existing tools specifically focus on **Perplexity SEO**, despite it being the most "reference-heavy" AI search engine.
- **Value**: Provide a "Search Visibility Matrix" across ChatGPT, Perplexity, and Google AIO.
- **Hook**: "Find out why Perplexity isn't citing your brand."

### Technical Blueprint
1.  **Scanner Skill**: A Python script in OpenClaw that uses the browser tool to search for specific brand/niche queries on Perplexity/ChatGPT/Google.
2.  **Matrix Generator**: A template that builds landing pages like `<framework>-ai-seo-checker.html`.
3.  **Monetization (Pivot)**: **Lead Generation First**.
    -   **Phase A**: Free "Light" Audit for Email. Build a "High-Intent Waitlist".
    -   **Phase B**: Once payment is ready, offer the "Deep Audit Report" via email marketing.

### Verification
1.  Verify the Scanner can detect if a domain is mentioned in a ChatGPT Search response.
2.  Generate the first 3 matrix pages: `nextjs-ai-seo`, `shopify-ai-seo`, `wordpress-ai-seo`.

### [STEP 1] Brain Integration (Scanner Refinement)
- **Tool Mapping**: `AI_SEARCH_SCANNER` now explicitly instructs the agent to use `web_fetch` for Perplexity and `browser` for ChatGPT Search.
- **Scoring**: Automated weights (40pts for Perplexity, 60pts for ChatGPT).

### [STEP 2] Lead Capture (The "Fishing Net")
- **Storage**: `captured_leads.json` on host.
- **Utility**: `Lead_Storage.py` for atomic updates.
- **Trigger**: Script parses the "Turn Response" for `<lead>domain|email</lead>` tags to auto-save.

### [STEP 5] Double-Track: Financial Infrastructure (Parallel)
- **Objective**: Ensure the factory is "Payment Ready" by the time lead volume hits threshold.
- **Recommended Gateway**: **Lemon Squeezy** (Merchant of Record - No need for complex foreign entity setup initially).
- **Secondary**: **Stripe** + Atlas (for formal US entity, higher cost/friction).
- **Integration**: Placeholder `handlePayment()` logic added to matrix pages.
