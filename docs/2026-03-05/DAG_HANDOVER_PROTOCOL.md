# ⚔️ DAG Handover Protocol: Local Gatekeeper (AG-3)
## Status: ACTIVE
## Purpose: Front-end (Discord Lobster) to Local (Antigravity) Audit & Implementation Bridge

### 1. Handover Triggers
The LOCAL-ANTIGRAVITY agent must be notified via `.tmp/openclaw-dispatch/` when:
- **Financial Intent**: Any trade logic or wallet interaction requires second-stage auditing.
- **Skill Synthesis**: Any `.py` or `.js` code generated on Discord must be "Landed" locally for SHC-Hardening.
- **Sovereignty Export**: Any local data (GA, Config, Logs) requested by the cloud agent.

### 2. Mandatory Artifacts per Handover
Every dispatch from the Discord-side must now include:
1. `context_sync.json`: A summary of the user's intent and the agent's preliminary vision.
2. `provisional_logic.py/md`: The un-hardened draft code.
3. `risk_assessment.json`: A self-audit by the Lobster agent against the SlowMist redlines.

### 3. Local Audit Sequence (SEAUR)
1. **S**: Verify logical consistency of the intent.
2. **E**: Generate the `SHC-Receipt` for the proposed logic.
3. **A**: Run `openclaw-audit --deep` on the landed code.
4. **U**: Inject SEAUR-compliant guardrails.
5. **R**: Final "Go/No-Go" decision for deployment back to the cloud.

---
**Protocol ID**: DAG-P-20260305-BETA
**Custodian**: Antigravity-3 (Local)
