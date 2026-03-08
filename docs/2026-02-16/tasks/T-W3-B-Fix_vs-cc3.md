# Task Skill Spec: T-W3-B-Fix

```yaml
task_id: "T-W3-B-Fix"
executor: "vs--cc3"
wave: "Wave 3"
input:
  impl: "skillforge/src/skills/experience_capture.py"
  issue: "FC-ATR-5 violation: tombstone=true AtTimeReference was NOT rejected."
output:
  files:
    - "skillforge/src/skills/experience_capture.py" (Fixed)
constraints:
  - "Must explicitly check `at_time_ref.tombstone` in `validate_input`."
  - "If tombstone is True, MUST return REJECTED with reason 'FC-ATR-5: tombstone=true'."
  - "Retain all other existing validations."
```
