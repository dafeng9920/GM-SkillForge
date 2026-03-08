# Wave 10 — Storage Integration + Acceptance Checklist

## Summary
Wired the storage layer into the pipeline engine, added 4 CLI commands for storage management, and created a formal acceptance test suite for Protocol v1.0 Section 9.

---

## 10A — Engine ↔ Storage Integration

#### [MODIFY] [engine.py](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/src/orchestration/engine.py)
- [PipelineEngine](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/src/orchestration/engine.py#93-368) now has `db_path` field (default: `db/skillforge.sqlite`)
- Lazy-init [SkillRepository](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/src/storage/repository.py#31-308) via [repo](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/src/orchestration/engine.py#114-120) property
- After `pack_audit_and_publish` → auto-persist: [ensure_skill()](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/src/storage/repository.py#51-64) → [append_revision()](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/src/storage/repository.py#81-113) → 7× [add_artifact()](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/src/storage/repository.py#154-175)
- Storage failure is silently caught — never breaks the pipeline

---

## 10B — CLI Storage Commands

#### [MODIFY] [cli.py](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/src/cli.py)

| Command | Maps to |
|---|---|
| `skillforge snapshot <id> [--at-time]` | `repo.get_snapshot()` |
| `skillforge index [--at-time] [--include-deprecated]` | `repo.get_index()` |
| `skillforge revisions <id> [--include-deprecated]` | `repo.get_revisions()` |
| `skillforge tombstone <id> --reason "..."` | `repo.tombstone_skill()` |

All commands accept `--db` to specify database path.

---

## 10C — Acceptance Tests

#### [NEW] [test_acceptance.py](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/tests/test_acceptance.py)

| # | Protocol Checklist Item | Test Class | Tests |
|---|---|---|---|
| 1 | Upstream 可复现 | [TestUpstreamReproducible](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/tests/test_acceptance.py#25-61) | 1 |
| 2 | Evidence 闭环 | [TestEvidenceChain](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/tests/test_acceptance.py#66-100) | 1 |
| 3 | Contracts-first | [TestContractsFirst](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/tests/test_acceptance.py#105-121) | 2 |
| 4 | Error policy 对齐 | [TestErrorPolicyAligned](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/tests/test_acceptance.py#126-144) | 1 |
| 5 | Revision/timepoint | [TestRevisionTimepoint](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/tests/test_acceptance.py#149-200) | 3 |
| 6 | Tombstone 生效 | [TestTombstoneEffective](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/tests/test_acceptance.py#205-240) | 2 |
| 7 | L3 Audit Pack | [TestL3AuditPackComplete](file:///D:/GM-SkillForge/skillforge-spec-pack/skillforge/tests/test_acceptance.py#245-324) | 2 |

**Result: 12/12 passed ✅**

---

## Regression

| Suite | Result |
|---|---|
| Acceptance tests | **12/12** ✅ |
| Audit config validation | **10/10** ✅ |
| Contract tests | **32/39** (7 pre-existing from format migration, unchanged) |
