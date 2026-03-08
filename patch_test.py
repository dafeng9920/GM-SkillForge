import os
import re

file_path = r'd:\GM-SkillForge\skillforge\tests\test_gate_permit.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the import in tearDown and add a resign helper
setup_replacement = '''    def setUp(self):
        \"\"\"Set up test fixtures.\"\"\"
        self.gate = GatePermit()
        import os, json, base64, hmac, hashlib
        self.test_key = "test-secret-key-123456"
        os.environ["PERMIT_HS256_KEY"] = self.test_key
        
        # Calculate real signature for VALID_PERMIT
        VALID_PERMIT["signature"]["value"] = self._sign_permit(VALID_PERMIT)

    def tearDown(self):
        import os
        os.environ.pop("PERMIT_HS256_KEY", None)
        
    def _sign_permit(self, permit):
        import json, base64, hmac, hashlib
        payload = dict(permit)
        payload.pop("signature", None)
        payload.pop("revocation", None)
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return base64.b64encode(
            hmac.new(self.test_key.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).digest()
        ).decode("utf-8")'''

# Replace the old setup/teardown logic
content = re.sub(r'    def setUp\(self\).*?(?=\n    # ----------------)', setup_replacement, content, flags=re.DOTALL)

# Re-sign the mutated permits in the failing tests
# Example: 
# input_data["permit_token"]["expires_at"] = "2020..."
# input_data["permit_token"]["signature"]["value"] = self._sign_permit(input_data["permit_token"])
content = content.replace('input_data["permit_token"]["expires_at"] = "2025-01-01T00:00:00Z"', 
                          'input_data["permit_token"]["expires_at"] = "2025-01-01T00:00:00Z"\n        input_data["permit_token"]["signature"]["value"] = self._sign_permit(input_data["permit_token"])')

content = content.replace('input_data["permit_token"]["scope"]["environment"] = "production"',
                          'input_data["permit_token"]["scope"]["environment"] = "production"\n        input_data["permit_token"]["signature"]["value"] = self._sign_permit(input_data["permit_token"])')

content = content.replace('input_data["permit_token"]["subject"]["commit_sha"] = "wrong-sha-123"',
                          'input_data["permit_token"]["subject"]["commit_sha"] = "wrong-sha-123"\n        input_data["permit_token"]["signature"]["value"] = self._sign_permit(input_data["permit_token"])')

content = content.replace('input_data["permit_token"]["subject"]["repo_url"] = "https://github.com/other/repo"',
                          'input_data["permit_token"]["subject"]["repo_url"] = "https://github.com/other/repo"\n        input_data["permit_token"]["signature"]["value"] = self._sign_permit(input_data["permit_token"])')

content = content.replace('input_data["permit_token"]["subject"]["run_id"] = "RUN-WRONG-123"',
                          'input_data["permit_token"]["subject"]["run_id"] = "RUN-WRONG-123"\n        input_data["permit_token"]["signature"]["value"] = self._sign_permit(input_data["permit_token"])')
                          
content = content.replace('input_data["permit_token"]["revocation"]["revoked"] = True',
                          'input_data["permit_token"]["revocation"]["revoked"] = True\n        # signature is outside revocation so changing revocation doesnt affect signature')


with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Applied resign patches to test_gate_permit.py")
