import re

file_path = r'd:\GM-SkillForge\scripts\run_3day_compliance_review.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'print(f"DEBUG PATH: {path}")\n    print(f"DEBUG TEXT LEN: {len(text)}")\n    print(f"DEBUG MATCH: {bool(has_env_guard)}")\n    ok = bool(has_env_guard) and not bool(unconditional_sample)',
    'ok = bool(has_env_guard) and not bool(unconditional_sample)'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Restored run_3day_compliance_review.py")
