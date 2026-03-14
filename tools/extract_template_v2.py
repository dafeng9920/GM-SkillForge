import re
import os

source_path = r"d:\GM-SkillForge\docs\2026-02-26\鱼塘\Claude对神经网络的设计.md"
target_path = r"d:\GM-SkillForge\templates\Audit_Report_Template.html"

try:
    with open(source_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_idx = -1
    end_idx = -1

    for i, line in enumerate(lines):
        if "<!DOCTYPE html>" in line and start_idx == -1:
            start_idx = i
        if "</html>" in line:
            end_idx = i

    if start_idx != -1 and end_idx != -1:
        html_content = "".join(lines[start_idx:end_idx+1])
        # Clean up any markdown artifacts if any
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Successfully extracted HTML to {target_path}")
    else:
        print(f"Could not find HTML boundaries. Start: {start_idx}, End: {end_idx}")

except Exception as e:
    print(f"Error: {e}")
