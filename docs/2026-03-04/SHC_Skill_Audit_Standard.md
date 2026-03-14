# SHC Skill Audit Standard v1.0 (De-sensitized)
# SHC Skill 安全审计标准 v1.0 (商业脱敏版)

*Guidance for deterministic security auditing of third-party OpenClaw Skills.*
*针对第三方 OpenClaw Skill 的确定性安全审计指南。*

---

## 🚩 Redline Patterns / 红线行为模式
*Any skill matching these patterns must be flagged as HIGH RISK (Level 5).*
*任何匹配以下模式的技能必须被标记为高风险（5级）。*

### 1. Unauthorized Ingress/Egress (越权通信)
- **Pattern**: `curl`, `wget`, `http`, `tls` outside the declared `API_ACCESS` list.
- **Risk**: Data exfiltration (Token theft), Command-and-Control (C2) callback.

### 2. Persistent Logic Injection (持久化注入)
- **Pattern**: `crontab`, `systemctl`, `init.d`, `rc.local`.
- **Risk**: Background persistence, bypassing temporary guard isolation.

### 3. Payload Obfuscation (载荷混淆)
- **Pattern**: `base64 -d`, `eval()`, `exec()`, `hex-to-bin`.
- **Risk**: Hiding malicious instructions from static text analysis.

### 4. Privilege Escalation (权限提升)
- **Pattern**: `sudo`, `chown`, `chmod +s`, `passwd`.
- **Risk**: Escaping the low-privilege sandbox restricted by Lobster Shield.

---

## 📊 Audit Score Tiers / 审计分级
- **💎 Verified (Green)**: 0 Redlines detected. Minimal permissions.
- **⚠️ Warning (Yellow)**: Read-only access to `/etc/` or non-standard environment variables.
- **🚫 Blocked (Red)**: Matches 1+ Redline patterns. Hard-blocked by SHC Gatekeepers.

---
## 🏆 Commercial Value / 商业价值
By using this standard, GM-SkillForge provides a **"Safe-to-Run"** guarantee for the Skill Marketplace, filling the gap where the SlowMist guide is "too technical" for end users.

---
*Status: Draft (Pending Phase 4 Implementation)*
