import json
import os
import time

LEAD_FILE = r"D:\GM-SkillForge\docs\2026-02-24\SEO建站\captured_leads.json"

def add_lead(domain, email):
    """
    Adds a new lead to the JSON database.
    This will be called by the local API or the OpenClaw agent when a lead is captured.
    """
    if not os.path.exists(LEAD_FILE):
        leads = []
    else:
        with open(LEAD_FILE, 'r', encoding='utf-8') as f:
            try:
                leads = json.load(f)
            except json.JSONDecodeError:
                leads = []
                
    new_lead = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "domain": domain,
        "email": email,
        "status": "UNPROCESSED"
    }
    
    leads.append(new_lead)
    
    with open(LEAD_FILE, 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2)
    
    return f"Lead saved: {email} for {domain}"

if __name__ == "__main__":
    import time
    print(add_lead("manual-test.com", "user@example.com"))
