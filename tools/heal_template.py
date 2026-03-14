import os

source_path = r"d:\GM-SkillForge\docs\2026-02-26\鱼塘\Claude对神经网络的设计.md"
template_path = r"d:\GM-SkillForge\templates\Audit_Report_Template.html"

# Common Header/Footer for Healing
HEALED_CLOSURE = """
          <div class="bp-impact">
            <div class="bi-item"><div class="bi-lbl">Recovery Delta</div><div class="bi-val bi-val-gold">+$120k AEV</div></div>
            <div class="bi-item"><div class="bi-lbl">Complexity</div><div class="bi-val">Low</div></div>
          </div>
        </div>
      </div>

      <!-- ── BLUEPRINT 02 ── -->
      <div class="bp-card">
        <div class="bp-num">02</div>
        <div>
          <div class="bp-title">Semantic Content Architecture — Neural Node Expansion</div>
          <div class="bp-desc">
            Develop high-density content clusters targeting the <code>Uncontested</code> search intents identified in Section 05. By establishing the "First-Mover" citation weight in these semantic voids, you bypass existing competitor moats.
          </div>
          <div class="bp-impact">
            <div class="bi-item"><div class="bi-lbl">Recovery Delta</div><div class="bi-val bi-val-gold">+$450k AEV</div></div>
            <div class="bi-item"><div class="bi-lbl">Complexity</div><div class="bi-val">Medium</div></div>
          </div>
        </div>
      </div>

      <!-- ── BLUEPRINT 03 ── -->
      <div class="bp-card">
        <div class="bp-num">03</div>
        <div>
          <div class="bp-title">Cross-Platform Co-Citation Campaign</div>
          <div class="bp-desc">
            Engage 3rd-party authority nodes (industry wikis, research papers, high-authority SaaS directories) to forge entity relationships between your brand and core category intents.
          </div>
          <div class="bp-impact">
            <div class="bi-item"><div class="bi-lbl">Recovery Delta</div><div class="bi-val bi-val-gold">+$770k AEV</div></div>
            <div class="bi-item"><div class="bi-lbl">Complexity</div><div class="bi-val">High</div></div>
          </div>
        </div>
      </div>

    </div>
  </section>

  <!-- =========================================================
       CTA
  ========================================================= -->
  <div class="cta-wrap">
    <div class="cta-eyebrow">NEURAL REPAIR INITIATED</div>
    <div class="cta-title">Ready to Recapture Your AI Search Surface?</div>
    <div class="cta-desc">
      Every 24 hours of invisibility costs your brand approximately <strong>$3,670</strong> in forfeited AEV. Our matrix recovery protocols are ready for deployment.
    </div>
    <a href="#" class="cta-btn">DEPLOY FULL RECOVERY PROTOCOL</a>
    <div class="cta-fine">Estimated recovery window: 4–6 weeks for primary citation recovery.</div>
  </div>

  <!-- =========================================================
       FOOTER
  ========================================================= -->
  <footer class="report-footer">
    <div class="footer-left">
      &copy; 2026 SkillForge SEO Matrix — Neural Integrity Division.<br>
      High-Fidelity AI Search Audit v3.1
    </div>
    <div class="footer-right">
      Protocol: AIO-PATHOLOGY-1142<br>
      Classification: SYSTEM_INTEGRITY_LEVEL_4
    </div>
  </footer>

</div>
</body>
</html>
"""

try:
    with open(source_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the start of HTML
    start_idx = -1
    for i, line in enumerate(lines):
        if "<!DOCTYPE html>" in line:
            start_idx = i
            break
    
    if start_idx != -1:
        # We take up to line 974 (from the source file, which is line 974 - start_idx in our logic)
        # But wait, line 974 in our previous read was the end.
        html_lines = lines[start_idx:]
        
        # Join lines and append our closure
        html_content = "".join(html_lines) + HEALED_CLOSURE
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Successfully healed and saved HTML template to {template_path}")
    else:
        print("Could not find start of HTML.")

except Exception as e:
    print(f"Error: {e}")
