import json
import os

class PSEOGenerator:
    def __init__(self, data_path, template_path, output_dir):
        self.data_path = data_path
        self.template_path = template_path
        self.output_dir = output_dir
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate(self):
        print(f"[⚙️] LOADING PSEO DATA: {self.data_path}")
        with open(self.data_path, 'r', encoding='utf-8') as f:
            industries = json.load(f)
            
        print(f"[⚙️] LOADING TEMPLATE: {self.template_path}")
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        for item in industries:
            print(f"  [+] Generating node: {item['id']} ({item['industry']})")
            
            # Replace placeholders
            page_content = template
            page_content = page_content.replace("{{INDUSTRY}}", item['industry'])
            page_content = page_content.replace("{{KEYWORDS}}", item['keywords'])
            page_content = page_content.replace("{{AEV}}", item['benchmark_aev'])
            page_content = page_content.replace("{{DESCRIPTION}}", item['description'])
            
            # Write output file
            filename = f"audit-{item['id']}.html"
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(page_content)
                
        print(f"[✅] PSEO GENERATION COMPLETE. {len(industries)} nodes deployed to {self.output_dir}")

if __name__ == "__main__":
    generator = PSEOGenerator(
        data_path="d:\\GM-SkillForge\\data\\pSEO_Industries.json",
        template_path="d:\\GM-SkillForge\\templates\\pSEO_Template_Industry.html",
        output_dir="d:\\GM-SkillForge\\pseo"
    )
    generator.generate()
