# p1-closing-freeze-skill Usage

## Quick Start

```powershell
python skills/p1-closing-freeze-skill/scripts/p1_closing_freeze_check.py --verify-dir docs/2026-02-22/verification --require-allow --require-hash-filled
```

## JSON Output

```powershell
python skills/p1-closing-freeze-skill/scripts/p1_closing_freeze_check.py --verify-dir docs/2026-02-22/verification --require-allow --require-hash-filled --output-mode json
```

## Exit Code

- `0`: ALLOW
- `2`: REQUIRES_CHANGES

