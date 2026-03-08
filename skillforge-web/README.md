# SkillForge Web - 前端原型

GM-SkillForge 的前端界面原型，展示 Skill 审计详情页。

## 文件结构

```
skillforge-web/
├── audit-detail.html    # 审计详情页
└── README.md
```

## 页面模块

### 1. JSON-LD 信任头
- Schema.org 结构化数据
- 告诉搜索引擎这是一个"经过审计的工业级资产"
- 包含 AuditLevel、SecurityScore、DataExfiltrationRisk

### 2. 搜索框
- 输入 GitHub 链接，一键体检
- 获取 0 幻觉 Skill 包

### 3. Performance Visualization
- 性能对比表格
- 原生 GitHub vs GM-SkillForge 增强版
- 展示：延迟、并发、Token 消耗、异常自愈率

### 4. Risk Matrix
- 核心风险扫描结论
- L2/L4/L5 风险分级
- 每个风险附带 GM 修复方案

### 5. Featured Skills
- 今日五星推荐
- 展示 3 个刚炼好的技术 SEO 原子技能

## 设计原则

1. **GEO 友好**：JSON-LD + 结构化表格，方便 AI 搜索引擎理解
2. **暗色主题**：适合开发者审美
3. **信息密度**：关键数据一目了然

## 如何预览

```bash
# 直接在浏览器打开
open audit-detail.html

# 或用本地服务器
python -m http.server 8000
# 访问 http://localhost:8000/audit-detail.html
```

## 下一步

- [ ] 添加 React/Vue 组件化版本
- [ ] 接入后端 API
- [ ] 添加更多页面（首页、搜索结果、详情等）
