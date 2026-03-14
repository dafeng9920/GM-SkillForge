import os
import re
from AIO_Scanner_Core import AIOScannerCore

class AIOReportGenerator:
    def __init__(self, template_path):
        self.template_path = template_path
        
    def generate(self, domain, output_path):
        scanner = AIOScannerCore(domain)
        data = scanner.run_diagnostic()
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. Basic Metadata Replacements
        mappings = {
            "genesismind.ai": data['target_domain'],
            "example-saas.com": data['target_domain'],
            "$1.28M": data['aev_value'],
            "$1.34M": data['aev_value'],
            "31,326": data['monthly_invisible_vol'],
            "33,000": data['monthly_invisible_vol'],
            "AIO-PATHOLOGY-8893": data['report_id'],
            "AIO-PATHOLOGY-1142": data['report_id'],
            "2026-02-26T07:20:35.022504Z": data['timestamp'],
            "2026-02-25T09:14Z": data['timestamp'],
            "$3.40": data['cpc_floor']
        }
        
        for k, v in mappings.items():
            content = content.replace(k, v)
        
        # 2. Score Matrix Synchronization
        dimensions = ["Neuromorphic Visibility", "Algorithmic Authority", "LLM Citation Rate", "Trust Signal Density"]
        for dim in dimensions:
            pattern = re.escape(dim) + r'.*?chip-low">.*?</'
            new_val = data["scores"]["citation_rate"] if "Citation Rate" in dim else str(data["scores"][dim.lower().replace(" ", "_")])
            content = re.sub(pattern, f'{dim}</span>\n            </td>\n            <td><span class="chip chip-low">{new_val}</', content, flags=re.DOTALL)

        # 3. Evidence Vault / Probing Log Injection (Updated for Reasoning)
        probe_html = ""
        for probe in data['probes']:
            citations = ", ".join(probe['citations'])
            
            # Reasoning sub-block (ONLY if using Jina/DeepSearch)
            reason_block = ""
            if "reasoning" in probe and probe['reasoning']:
                # Pre-process reasoning to avoid f-string backslash issues
                safe_reasoning = probe['reasoning'].replace('\n', '<br>')
                reason_block = f"""
            <div class="thought-process">
              <div class="thought-header"><div class="thought-dot"></div> Neural Thought Process (DeepSearch)</div>
              {safe_reasoning}
            </div>"""

            probe_html += f"""
      <div class="bp-card" style="border-style: dashed; border-color: #1e3a5f; opacity: 1;">
        <div class="bp-num">PRB</div>
        <div>
          <div class="bp-title">Engine: {probe['engine']} &nbsp;·&nbsp; <span style="color:#ef4444">Result: {probe['result']}</span></div>
          <div class="bp-desc">
            <strong>Probe Query:</strong> "{probe['query']}"<br><br>
            <strong>Detected Citations:</strong> <span class="mono" style="font-size:11px">{citations}</span><br><br>
            <div class="codeblock"><span class="cc">/* Raw Response Snippet */</span><br>{probe['snippet']}</div>
            {reason_block}
          </div>
        </div>
      </div>"""
        
        marker = "<!-- PROBING_LOG_INJECTION_MARKER -->"
        content = content.replace(marker, probe_html)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return output_path

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "genesismind.ai"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    template = os.path.join(base_dir, "templates", "Audit_Report_Template.html")
    
    output_filename = f"Audit_Report_{target.replace('.', '_')}.html"
    output = sys.argv[2] if len(sys.argv) > 2 else os.path.join(base_dir, "pseo", output_filename)
    
    # Ensure pseo directory exists
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    gen = AIOReportGenerator(template)
    report = gen.generate(target, output)
    print(f"Deep Diagnostic Report generated SUCCESSFULLY: {report}")
