# T06 Nonce Challenge Report

**Task ID:** T06
**Issue:** ISSUE-05 - Nonce Challenge 防重放
**Executor:** Kior-A
**Reviewer:** Antigravity-1
**Compliance Officer:** Kior-C
**Date:** 2026-02-26

---

## 1. Executive Summary

This task implements a complete nonce challenge system for replay attack prevention in the SkillForge evidence envelope protocol. The implementation includes:

- **Challenge generation** with cryptographically secure random nonces
- **TTL-based expiration** for time-bound challenges
- **Replay detection** with `REPLAY_DETECTED` error code
- **Challenge expiration** with `CHALLENGE_EXPIRED` error code
- **Thread-safe storage** with automatic cleanup
- **Ed25519 signature integration** for challenge-response authentication

---

## 2. Acceptance Criteria Status

| Criteria | Status | Evidence |
|----------|--------|----------|
| 重放旧包返回 `REPLAY_DETECTED` | ✅ PASS | `test_replay_detected_error_code` |
| 过期返回 `CHALLENGE_EXPIRED` | ✅ PASS | `test_challenge_expired_error_code` |

---

## 3. Implementation Details

### 3.1 Module Structure

```
skillforge/src/utils/nonce_challenge.py
├── Exceptions
│   ├── ChallengeError (base)
│   ├── ReplayDetectedError (error_code: REPLAY_DETECTED)
│   ├── ChallengeExpiredError (error_code: CHALLENGE_EXPIRED)
│   └── ChallengeInvalidError (error_code: CHALLENGE_INVALID)
├── Data Classes
│   ├── Challenge
│   ├── ChallengeResponse
│   └── ValidationResult
├── Core Classes
│   ├── ChallengeStore (thread-safe storage)
│   └── NonceChallengeManager (main API)
└── Utility Functions
    ├── build_challenge_response_payload()
    ├── create_challenge_response()
    └── verify_challenge_response_signature()
```

### 3.2 Key Features

#### Challenge Generation
- Uses `secrets.token_bytes()` for cryptographically secure randomness
- Default 32-byte nonces (64 hex characters)
- Configurable TTL (default 5 minutes)
- Optional node binding for targeted challenges

#### Replay Prevention
- One-time use challenges (consumed on validation)
- Thread-safe store with `threading.RLock`
- Automatic cleanup of expired challenges
- Memory protection with configurable max size

#### Error Codes
| Code | Scenario |
|------|----------|
| `REPLAY_DETECTED` | Nonce has been previously used |
| `CHALLENGE_EXPIRED` | Challenge TTL has elapsed |
| `CHALLENGE_INVALID` | Format/signature/node mismatch |

### 3.3 Integration Points

#### T03 (Envelope Structure)
- Uses `header.nonce` field in evidence envelopes
- Challenge can be bound to envelope via `context` field

#### T05 (Ed25519 Signature)
- `create_challenge_response()` uses Ed25519 for signing
- `verify_challenge_response_signature()` validates signatures
- Signature covers `nonce:node_id:timestamp` payload

---

## 4. Test Coverage

### 4.1 Test Summary

```
38 tests collected
38 tests passed
0 tests failed
```

### 4.2 Test Categories

| Category | Tests | Description |
|----------|-------|-------------|
| TestChallenge | 4 | Challenge data class |
| TestChallengeResponse | 2 | Response data class |
| TestValidationResult | 3 | Result data class |
| TestChallengeStore | 5 | Storage operations |
| TestNonceChallengeManager | 12 | Main API tests |
| TestSignatureFunctions | 4 | Ed25519 signing |
| TestAcceptanceCriteria | 3 | ISSUE-05 criteria |
| TestEdgeCases | 3 | Boundary conditions |
| TestIntegrationWithEd25519 | 2 | T05 integration |

### 4.3 Acceptance Criteria Tests

```python
def test_replay_detected_error_code(self):
    """Test that replay returns REPLAY_DETECTED error code."""
    manager = NonceChallengeManager()
    challenge = manager.generate_challenge()
    result1 = manager.consume_nonce(challenge.nonce)
    assert result1.valid

    result2 = manager.consume_nonce(challenge.nonce)
    assert not result2.valid
    assert result2.error_code == "REPLAY_DETECTED"

def test_challenge_expired_error_code(self):
    """Test that expired challenge returns CHALLENGE_EXPIRED error code."""
    store = ChallengeStore()
    manager = NonceChallengeManager(store=store, ttl_seconds=1)
    challenge = manager.generate_challenge()

    stored = store.get(challenge.nonce)
    stored.expires_at = time.time() - 1

    result = manager.validate_challenge(challenge.nonce)
    assert not result.valid
    assert result.error_code == "CHALLENGE_EXPIRED"
```

---

## 5. API Reference

### 5.1 NonceChallengeManager

```python
class NonceChallengeManager:
    def __init__(
        self,
        store: Optional[ChallengeStore] = None,
        ttl_seconds: int = 300,
        challenge_length: int = 32
    ): ...

    def generate_challenge(
        self,
        node_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None
    ) -> Challenge: ...

    def validate_challenge(self, nonce: str) -> ValidationResult: ...

    def validate_response(
        self,
        response: ChallengeResponse,
        signature_verifier: Optional[Callable] = None
    ) -> ValidationResult: ...

    def consume_nonce(self, nonce: str) -> ValidationResult: ...

    def is_nonce_used(self, nonce: str) -> bool: ...
```

### 5.2 Usage Example

```python
from skillforge.src.utils.nonce_challenge import (
    NonceChallengeManager,
    create_challenge_response,
    verify_challenge_response_signature,
)

# Server side
manager = NonceChallengeManager(ttl_seconds=60)
challenge = manager.generate_challenge(node_id="node-001")

# Send challenge to client...

# Client side
response = create_challenge_response(
    nonce=challenge.nonce,
    node_id="node-001",
    private_key_hex=client_private_key,
)

# Send response to server...

# Server validation
def verifier(nonce, node_id, timestamp, signature):
    return verify_challenge_response_signature(
        nonce, node_id, timestamp, signature, node_public_key
    )

result = manager.validate_response(response, verifier)
if result.valid:
    print(f"Authenticated: {result.node_id}")
else:
    print(f"Rejected: {result.error_code} - {result.error_message}")
```

---

## 6. Dependencies

### 6.1 Upstream (Required)

| Task | Module | Status |
|------|--------|--------|
| T03 | `evidence_envelope.py` | ✅ ALLOW |
| T05 | `ed25519_signature.py` | ✅ ALLOW |

### 6.2 External

| Package | Version | Purpose |
|---------|---------|---------|
| `cryptography` | ≥41.0.0 | Ed25519 signatures |

---

## 7. Security Considerations

### 7.1 Cryptographic Strength
- Nonce length: 32 bytes (256 bits) - cryptographically secure
- Random generation: `secrets.token_bytes()` - CSPRNG
- Signature algorithm: Ed25519 - 128-bit security level

### 7.2 Attack Prevention
- **Replay attacks**: One-time use challenges with `REPLAY_DETECTED`
- **Timing attacks**: Constant-time signature verification via Ed25519
- **Memory exhaustion**: Configurable max store size
- **Race conditions**: Thread-safe with `threading.RLock`

### 7.3 Configuration
- Default TTL: 300 seconds (5 minutes)
- Max challenges: 10,000 (configurable)
- Cleanup interval: 60 seconds

---

## 8. Evidence References

| ID | Kind | Locator |
|----|------|---------|
| EV-T06-CODE-001 | FILE | `skillforge-spec-pack/skillforge/src/utils/nonce_challenge.py` |
| EV-T06-CODE-002 | FILE | `skillforge-spec-pack/skillforge/src/utils/__init__.py` |
| EV-T06-TEST-001 | FILE | `skillforge-spec-pack/skillforge/tests/test_nonce_challenge.py` |
| EV-T06-TEST-002 | OUTPUT | `pytest: 38 passed in 0.14s` |
| EV-T06-REPORT-001 | FILE | `docs/2026-02-26/p0-governed-execution/verification/T06_nonce_report.md` |

---

## 9. Conclusion

Task T06 successfully implements the Nonce Challenge system as specified in ISSUE-05:

- ✅ Challenge generation with configurable TTL
- ✅ `REPLAY_DETECTED` error code for replay attacks
- ✅ `CHALLENGE_EXPIRED` error code for expired challenges
- ✅ Thread-safe storage with automatic cleanup
- ✅ Ed25519 signature integration (T05)
- ✅ Envelope structure integration (T03)
- ✅ 38/38 tests passing

**Task Status: COMPLETE**
