import time

def generate_audit_report(scan_results):
    """
    Generates a Markdown audit report based on scan results.
    This report is the "Incentive" for users to leave their email.
    """
    domain = scan_results.get("domain", "Unknown")
    score = scan_results.get("score", 0)
    
    report = f"""# AI Search Visibility Audit: {scan_results['domain']}
**Status**: {"✅ Protected & Cited" if scan_results['score'] > 50 else "⚠️ Action Needed. Your AI search presence is weak."}

## 📸 Visual Evidence (Proof of Work)
![Scan Screenshot]({scan_results.get('screenshot_url', '#')})

## Platform Breakdown
"""
    for detail in scan_results.get("details", []):
        icon = "✅" if detail['status'] == "CITED" else "❌"
        report += f"- {icon} **{detail['platform']}**: {detail['status']} - {detail['context']}\n"
        
    report += f"""
## Recommended Actions
1. **Schema Optimization**: Implement JSON-LD for "AI-Ready" indexing.
2. **Authority Building**: Increase mentions on citation-heavy platforms (GitHub, Reddit).
3. **Keyword Alignment**: Update meta descriptions to target "Informational Intent" queries.

---
*Report generated on {time.strftime("%Y-%m-%d")} by AIO Checker Factory.*
"""
    return report

if __name__ == "__main__":
    # Test Data
    mock_results = {
        "domain": "skillforge.ai",
        "score": 40,
        "details": [
            {"platform": "Perplexity.ai", "status": "CITED", "context": "Found in documentation references.", "points": 40},
            {"platform": "ChatGPT Search", "status": "NOT_FOUND", "context": "No direct search result citation.", "points": 0}
        ]
    }
    print(generate_audit_report(mock_results))
