import sys
from pathlib import Path

# Add the script to print debugging info
with open(r'd:\GM-SkillForge\scripts\run_3day_compliance_review.py', 'r', encoding='utf-8') as f:
    text = f.read()

debug_code = '''def check_prod_sample_pollution() -> CheckResult:
    path = ROOT / "skillforge" / "src" / "storage" / "audit_pack_store.py"
    text = _read(path)
    import re
    has_env_guard = re.search(
        r"os\.getenv\(\"SKILLFORGE_ENV\"\).*?(dev|test).*?_create_sample_packs",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    unconditional_sample = re.search(
        r"if not self\._packs:\s*self\._create_sample_packs\(\)",
        text,
        flags=re.MULTILINE,
    )
    print("DEBUG PATH:", path)
    print("DEBUG FILE EXISTS:", path.exists())
    print("DEBUG FILE LEN:", len(text))
    print("DEBUG REGEX MATCH:", bool(has_env_guard))
    
    ok = bool(has_env_guard) and not bool(unconditional_sample)'''

import re
text = re.sub(r'def check_prod_sample_pollution\(\).*?ok = bool\(has_env_guard\) and not bool\(unconditional_sample\)', debug_code, text, flags=re.DOTALL)

with open(r'd:\GM-SkillForge\scripts\run_3day_compliance_review_DEBUG.py', 'w', encoding='utf-8') as f:
    f.write(text)

