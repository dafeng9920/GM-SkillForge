# 🛡️ Lobster Guard: Security & Governance Protocol

**Objective**: Ensure all sub-agents operate within the 'SkillForge' project boundary with zero destructive side-effects and strict code integrity.

## 🚧 Workspace Containment
- **Approved Root**: `d:\GM-SkillForge`
- **Restricted Directories**: Any path outside the approved root is strictly off-limits.
- **Permission Model (STRICT)**: 
  - **READ-ONLY**: All `.py`, `.js`, `.html` (templates), and `.css` files are READ-ONLY. Agents are FORBIDDEN from modifying core project logic.
  - **WRITE-ZONE**: Agents are only permitted to write/append to:
    - `data/*.json` (Industry data)
    - `skillforge/captured_leads.json` (Leads)
    - `pseo/*.html` (Generated pSEO pages)
    - `docs/*.md` (Reports and Intel)

## 🚫 Restricted Operations
1. **No System Alteration**: Any command attempting to modify OS settings, registry, or install system-level packages will be blocked.
2. **No Code Modification**: Any attempt to rewrite or edit files in the root or `skillforge/` (except `captured_leads.json`) will trigger a security violation.
3. **Fail-Closed Governance**: If an agent requests access to a forbidden path or attempts a forbidden write, the session must be immediately terminated.

---
*Status: ENFORCED (Code Integrity Lock Active)* 🛡️⚓
