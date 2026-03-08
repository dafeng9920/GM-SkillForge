# Frontend v1.0 Aesthetic UI Rewrite

## Objective
The current React/Vite web application requires an aesthetic upgrade, but it must be a "Constrained Aesthetic Refactor". The goal is to elevate the UI to a premium GM.OS standard without sacrificing the core function of a governance console: clear information hierarchy and accessibility.

## Design Constraints & Execution Details (Commander Approved)
1. **Semantic Clarity**: `GateDecision`, `blocked_by`, `evidence_ref`, and `required_changes` MUST remain the most prominent information. Visual effects must never overpower data.
    - *Metric*: These fields must be visible above the fold and at least match headline typographical hierarchy.
2. **Design Tokens**: Replace the monolithic 45KB CSS file with a structured token system (color, space, radius, shadow, typography). No third-party dependencies.
3. **Accessibility (a11y) Hard Gates**: 
    - Contrast ratio >= WCAG AA for all key status cards.
    - Full keyboard Tab path accessibility. Focus rings CANNOT be visually hidden.
4. **Performance Budgets**: 
    - CSS increment strictly capped (+15KB gzip). 
    - Maximum of 3 distinct interaction animations globally. 
    - All complex animations MUST degrade or disable under `@media (prefers-reduced-motion)`.
5. **Aesthetic Restrictions**: 
    - *Neon*: Strictly reserved for state dots (PASS/BLOCK) and minimal borders. No large glowing surfaces.
    - *Glassmorphism*: Banned on primary information cards (must remain solid/high-contrast). Allowed only on secondary containers (e.g., sidebars).
6. **Rollback Strategy**: 
    - Changes must be atomic per component (Component + CSS Module in the same commit) to allow file-level reversions.

## Copywriting & Information Architecture (IA) Prep
Before visual styles are applied, harmonize all status copy (`ALLOW`, `BLOCK`, `REQUIRES_CHANGES`) across the application to ensure systemic consistency.

## Implementation Phases
We will implement this using pure CSS Modules and a global token system.

### Phase 1: Foundation (Design Tokens & A11y)
- [ ] Create `ui/app/src/styles/tokens.css` (variables for colors, spacing, typography).
- [ ] Establish base accessibility rules (focus rings, high-contrast text) in `global.css`.

### Phase 2: Component Proof of Concept (The Go/No-Go Gate)
- [ ] Harmonize Status Copy (`ALLOW`/`BLOCK`/`REQUIRES_CHANGES`).
- [ ] Refactor `BlockReasonCard.tsx` (Clear error hierarchy, strict neon usage).
- [ ] Refactor `DecisionHeroCard` (Solid background, clear PASS/BLOCK state).
- [ ] Refactor `ImportSkillPage.tsx` (Pipeline visualization).

**[GO/NO-GO REVIEW REQUIRED]**  
*At the end of Phase 2, a side-by-side Before/After screenshot comparison will be provided. If ANY constraint (a11y, perf, semantics) fails, Phase 3 is blocked.*

### Phase 3: Global Rollout (Post-Approval)
- [ ] Apply tokens to `Layout.tsx` and Navigation (using restricted glassmorphism here).
- [ ] Refactor `RunIntent.tsx`, `AuditPacks.tsx`, and `SystemHealth.tsx`.
