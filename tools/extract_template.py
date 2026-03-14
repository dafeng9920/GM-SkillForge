import re

source_path = r"d:\GM-SkillForge\docs\2026-02-26\鱼塘\Claude对神经网络的设计.md"
target_path = r"d:\GM-SkillForge\templates\Audit_Report_Template.html"

with open(source_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the HTML block
match = re.search(r'```html\s*(.*?)\s*```', content, re.DOTALL)
if match:
    html_content = match.group(1)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Successfully extracted HTML to {target_path}")
else:
    print("Could not find HTML block in source file.")
