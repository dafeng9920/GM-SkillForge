<think>The user wants me to design a sophisticated "AIO Pathology & AEV Assessment" HTML report template for "SkillForge SEO Matrix". This is a continuation/expansion of the previous request. Let me build a comprehensive, visually stunning HTML template with all the required sections.

Key requirements:
1. **AEV (Annual Equivalent Value)** - Financial impact counter
2. **AIO Pathology** - 3 pathology types (Citation Hemorrhage, Semantic Vacuum, Data Friction)
3. **Competitive Nexus** - Brand vs Top 3 competitors matrix across AI engines
4. **Specific Sections**:
   - Lost Revenue Counter (AEV display)
   - Diagnostic Matrix (4x4 table)
   - Neural Coverage Map
   - Actionable Repair Blueprint

**Visual Identity**:
- Background: #07090f (deep space black)
- Primary: #0ea5e9 (electric blue)
- Warning: #f59e0b (alert gold)
- High-end, cold, scientific tone
- Mobile first

I'm structuring this with inline CSS for reliability and building a responsive layout that works on mobile devices first. Now I'm creating the HTML template with all the diagnostic sections, animated counters for the revenue impact, and a competitive matrix that displays how the brand stacks up against competitors across different AI engines.

Building the complete HTML document... Still writing styles... Still writing styles... Still writing styles... Still writing styles... Still writing responsive styles... Building the financial impact dashboard... Building the diagnostic matrix... I'm building out the intent coverage grid with a structured table showing 14 high-value search queries across the category, tracking which competitor owns each semantic territory and identifying gaps where my brand could establish presence. The data shows a mix of owned, captured, contested, and completely uncontested intents—with the biggest opportunity being that 12,700 monthly volume query on automation that nobody's currently dominating.

Now I'm moving into the repair blueprint section, starting with the first intervention: injecting corrected JSON-LD schema across product pages to add the missing applicationCategory and featureList properties that AI systems use for entity resolution. This is a low-effort, high-impact fix that should start showing signal lift within 2-4 weeks.

Building the semantic content architecture next...</think>```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AIO Pathology & AEV Assessment — SkillForge SEO Matrix</title>
  <style>
    /* ============================================================
       SKILLFORGE SEO MATRIX
       AIO Pathology & AEV Assessment Report — Release 3.1
    ============================================================ */

    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }

    body {
      background-color: #07090f;
      background-image:
        radial-gradient(ellipse 60% 40% at 15% 30%, rgba(14,165,233,0.05) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 85% 70%, rgba(99,102,241,0.04) 0%, transparent 60%),
        radial-gradient(circle, rgba(14,165,233,0.045) 1px, transparent 1px);
      background-size: auto, auto, 28px 28px;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, Helvetica, Arial, sans-serif;
      font-size: 15px;
      line-height: 1.65;
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
    }

    /* Tri-color accent rail */
    body::before {
      content: '';
      display: block;
      height: 3px;
      background: linear-gradient(90deg, #0ea5e9 0%, #6366f1 40%, #f59e0b 65%, #6366f1 85%, #0ea5e9 100%);
      position: fixed;
      top: 0; left: 0; right: 0;
      z-index: 999;
    }

    .wrapper { max-width: 960px; margin: 0 auto; padding: 52px 20px 80px; }

    /* ======== UTILITIES ======== */
    .mono { font-family: 'Courier New', Courier, monospace; }
    .divider {
      height: 1px;
      background: linear-gradient(90deg, transparent, #0e1c30, transparent);
      margin: 44px 0;
    }

    /* ======== SECTION LABELS ======== */
    .section-tag {
      display: inline-block;
      font-size: 10px; font-weight: 700;
      letter-spacing: 2.5px; text-transform: uppercase;
      color: #0ea5e9; margin-bottom: 8px;
    }
    .section-title {
      font-size: 22px; font-weight: 800;
      color: #f1f5f9; letter-spacing: -0.5px; line-height: 1.3;
      margin-bottom: 6px;
    }
    .section-desc { font-size: 13px; color: #64748b; max-width: 680px; }
    .section-header { margin-bottom: 28px; }


    /* ============================================================
       HEADER
    ============================================================ */
    .report-header {
      display: flex; justify-content: space-between; align-items: flex-start;
      gap: 20px; flex-wrap: wrap;
      padding-bottom: 30px; margin-bottom: 36px;
      border-bottom: 1px solid #0d1825;
    }
    .brand { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
    .brand-mark {
      width: 42px; height: 42px;
      background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 13px; font-weight: 900; color: #fff; letter-spacing: -1px;
      flex-shrink: 0;
    }
    .brand-name { font-size: 13px; font-weight: 700; color: #f1f5f9; }
    .brand-sub  { font-size: 10px; color: #243347; text-transform: uppercase; letter-spacing: 2.5px; margin-top: 3px; }
    .report-meta { text-align: right; }
    .meta-lbl    { font-size: 10px; color: #1e3a5f; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 4px; }
    .meta-domain { font-size: 22px; font-weight: 800; color: #0ea5e9; letter-spacing: -0.5px; }
    .meta-id     { font-family: 'Courier New', monospace; font-size: 10px; color: #1e3050; margin-top: 5px; letter-spacing: 1px; }

    /* ============================================================
       CRITICAL ALERT BANNER
    ============================================================ */
    .alert-banner {
      background: linear-gradient(135deg, rgba(245,158,11,0.07), rgba(239,68,68,0.04));
      border: 1px solid rgba(245,158,11,0.22);
      border-left: 4px solid #f59e0b;
      border-radius: 10px;
      padding: 16px 20px;
      display: flex; align-items: flex-start; gap: 14px;
      margin-bottom: 48px;
    }
    .alert-icon { font-size: 18px; flex-shrink: 0; margin-top: 1px; }
    .alert-body { font-size: 13px; color: #94a3b8; line-height: 1.6; }
    .alert-body strong { color: #f59e0b; }


    /* ============================================================
       §01 — AEV "LOST REVENUE" COUNTER
    ============================================================ */
    .aev-shell {
      background: linear-gradient(145deg, #0c1422 0%, #080d1a 100%);
      border: 1px solid #0e1c30;
      border-radius: 16px;
      padding: 36px 32px;
      position: relative; overflow: hidden;
      margin-bottom: 48px;
    }
    /* Glow orb */
    .aev-shell::after {
      content: ''; pointer-events: none;
      position: absolute; top: -80px; right: -80px;
      width: 280px; height: 280px;
      background: radial-gradient(circle, rgba(245,158,11,0.08), transparent 65%);
    }
    .aev-grid {
      display: grid;
      grid-template-columns: 220px 1fr;
      gap: 28px;
      margin-top: 24px;
    }
    .aev-hero-col {
      border-right: 1px solid #0e1c30;
      padding-right: 28px;
      display: flex; flex-direction: column; justify-content: center;
    }
    .aev-hero-label {
      font-size: 10px; font-weight: 700; letter-spacing: 2.5px;
      text-transform: uppercase; color: #f59e0b; margin-bottom: 10px;
    }
    .aev-hero-value {
      font-size: 54px; font-weight: 900; line-height: 1;
      color: #f59e0b; letter-spacing: -2px;
      font-variant-numeric: tabular-nums;
    }
    .aev-hero-unit  { font-size: 13px; color: #92400e; margin-top: 6px; font-weight: 600; }
    .aev-hero-note  { font-size: 11px; color: #334155; margin-top: 12px; line-height: 1.6; }

    .aev-kpi-grid   { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .aev-kpi-card {
      background: #060912;
      border: 1px solid #0e1c2e;
      border-radius: 10px; padding: 16px;
    }
    .kpi-label { font-size: 10px; color: #334155; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; }
    .kpi-val   { font-size: 22px; font-weight: 700; color: #cbd5e1; letter-spacing: -0.5px; }
    .kpi-delta { font-size: 11px; margin-top: 4px; }
    .delta-bad  { color: #ef4444; }
    .delta-warn { color: #f59e0b; }


    /* ============================================================
       §02 — AIO PATHOLOGY
    ============================================================ */
    .pathology-grid {
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
      margin-bottom: 48px;
    }
    .p-card {
      border-radius: 14px; padding: 24px;
      background: #0b0e19;
      position: relative; overflow: hidden;
    }
    .p-card-hem { border: 1px solid rgba(239,68,68,0.28); }
    .p-card-vac { border: 1px solid rgba(245,158,11,0.28); }
    .p-card-fri { border: 1px solid rgba(99,102,241,0.28); }
    .p-card-hem::before { content:''; position:absolute; inset:0; pointer-events:none; background: radial-gradient(ellipse at top right, rgba(239,68,68,0.07), transparent 55%); }
    .p-card-vac::before { content:''; position:absolute; inset:0; pointer-events:none; background: radial-gradient(ellipse at top right, rgba(245,158,11,0.07), transparent 55%); }
    .p-card-fri::before { content:''; position:absolute; inset:0; pointer-events:none; background: radial-gradient(ellipse at top right, rgba(99,102,241,0.07), transparent 55%); }

    .p-badge {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 4px 10px; border-radius: 20px;
      font-size: 10px; font-weight: 700;
      text-transform: uppercase; letter-spacing: 1px;
      margin-bottom: 16px;
    }
    .badge-red    { background: rgba(239,68,68,0.10);  color: #ef4444; border: 1px solid rgba(239,68,68,0.18); }
    .badge-gold   { background: rgba(245,158,11,0.10); color: #f59e0b; border: 1px solid rgba(245,158,11,0.18); }
    .badge-indigo { background: rgba(99,102,241,0.10); color: #818cf8; border: 1px solid rgba(99,102,241,0.18); }

    .p-sev       { font-size: 26px; font-weight: 900; line-height: 1; margin-bottom: 4px; }
    .sev-crit    { color: #ef4444; }
    .sev-high    { color: #f59e0b; }
    .sev-mod     { color: #818cf8; }
    .p-title     { font-size: 14px; font-weight: 700; color: #f1f5f9; margin-bottom: 10px; }
    .p-body      { font-size: 12px; color: #64748b; line-height: 1.65; }
    .p-stat {
      margin-top: 16px; padding-top: 14px;
      border-top: 1px solid #0e1824;
      font-size: 11px; color: #94a3b8;
    }
    .p-stat span { font-weight: 700; }
    .c-red    { color: #ef4444; }
    .c-gold   { color: #f59e0b; }
    .c-indigo { color: #818cf8; }


    /* ============================================================
       §03 — DIAGNOSTIC MATRIX TABLE
    ============================================================ */
    .matrix-scroll {
      overflow-x: auto; -webkit-overflow-scrolling: touch;
      border: 1px solid #0d1825;
      border-radius: 14px;
      margin-bottom: 12px;
    }
    table { width: 100%; border-collapse: collapse; min-width: 580px; }
    thead th {
      background: #060a12;
      padding: 14px 16px;
      font-size: 10px; font-weight: 700;
      text-transform: uppercase; letter-spacing: 1.5px;
      color: #334155; text-align: center;
      border-bottom: 1px solid #0d1825;
    }
    thead th:first-child { text-align: left; min-width: 160px; }
    .th-own { color: #0ea5e9 !important; }
    tbody tr { border-bottom: 1px solid #0a1020; transition: background 0.15s; }
    tbody tr:last-child { border-bottom: none; }
    tbody tr:hover { background: rgba(14,165,233,0.025); }
    tbody td {
      padding: 14px 16px;
      font-size: 13px; color: #94a3b8;
      text-align: center; vertical-align: middle;
    }
    tbody td:first-child { text-align: left; color: #cbd5e1; font-weight: 600; }
    .dim-sub { display: block; font-size: 10px; color: #334155; font-weight: 400; margin-top: 2px; }

    /* Score chips */
    .chip {
      display: inline-flex; align-items: center; justify-content: center;
      min-width: 54px; padding: 4px 9px;
      border-radius: 7px; font-size: 13px; font-weight: 700;
      font-family: 'Courier New', monospace;
    }
    .chip-own  { background: rgba(14,165,233,0.10); color: #0ea5e9; border: 1px solid rgba(14,165,233,0.2); }
    .chip-high { background: rgba(16,185,129,0.10); color: #10b981; border: 1px solid rgba(16,185,129,0.2); }
    .chip-mid  { background: rgba(245,158,11,0.10); color: #f59e0b; border: 1px solid rgba(245,158,11,0.2); }
    .chip-low  { background: rgba(239,68,68,0.10);  color: #ef4444; border: 1px solid rgba(239,68,68,0.2); }

    .legend {
      display: flex; flex-wrap: wrap; gap: 14px;
      margin-top: 14px;
    }
    .leg-item { display: flex; align-items: center; gap: 6px; font-size: 11px; color: #334155; }
    .leg-dot  { width: 8px; height: 8px; border-radius: 2px; flex-shrink: 0; }


    /* ============================================================
       §04 — COMPETITIVE NEXUS
    ============================================================ */
    .nexus-grid { display: grid; gap: 14px; margin-bottom: 0; }
    .nexus-card {
      background: #0b0e19; border: 1px solid #0d1825;
      border-radius: 12px; padding: 22px 24px;
    }
    .nexus-header {
      display: flex; align-items: center; gap: 10px;
      margin-bottom: 18px;
    }
    .eng-dot {
      width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
    }
    .dot-p { background: #0ea5e9; box-shadow: 0 0 7px rgba(14,165,233,0.7); }
    .dot-c { background: #10b981; box-shadow: 0 0 7px rgba(16,185,129,0.7); }
    .dot-g { background: #818cf8; box-shadow: 0 0 7px rgba(129,140,248,0.7); }
    .eng-name { font-size: 13px; font-weight: 700; color: #f1f5f9; }
    .eng-meta { font-size: 10px; color: #334155; margin-left: auto; text-transform: uppercase; letter-spacing: 1px; }

    .bar-rows { display: grid; gap: 11px; }
    .bar-row {
      display: grid;
      grid-template-columns: 110px 1fr 42px;
      align-items: center; gap: 12px;
    }
    .bar-lbl { font-size: 12px; color: #94a3b8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .bar-lbl-own { color: #38bdf8; font-weight: 600; }
    .bar-track { height: 6px; background: #060a12; border-radius: 3px; overflow: hidden; }
    .bar-fill  { height: 100%; border-radius: 3px; }
    .bf-own  { background: linear-gradient(90deg, #0369a1, #0ea5e9); }
    .bf-d1   { background: linear-gradient(90deg, #7c1d13, #ef4444); }
    .bf-d2   { background: #1a2f48; }
    .bf-d3   { background: #142233; }
    .bar-pct { font-family: 'Courier New', monospace; font-size: 11px; font-weight: 700; text-align: right; }
    .pct-own { color: #0ea5e9; }
    .pct-d   { color: #ef4444; }
    .pct-n   { color: #334155; }


    /* ============================================================
       §05 — NEURAL COVERAGE MAP
    ============================================================ */
    .coverage-table {
      display: grid; gap: 8px;
    }
    .coverage-head {
      display: grid;
      grid-template-columns: 1fr 70px 120px 90px;
      gap: 12px; padding: 0 18px 8px;
      font-size: 10px; font-weight: 700;
      color: #1e3050; text-transform: uppercase; letter-spacing: 1.5px;
    }
    .coverage-head span:not(:first-child) { text-align: right; }

    .cov-row {
      display: grid;
      grid-template-columns: 1fr 70px 120px 90px;
      align-items: center; gap: 12px;
      padding: 14px 18px;
      background: #0b0e19; border: 1px solid #0d1825;
      border-radius: 10px;
      transition: border-color 0.15s;
    }
    .cov-row:hover { border-color: #1e3a5f; }

    .cov-query { font-size: 13px; font-weight: 500; color: #cbd5e1; }
    .cov-sub   { font-size: 11px; color: #334155; margin-top: 2px; }
    .cov-vol   { font-family: 'Courier New', monospace; font-size: 11px; color: #334155; text-align: right; }
    .cov-owner { font-size: 11px; font-weight: 600; text-align: right; white-space: nowrap; }
    .ow-self   { color: #10b981; }
    .ow-comp   { color: #ef4444; }
    .ow-void   { color: #475569; }
    .ow-cont   { color: #f59e0b; }

    .status-chip {
      display: inline-block; padding: 3px 9px; border-radius: 5px;
      font-size: 10px; font-weight: 700;
      text-transform: uppercase; letter-spacing: 1px;
      float: right;
    }
    .sc-owned    { background: rgba(16,185,129,0.08);  color: #10b981; border: 1px solid rgba(16,185,129,0.18); }
    .sc-captured { background: rgba(239,68,68,0.08);   color: #ef4444; border: 1px solid rgba(239,68,68,0.18); }
    .sc-void     { background: rgba(100,116,139,0.08); color: #475569; border: 1px solid rgba(100,116,139,0.18); }
    .sc-contest  { background: rgba(245,158,11,0.08);  color: #f59e0b; border: 1px solid rgba(245,158,11,0.18); }


    /* ============================================================
       §06 — REPAIR BLUEPRINT
    ============================================================ */
    .blueprint-list { display: grid; gap: 16px; }
    .bp-card {
      background: #0b0e19; border: 1px solid #0d1825;
      border-radius: 14px; padding: 26px;
      display: grid; grid-template-columns: auto 1fr;
      gap: 20px;
    }
    .bp-num {
      width: 34px; height: 34px; flex-shrink: 0;
      border: 1px solid #0ea5e9; border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 13px; font-weight: 700; color: #0ea5e9;
      font-family: 'Courier New', monospace;
    }
    .bp-title { font-size: 15px; font-weight: 700; color: #f1f5f9; margin-bottom: 8px; }
    .bp-desc  { font-size: 13px; color: #64748b; line-height: 1.65; margin-bottom: 16px; }
    .bp-desc code {
      font-family: 'Courier New', monospace;
      font-size: 11px; color: #7dd3fc;
      background: #050810; padding: 1px 5px; border-radius: 3px;
    }

    /* Syntax-highlighted code block */
    .codeblock {
      background: #04060e;
      border: 1px solid #0e1928;
      border-radius: 10px;
      padding: 16px 18px;
      font-family: 'Courier New', Courier, monospace;
      font-size: 11px;
      line-height: 1.75;
      overflow-x: auto;
      white-space: pre;
    }
    .ck { color: #818cf8; }   /* key */
    .cs { color: #7dd3fc; }   /* string */
    .cv { color: #86efac; }   /* value */
    .cc { color: #1e3050; }   /* comment */

    .bp-tags {
      display: flex; flex-wrap: wrap; gap: 6px;
      margin-top: 16px;
    }
    .bp-tag {
      padding: 3px 9px; border-radius: 5px;
      font-size: 10px; font-weight: 600;
      background: rgba(14,165,233,0.07);
      color: #38bdf8; border: 1px solid rgba(14,165,233,0.14);
    }
    .bp-tag-gold {
      background: rgba(245,158,11,0.07);
      color: #f59e0b; border: 1px solid rgba(245,158,11,0.14);
    }
    .bp-impact {
      display: flex; gap: 20px;
      margin-top: 16px; padding-top: 16px;
      border-top: 1px solid #0d1825;
    }
    .bi-item { display: flex; flex-direction: column; gap: 2px; }
    .bi-lbl  { font-size: 10px; color: #243347; text-transform: uppercase; letter-spacing: 1px; }
    .bi-val  { font-size: 13px; font-weight: 700; color: #0ea5e9; }
    .bi-val-gold { color: #f59e0b; }


    /* ============================================================
       CTA
    ============================================================ */
    .cta-wrap {
      background: linear-gradient(145deg, #0c1727 0%, #080d1c 100%);
      border: 1px solid #0f2040;
      border-radius: 16px;
      padding: 44px 32px;
      text-align: center;
      position: relative; overflow: hidden;
      margin-bottom: 48px;
    }
    .cta-wrap::before {
      content: ''; pointer-events: none;
      position: absolute; top: 50%; left: 50%;
      transform: translate(-50%, -50%);
      width: 400px; height: 400px;
      background: radial-gradient(circle, rgba(14,165,233,0.05), transparent 65%);
    }
    .cta-eyebrow {
      display: inline-block;
      background: rgba(14,165,233,0.08);
      border: 1px solid rgba(14,165,233,0.18);
      color: #0ea5e9;
      padding: 4px 14px; border-radius: 20px;
      font-size: 10px; font-weight: 700;
      letter-spacing: 2px; text-transform: uppercase;
      margin-bottom: 18px;
    }
    .cta-title { font-size: 26px; font-weight: 800; color: #f1f5f9; letter-spacing: -0.5px; margin-bottom: 14px; }
    .cta-desc  { font-size: 14px; color: #475569; line-height: 1.7; max-width: 500px; margin: 0 auto 30px; }
    .cta-btn {
      display: inline-block;
      background: linear-gradient(135deg, #0284c7, #0ea5e9);
      color: #fff; font-size: 14px; font-weight: 700;
      padding: 14px 34px; border-radius: 10px;
      text-decoration: none; letter-spacing: 0.3px;
      box-shadow: 0 0 28px rgba(14,165,233,0.28);
      transition: box-shadow 0.2s, transform 0.15s;
    }
    .cta-btn:hover { box-shadow: 0 0 44px rgba(14,165,233,0.45); transform: translateY(-2px); }
    .cta-fine { font-size: 11px; color: #1a2d42; margin-top: 16px; }

    /* ============================================================
       FOOTER
    ============================================================ */
    .report-footer {
      border-top: 1px solid #0a1420;
      padding-top: 26px;
      display: flex; justify-content: space-between; align-items: center;
      flex-wrap: wrap; gap: 12px;
    }
    .footer-left  { font-size: 11px; color: #1a2d42; line-height: 1.7; }
    .footer-right { font-size: 10px; color: #1a2d42; text-align: right; line-height: 1.7; }


    /* ============================================================
       RESPONSIVE
    ============================================================ */
    @media (max-width: 800px) {
      .aev-grid { grid-template-columns: 1fr; }
      .aev-hero-col { border-right: none; border-bottom: 1px solid #0e1c30; padding-right: 0; padding-bottom: 22px; }
      .pathology-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 640px) {
      .wrapper { padding: 40px 16px 60px; }
      .report-header { flex-direction: column; }
      .report-meta { text-align: left; }
      .aev-hero-value { font-size: 42px; }
      .aev-kpi-grid { grid-template-columns: 1fr 1fr; }
      .section-title { font-size: 18px; }
      .bp-card { grid-template-columns: 1fr; gap: 14px; }
      .coverage-head,
      .cov-row { grid-template-columns: 1fr auto; }
      .coverage-head span:nth-child(2),
      .coverage-head span:nth-child(3),
      .cov-vol, .cov-owner { display: none; }
      .cta-wrap { padding: 30px 20px; }
      .cta-title { font-size: 20px; }
      .bar-row { grid-template-columns: 80px 1fr 36px; }
      .bp-impact { flex-wrap: wrap; gap: 14px; }
    }

    @media (max-width: 420px) {
      .aev-kpi-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
<div class="wrapper">


  <!-- =========================================================
       HEADER
  ========================================================= -->
  <header class="report-header">
    <div class="brand">
      <div class="brand-mark">SF</div>
      <div>
        <div class="brand-name">SkillForge SEO Matrix</div>
        <div class="brand-sub">Neural AIO Intelligence Platform</div>
      </div>
    </div>
    <div class="report-meta">
      <div class="meta-lbl">Audit Target Domain</div>
      <div class="meta-domain">example-saas.com</div>
      <div class="meta-id mono">REPORT #AIO-PATHOLOGY-1142 &nbsp;·&nbsp; 2026-02-25T09:14Z &nbsp;·&nbsp; CLASSIFICATION: CONFIDENTIAL</div>
    </div>
  </header>


  <!-- =========================================================
       CRITICAL ALERT BANNER
  ========================================================= -->
  <div class="alert-banner">
    <div class="alert-icon">⚠</div>
    <div class="alert-body">
      <strong>SYSTEMIC ALGORITHMIC DISPLACEMENT CONFIRMED.</strong> &nbsp;Cross-engine citation sampling across 60 category-level queries reveals that 3 competitors are collectively capturing <strong>78% of your brand's addressable AI search surface</strong>. Neuromorphic visibility is measured at <strong>9% on Perplexity</strong> and <strong>7% on ChatGPT Search</strong> — well below the 48% vertical benchmark. Without structured remediation, this gap compounds as LLMs continuously reinforce established citation hierarchies.
    </div>
  </div>


  <!-- =========================================================
       §01 — AEV: ANNUAL EQUIVALENT VALUE AT RISK
  ========================================================= -->
  <section>
    <div class="section-header">
      <div class="section-tag">§ 01 — Financial Impact Quantification</div>
      <div class="section-title">Annual Equivalent Value (AEV) at Risk</div>
      <div class="section-desc">The monetary equivalent of AI-displaced branded traffic, expressed as the annual paid-search (CPC) investment required to recapture it through traditional channels. This is what your current invisibility costs you — every year.</div>
    </div>

    <div class="aev-shell">
      <div class="aev-grid">
        <div class="aev-hero-col">
          <div class="aev-hero-label">AEV — Annual Exposure</div>
          <div class="aev-hero-value">$1.34M</div>
          <div class="aev-hero-unit">Per annum / CPC-equivalent</div>
          <div class="aev-hero-note">
            Derived from: 45,200 monthly category AI queries × 73% invisible share × $3.40 category CPC floor × 12 months. Represents the minimum paid media capital required to substitute organic AI presence currently forfeited to competitors.
          </div>
        </div>
        <div class="aev-kpi-grid">
          <div class="aev-kpi-card">
            <div class="kpi-label">Monthly Invisible Query Volume</div>
            <div class="kpi-val">33,000</div>
            <div class="kpi-delta delta-bad">↑ 18% YoY as AI search adoption scales</div>
          </div>
          <div class="aev-kpi-card">
            <div class="kpi-label">Category CPC Floor</div>
            <div class="kpi-val">$3.40</div>
            <div class="kpi-delta delta-warn">Trending to $4.20 by Q4 2026</div>
          </div>
          <div class="aev-kpi-card">
            <div class="kpi-label">AIO Composite Score</div>
            <div class="kpi-val" style="color:#ef4444">34 / 100</div>
            <div class="kpi-delta delta-bad">Bottom decile for your vertical</div>
          </div>
          <div class="aev-kpi-card">
            <div class="kpi-label">LLM Citation Capture Rate</div>
            <div class="kpi-val" style="color:#ef4444">11%</div>
            <div class="kpi-delta delta-bad">Vertical benchmark: 48–62%</div>
          </div>
        </div>
      </div>
    </div>
  </section>


  <!-- =========================================================
       §02 — AIO PATHOLOGY ASSESSMENT
  ========================================================= -->
  <section>
    <div class="section-header">
      <div class="section-tag">§ 02 — AIO Pathology Assessment</div>
      <div class="section-title">Three Concurrent Failure Modes Identified</div>
      <div class="section-desc">AI search invisibility is not a single root cause — it is a convergence of distinct, diagnosable pathologies. Your domain exhibits all three in an advanced state.</div>
    </div>

    <div class="pathology-grid">

      <div class="p-card p-card-hem">
        <div class="p-badge badge-red">⬤ Citation Hemorrhage</div>
        <div class="p-sev sev-crit">CRITICAL</div>
        <div class="p-title">Competitor Algorithmic Capture</div>
        <div class="p-body">
          When users submit queries mapping directly to your brand's core value proposition, LLM citation engines on Perplexity and ChatGPT Search are systematically routing authority to competitor content nodes. Your brand entity fails to register as a first-tier or second-tier citation source — a condition that self-reinforces with every new query cycle.
        </div>
        <div class="p-stat">
          <span class="c-red">8 of 12</span> core brand-intent queries actively surface a direct competitor in the primary citation position. Your brand is absent from the top 3 citations entirely.
        </div>
      </div>

      <div class="p-card p-card-vac">
        <div class="p-badge badge-gold">⬤ Semantic Vacuum</div>
        <div class="p-sev sev-high">HIGH</div>
        <div class="p-title">Neuromorphic Signal Absence</div>
        <div class="p-body">
          Large language models construct internal knowledge representations by identifying semantically dense content clusters where a brand entity co-occurs with high-frequency intent terms across multiple independent sources. Your domain's current content architecture lacks the structural density, repetition, and cross-platform co-citation signals needed for LLMs to form stable brand-to-value associations.
        </div>
        <div class="p-stat">
          <span class="c-gold">Zero</span> identifiable co-citation clusters linking your brand to its primary intent keywords. Your entity exists in a neuromorphic signal vacuum.
        </div>
      </div>

      <div class="p-card p-card-fri">
        <div class="p-badge badge-indigo">⬤ Data Friction</div>
        <div class="p-sev sev-mod">MODERATE</div>
        <div class="p-title">Structured Signal Degradation</div>
        <div class="p-body">
          AI retrieval and indexing pipelines weight well-formed structured data as a primary entity trust vector. Your current JSON-LD implementation contains deprecated property types, missing entity relationships, and parse-breaking syntax — generating silent indexing failures that cause AI systems to reject your content nodes during knowledge graph construction.
        </div>
        <div class="p-stat">
          <span class="c-indigo">4 schema errors</span> confirmed. <code style="font-family:'Courier New';font-size:10px;color:#818cf8">Organization</code>, <code style="font-family:'Courier New';font-size:10px;color:#818cf8">SoftwareApplication</code>, and <code style="font-family:'Courier New';font-size:10px;color:#818cf8">FAQPage</code> nodes are malformed or entirely absent.
        </div>
      </div>

    </div>
  </section>


  <!-- =========================================================
       §03 — DIAGNOSTIC MATRIX
  ========================================================= -->
  <section>
    <div class="section-header">
      <div class="section-tag">§ 03 — Multi-Dimensional Diagnostic Matrix</div>
      <div class="section-title">Brand AI Perception Score vs. Top 3 Competitors</div>
      <div class="section-desc">Composite signal strength analysis across four critical AI visibility dimensions. Scores derived from structured LLM sampling, entity graph analysis, and cross-platform citation frequency auditing.</div>
    </div>

    <div class="matrix-scroll">
      <table>
        <thead>
          <tr>
            <th>Dimension</th>
            <th class="th-own">Your Domain</th>
            <th>Competitor A</th>
            <th>Competitor B</th>
            <th>Competitor C</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>
              Neuromorphic Visibility
              <span class="dim-sub">LLM Knowledge Graph Presence</span>
            </td>
            <td><span class="chip chip-low">18</span></td>
            <td><span class="chip chip-high">82</span></td>
            <td><span class="chip chip-high">74</span></td>
            <td><span class="chip chip-mid">61</span></td>
          </tr>
          <tr>
            <td>
              Algorithmic Authority
              <span class="dim-sub">Cross-Platform Citation Weight</span>
            </td>
            <td><span class="chip chip-low">24</span></td>
            <td><span class="chip chip-high">88</span></td>
            <td><span class="chip chip-mid">67</span></td>
            <td><span class="chip chip-mid">55</span></td>
          </tr>
          <tr>
            <td>
              LLM Citation Rate
              <span class="dim-sub">Mention Frequency / 60 Queries</span>
            </td>
            <td><span class="chip chip-low">11%</span></td>
            <td><span class="chip chip-high">71%</span></td>
            <td><span class="chip chip-high">58%</span></td>
            <td><span class="chip chip-mid">43%</span></td>
          </tr>
          <tr>
            <td>
              Trust Signal Density
              <span class="dim-sub">Schema + Entity + Co-Citation Index</span>
            </td>
            <td><span class="chip chip-low">29</span></td>
            <td><span class="chip chip-high">91</span></td>
            <td><span class="chip chip-high">76</span></td>
            <td><span class="chip chip-mid">62</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="legend">
      <div class="leg-item"><div class="leg-dot" style="background:#10b981"></div>70–100 Strong Signal</div>
      <div class="leg-item"><div class="leg-dot" style="background:#f59e0b"></div>40–69 Contested Zone</div>
      <div class="leg-item"><div class="leg-dot" style="background:#ef4444"></div>0–39 Critical Deficit</div>
    </div>
  </section>

  <div class="divider"></div>


  <!-- =========================================================
       §04 — COMPETITIVE NEXUS
  ========================================================= -->
  <section style="margin-bottom:48px">
    <div class="section-header">
      <div class="section-tag">§ 04 — Competitive Nexus</div>
      <div class="section-title">AI Engine Perception Weight Distribution</div>
      <div class="section-desc">Estimated brand mention and citation-weight allocation across the three dominant AI search engines. Derived from structured prompt sampling across 60 category-level queries per engine.</div>
    </div>

    <div class="nexus-grid">

      <div class="nexus-card">
        <div class="nexus-header">
          <div class="eng-dot dot-p"></div>
          <div class="eng-name">Perplexity AI</div>
          <div class="eng-meta">60 queries sampled</div>
        </div>
        <div class="bar-rows">
          <div class="bar-row">
            <div class="bar-lbl bar-lbl-own">Your Domain</div>
            <div class="bar-track"><div class="bar-fill bf-own" style="width:9%"></div></div>
            <div class="bar-pct pct-own">9%</div>
          </div>
          <div class="bar-row">
            <div class="bar-lbl">Competitor A</div>
            <div class="bar-track"><div class="bar-fill bf-d1" style="width:42%"></div></div>
            <div class="bar-pct pct-d">42%</div>
          </div>
          <div class="bar-row">
            <div class="bar-lbl">Competitor B</div>
            <div class="bar-track"><div class="bar-fill bf-d2" style="width:31%"></div></div>
            <div class="bar-pct pct-n">31%</div>
          </div>
          <div class="bar-row">
            <div class="bar-lbl">Competitor C</div>
            <div class="bar-track"><div class="bar-fill bf-d3" style="width:18%"></div></div>
            <div class="bar-pct pct-n">18%</div>
          </div>
        </div>
      </div>

      <div class="nexus-card">
        <div class="nexus-header">
          <div class="eng-dot dot-c"></div>
          <div class="eng-name">ChatGPT Search Mode</div>
          <div class="eng-meta">60 queries sampled</div>
        </div>
        <div class="bar-rows">
          <div class="bar-row">
            <div class="bar-lbl bar-lbl-own">Your Domain</div>
            <div class="bar-track"><div class="bar-fill bf-own" style="width:7%"></div></div>
            <div class="bar-pct pct-own">7%</div>
          </div>
          <div class="bar-row">
            <div class="bar-lbl">Competitor A</div>
            <div class="bar-track"><div class="bar-fill bf-d1" style="width:48%"></div></div>
            <div class="bar-pct pct-d">48%</div>
          </div>
          <div class="bar-row">
            <div class="bar-lbl">Competitor B</div>
            <div class="bar-track"><div class="bar-fill bf-d2" style="width:28%"></div></div>
            <div class="bar-pct pct-n">28%</div>
          </div>
          <div class="bar-row">
            <div class="bar-lbl">Competitor C</div>
            <div class="bar-track"><div class="bar-fill bf-d3" style="width:17%"></div></div>
            <div class="bar-pct pct-n">17%</div>
          </div>
        </div>
      </div>

      <div class="nexus-card">
        <div class="nexus-header">
          <div class="eng-dot dot-g"></div>
          <div class="eng-name">Gemini / Google AI Overviews</div>
          <div class="eng-meta">60 queries sampled</div>
        </div>
        <div class="bar-rows">
          <div class="bar-row">
            <div class="bar-lbl bar-lbl-own">Your Domain</div>
            <div class="bar-track"><div class="bar-fill bf-own" style="width:16%"></div></div>
            <div class="bar-pct pct-own">16%</div>
          </div>
          <div class="bar-row">
            <div class="bar-lbl">Competitor A</div>
            <div class="bar-track"><div class="bar-fill bf-d1" style="width:38%"></div></div>
            <div class="bar-pct pct-d">38%</div>
          </div>
          <div class="bar-row">
            <div class="bar-lbl">Competitor B</div>
            <div class="bar-track"><div class="bar-fill bf-d2" style="width:27%"></div></div>
            <div class="bar-pct pct-n">27%</div>
          </div>
          <div class="bar-row">
            <div class="bar-lbl">Competitor C</div>
            <div class="bar-track"><div class="bar-fill bf-d3" style="width:19%"></div></div>
            <div class="bar-pct pct-n">19%</div>
          </div>
        </div>
      </div>

    </div>
  </section>


  <!-- =========================================================
       §05 — NEURAL COVERAGE MAP
  ========================================================= -->
  <section style="margin-bottom:48px">
    <div class="section-header">
      <div class="section-tag">§ 05 — Neural Coverage Map</div>
      <div class="section-title">User Intent Ownership Analysis — 14 Nodes Audited</div>
      <div class="section-desc">Each row represents a high-value semantic territory your brand should control. Status indicates the current AI citation ownership state across the three primary engines.</div>
    </div>

    <div class="coverage-table">
      <div class="coverage-head">
        <span>Query Intent / Node</span>
        <span>Vol / mo</span>
        <span>Current Owner</span>
        <span>Status</span>
      </div>

      <div class="cov-row">
        <div>
          <div class="cov-query">Best [category] tool for SaaS teams</div>
          <div class="cov-sub">Commercial intent — highest conversion proximity</div>
        </div>
        <div class="cov-vol">8,400</div>
        <div class="cov-owner ow-comp">Competitor A</div>
        <div><span class="status-chip sc-captured">Captured</span></div>
      </div>

      <div class="cov-row">
        <div>
          <div class="cov-query">[Your Brand] pricing and plans</div>
          <div class="cov-sub">Navigational — direct revenue intent</div>
        </div>
        <div class="cov-vol">3,200</div>
        <div class="cov-owner ow-self">Your Domain</div>
        <div><span class="status-chip sc-owned">Owned</span></div>
      </div>

      <div class="cov-row">
        <div>
          <div class="cov-query">[Category] alternative to [Competitor A]</div>
          <div class="cov-sub">Comparative — high switching intent, late funnel</div>
        </div>
        <div class="cov-vol">5,100</div>
        <div class="cov-owner ow-comp">Competitor B</div>
        <div><span class="status-chip sc-captured">Captured</span></div>
      </div>

      <div class="cov-row">
        <div>
          <div class="cov-query">How to automate [core use case]</div>
          <div class="cov-sub">Informational — top-of-funnel, high volume</div>
        </div>
        <div class="cov-vol">12,700</div>
        <div class="cov-owner ow-void">Uncontested</div>
        <div><span class="status-chip sc-void">Void</span></div>
      </div>

      <div class="cov-row">
        <div>
          <div class="cov-query">[Category] integrations with Slack and Notion</div>
          <div class="cov-sub">Feature-specific — integration research intent</div>
        </div>
        <div class="cov-vol">4,400</div>
        <div class="cov-owner ow-cont">Rotating</div>
        <div><span class="status-chip sc-contest">Contested</span></div>
      </div>

      <div class="cov-row">
        <div>
          <div class="cov-query">Enterprise [category] SOC2 and GDPR compliance</div>
          <div class="cov-sub">Enterprise intent — security and trust evaluation</div>
        </div>
        <div class="cov-vol">2,900</div>
        <div class="cov-owner ow-void">Uncontested</div>
        <div><span class="status-chip sc-void">Void</span></div>
      </div>

      <div class="cov-row">
        <div>
          <div class="cov-query">[Category] ROI metrics and case studies</div>
          <div class="cov-sub">Evaluation intent — final-stage decision support</div>
        </div>
        <div class="cov-vol">3,700</div>
        <div class="cov-owner ow-comp">Competitor A</div>
        <div><span class="status-chip sc-captured">Captured</span></div>
      </div>

      <div class="cov-row">
        <div>
          <div class="cov-query">What is [Your Brand] used for</div>
          <div class="cov-sub">Brand awareness — LLM knowledge graph entity node</div>
        </div>
        <div class="cov-vol">1,800</div>
        <div class="cov-owner ow-cont">Unstable</div>
        <div><span class="status-chip sc-contest">Contested</span></div>
      </div>

    </div>

    <div class="legend" style="margin-top:14px">
      <div class="leg-item"><div class="leg-dot" style="background:#10b981"></div>Owned — Your brand is the primary AI citation</div>
      <div class="leg-item"><div class="leg-dot" style="background:#ef4444"></div>Captured — Competitor holds the slot</div>
      <div class="leg-item"><div class="leg-dot" style="background:#f59e0b"></div>Contested — Citation is rotating (unstable)</div>
      <div class="leg-item"><div class="leg-dot" style="background:#475569"></div>Void — No brand owns this node (opportunity)</div>
    </div>
  </section>


  <!-- =========================================================
       §06 — NEURAL REPAIR BLUEPRINT
  ========================================================= -->
  <section style="margin-bottom:48px">
    <div class="section-header">
      <div class="section-tag">§ 06 — Actionable Neural Repair Blueprint</div>
      <div class="section-title">Precision Signal Remediation Protocol</div>
      <div class="section-desc">Three prioritized interventions derived directly from the pathology findings above. Each targets a specific failure node in your AI search architecture with defined execution steps and projected AEV recovery.</div>
    </div>

    <div class="blueprint-list">

      <!-- ── BLUEPRINT 01 ── -->
      <div class="bp-card">
        <div class="bp-num">01</div>
        <div>
          <div class="bp-title">Structured Data Injection — SoftwareApplication + FAQPage Node Rebuild</div>
          <div class="bp-desc">
            Your current JSON-LD implementation is missing the <code>applicationCategory</code>, <code>featureList</code>, and <code>aggregateRating</code> properties — all of which are primary signals for AI entity resolution pipelines. Deploy