import json
import os
import time
from Lead_Storage import add_lead
from Report_Generator import generate_audit_report
from AIO_Scanner_Core import simulate_ai_search

# Paths
OUTPUT_DIR = r"D:\GM-SkillForge\docs\2026-02-24\SEO建站\POC_Results"

def run_proof_of_concept(domain, email):
    print(f"--- Starting Proof of Concept for {domain} ---")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # 1. Simulate Landing Page Lead Capture
    print(f"[Step 1] Capturing Lead: {email} for {domain}...")
    save_status = add_lead(domain, email)
    print(f"Success: {save_status}")
    
    # 2. Trigger AI Search Scan (Brain Integration)
    print(f"[Step 2] Triggering AIO_Scanner_Core for {domain}...")
    scan_results = simulate_ai_search(domain, ["best AI tools"])
    
    # 3. Generate Unified Audit Report
    print(f"[Step 3] Generating professional audit report...")
    report_md = generate_audit_report(scan_results)
    
    # 4. Save POC Evidence
    report_file = os.path.join(OUTPUT_DIR, f"audit_report_{domain.replace('.', '_')}.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_md)
    
    print(f"--- POC Complete! ---")
    print(f"Verified Audit Report saved to: {report_file}")
    
if __name__ == "__main__":
    # Simulate a user from the Shopify Matrix Page
    run_proof_of_concept("myshopify-store.com", "merchant@example.com")
