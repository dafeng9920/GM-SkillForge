import os

# Configuration
TEMPLATE_FILE = r"D:\GM-SkillForge\docs\2026-02-24\SEO建站\AIO_Checker_Mockup.html"
OUTPUT_DIR = r"D:\GM-SkillForge\docs\2026-02-24\SEO建站\Matrix_Pages"
FRAMEWORKS = [
    {"id": "nextjs", "name": "Next.js", "hook": "Is your Next.js app invisible to Perplexity?"},
    {"id": "shopify", "name": "Shopify", "hook": "Why isn't Perplexity citing your Shopify store?"},
    {"id": "wordpress", "name": "WordPress", "hook": "Audit your WordPress AI-SEO in seconds."},
    {"id": "svelte", "name": "SvelteKit", "hook": "The first AI-Search audit for SvelteKit apps."},
    {"id": "vite", "name": "Vite/React", "hook": "How visible is your Vite app in AI Overviews?"}
]

def generate_matrix():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
        
    for fw in FRAMEWORKS:
        output_file = os.path.join(OUTPUT_DIR, f"{fw['id']}-ai-seo-checker.html")
        
        # Matrix Expansion Logic: Customize the template
        custom_content = template.replace(
            "Is Perplexity Citing You?", 
            fw['hook']
        ).replace(
            "The first AI-Search Audit tool.",
            f"Dedicated AI-Search Visibility Audit for **{fw['name']}** power users."
        )
        
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write(custom_content)
        print(f"Generated: {output_file}")

if __name__ == "__main__":
    generate_matrix()
