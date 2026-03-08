import re

file_path = r'd:\GM-SkillForge\skillforge\src\skills\gates\gate_intake.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the import
text = text.replace('from skillforge.src.skills.experience_capture', 'from ..experience_capture')
text = text.replace('GateIntakeRepo — validates repository intake request and produces intake manifest.', 'GateIntakeRepo - validates repository intake request and produces intake manifest.')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Patched gate_intake.py")
