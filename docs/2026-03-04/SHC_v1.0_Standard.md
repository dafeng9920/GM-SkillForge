# SHC v1.0: SKILL Hardening Certification Standard
*Commercial & Technical Specifications*

## Overview
A "Hardened" Skill is a governed asset. SHC v1.0 ensures every automated action is auditable, reversible, and secure through **Tri-Signature Mapping (TSM)**.

## The 4 Pillars of Hardening

### 1. Fail-Closed Metadata
- Every skill must define `risk_level` and `security_policy: CLOSED`.
- If the **Local-Guard** is offline, all skill execution is hard-blocked to prevent drift.

### 2. Tri-Signature Integrity (TSI)
- Skill outputs must support the **IAR (Intent-Agreement-Result)** signature binding.
- Every generated asset must include an **Integrity Anchor** in its metadata to ensure causal consistency.

### 3. Minimal Exposure (Sandbox)
- Skills must strictly operate within the designated workspace boundary.
- **[SHC-v1.1]**: Physical locking of sensitive system directories during runtime to prevent "Logic Probing."

### 4. Idempotent & Failsafe Execution
- **Idempotency**: Verification of existing state before creation is mandatory.
- **Failsafe**: All external integrations must use "Fail-to-Log" branching for auditability.

## Pillar 5: Core Logic Obfuscation (Causal Isolation)
To protect proprietary mechanisms from unauthorized reverse-engineering ("Philosophy Theft"), SHC-certified skills must implement:

### 1. External Decision Oracle
- All high-value adjudication logic resides in external, pre-compiled binaries.
- The Agent receives a binary **"Execution Permit"** but remains blind to the underlying signature verification math.

### 2. Behavioral Homogenization (The Bucket Strategy)
- **Response Masking**: System failures must return generic **Integrity Error Buckets** (e.g., `SHC-ERR-01`) rather than specific logic descriptions.
- **Stochastic Hardening**: Randomized failure template variations to prevent "Logic Search" by adversarial users.

### 3. Metaphorical Masking (Lore Stealth)
Proprietary concepts must be replaced with neutral engineering metaphors in all AI-facing instructions:
- *Internal Logic [Redacted]* -> **Runtime Security Constraints**
- *Verification Chain [Redacted]* -> **System Stability Protocol**
- *Instruction Set [Redacted]* -> **Environmental Constants**

### 4. Memory Truncation & Isolation
- The Agent's context must be purged of the raw communication logs with the security layer, retaining only the final "Success/Failure" outcome.

---
## The Certification Seal
Successful hardening generates a `SHC-V1-CERTIFIED` metadata badge, confirming that the asset meets the **Industrial Grade** security standard of GM-SkillForge.
