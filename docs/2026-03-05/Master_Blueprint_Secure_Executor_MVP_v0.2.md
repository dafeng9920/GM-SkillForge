# 🤖 MASTER BLUEPRINT: Secure Executor Skill (MVP v0.2)
## Mission: Automated Synthesis Spec for OpenClaw Agent
## Standard: SEAUR (Signature, Evidence, Audit, Update, Response)

---

### [1] DESIGN PHILOSOPHY
- **Non-Custodial**: Agent builds the payload; Hardware (Ledger/Trezor) signs it. Agent NEVER sees the private key.
- **Fail-Closed**: If Geoblock fails or Audit fails, all execution stops immediately.
- **Sim-to-Live**: Mandatory simulation before physical broadcast.

---

### [2] TECHNICAL SPECIFICATIONS FOR SYNTHESIS

#### A. Geoblock Enforcement (`geoblock_checker.py`)
- **Action**: Check IP/API before every transaction intent.
- **Rules**: 
  - `USA` -> Blocked.
  - `Singapore` -> Close-only mode.
  - `Global` -> Normal flow.
- **Error Handling**: Raise `GeoblockException` to trigger Fail-Closed.

#### B. Simulation Bridge (`simulation_bridge.py`)
- **Action**: Intercept `broadcast_tx` calls when `SIMULATION_MODE=True`.
- **Mocking**: Return a deterministic "Sim-Hash" (e.g., `0xsimulated_...`) and log the predicted outcome.

#### C. Hardware Bridge (`hw_bridge.py`)
- **Driver**: Use `ledgerblue` or `trezorlib`.
- **Security Logic**:
  - Request user confirmation on the physical device.
  - Return the signed transaction hex.
  - Interface via a local IPC socket to keep keys isolated from the main Agent memory.

---

### [3] PROMPT-LEVEL INSTRUCTIONS FOR OPENCLAW AGENT

1.  **Architecture Initialization**: Create the `src/` directory structure with strict separation between `geoblock`, `simulation`, and `hardware` modules.
2.  **Configuration Safety**: Set `SIMULATION_MODE = True` as the immutable hard-coded default in `config.py`.
3.  **Audit Integration**: Wrap the main execution loop in `main.py` with an `audit_logger` that records:
    - User IP & Geolocation.
    - Transaction Intent (Human Readable).
    - Simulation Result (Success/Fail).
    - User Confirmation Timestamp.
4.  **Verification Step**: After implementation, run `openclaw-audit --deep` to verify no dangerous imports or network leaks were introduced during synthesis.

---

### [4] ACCEPTANCE CRITERIA (SEAUR)
- **S**: Is the `hw_bridge` returning a valid signature without private key exposure?
- **E**: Does the `Evidence Vault` contain the IP info and simulation logs?
- **A**: Does the `geoblock_checker` correctly identify a mock USA IP?
- **U**: Is the architecture modular enough for future Protocol Adapters?
- **R**: Does the system halt if the Geoblock API returns a 500 error?

---
**Status**: Ready for GPT Review & Agent Synthesis.
**ID**: FORGE-SPEC-20260305-DEFI-001
