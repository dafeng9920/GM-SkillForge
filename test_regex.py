import re
text = '''env = os.getenv("SKILLFORGE_ENV")
env = env.lower() if env else "prod"
if env in ("dev", "test") and len(self._packs) == 0:
    self._create_sample_packs()'''

has_env_guard = re.search(
    r"os\.getenv\(\"SKILLFORGE_ENV\"\).*?(dev|test).*?_create_sample_packs",
    text,
    flags=re.MULTILINE | re.DOTALL,
)

print('has_env_guard matched:', bool(has_env_guard))
