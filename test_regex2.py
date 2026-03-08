import re

with open(r'd:\GM-SkillForge\skillforge\src\storage\audit_pack_store.py', 'r', encoding='utf-8') as f:
    text = f.read()

has_env_guard = re.search(
    r"os\.getenv\(\"SKILLFORGE_ENV\"\).*?(dev|test).*?_create_sample_packs",
    text,
    flags=re.MULTILINE | re.DOTALL,
)

print('has_env_guard matched:', bool(has_env_guard))
if has_env_guard:
    print('match group:', has_env_guard.group(0))

