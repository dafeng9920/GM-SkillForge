import time
import json
import os
import requests
from AIO_Scanner_Core import AIOScannerCore
from AIO_Report_Generator import AIOReportGenerator

class LeadManager:
    """
    SkillForge SEO Matrix - Operation Hub v2.0 (DAEMON MODE)
    The "Brain" that orchestrates lead polling and audit fulfillment.
    Built for industrial-scale automation and persistent monitoring.
    """
    
    def __init__(self, lead_source=None):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if lead_source is None:
            self.lead_source = os.path.join(self.base_dir, "data", "captured_leads.json")
        else:
            self.lead_source = lead_source
            
        self.sc_key = "SCT316594TCOAuzL0GaVMG8Ctnyv4S2wd8" # Provided by user
        self.template = os.path.join(self.base_dir, "templates", "Audit_Report_Template.html")
        self.pseo_dir = os.path.join(self.base_dir, "pseo")
        
        # Ensure output directories exist
        if not os.path.exists(self.pseo_dir):
            os.makedirs(self.pseo_dir)
        
    def notify(self, title, message):
        """Sends a notification via ServerChan (WeChat)."""
        url = f"https://sctapi.ftqq.com/{self.sc_key}.send"
        params = {"title": title, "desp": message}
        try:
            requests.get(url, params=params, timeout=10)
            print(f"Notification sent: {title}")
        except Exception as e:
            print(f"Failed to notify: {e}")

    def process_lead(self, lead):
        """Runs the end-to-end audit for a single lead."""
        domain = lead.get("domain")
        if not domain:
            return False
            
        print(f"\n[🚀] PROCESSING AUDIT FOR: {domain}")
        output_report = os.path.join(self.pseo_dir, f"Audit_Report_{domain.replace('.', '_')}.html")
            
        try:
            gen = AIOReportGenerator(self.template)
            report_path = gen.generate(domain, output_report)
            
            # Prepare notification message
            msg = f"### 🛰️ AIO Audit Engine: NEW REPORT LIVE\n\n"
            msg += f"**Domain:** {domain}\n"
            msg += f"**Anxiety Signal:** {lead.get('anxiety_signal', 'N/A')}\n"
            msg += f"**Status:** Real-time Probing COMPLETED\n"
            msg += f"**Path:** {report_path}\n\n"
            msg += f"The high-fidelity audit for `{domain}` has been generated with real-time Perplexity Sonar citations."
            
            self.notify(f"AIO Audit Ready: {domain}", msg)
            return True
        except Exception as e:
            print(f"Process Error for {domain}: {e}")
            # self.notify(f"Audit FAILURE: {domain}", str(e)) # Avoid spamming failures in daemon mode
            return False

    def poll(self, interval=60):
        """Infinite loop to poll for new leads with status monitoring."""
        print(f"[📶] DAEMON ACTIVE. Monitoring {self.lead_source} every {interval}s...")
        
        processed_domains = set()

        while True:
            updated = False
            try:
                if not os.path.exists(self.lead_source):
                    print(f"Warning: {self.lead_source} not found. Waiting...")
                    time.sleep(interval)
                    continue

                with open(self.lead_source, 'r', encoding='utf-8') as f:
                    leads = json.load(f)
                
                for lead in leads:
                    domain = lead.get("domain")
                    if domain and lead.get("status") == "pending_audit":
                        success = self.process_lead(lead)
                        if success:
                            lead["status"] = "audit_completed"
                            lead["processed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                            updated = True
                            processed_domains.add(domain)
                
                if updated:
                    with open(self.lead_source, 'w', encoding='utf-8') as f:
                        json.dump(leads, f, indent=4, ensure_ascii=False)
                    print(f"[✅] Database synced at {time.strftime('%H:%M:%S')}.")
                
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n[🛑] Daemon shutting down gracefully...")
                break
            except Exception as e:
                print(f"Daemon Loop Error: {e}")
                time.sleep(interval * 2)

if __name__ == "__main__":
    manager = LeadManager()
    manager.poll(interval=30) # Poll every 30 seconds for real-time response
