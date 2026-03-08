# experience-template-retriever-skill

> 版本: v0.1.0  
> 适用阶段: Experience Capture 检索与模板复用

---

## 触发词

- `按 IssueKey 检索经验`
- `按 FixKind 检索模板`
- `retrieve_templates`
- `经验库建议修复`
- `evolution.json 检索`

---

## 输入

```yaml
input:
  issue_key: string               # 可选
  fix_kind: string                # 可选
  evolution_file: string          # 默认 AuditPack/experience/evolution.json
  top_k: int                      # 默认 5
  require_evidence: bool          # 默认 true
  output_mode: string             # summary | detailed
```

---

## 步骤

1. 读取 `evolution.json`，过滤 `MISSING_EVIDENCE` 条目。  
2. 按 `issue_key` 精确匹配；不足时按 `fix_kind` 回退检索。  
3. 基于 `ContentHash` 去重，选取最近且可复核条目。  
4. 输出修复模板建议：`Summary/FixKind/EvidenceRef/适用边界`。  
5. 记录检索命中率与未命中原因。  

---

## DoD

- 至少返回 1 条可复核模板，或明确 `NO_MATCH_FOUND`。  
- 所有返回项都带 `EvidenceRef`。  
- 输出包含检索条件与命中统计。  
- 不修改源码，仅提供建议模板与证据链接。  

---

## 失败处理

| 场景 | 处理 |
|---|---|
| evolution.json 不存在 | 返回 `EXPERIENCE_STORE_MISSING` |
| 全部条目无证据 | 返回 `NO_AUDITABLE_EXPERIENCE` |
| issue_key/fix_kind 都缺失 | 返回 `INVALID_QUERY` |
| top_k 过大 | 自动裁剪并警告 |

