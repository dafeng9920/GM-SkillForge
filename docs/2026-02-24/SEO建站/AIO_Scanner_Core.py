import json
import time

def simulate_ai_search(target_domain, keywords):
    """
    Simultates a scan of AI search engines for a target domain.
    In the real implementation, this will use the OpenClaw Browser Tool 
    to navigate to chatgpt.com and perplexity.ai.
    """
    platforms = ["ChatGPT Search", "Perplexity.ai", "Google AIO"]
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "domain": target_domain,
        "score": 0,
        "screenshot_url": "https://raw.githubusercontent.com/SkillForge/AIO-Matrix/main/evidence/sample-scan.png",
        "details": []
    }
    
    # Logic for Perplexity (The Core Differentiation)
    perplexity_found = True # Simulated finding
    if perplexity_found:
        results["details"].append({
            "platform": "Perplexity.ai",
            "status": "CITED",
            "context": "Found in 'Top 5 Providers' list.",
            "points": 40
        })
        results["score"] += 40
        
    # Logic for ChatGPT
    chatgpt_found = False # Simulated missing
    if not chatgpt_found:
        results["details"].append({
            "platform": "ChatGPT Search",
            "status": "NOT_FOUND",
            "context": "Cited competitors: CompetitorA.com, CompetitorB.com",
            "points": 0
        })
    
    # Final Score Calculation
    results["score"] = min(100, results["score"])
    
    return results

def generate_report_markdown(scan_results):
    """
    Generates a markdown report from the scan results.
    """
    report = f"""# AI Search Visibility Audit: {scan_results['domain']}
**Status**: {"✅ Protected & Cited" if scan_results['score'] > 50 else "⚠️ Action Needed. Your AI search presence is weak."}

## 📸 Visual Evidence (Proof of Work)
![Scan Screenshot]({scan_results.get('screenshot_url', '#')})

## Platform Breakdown
"""
    for detail in scan_results['details']:
        status_icon = "✅" if detail['status'] == "CITED" else "❌"
        report += f"""
### {status_icon} {detail['platform']}
- **Status**: {detail['status']}
- **Context**: {detail['context']}
- **Points**: {detail['points']}
"""
    report += f"""
## Overall Score
**Total Score**: {scan_results['score']}/100
"""
    return report

if __name__ == "__main__":
    # Test Run
    target = "example.com"
    kw = ["best AI dev tools"]
    scan_results = simulate_ai_search(target, kw)
    print(json.dumps(scan_results, indent=2))
    
    # Generate and print markdown report
    markdown_report = generate_report_markdown(scan_results)
    print("\n--- Markdown Report ---")
    print(markdown_report)
