import re
from pathlib import Path

ROOT = Path(r'd:\GM-SkillForge')
path = ROOT / "skillforge" / "src" / "storage" / "audit_pack_store.py"
text = path.read_text(encoding="utf-8")

has_env_guard = re.search(
    r"os\.getenv\(\"SKILLFORGE_ENV\"\).*?(dev|test).*?_create_sample_packs",
    text,
    flags=re.MULTILINE | re.DOTALL,
)

print('has_env_guard:', bool(has_env_guard))
if has_env_guard:
    print('Match:', repr(has_env_guard.group(0)))
