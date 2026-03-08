"""
SkillForge Storage Layer — 3D RAG Model (Entity × Artifact × Time).

Per AUDIT_ENGINE_PROTOCOL_v1.md:
- Revision model: event-sourcing, never overwrites history
- Tombstone: logical delete, history preserved
- Snapshot at_time: temporal queries
- Evidence chain: manifest is single source of truth
"""
