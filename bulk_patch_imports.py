import os
import re

directory = r'd:\GM-SkillForge\skillforge\src'

for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Target: from skillforge.src.skills.experience_capture import ...
            # Replacement context depends on the depth. 
            # We'll replace it specifically for skills/gates first.
            if r'skills\gates' in filepath:
                new_content = re.sub(r'from skillforge\.src\.skills\.experience_capture import', 'from ..experience_capture import', content)
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Patched: {filepath}")

            elif r'api\routes' in filepath:
                new_content = re.sub(r'from skillforge\.src\.api\.routes\.n8n_boundary_adapter import', 'from .n8n_boundary_adapter import', content)
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Patched: {filepath}")

            elif r'contracts\governance' in filepath:
                new_content = re.sub(r'from skillforge\.src\.contracts\.governance\.feature_flag_loader import', 'from .feature_flag_loader import', content)
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Patched: {filepath}")
