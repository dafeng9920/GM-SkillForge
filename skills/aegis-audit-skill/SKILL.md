---
name: aegis-audit-skill
description: OpenClaw 的“宙斯盾”自动审计系统。在代码提交或配置更新前进行多层敏感信息扫描，防止密钥、ID 或隐私数据泄露。
---

# aegis-audit-skill

## 触发条件

- 任何涉及 `git commit` 或 `git push` 的操作前
- 任何涉及 `openclaw.json` 或 `.env` 修改的操作后
- 需要对 workspace 中的敏感文件进行深度扫描时

## 核心功能

1. **Static Secret Scanning**: 扫描包括 API Keys, SSH Keys, Passwords 的正则匹配。
2. **Contextual Privacy Audit**: 识别并脱敏可能包含个人隐私信息（手机号、非公开 ID）的文本。
3. **Bloat Detection**: 自动识别并建议删除低质量、冗余的 AI 生成文本（针对“脱水策略”）。

## 输入 (Input)

```yaml
target_paths: 
  - "d:/GM-SkillForge/openclaw-box/data/openclaw.json"
  - "d:/GM-SkillForge/skills/custom-skill/"
scan_level: "STRICT" # LIGHT|NORMAL|STRICT
```

## 输出 (Output)

```yaml
audit_result: "PASS|FAIL|WARNING"
findings:
  - file: "openclaw.json"
    type: "KEY_EXPOSURE"
    risk_level: "HIGH"
    recommendation: "Use environment variables or placeholders."
  - file: "custom-skill/SKILL.md"
    type: "CONTENT_BLOAT"
    risk_level: "LOW"
    reduction_potential: "45%"
```

## DoD

- [ ] 正则库已覆盖所有已知敏感前缀（sk-, ai-, ssh-, etc.）
- [ ] 审计失败时强制拦截后续执行指令
- [ ] 生成脱敏后的预览文件供用户确认
